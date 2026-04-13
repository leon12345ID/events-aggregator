from .events_provider import EventsProviderClient


class MockEventsProviderClient(EventsProviderClient):
    def __init__(self):
        # Вызываем конструктор родителя с фиктивным URL
        super().__init__("http://mock")

    async def get_events(self, changed_at: str = "2000-01-01", page: int = 1):
        return []

    async def get_seats(self, event_id: str):
        return ["A1", "A2", "B1", "B2"]

    async def register(self, event_id: str, first_name: str, last_name: str, email: str, seat: str):
        return f"mock-ticket-{event_id}-{seat}"
