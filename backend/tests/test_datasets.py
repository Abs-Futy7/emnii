import json
from io import BytesIO
from uuid import UUID

import pandas as pd
import pytest
from sqlalchemy import func, select

from app.db.models import AuditLog, Client, Dataset
from app.domain.enums import ClientStatus
from tests.conftest import ApiTestContext

pytestmark = pytest.mark.anyio


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_client_record(context: ApiTestContext, organization_id: UUID) -> Client:
    with context.session_factory() as session:
        client = Client(
            organization_id=organization_id,
            name="ShopNest",
            slug="shopnest",
            status=ClientStatus.ACTIVE,
        )
        session.add(client)
        session.commit()
        return client


def xlsx_fixture() -> bytes:
    buffer = BytesIO()
    pd.DataFrame(
        {
            "customer_id": [1, 2],
            "email": ["one@example.com", "two@example.com"],
        }
    ).to_excel(buffer, index=False)
    return buffer.getvalue()


async def test_upload_parse_list_and_get_structured_datasets(
    api_context: ApiTestContext,
) -> None:
    owner = api_context.create_identity(
        email="uploader@example.com",
        organization_name="Upload Org",
        organization_slug="upload-org",
    )
    client = create_client_record(api_context, owner.organization.id)
    headers = auth_headers(owner.token)
    fixtures = [
        (
            "customers.csv",
            "text/csv",
            b"customer_id,email,active\n1,one@example.com,true\n2,,false\n",
        ),
        (
            "customers.json",
            "application/json",
            json.dumps(
                [
                    {"customer_id": 1, "email": "one@example.com"},
                    {"customer_id": 2, "email": "two@example.com"},
                ]
            ).encode(),
        ),
        (
            "customers.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            xlsx_fixture(),
        ),
    ]

    uploaded: list[dict[str, object]] = []
    for filename, content_type, content in fixtures:
        response = await api_context.client.post(
            f"/api/v1/clients/{client.id}/datasets",
            headers=headers,
            files={"file": (filename, content, content_type)},
        )
        assert response.status_code == 201, response.text
        uploaded.append(response.json())

    csv_dataset = uploaded[0]
    assert csv_dataset["original_filename"] == "customers.csv"
    assert csv_dataset["row_count"] == 2
    assert csv_dataset["column_count"] == 3
    assert csv_dataset["status"] == "needs_review"
    assert len(csv_dataset["columns"]) == 3
    email_column = next(
        column for column in csv_dataset["columns"] if column["source_name"] == "email"
    )
    assert email_column["null_count"] == 1
    assert email_column["unique_count"] == 1

    listing = await api_context.client.get(
        f"/api/v1/clients/{client.id}/datasets",
        headers=headers,
    )
    assert listing.status_code == 200
    assert listing.json()["pagination"]["total"] == 3

    detail = await api_context.client.get(
        f"/api/v1/clients/{client.id}/datasets/{csv_dataset['id']}",
        headers=headers,
    )
    assert detail.status_code == 200
    assert detail.json()["columns"] == csv_dataset["columns"]

    with api_context.session_factory() as session:
        stored = session.get(Dataset, UUID(str(csv_dataset["id"])))
        assert stored is not None
        assert stored.stored_filename != stored.original_filename
        assert "/" not in stored.stored_filename
        assert (api_context.settings.upload_dir / stored.stored_filename).is_file()
        audit_count = session.scalar(
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.action == "dataset.uploaded")
        )
        assert audit_count == 3


async def test_malformed_and_oversized_uploads_are_rejected(
    api_context: ApiTestContext,
) -> None:
    owner = api_context.create_identity(
        email="limits@example.com",
        organization_name="Limits Org",
        organization_slug="limits-org",
    )
    client = create_client_record(api_context, owner.organization.id)
    headers = auth_headers(owner.token)

    malformed_files = [
        ("broken.csv", b'a,b\n"unterminated,2\n', "text/csv"),
        ("broken.json", b"{not-json", "application/json"),
        (
            "broken.xlsx",
            b"PK-not-a-real-workbook",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
    ]
    for filename, content, content_type in malformed_files:
        malformed = await api_context.client.post(
            f"/api/v1/clients/{client.id}/datasets",
            headers=headers,
            files={"file": (filename, content, content_type)},
        )
        assert malformed.status_code == 422

    oversized = await api_context.client.post(
        f"/api/v1/clients/{client.id}/datasets",
        headers=headers,
        files={"file": ("huge.csv", b"a" * (1024 * 1024 + 1), "text/csv")},
    )

    assert oversized.status_code == 413
    with api_context.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(Dataset)) == 0


async def test_dataset_upload_validates_client_tenant_ownership(
    api_context: ApiTestContext,
) -> None:
    organization_a = api_context.create_identity(
        email="dataset-a@example.com",
        organization_name="Dataset A",
        organization_slug="dataset-a",
    )
    organization_b = api_context.create_identity(
        email="dataset-b@example.com",
        organization_name="Dataset B",
        organization_slug="dataset-b",
    )
    client_b = create_client_record(api_context, organization_b.organization.id)

    response = await api_context.client.post(
        f"/api/v1/clients/{client_b.id}/datasets",
        headers=auth_headers(organization_a.token),
        files={"file": ("customers.csv", b"id,name\n1,Alice\n", "text/csv")},
    )

    assert response.status_code == 404
