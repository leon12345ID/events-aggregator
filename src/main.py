import asyncio

from fastapi import FastAPI

from src.api.events import router
from src.clients.events_provider import EventsProviderClient
from src.db.database import SessionLocal
from src.repositories import EventRepository, SyncMetadataRepository
from src.usecases import SyncEventsUsecase

app = FastAPI(title="Events Aggregator")

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
