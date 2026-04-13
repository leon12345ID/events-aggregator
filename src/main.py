import asyncio
import threading
from fastapi import FastAPI
from src.api.events import router
from src.db.database import engine, Base, SessionLocal
from src.db.models import Event, Place
from datetime import datetime
from src.usecases import SyncEventsUsecase
from src.repositories import EventRepository, SyncMetadataRepository
from src.clients.events_provider import EventsProviderClient

app = FastAPI(title="Events Aggregator")

def add_test_data_if_empty():
    db = SessionLocal()
    try:
        if db.query(Event).count() == 0:
            print("📦 База пуста, добавляю тестовое событие...")
            place = Place(
                external_id="place-1",
                name="Test Place",
                city="Test City",
                address="Test Address",
                seats_pattern="A1-100"
            )
            db.add(place)
            db.commit()

            event = Event(
                external_id="event-1",
                name="Test Event",
                event_time=datetime.now(),
                registration_deadline=datetime.now(),
                status="published",
                number_of_visitors=0,
                place_id=place.id
            )
            db.add(event)
            db.commit()
            print("✅ Тестовое событие добавлено")
        else:
            print("ℹ️ В базе уже есть события")
    finally:
        db.close()

def sync_job():
    print("🔄 Запущена фоновая синхронизация")
    db = SessionLocal()
    try:
        event_repo = EventRepository(db)
        sync_repo = SyncMetadataRepository(db)
        client = EventsProviderClient("http://localhost:8001")
        usecase = SyncEventsUsecase(client, event_repo, sync_repo)
        usecase.execute()
        print("✅ Фоновая синхронизация завершена")
    except Exception as e:
        print(f"❌ Ошибка синхронизации: {e}")
    finally:
        db.close()

async def scheduler():
    while True:
        sync_job()
        await asyncio.sleep(86400)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы")
    add_test_data_if_empty()
    threading.Thread(target=lambda: asyncio.run(scheduler()), daemon=True).start()

app.include_router(router)

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}