import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Собираем URL из переменных LMS
POSTGRES_CONNECTION_STRING = os.getenv("POSTGRES_CONNECTION_STRING")
POSTGRES_DATABASE_NAME = os.getenv("POSTGRES_DATABASE_NAME")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRESS_PORT = os.getenv("POSTGRESS_PORT")  # опечатка в названии переменной, но оставим как есть

# Если есть готовая строка подключения — используем её
if POSTGRES_CONNECTION_STRING:
    DATABASE_URL = POSTGRES_CONNECTION_STRING
else:
    # Иначе собираем из частей
    DATABASE_URL = f"postgresql://{POSTGRES_HOST}:{POSTGRESS_PORT}/{POSTGRES_DATABASE_NAME}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()