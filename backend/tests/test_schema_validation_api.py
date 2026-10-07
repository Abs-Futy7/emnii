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


async def upload_dataset(
    context: ApiTestContext, identity: Identity, client: Client
) -> dict[str, object]:
    csv_content = (
        b"cust_id,cust_nm,mob_no,email_address,created_date,code\n"
        b"1,Alice,+12025550100,alice@example.com,2025-01-01,A\n"
        b"2,Bob,12,invalid-email,not-a-date,B\n"
        b"2,Robert,+12025550102,robert@example.com,2025-01-03,C\n"
    )
    response = await context.client.post(
        f"/api/v1/clients/{client.id}/datasets",
        headers=auth_headers(identity.token),
        files={"file": ("customers.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_schema_detection_override_and_validation_workflow(
    api_context: ApiTestContext,
) -> None:
    owner = api_context.create_identity(
        email="quality@example.com",
        organization_name="Quality Org",
        organization_slug="quality-org",
    )
    client = create_client(api_context, owner, "quality-client")
    dataset = await upload_dataset(api_context, owner, client)
    schema_url = f"/api/v1/clients/{client.id}/datasets/{dataset['id']}/schema"
    headers = auth_headers(owner.token)

    detected = await api_context.client.post(f"{schema_url}/detect", headers=headers)
    assert detected.status_code == 200, detected.text
    by_source = {item["source_column"]: item for item in detected.json()}
    assert by_source["cust_nm"]["suggested_field"] == "customer_name"
    assert by_source["mob_no"]["suggested_field"] == "phone"
    assert by_source["email_address"]["suggested_field"] == "email"
    assert by_source["created_date"]["suggested_field"] == "created_at"
    assert by_source["code"]["suggested_field"] is None

    overrides = [
        {
            "source_column": source,
            "target_field": mapping["suggested_field"],
            "status": "approved",
        }
        for source, mapping in by_source.items()
        if mapping["suggested_field"] is not None
    ]
    overrides.append(
        {"source_column": "code", "target_field": None, "status": "ignored"}
    )
    updated = await api_context.client.put(
        schema_url,
        headers=headers,
        json={"mappings": overrides},
    )
    assert updated.status_code == 200, updated.text
    assert all(item["manually_overridden"] for item in updated.json())

    fetched = await api_context.client.get(schema_url, headers=headers)
    assert fetched.status_code == 200
    assert fetched.json() == updated.json()

    validation_url = f"/api/v1/clients/{client.id}/datasets/{dataset['id']}/validate"
    validation = await api_context.client.post(validation_url, headers=headers)
    assert validation.status_code == 200, validation.text
    report = validation.json()
    assert report["status"] == "completed"
    assert report["total_records"] == 3
    assert report["valid_records"] == 1
    assert report["error_count"] == 2
    assert report["dimensions"] == {
        "completeness": 100.0,
        "validity": 66.67,
        "uniqueness": 66.67,
        "consistency": 100.0,
    }
    assert report["quality_score"] == 81.67
    assert all(len(issue["example_rows"]) <= 5 for issue in report["issues"])

    latest = await api_context.client.get(
        validation_url.replace("/validate", "/validation/latest"),
        headers=headers,
    )
    assert latest.status_code == 200
    assert latest.json()["id"] == report["id"]


async def test_schema_and_validation_are_tenant_scoped(
    api_context: ApiTestContext,
) -> None:
    organization_a = api_context.create_identity(
        email="schema-a@example.com",
        organization_name="Schema A",
        organization_slug="schema-a",
    )
    organization_b = api_context.create_identity(
        email="schema-b@example.com",
        organization_name="Schema B",
        organization_slug="schema-b",
    )
    client_b = create_client(api_context, organization_b, "tenant-b-schema")
    dataset_b = await upload_dataset(api_context, organization_b, client_b)
    base_url = f"/api/v1/clients/{client_b.id}/datasets/{dataset_b['id']}"
    headers_a = auth_headers(organization_a.token)

    detect = await api_context.client.post(
        f"{base_url}/schema/detect", headers=headers_a
    )
    schema = await api_context.client.get(f"{base_url}/schema", headers=headers_a)
    validate = await api_context.client.post(f"{base_url}/validate", headers=headers_a)
    latest = await api_context.client.get(
        f"{base_url}/validation/latest", headers=headers_a
    )

    assert detect.status_code == 404
    assert schema.status_code == 404
    assert validate.status_code == 404
    assert latest.status_code == 404
