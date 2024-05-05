from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

# Enum for event status
class EventStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    UNDER_REVIEW = "under_review"

# API Router
event_router = APIRouter()

# Package model with dynamic details
class Package(BaseModel):
    name: str
    price: float
    details: Dict[str, str]  # Dynamic details as key-value pairs

# Event model using Package model
class Event(BaseModel):
    id: Optional[str]
    name: str
    date: int
    views: int
    status: EventStatus = EventStatus.PENDING
    packages: List[Package]
    CreatedBy : str
    Tags : List[str]

# Database Simulation
events_db = {}

# Enhanced GET all events with filters
@event_router.get("/", response_model=List[Event], tags=["event"])
async def get_all_events(
    created_by: Optional[str] = None, 
    after_date: Optional[int] = None,
    tags: Optional[List[str]] = Query(None),
    min_views: Optional[int] = None,
    name: Optional[str] = None
):
    """Retrieve all events, with optional filters."""
    events = list(events_db.values())
    if created_by:
        events = [event for event in events if event.created_by == created_by]
    if after_date:
        events = [event for event in events if event.date >= after_date]
    if tags:
        events = [event for event in events if any(tag in event.tags for tag in tags)]
    if min_views:
        events = [event for event in events if event.views >= min_views]
    if name:
        events = [event for event in events if name.lower() in event.name.lower()]
    return events

@event_router.get("/{event_id}", response_model=Event, tags=["event"])
async def get_specific_event(event_id: str):
    """Retrieve specific event details by ID."""
    event = events_db.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

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

@event_router.get("/review/{event_id}", response_model=Event, tags=["event"])
async def check_event_review_status(event_id: str):
    """Check the review status of an event."""
    event = events_db.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
# Submit for review
@event_router.post("/submit-for-review/{event_id}", response_model=dict, tags=["event"])
async def submit_event_for_review(event_id: str):
    """Submit an event for review."""
    event = events_db.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status != EventStatus.PAID:
        raise HTTPException(status_code=400, detail="Event must be paid before review")
    event.status = EventStatus.UNDER_REVIEW
    return {"message": "Event submitted for review"}

# Check payment status
@event_router.get("/check-payment/{event_id}", response_model=dict, tags=["event"])
async def check_payment_status(event_id: str):
    """Check payment status of an event."""
    event = events_db.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"status": event.status.value}

# Purchase additional packages
@event_router.post("/purchase-package/{event_id}", response_model=Event, tags=["event"])
async def purchase_feature_package(event_id: str, package: Package):
    """Add a feature package to an event."""
    event = events_db.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status != EventStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Only approved events can purchase additional packages")
    event.packages.append(package)
    return event