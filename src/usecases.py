from typing import Optional, List
from src.repositories import EventRepository, TicketRepository, SyncMetadataRepository
from src.clients.events_provider import EventsProviderClient
from src.db.models import Event

class GetEventsWithPaginationUsecase:
    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo

    def execute(self, date_from: Optional[str] = None, page: int = 1, page_size: int = 20):
        events = self.event_repo.get_list(date_from, page, page_size)
        total = self.event_repo.count(date_from)
        return events, total

class GetEventUsecase:
    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo

    def execute(self, event_id: str) -> Optional[Event]:
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
        events_data = self.client.get_events(changed_at=changed_at)
        # Здесь будет логика сохранения
        self.sync_metadata_repo.update(changed_at, status="completed")