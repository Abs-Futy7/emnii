from dataclasses import dataclass
from math import ceil
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.db.models import Client
from app.domain.enums import ClientStatus
from app.repositories.audit_logs import AuditLogRepository
from app.repositories.clients import ClientRepository
from app.schemas.client import ClientCreate, ClientUpdate


@dataclass(frozen=True)
class ClientPage:
    items: list[Client]
    page: int
    page_size: int
    total: int
    total_pages: int


class ClientService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.clients = ClientRepository(session)
        self.audit_logs = AuditLogRepository(session)

    def create(
        self,
        organization_id: UUID,
        actor_id: UUID,
        payload: ClientCreate,
    ) -> Client:
        if self.clients.slug_exists(organization_id, payload.slug):
            raise ConflictError("A client with this slug already exists")

        client = Client(organization_id=organization_id, **payload.model_dump())
        self.clients.add(client)
        try:
            self.session.flush()
            self.audit_logs.add(
                organization_id=organization_id,
                user_id=actor_id,
                client_id=client.id,
                action="client.created",
                resource_type="client",
                resource_id=client.id,
                metadata={"name": client.name, "slug": client.slug},
            )
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("A client with this slug already exists") from exc

        self.session.refresh(client)
        return client

    def list(
        self,
        organization_id: UUID,
        *,
        page: int,
        page_size: int,
        search: str | None,
        status: ClientStatus | None,
        industry: str | None,
    ) -> ClientPage:
        items, total = self.clients.list(
            organization_id,
            offset=(page - 1) * page_size,
            limit=page_size,
            search=search,
            status=status,
            industry=industry,
        )
        return ClientPage(items, page, page_size, total, ceil(total / page_size))

    def get(self, organization_id: UUID, client_id: UUID) -> Client:
        client = self.clients.get(organization_id, client_id)
        if client is None:
            raise NotFoundError("Client not found")
        return client

    def update(
        self,
        organization_id: UUID,
        actor_id: UUID,
        client_id: UUID,
        payload: ClientUpdate,
    ) -> Client:
        client = self.get(organization_id, client_id)
        changes = payload.model_dump(exclude_unset=True)
        new_slug = changes.get("slug")
        if isinstance(new_slug, str) and self.clients.slug_exists(
            organization_id,
            new_slug,
            exclude_client_id=client.id,
        ):
            raise ConflictError("A client with this slug already exists")

        for field, value in changes.items():
            setattr(client, field, value)

        if changes:
            self.audit_logs.add(
                organization_id=organization_id,
                user_id=actor_id,
                client_id=client.id,
                action="client.updated",
                resource_type="client",
                resource_id=client.id,
                metadata={"changed_fields": sorted(changes)},
            )
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("Client update conflicts with existing data") from exc

        self.session.refresh(client)
        return client

    def disable(
        self,
        organization_id: UUID,
        actor_id: UUID,
        client_id: UUID,
    ) -> None:
        client = self.get(organization_id, client_id)
        if client.status != ClientStatus.DISABLED:
            client.status = ClientStatus.DISABLED
            self.audit_logs.add(
                organization_id=organization_id,
                user_id=actor_id,
                client_id=client.id,
                action="client.disabled",
                resource_type="client",
                resource_id=client.id,
            )
            self.session.commit()
