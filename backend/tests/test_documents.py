from uuid import UUID

import pytest
from sqlalchemy import func, select

from app.db.models import AuditLog, Client, Document
from app.domain.enums import ClientStatus, DocumentStatus
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


async def test_txt_ingestion_list_detail_and_soft_delete(
    api_context: ApiTestContext,
) -> None:
    owner = api_context.create_identity(
        email="docs@example.com",
        organization_name="Docs Org",
        organization_slug="docs-org",
    )
    client = create_client(api_context, owner, "docs-client")
    headers = auth_headers(owner.token)
    url = f"/api/v1/clients/{client.id}/documents"
    text = ("ResolveOps support policy. " * 20).encode()

    uploaded = await api_context.client.post(
        url,
        headers=headers,
        files={"file": ("support.txt", text, "text/plain")},
    )
    assert uploaded.status_code == 201, uploaded.text
    document = uploaded.json()
    assert document["status"] == "processed"
    assert document["file_type"] == "txt"
    assert document["indexing_status"] == "not_indexed"
    assert len(document["chunks"]) > 1
    assert [chunk["chunk_index"] for chunk in document["chunks"]] == list(
        range(len(document["chunks"]))
    )
    assert all(chunk["content"].strip() for chunk in document["chunks"])
    assert all(
        chunk["metadata"]["client_id"] == str(client.id) for chunk in document["chunks"]
    )

    listing = await api_context.client.get(url, headers=headers)
    detail = await api_context.client.get(f"{url}/{document['id']}", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["pagination"]["total"] == 1
    assert detail.status_code == 200
    assert detail.json()["id"] == document["id"]

    deleted = await api_context.client.delete(
        f"{url}/{document['id']}", headers=headers
    )
    assert deleted.status_code == 204
    assert (
        await api_context.client.get(f"{url}/{document['id']}", headers=headers)
    ).status_code == 404
    assert (await api_context.client.get(url, headers=headers)).json()["pagination"][
        "total"
    ] == 0

    with api_context.session_factory() as session:
        stored = session.get(Document, UUID(document["id"]))
        assert stored is not None
        assert stored.deleted_at is not None
        assert stored.status == DocumentStatus.PROCESSED
        audit_count = session.scalar(
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.resource_id == stored.id)
        )
        assert audit_count == 2


async def test_markdown_ingestion_extracts_title(api_context: ApiTestContext) -> None:
    owner = api_context.create_identity(
        email="markdown@example.com",
        organization_name="Markdown Org",
        organization_slug="markdown-org",
    )
    client = create_client(api_context, owner, "markdown-client")
    response = await api_context.client.post(
        f"/api/v1/clients/{client.id}/documents",
        headers=auth_headers(owner.token),
        files={
            "file": (
                "refund-policy.md",
                b"# Refund Policy\n\nCustomers can request a refund within 30 days.",
                "text/markdown",
            )
        },
    )

    assert response.status_code == 201, response.text
    assert response.json()["title"] == "Refund Policy"
    assert response.json()["file_type"] == "markdown"


async def test_unsupported_document_is_rejected(api_context: ApiTestContext) -> None:
    owner = api_context.create_identity(
        email="unsupported@example.com",
        organization_name="Unsupported Org",
        organization_slug="unsupported-org",
    )
    client = create_client(api_context, owner, "unsupported-client")
    response = await api_context.client.post(
        f"/api/v1/clients/{client.id}/documents",
        headers=auth_headers(owner.token),
        files={"file": ("archive.zip", b"PK-not-supported", "application/zip")},
    )

    assert response.status_code == 422
    with api_context.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(Document)) == 0


async def test_document_routes_are_tenant_scoped(api_context: ApiTestContext) -> None:
    organization_a = api_context.create_identity(
        email="docs-a@example.com",
        organization_name="Docs A",
        organization_slug="docs-a",
    )
    organization_b = api_context.create_identity(
        email="docs-b@example.com",
        organization_name="Docs B",
        organization_slug="docs-b",
    )
    client_b = create_client(api_context, organization_b, "docs-client-b")
    upload = await api_context.client.post(
        f"/api/v1/clients/{client_b.id}/documents",
        headers=auth_headers(organization_b.token),
        files={"file": ("private.txt", b"Tenant B private knowledge", "text/plain")},
    )
    assert upload.status_code == 201
    document_id = upload.json()["id"]
    url = f"/api/v1/clients/{client_b.id}/documents/{document_id}"
    headers_a = auth_headers(organization_a.token)

    assert (await api_context.client.get(url, headers=headers_a)).status_code == 404
    assert (await api_context.client.delete(url, headers=headers_a)).status_code == 404

    with api_context.session_factory() as session:
        untouched = session.get(Document, UUID(document_id))
        assert untouched is not None
        assert untouched.deleted_at is None
