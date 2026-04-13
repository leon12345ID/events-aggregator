import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI

from src.api.events import router
from src.clients.events_provider import EventsProviderClient
from src.db.database import SessionLocal
from src.repositories import EventRepository, SyncMetadataRepository
from src.usecases import SyncEventsUsecase

from src.db.models import Event, Place
from datetime import datetime

load_dotenv()

app = FastAPI(title="Events Aggregator")

add_test_data_if_empty()

app.include_router(router)

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# --- Фоновая синхронизация ---
def sync_job():
    """Задача синхронизации, запускается в фоновом потоке"""
    print(" Запущена фоновая синхронизация")
    db = SessionLocal()
    try:
        event_repo = EventRepository(db)
        sync_repo = SyncMetadataRepository(db)
        client = EventsProviderClient("http://localhost:8001")  # заглушка
        usecase = SyncEventsUsecase(client, event_repo, sync_repo)
        usecase.execute()
        print(" Фоновая синхронизация завершена")
    except Exception as e:
        print(f" Ошибка синхронизации: {e}")
    finally:
        db.close()

async def scheduler():
    #Запускает sync_job() раз в сутки (каждые 86400 секунд)
    while True:
        sync_job()
        await asyncio.sleep(86400)  # 24 часа

@app.on_event("startup")
async def start_scheduler():
    asyncio.create_task(scheduler())


def add_test_data_if_empty():
    """Добавляет тестовое событие, если база пуста"""
    db = SessionLocal()
    try:
        if db.query(Event).count() == 0:
            print(" База пуста, добавляю тестовое событие...")

            # Создаём тестовое место
            place = Place(
                external_id="test-place-1",
                name="Тестовая площадка",
                city="Тестовый город",
                address="Тестовый адрес, 1",
                seats_pattern="A1-100"
            )
            db.add(place)
            db.commit()

            # Создаём тестовое событие
            event = Event(
                external_id="test-event-1",
                name="Тестовое мероприятие",
                event_time=datetime.now(),
                registration_deadline=datetime.now(),
                status="published",
                number_of_visitors=0,
                place_id=place.id
            )
            db.add(event)
            db.commit()
            print(" Тестовое событие добавлено")
        else:
            print("️ В базе уже есть события, тестовые данные не нужны")
    finally:
        db.close()
