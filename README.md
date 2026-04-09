Events Aggregator

Бэкенд-сервис для агрегации мероприятий из внешнего API.
Реализован на FastAPI, синхронизация с внешним API, управление билетами, кэширование мест, пагинация.

стек:

Python 3.11
FastAPI — REST API
PostgreSQL — база данных
SQLAlchemy — ORM
Docker + docker-compose — контейнеризация
Ruff — линтер
GitHub Actions — CI/CD
запуск через Docker (рекомендуется)

docker-compose up --build

API:  http://localhost:8000/docs

локально:

python -m venv .venv
.venv\Scripts\activate     #                              ДЛЯ Windows
source .venv/bin/activate  #                              ДЛЯ Linux/Mac

pip install -r requirements.txt
uvicorn src.main:app --reload