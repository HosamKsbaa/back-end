from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from notification_router import notifications_db
event_router = APIRouter()

# Models
class Event(BaseModel):
    id: Optional[str]
    name: str
    date: int
    views : int
    status: Optional[str]
    package: List[str]

# Database Simulation
events_db = {}





# Endpoints
@event_router.get("/", response_model=List[Event],tags=["event"])
async def get_all_events():
    return list(events_db.values())

@event_router.get("/{event_id}", response_model=Event,tags=["event"])
async def get_specific_event(event_id: str):
    event = events_db.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@event_router.post("/", response_model=Event,tags=["event"])
async def create_event(event: Event):
    event.id = str(len(events_db) + 1)  # simple unique ID generation
    events_db[event.id] = event
    return event

@event_router.put("/{event_id}", response_model=Event,tags=["event"])
async def update_event(event_id: str, event: Event):
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")
    events_db[event_id] = event
    return event

@event_router.delete("/{event_id}", response_model=dict,tags=["event"])
async def delete_event(event_id: str):
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")
    del events_db[event_id]
    return {"message": "Event deleted successfully"}

@event_router.get("/review/{event_id}", response_model=Event,tags=["event"])
async def check_event_review_status(event_id: str):
    event = events_db.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

# Include other endpoints as necessary


