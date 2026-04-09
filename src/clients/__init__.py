import os
from .events_provider import EventsProviderClient
from .mock_events_provider import MockEventsProviderClient

def get_events_provider_client():
    mode = os.getenv("API_MODE", "mock")
    if mode == "real":
        url = os.getenv("EVENTS_API_URL")
        if not url:
            raise ValueError("EVENTS_API_URL not set in .env")
        return EventsProviderClient(url)
    else:
        return MockEventsProviderClient()