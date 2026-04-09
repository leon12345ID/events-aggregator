from typing import Any

import httpx


class EventsProviderClient:
    """Клиент для взаимодействия с внешним Events Provider API"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    async def get_events(self, changed_at: str = "2000-01-01", page: int = 1) -> list[dict[str, Any]]:
        """
        Получает одну страницу событий, изменённых после указанной даты.
        В реальном API параметры могут называться иначе (например, `cursor`, `offset`).
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/events",
                params={
                    "changed_at": changed_at,
                    "page": page,
                    "per_page": 100
                }
            )
            response.raise_for_status()
            data = response.json()
            # Ожидаем, что API вернёт список событий в поле `results` или напрямую
            return data.get("results", data)

    async def get_seats(self, event_id: str) -> list[str]:
        """Получает список свободных мест для события"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/events/{event_id}/seats")
            response.raise_for_status()
            data = response.json()
            return data.get("available_seats", [])

    async def register(
        self,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str
    ) -> str:
        """Регистрирует участника на событие. Возвращает ticket_id"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/events/{event_id}/register",
                json={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "seat": seat
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["ticket_id"]
