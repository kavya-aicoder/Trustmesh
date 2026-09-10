from dataclasses import dataclass

from sqlalchemy import select

from app.db.models import ResourceRecord
from app.db.session import SessionLocal


@dataclass(frozen=True)
class Resource:
    resource_id: str
    name: str
    resource_type: str
    application: str
    owner: str
    status: str
    access_level: str


class ResourceService:
    """PostgreSQL-backed resource service."""

    def list_resources(self) -> list[Resource]:
        with SessionLocal() as db:
            records = db.scalars(
                select(ResourceRecord).order_by(ResourceRecord.name)
            ).all()

        return [
            Resource(
                resource_id=record.id,
                name=record.name,
                resource_type=record.resource_type,
                application=record.application,
                owner=record.owner,
                status=record.status,
                access_level=record.access_level,
            )
            for record in records
        ]

    def get_resource(self, resource_id: str) -> Resource | None:
        with SessionLocal() as db:
            record = db.get(ResourceRecord, resource_id)

        if record is None:
            return None

        return Resource(
            resource_id=record.id,
            name=record.name,
            resource_type=record.resource_type,
            application=record.application,
            owner=record.owner,
            status=record.status,
            access_level=record.access_level,
        )


resource_service = ResourceService()
