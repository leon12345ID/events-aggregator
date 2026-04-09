import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from src.db.models import Event, SyncMetadata, Ticket


class EventRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_list(self, date_from: str | None = None, page: int = 1, page_size: int = 20) -> list[Event]:
        query = select(Event).options(selectinload(Event.place))
        if date_from:
            query = query.where(Event.event_time >= date_from)
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = self.session.execute(query)
        return result.scalars().all()

    def count(self, date_from: str | None = None) -> int:
        query = select(func.count()).select_from(Event)
        if date_from:
            query = query.where(Event.event_time >= date_from)
        result = self.session.execute(query)
        return result.scalar_one()

    def get_by_id(self, event_id: str) -> Event | None:
        query = select(Event).options(selectinload(Event.place)).where(Event.id == uuid.UUID(event_id))
        result = self.session.execute(query)
        return result.scalar_one_or_none()

class TicketRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, event_id: str, ticket_id: str, first_name: str, last_name: str, email: str, seat: str) -> Ticket:
        ticket = Ticket(
            external_ticket_id=ticket_id,
            event_id=uuid.UUID(event_id),
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat
        )
        self.session.add(ticket)
        self.session.commit()
        return ticket

    def delete(self, ticket_id: str) -> None:
        self.session.execute(delete(Ticket).where(Ticket.external_ticket_id == ticket_id))
        self.session.commit()

class SyncMetadataRepository:

    def __init__(self, session: Session):
        self.session = session

    def get(self) -> SyncMetadata | None:
        result = self.session.execute(select(SyncMetadata).limit(1))
        return result.scalar_one_or_none()

    def update(self, last_changed_at: str, status: str = "idle") -> SyncMetadata:
        metadata = self.get()
        if metadata:
            metadata.last_changed_at = last_changed_at
            metadata.sync_status = status
        else:
            metadata = SyncMetadata(last_changed_at=last_changed_at, sync_status=status)
            self.session.add(metadata)
        self.session.commit()
        return metadata
