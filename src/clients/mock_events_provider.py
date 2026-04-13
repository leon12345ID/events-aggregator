from .events_provider import EventsProviderClient


class MockEventsProviderClient(EventsProviderClient):
    """Заглушка для тестов и разработки"""

    async def get_events(self, changed_at: str = "2000-01-01", page: int = 1):
        return [
            {
                "id": "mock-event-1",
                "name": "Mock Event 1",
                "event_time": "2025-12-31T19:00:00Z",
                "status": "published",
                "place": {"id": "place-1", "name": "Mock Place", "city": "Mock City", "address": "Mock Address"},
            }
        ]

    async def get_seats(self, event_id: str):
        return ["A1", "A2", "B1", "B2"]

    async def register(self, event_id: str, first_name: str, last_name: str, email: str, seat: str):
        return f"mock-ticket-{event_id}-{seat}"
