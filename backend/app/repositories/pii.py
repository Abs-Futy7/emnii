from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import PIIScan


class PIIRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, scan: PIIScan) -> None:
        self.session.add(scan)

    def latest(
        self, organization_id: UUID, client_id: UUID, dataset_id: UUID
    ) -> PIIScan | None:
        statement = (
            select(PIIScan)
            .options(selectinload(PIIScan.findings))
            .where(
                PIIScan.organization_id == organization_id,
                PIIScan.client_id == client_id,
                PIIScan.dataset_id == dataset_id,
            )
            .order_by(PIIScan.created_at.desc(), PIIScan.id.desc())
            .limit(1)
        )
        return self.session.scalar(statement)
