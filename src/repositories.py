import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from src.db.models import Event, Place, SyncMetadata, Ticket


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

    def get_list_with_count(self, date_from: Optional[str] = None, page: int = 1, page_size: int = 20):
        events = self.get_list(date_from, page, page_size)
        total = self.count(date_from)
        return events, total

    def get_by_id(self, event_id: str) -> Event | None:
        try:
            uid = uuid.UUID(event_id)
        except ValueError:
            return None
        query = select(Event).options(selectinload(Event.place)).where(Event.id == uid)
        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_or_create_place(self, external_id: str, name: str, city: str, address: str, seats_pattern: str = None):
        place = self.session.query(Place).filter_by(external_id=external_id).first()
        if not place:
            place = Place(external_id=external_id, name=name, city=city, address=address, seats_pattern=seats_pattern)
            self.session.add(place)
            self.session.commit()
        return place

    def upsert_event(
        self,
        external_id: str,
        name: str,
        event_time,
        registration_deadline,
        status: str,
        number_of_visitors: int,
        place_id,
    ):
        event = self.session.query(Event).filter_by(external_id=external_id).first()
        if not event:
            event = Event(
                external_id=external_id,
                name=name,
                event_time=event_time,
                registration_deadline=registration_deadline,
                status=status,
                number_of_visitors=number_of_visitors,
                place_id=place_id,
            )
            self.session.add(event)
        else:
            event.name = name
            event.event_time = event_time
            event.registration_deadline = registration_deadline
            event.status = status
            event.number_of_visitors = number_of_visitors
            event.place_id = place_id
        self.session.commit()
        return event


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
            seat=seat,
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
