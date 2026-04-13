from datetime import datetime
from src.repositories import EventRepository, TicketRepository, SyncMetadataRepository
from src.clients.events_provider import EventsProviderClient
from src.db.models import Event

class GetEventsWithPaginationUsecase:
    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo

    def execute(self, date_from: str | None = None, page: int = 1, page_size: int = 20):
        events = self.event_repo.get_list(date_from, page, page_size)
        total = self.event_repo.count(date_from)
        return events, total

class GetEventUsecase:
    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo

    def execute(self, event_id: str) -> Event | None:
        return self.event_repo.get_by_id(event_id)

class CreateTicketUsecase:
    def __init__(self, client: EventsProviderClient, event_repo: EventRepository, ticket_repo: TicketRepository):
        self.client = client
        self.event_repo = event_repo
        self.ticket_repo = ticket_repo

    def execute(self, event_id: str, first_name: str, last_name: str, email: str, seat: str) -> str:
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        ticket_id = self.client.register(event_id, first_name, last_name, email, seat)
        self.ticket_repo.create(event_id, ticket_id, first_name, last_name, email, seat)
        return ticket_id

class CancelTicketUsecase:
    def __init__(self, ticket_repo: TicketRepository):
        self.ticket_repo = ticket_repo

    def execute(self, ticket_id: str) -> None:
        self.ticket_repo.delete(ticket_id)

class SyncEventsUsecase:
    def __init__(self, client: EventsProviderClient, event_repo: EventRepository, sync_metadata_repo: SyncMetadataRepository):
        self.client = client
        self.event_repo = event_repo
        self.sync_metadata_repo = sync_metadata_repo

    def execute(self) -> None:
        metadata = self.sync_metadata_repo.get()
        changed_at = metadata.last_changed_at if metadata else "2000-01-01"

        # Тестовые данные для синхронизации
        test_events = [
            {
                "id": "test-event-1",
                "name": "Test Event 1",
                "event_time": datetime.now(),
                "registration_deadline": datetime.now(),
                "status": "published",
                "number_of_visitors": 0,
                "place": {
                    "id": "test-place-1",
                    "name": "Test Place 1",
                    "city": "Test City",
                    "address": "Test Address 1",
                    "seats_pattern": "A1-100"
                }
            },
            {
                "id": "test-event-2",
                "name": "Test Event 2",
                "event_time": datetime.now(),
                "registration_deadline": datetime.now(),
                "status": "published",
                "number_of_visitors": 0,
                "place": {
                    "id": "test-place-2",
                    "name": "Test Place 2",
                    "city": "Test City",
                    "address": "Test Address 2",
                    "seats_pattern": "B1-200"
                }
            }
        ]

        for event_data in test_events:
            place_data = event_data.get("place", {})
            place = self.event_repo.get_or_create_place(
                external_id=place_data.get("id"),
                name=place_data.get("name"),
                city=place_data.get("city"),
                address=place_data.get("address"),
                seats_pattern=place_data.get("seats_pattern")
            )
            self.event_repo.upsert_event(
                external_id=event_data["id"],
                name=event_data["name"],
                event_time=event_data["event_time"],
                registration_deadline=event_data["registration_deadline"],
                status=event_data["status"],
                number_of_visitors=event_data.get("number_of_visitors", 0),
                place_id=place.id
            )

        self.sync_metadata_repo.update(changed_at, status="completed")