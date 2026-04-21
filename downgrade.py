import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def alter_tables():
    engine = create_async_engine(settings.MYSQL_URL, echo=False)
    async with engine.begin() as conn:
        print("Migrating Events table...")
        try:
            await conn.execute(text("ALTER TABLE Events ADD COLUMN latitude FLOAT;"))
            await conn.execute(text("ALTER TABLE Events ADD COLUMN longitude FLOAT;"))
        except Exception: 
            pass # columns might already exist
        
        # Convert existing blob data back into floats
        try:
            await conn.execute(text("UPDATE Events SET latitude = ST_Y(location), longitude = ST_X(location) WHERE location IS NOT NULL;"))
            await conn.execute(text("ALTER TABLE Events DROP COLUMN location;"))
        except Exception:
            pass
        
        print("Migrating Users table...")
        try:
            await conn.execute(text("ALTER TABLE Users ADD COLUMN latitude FLOAT;"))
            await conn.execute(text("ALTER TABLE Users ADD COLUMN longitude FLOAT;"))
        except Exception: 
            pass
            
        try:
            await conn.execute(text("UPDATE Users SET latitude = ST_Y(location), longitude = ST_X(location) WHERE location IS NOT NULL;"))
            await conn.execute(text("ALTER TABLE Users DROP COLUMN location;"))
        except Exception:
            pass

        print("Migrating Authorities table...")
        try:
            await conn.execute(text("ALTER TABLE Authorities ADD COLUMN latitude FLOAT;"))
            await conn.execute(text("ALTER TABLE Authorities ADD COLUMN longitude FLOAT;"))
        except Exception: 
            pass
            
        try:
            await conn.execute(text("ALTER TABLE Authorities DROP COLUMN location;"))
        except Exception:
            pass
            
    print("✅ Successfully downgraded Spatial Data to plain Latitude/Longitude fields!")

if __name__ == "__main__":
    asyncio.run(alter_tables())
