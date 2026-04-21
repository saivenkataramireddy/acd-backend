from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class EventType(str, Enum):
    accident = "accident"
    crime = "crime"

class SourceType(str, Enum):
    auto = "auto"
    manual = "manual"

class EventCreate(BaseModel):
    type: EventType
    severity: int = 1
    lat: float
    lon: float
    source: SourceType
    userFullName: Optional[str] = None
    contacts: Optional[List[str]] = None

class EventResponse(BaseModel):
    id: str
    status: str
    message: Optional[str] = None
