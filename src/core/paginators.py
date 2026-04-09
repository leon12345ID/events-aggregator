from typing import Any

from src.clients.events_provider import EventsProviderClient


class EventsPaginator:
    """Асинхронный итератор для постраничного получения событий от внешнего API"""

    def __init__(self, client: EventsProviderClient, changed_at: str = "2000-01-01"):
        self.client = client
        self.changed_at = changed_at
        self._current_page = 1
        self._items: list[dict[str, Any]] = []
        self._has_more = True

    def __aiter__(self):
        return self

    async def __anext__(self) -> dict[str, Any]:
        """Возвращает следующее событие или останавливает итерацию"""
        if not self._items and not self._has_more:
            raise StopAsyncIteration

        if not self._items:
            await self._fetch_next_page()
            if not self._items:
                raise StopAsyncIteration

        return self._items.pop(0)

    async def _fetch_next_page(self):
        """Загружает следующую страницу событий"""
        events = await self.client.get_events(
            changed_at=self.changed_at,
            page=self._current_page
        )

        self._items = events
        self._current_page += 1

        # Если API не возвращает признак последней страницы,
        # считаем, что страница пустая — значит, больше нет
        if not events:
            self._has_more = False
