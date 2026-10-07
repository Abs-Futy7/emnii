import json

import pytest

from app.db.models import Client
from app.domain.enums import ClientStatus
from tests.conftest import ApiTestContext, Identity

pytestmark = pytest.mark.anyio


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_client(context: ApiTestContext, identity: Identity, slug: str) -> Client:
    with context.session_factory() as session:
        client = Client(
            organization_id=identity.organization.id,
            name=slug.title(),
            slug=slug,
            status=ClientStatus.ACTIVE,
        )
        session.add(client)
        session.commit()
        return client


async def upload_pii_dataset(
    context: ApiTestContext, identity: Identity, client: Client
) -> dict[str, object]:
    content = (
        b"Customer Name,address,email,phone,ip,card\n"
        b'John Doe,"10 Main Street",john@example.com,+8801712345678,'
        b"192.168.1.10,4111111111111111\n"
    )
    response = await context.client.post(
        f"/api/v1/clients/{client.id}/datasets",
        headers=auth_headers(identity.token),
        files={"file": ("pii.csv", content, "text/csv")},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_pii_scan_uses_schema_context_and_never_returns_raw_samples(
    api_context: ApiTestContext,
) -> None:
    owner = api_context.create_identity(
        email="pii@example.com",
        organization_name="PII Org",
        organization_slug="pii-org",
    )
    client = create_client(api_context, owner, "pii-client")
    dataset = await upload_pii_dataset(api_context, owner, client)
    base_url = f"/api/v1/clients/{client.id}/datasets/{dataset['id']}"
    headers = auth_headers(owner.token)

    detected_schema = await api_context.client.post(
        f"{base_url}/schema/detect", headers=headers
    )
    assert detected_schema.status_code == 200, detected_schema.text

    scanned = await api_context.client.post(f"{base_url}/pii/scan", headers=headers)
    assert scanned.status_code == 201, scanned.text
    report = scanned.json()
    assert report["status"] == "completed"
    assert report["findings_count"] == 6
    assert {finding["pii_type"] for finding in report["findings"]} == {
        "EMAIL",
        "PHONE",
        "IP_ADDRESS",
        "CREDIT_CARD",
        "PERSON_NAME",
        "ADDRESS",
    }

    serialized = json.dumps(report)
    for raw_value in (
        "John Doe",
        "10 Main Street",
        "john@example.com",
        "+8801712345678",
        "192.168.1.10",
        "4111111111111111",
    ):
        assert raw_value not in serialized

    latest = await api_context.client.get(f"{base_url}/pii", headers=headers)
    assert latest.status_code == 200
    assert latest.json() == report


async def test_pii_routes_do_not_expose_another_tenant(
    api_context: ApiTestContext,
) -> None:
    organization_a = api_context.create_identity(
        email="pii-a@example.com",
        organization_name="PII A",
        organization_slug="pii-a",
    )
    organization_b = api_context.create_identity(
        email="pii-b@example.com",
        organization_name="PII B",
        organization_slug="pii-b",
    )
    client_b = create_client(api_context, organization_b, "pii-client-b")
    dataset_b = await upload_pii_dataset(api_context, organization_b, client_b)
    base_url = f"/api/v1/clients/{client_b.id}/datasets/{dataset_b['id']}/pii"
    headers_a = auth_headers(organization_a.token)

    scan = await api_context.client.post(f"{base_url}/scan", headers=headers_a)
    latest = await api_context.client.get(base_url, headers=headers_a)

    assert scan.status_code == 404
    assert latest.status_code == 404
