from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Dataset


class DatasetRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, dataset: Dataset) -> None:
        self.session.add(dataset)

    def get(
        self,
        organization_id: UUID,
        client_id: UUID,
        dataset_id: UUID,
    ) -> Dataset | None:
        statement = (
            select(Dataset)
            .options(selectinload(Dataset.columns))
            .where(
                Dataset.organization_id == organization_id,
                Dataset.client_id == client_id,
                Dataset.id == dataset_id,
            )
        )
        return self.session.scalar(statement)

    def list(
        self,
        organization_id: UUID,
        client_id: UUID,
        *,
        offset: int,
        limit: int,
    ) -> tuple[list[Dataset], int]:
        filters = (
            Dataset.organization_id == organization_id,
            Dataset.client_id == client_id,
        )
        total = (
            self.session.scalar(
                select(func.count()).select_from(Dataset).where(*filters)
            )
            or 0
        )
        statement = (
            select(Dataset)
            .where(*filters)
            .order_by(Dataset.created_at.desc(), Dataset.id)
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.scalars(statement)), total
