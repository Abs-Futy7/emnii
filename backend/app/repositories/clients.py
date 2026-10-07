from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Client
from app.domain.enums import ClientStatus


class ClientRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, client: Client) -> None:
        self.session.add(client)

    def get(self, organization_id: UUID, client_id: UUID) -> Client | None:
        statement = select(Client).where(
            Client.organization_id == organization_id,
            Client.id == client_id,
        )
        return self.session.scalar(statement)

    def slug_exists(
        self,
        organization_id: UUID,
        slug: str,
        *,
        exclude_client_id: UUID | None = None,
    ) -> bool:
        statement = select(Client.id).where(
            Client.organization_id == organization_id,
            Client.slug == slug,
        )
        if exclude_client_id is not None:
            statement = statement.where(Client.id != exclude_client_id)
        return self.session.scalar(statement.limit(1)) is not None

    def list(
        self,
        organization_id: UUID,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        status: ClientStatus | None = None,
        industry: str | None = None,
    ) -> tuple[list[Client], int]:
        filters = [Client.organization_id == organization_id]
        if search:
            filters.append(Client.name.ilike(f"%{search}%"))
        if status is not None:
            filters.append(Client.status == status)
        if industry:
            filters.append(func.lower(Client.industry) == industry.lower())

        total = (
            self.session.scalar(
                select(func.count()).select_from(Client).where(*filters)
            )
            or 0
        )
        statement = (
            select(Client)
            .where(*filters)
            .order_by(Client.name, Client.id)
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.scalars(statement)), total
