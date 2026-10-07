from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Document


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, document: Document) -> None:
        self.session.add(document)

    def get(
        self,
        organization_id: UUID,
        client_id: UUID,
        document_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> Document | None:
        filters = [
            Document.organization_id == organization_id,
            Document.client_id == client_id,
            Document.id == document_id,
        ]
        if not include_deleted:
            filters.append(Document.deleted_at.is_(None))
        statement = (
            select(Document).options(selectinload(Document.chunks)).where(*filters)
        )
        return self.session.scalar(statement)

    def list(
        self,
        organization_id: UUID,
        client_id: UUID,
        *,
        offset: int,
        limit: int,
    ) -> tuple[list[Document], int]:
        filters = (
            Document.organization_id == organization_id,
            Document.client_id == client_id,
            Document.deleted_at.is_(None),
        )
        total = (
            self.session.scalar(
                select(func.count()).select_from(Document).where(*filters)
            )
            or 0
        )
        statement = (
            select(Document)
            .where(*filters)
            .order_by(Document.created_at.desc(), Document.id)
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.scalars(statement)), total
