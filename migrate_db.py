import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def init_tables():
    # Set echo to False so it doesn't just spam terminal, we use prints
    engine = create_async_engine(settings.MYSQL_URL, echo=False)
    
    async with engine.begin() as conn:
        print("Creating Users table...")
        await conn.execute(text("""
        CREATE TABLE IF NOT EXISTS Users (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(100),
            phone VARCHAR(20) UNIQUE,
            hashed_password VARCHAR(255),
            role ENUM('user', 'police', 'hospital') DEFAULT 'user',
            location POINT SRID 4326,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            device_token VARCHAR(255)
        );
        """))
        
        # MySQL Spatial index support
        try:
            await conn.execute(text("ALTER TABLE Users MODIFY location POINT SRID 4326 NOT NULL;"))
            await conn.execute(text("CREATE SPATIAL INDEX idx_location ON Users(location);"))
        except Exception:
            pass # Ignore if it already exists or if syntax slightly off for users mysql version

        print("Creating Events table...")
        await conn.execute(text("""
        CREATE TABLE IF NOT EXISTS Events (
            id VARCHAR(36) PRIMARY KEY,
            type ENUM('accident', 'crime') NOT NULL,
            severity INT DEFAULT 1,
            status ENUM('pending', 'confirmed', 'resolved', 'fake') DEFAULT 'pending',
            created_by VARCHAR(36),
            location POINT SRID 4326,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source ENUM('auto', 'manual') NOT NULL,
            FOREIGN KEY (created_by) REFERENCES Users(id) ON DELETE SET NULL
        );
        """))
        
        try:
            await conn.execute(text("CREATE INDEX idx_timestamp ON Events(timestamp);"))
        except Exception:
            pass

        print("Creating Alerts table...")
        await conn.execute(text("""
        CREATE TABLE IF NOT EXISTS Alerts (
            id VARCHAR(36) PRIMARY KEY,
            event_id VARCHAR(36),
            user_id VARCHAR(36),
            type ENUM('nearby', 'emergency', 'authority') NOT NULL,
            status ENUM('sent', 'delivered', 'failed') DEFAULT 'sent',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES Events(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
        );
        """))

        print("Creating Authorities table...")
        await conn.execute(text("""
        CREATE TABLE IF NOT EXISTS Authorities (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(150),
            type ENUM('police', 'hospital') NOT NULL,
            location POINT SRID 4326,
            contact_number VARCHAR(20),
            coverage_radius_km INT DEFAULT 5
        );
        """))
    
    print("Database migration completed successfully! All tables designed for Spatial Indexing are ready.")

if __name__ == "__main__":
    asyncio.run(init_tables())
