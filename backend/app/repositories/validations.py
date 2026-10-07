from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import ValidationRun


class ValidationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, validation_run: ValidationRun) -> None:
        self.session.add(validation_run)

    def latest(
        self, organization_id: UUID, client_id: UUID, dataset_id: UUID
    ) -> ValidationRun | None:
        statement = (
            select(ValidationRun)
            .options(selectinload(ValidationRun.issues))
            .where(
                ValidationRun.organization_id == organization_id,
                ValidationRun.client_id == client_id,
                ValidationRun.dataset_id == dataset_id,
            )
            .order_by(ValidationRun.started_at.desc(), ValidationRun.id.desc())
            .limit(1)
        )
        return self.session.scalar(statement)
