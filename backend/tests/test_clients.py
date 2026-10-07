import pytest
from sqlalchemy import func, select

from app.db.models import AuditLog, Client
from app.domain.enums import ClientStatus, OrganizationRole
from tests.conftest import ApiTestContext

pytestmark = pytest.mark.anyio


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def create_client(
    context: ApiTestContext,
    token: str,
    *,
    name: str = "ShopNest",
    slug: str = "shopnest",
    industry: str = "E-commerce",
) -> dict[str, object]:
    response = await context.client.post(
        "/api/v1/clients",
        headers=auth_headers(token),
        json={"name": name, "slug": slug, "industry": industry},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_client_crud_filters_pagination_and_audit(
    api_context: ApiTestContext,
) -> None:
    owner = api_context.create_identity(
        email="owner@example.com",
        organization_name="SupportOps A",
        organization_slug="supportops-a",
    )
    first = await create_client(api_context, owner.token)
    await create_client(
        api_context,
        owner.token,
        name="TechMart",
        slug="techmart",
        industry="Technology",
    )

    filtered = await api_context.client.get(
        "/api/v1/clients",
        headers=auth_headers(owner.token),
        params={
            "page": 1,
            "page_size": 10,
            "search": "shop",
            "status": "onboarding",
            "industry": "E-commerce",
        },
    )
    assert filtered.status_code == 200
    assert [item["name"] for item in filtered.json()["items"]] == ["ShopNest"]
    assert filtered.json()["pagination"] == {
        "page": 1,
        "page_size": 10,
        "total": 1,
        "total_pages": 1,
    }

    updated = await api_context.client.patch(
        f"/api/v1/clients/{first['id']}",
        headers=auth_headers(owner.token),
        json={"industry": "Retail", "status": "active"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "active"

    disabled = await api_context.client.delete(
        f"/api/v1/clients/{first['id']}",
        headers=auth_headers(owner.token),
    )
    assert disabled.status_code == 204

    fetched = await api_context.client.get(
        f"/api/v1/clients/{first['id']}",
        headers=auth_headers(owner.token),
    )
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "disabled"

    with api_context.session_factory() as session:
        audit_count = session.scalar(
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.organization_id == owner.organization.id)
        )
        assert audit_count == 4


async def test_agent_can_read_but_cannot_mutate_clients(
    api_context: ApiTestContext,
) -> None:
    agent = api_context.create_identity(
        email="agent@example.com",
        organization_name="Agent Org",
        organization_slug="agent-org",
        role=OrganizationRole.AGENT,
    )

    create_response = await api_context.client.post(
        "/api/v1/clients",
        headers=auth_headers(agent.token),
        json={"name": "Blocked", "slug": "blocked"},
    )
    list_response = await api_context.client.get(
        "/api/v1/clients",
        headers=auth_headers(agent.token),
    )

    assert create_response.status_code == 403
    assert list_response.status_code == 200


async def test_client_routes_do_not_expose_another_tenant(
    api_context: ApiTestContext,
) -> None:
    organization_a = api_context.create_identity(
        email="owner-a@example.com",
        organization_name="Organization A",
        organization_slug="organization-a",
    )
    organization_b = api_context.create_identity(
        email="owner-b@example.com",
        organization_name="Organization B",
        organization_slug="organization-b",
    )
    with api_context.session_factory() as session:
        client_b = Client(
            organization_id=organization_b.organization.id,
            name="Tenant B Client",
            slug="tenant-b-client",
            status=ClientStatus.ACTIVE,
        )
        session.add(client_b)
        session.commit()
        client_b_id = client_b.id

    headers = auth_headers(organization_a.token)
    get_response = await api_context.client.get(
        f"/api/v1/clients/{client_b_id}",
        headers=headers,
    )
    patch_response = await api_context.client.patch(
        f"/api/v1/clients/{client_b_id}",
        headers=headers,
        json={"name": "Compromised"},
    )
    delete_response = await api_context.client.delete(
        f"/api/v1/clients/{client_b_id}",
        headers=headers,
    )

    assert get_response.status_code == 404
    assert patch_response.status_code == 404
    assert delete_response.status_code == 404

    with api_context.session_factory() as session:
        untouched = session.get(Client, client_b_id)
        assert untouched is not None
        assert untouched.name == "Tenant B Client"
        assert untouched.status == ClientStatus.ACTIVE
