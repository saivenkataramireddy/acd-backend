import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def check_db():
    print("------- READING LOCATION DATA FROM DATABASE --------")
    engine = create_async_engine(settings.MYSQL_URL, echo=False)
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT id, ST_AsText(location) FROM Events"))
        for row in result:
            print(f"Event ID: {row[0]}")
            print(f"Decoded Native WKT Location: {row[1]}")
            print("---------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(check_db())
