from datetime import datetime, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from src.clients.events_provider import EventsProviderClient
from src.db.database import get_db
from src.repositories import EventRepository, SyncMetadataRepository, TicketRepository
from src.usecases import (
    CancelTicketUsecase,
    CreateTicketUsecase,
    GetEventsWithPaginationUsecase,
    GetEventUsecase,
    SyncEventsUsecase,
)

router = APIRouter(prefix="/api", tags=["events"])


# --- Вспомогательные функции для зависимостей ---
def get_events_provider_client() -> EventsProviderClient:
    return EventsProviderClient("http://localhost:8001")


def get_event_repo(db: Session = Depends(get_db)) -> EventRepository:
    return EventRepository(db)


def get_ticket_repo(db: Session = Depends(get_db)) -> TicketRepository:
    return TicketRepository(db)


def get_sync_metadata_repo(db: Session = Depends(get_db)) -> SyncMetadataRepository:
    return SyncMetadataRepository(db)


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
    event_repo: EventRepository = Depends(get_event_repo),
):
    usecase = GetEventsWithPaginationUsecase(event_repo)
    events, total = usecase.execute(date_from, page, page_size)

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

    return {"count": total, "next": next_url, "previous": previous_url, "results": events}


@router.get("/events/{event_id}")
def get_event(event_id: str, event_repo: EventRepository = Depends(get_event_repo)):
    usecase = GetEventUsecase(event_repo)
    event = usecase.execute(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/events/{event_id}/seats")
def get_event_seats(event_id: str, client: EventsProviderClient = Depends(get_events_provider_client)):
    cached = get_cached_seats(event_id)
    if cached is not None:
        return {"event_id": event_id, "available_seats": cached, "cached": True}

    try:
        seats = await client.get_seats(event_id)
        set_cached_seats(event_id, seats)
        return {"event_id": event_id, "available_seats": seats, "cached": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения мест: {str(e)}")


@router.post("/sync/trigger")
def trigger_sync(
    sync_repo: SyncMetadataRepository = Depends(get_sync_metadata_repo),
    event_repo: EventRepository = Depends(get_event_repo),
):
    client = get_events_provider_client()
    usecase = SyncEventsUsecase(client, event_repo, sync_repo)
    usecase.execute()
    return {"status": "sync completed"}


@router.post("/tickets", status_code=201)
def create_ticket(
    event_id: str,
    first_name: str,
    last_name: str,
    email: str,
    seat: str,
    event_repo: EventRepository = Depends(get_event_repo),
    ticket_repo: TicketRepository = Depends(get_ticket_repo),
):
    client = get_events_provider_client()
    usecase = CreateTicketUsecase(client, event_repo, ticket_repo)
    try:
        ticket_id = usecase.execute(event_id, first_name, last_name, email, seat)
        return {"ticket_id": ticket_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/tickets/{ticket_id}", status_code=200)
def cancel_ticket(ticket_id: str, ticket_repo: TicketRepository = Depends(get_ticket_repo)):
    usecase = CancelTicketUsecase(ticket_repo)
    usecase.execute(ticket_id)
    return {"success": True}
