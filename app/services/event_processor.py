import redis.asyncio as redis
import uuid
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.event import EventCreate

# We setup the redis pool
try:
    redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
except Exception as e:
    redis_client = None

async def check_event_deduplication(lat: float, lon: float, event_type: str) -> bool:
    """ GeoHash / Grid based caching to prevent duplicates """
    if not redis_client:
        return False
        
    grid_id = f"event:{event_type}:{round(lat, 3)}:{round(lon, 3)}" # Approx 100x100m grid
    
    try:
        exists = await redis_client.get(grid_id)
        if exists:
            return True # Duplicate detected
        
        # Lock this grid for 5 minutes (300s)
        await redis_client.setex(grid_id, 300, "active")
    except Exception as e:
        print(f"Redis cache connection failed (ignoring deduplication): {e}")
        return False
        
    return False

async def process_emergency_event(db: AsyncSession, payload: EventCreate, user: dict):
    is_duplicate = await check_event_deduplication(payload.lat, payload.lon, payload.type.value)
    
    if is_duplicate:
        return {"id": "N/A", "status": "merged", "message": "Event already tracked"}
    
    event_id = str(uuid.uuid4())
    
    # Insert new event with native Spatial location mapped from WKT (Well-Known Text)
    from sqlalchemy import text
    query = text("""
        INSERT INTO Events (id, type, severity, latitude, longitude, source)
        VALUES (:id, :type, :severity, :lat, :lon, :source)
    """)
    
    await db.execute(query, {
        "id": event_id,
        "type": payload.type.value,
        "severity": payload.severity,
        "lat": payload.lat,
        "lon": payload.lon,
        "source": payload.source.value
    })
    
    # Commit transaction asynchronously 
    await db.commit()
    
    return {"id": event_id, "status": "created", "message": "Event saved in MySQL successfully!"}
