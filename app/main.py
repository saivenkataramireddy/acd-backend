from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import events

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend for the Accident & Emergency Alert System",
)

# Setup CORS Middleware to allow requests from the React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev. E.g. "http://localhost:5173"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(events.router, prefix=f"{settings.API_V1_STR}/events", tags=["Events"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
