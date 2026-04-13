import asyncio

import asyncpg


async def check():
    try:
        conn = await asyncpg.connect(
            user="user", password="password", database="events_db", host="localhost", port=5432
        )
        print("✅ Подключение к PostgreSQL успешно!")
        await conn.close()
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")


asyncio.run(check())
