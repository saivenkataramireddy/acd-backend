from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def get_users_within_radius(db: AsyncSession, lat: float, lon: float, radius_km: float = 3.0):
    """ Returns users within a given radius using ST_Distance_Sphere. """
    radius_meters = radius_km * 1000
    
    query = text("""
        SELECT id, device_token, ST_Distance_Sphere(POINT(longitude, latitude), POINT(:lon, :lat)) AS distance
        FROM Users
        WHERE role = 'user' 
          AND device_token IS NOT NULL
          AND ST_Distance_Sphere(POINT(longitude, latitude), POINT(:lon, :lat)) <= :radius
        ORDER BY distance ASC
    """)
    
    result = await db.execute(query, {
        "point": f"POINT({lon} {lat})",
        "radius": radius_meters
    })
    
    return result.fetchall()
