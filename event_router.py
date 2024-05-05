from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

# Enum for event status
class Status(Enum):
    waitingForPayment = "waitingForPayment"
    waitingForReview = "waitingForReview"
    APPROVED = "approved"
    REJECTED = "rejected"


# API Router
event_router = APIRouter()


class Payment(BaseModel):
    payment_id: str
    payment_status: str
    payment_amount: float
    payment_method: str
    payment_date: int

# Package model with dynamic details
class Package(BaseModel):
    id : Optional[str]
    name: str
    status: Status 
    payment : Payment
    price: float
    details: Dict[str, str]  # Dynamic details as key-value pairs

# Event model using Package model
class Event(BaseModel):
    id: Optional[str]
    name: str
    date: int
    views: int
    status: Status 
    packages: List[Package]
    payment : Payment
    CreatedBy : str
    Tags : List[str]

# Database Simulation
events_db = {}

# Enhanced GET all events with filters
@event_router.get("/", response_model=List[Event], tags=["event"])
async def get_all_events(
    created_by: Optional[str] = None,
    from_date: Optional[int] = None,  # Using UNIX timestamp for dates
    to_date: Optional[int] = None,
    tags: Optional[List[str]] = Query(None),
    min_views: Optional[int] = None,
    name: Optional[str] = None,
    event_id: Optional[str] = None
) -> List[Event]:
    """
    Retrieve events based on various filters. This function supports filtering by creator,
    date range, tags, minimum views, name, and specific event ID.
    
    Parameters:
    - created_by (str, optional): Filter events created by a specific user.
    - from_date (int, optional): Filter events after this date (UNIX timestamp).
    - to_date (int, optional): Filter events before this date (UNIX timestamp).
    - tags (List[str], optional): Filter events that include any of the specified tags.
    - min_views (int, optional): Filter events that have at least a certain number of views.
    - name (str, optional): Filter events whose names contain the given substring.
    - event_id (str, optional): Retrieve a specific event by its unique ID.
    
    Returns:
    List[Event]: A list of events that match the filters.
    """
    events = list(events_db.values())
    if event_id:
        return [event for event in events if event.id == event_id]
    if created_by:
        events = [event for event in events if event.CreatedBy == created_by]
    if from_date:
        events = [event for event in events if event.date >= from_date]
    if to_date:
        events = [event for event in events if event.date <= to_date]
    if tags:
        events = [event for event in events if set(tags).intersection(event.Tags)]
    if min_views:
        events = [event for event in events if event.views >= min_views]
    if name:
        events = [event for event in events if name.lower() in event.name.lower()]
    return events

@event_router.post("/", response_model=Event, tags=["event"])
async def create_event(event: Event):
    """Create a new event with the given details."""
    event.id = str(len(events_db) + 1)  # Simple unique ID generation
    events_db[event.id] = event
    return event

@event_router.put("/{event_id}", response_model=Event, tags=["event"])
async def update_event(event_id: str, event: Event):
    """Update an existing event."""
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")
    events_db[event_id] = event
    return event

@event_router.delete("/{event_id}", response_model=dict, tags=["event"])
async def delete_event(event_id: str):
    """Delete an event by its ID."""
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")
    del events_db[event_id]
    return {"message": "Event deleted successfully"}
