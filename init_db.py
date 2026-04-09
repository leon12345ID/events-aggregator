# init_db.py
import os

from sqlalchemy import create_engine

from src.db.models import Base

# Используем ту же переменную окружения, что и приложение
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/events_db")

engine = create_engine(DATABASE_URL)

def init_db():
    print(f"Создаю таблицы в базе: {DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы (или уже существуют)")

if __name__ == "__main__":
    init_db()
