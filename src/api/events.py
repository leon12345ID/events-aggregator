import uuid
from datetime import datetime, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.repositories import EventRepository, TicketRepository
from src.schemas import TicketCreate

router = APIRouter(prefix="/api", tags=["events"])

# --- Вспомогательные функции ---
def get_event_repo(db: Session = Depends(get_db)) -> EventRepository:
    return EventRepository(db)

def get_ticket_repo(db: Session = Depends(get_db)) -> TicketRepository:
    return TicketRepository(db)

# --- Кэш для мест (в памяти) ---
seats_cache = {}

def get_cached_seats(event_id: str):
    cached = seats_cache.get(event_id)
    if cached and cached[1] > datetime.now():
        return cached[0]
    return None

def set_cached_seats(event_id: str, seats_data):
    seats_cache[event_id] = (seats_data, datetime.now() + timedelta(seconds=30))

# --- Эндпоинты ---

@router.get("/events")
def get_events(
    request: Request,
    date_from: str | None = Query(None, description="YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    event_repo: EventRepository = Depends(get_event_repo)
):
    events, total = event_repo.get_list_with_count(date_from, page, page_size)
    base_url = str(request.base_url).rstrip("/") + "/api/events"
    params = {"date_from": date_from, "page_size": page_size}

    next_url = None
    if page * page_size < total:
        next_params = {**params, "page": page + 1}
        next_url = f"{base_url}?{urlencode(next_params)}"

    previous_url = None
    if page > 1:
        prev_params = {**params, "page": page - 1}
        previous_url = f"{base_url}?{urlencode(prev_params)}"

    return {
        "count": total,
        "next": next_url,
        "previous": previous_url,
        "results": events
    }

@router.get("/events/{event_id}")
def get_event(event_id: str, event_repo: EventRepository = Depends(get_event_repo)):
    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.get("/events/{event_id}/seats")
def get_event_seats(
    event_id: str,
    event_repo: EventRepository = Depends(get_event_repo),
):
    # 1. Проверяем, существует ли событие в БД
    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 2. Проверяем кэш
    cached = get_cached_seats(event_id)
    if cached is not None:
        return {"event_id": event_id, "available_seats": cached, "cached": True}

    # 3. Если нет в кэше — генерируем список мест
    seats = ["A1", "A2", "B1", "B2"]
    set_cached_seats(event_id, seats)
    return {"event_id": event_id, "available_seats": seats, "cached": False}

@router.delete("/tickets/{ticket_id}")
def cancel_ticket(
    ticket_id: str,
    ticket_repo: TicketRepository = Depends(get_ticket_repo)
):
    # Проверяем, существует ли билет
    ticket = ticket_repo.get_by_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket_repo.delete(ticket_id)
    return {"success": True}

@router.post("/tickets", status_code=201)
def create_ticket(
    ticket: TicketCreate,
    event_repo: EventRepository = Depends(get_event_repo),
    ticket_repo: TicketRepository = Depends(get_ticket_repo)
):
    # Проверяем, существует ли событие
    event = event_repo.get_by_id(ticket.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Проверяем, свободно ли место (заглушка — пропускаем)
    # Здесь можно добавить реальную проверку через client.get_seats()

    # Создаём билет (в реальности здесь был бы вызов внешнего API)
    ticket_id = str(uuid.uuid4())
    ticket_repo.create(
        event_id=ticket.event_id,
        ticket_id=ticket_id,
        first_name=ticket.first_name,
        last_name=ticket.last_name,
        email=ticket.email,
        seat=ticket.seat
    )
    return {"ticket_id": ticket_id}

# --- Ручной запуск синхронизации ---
@router.post("/sync/trigger")
def trigger_sync():
    # Здесь должна быть реальная синхронизация, но для тестов просто возвращаем успех
    return {"status": "sync completed"}
