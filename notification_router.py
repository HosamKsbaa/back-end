    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel, Field
    from typing import List
    from enum import Enum

    # Enum for notification status
    class NotificationStatus(Enum):
        SENT = "sent"
        OPENED = "opened"
        NOT_SENT = "notsent"

    # Create an API router
    notification_router = APIRouter()
    from pydantic import BaseModel

    class NotificationTitle(BaseModel):
        title: str
        status: str

        class Config:
            schema_extra = {
                "example": {
                    "title": "Notification1",
                    "status": "SENT"
                }
            }
    # Notification model
    class Notification(BaseModel):
        user_id: str
        title: str
        body: str
        method: str
        seen: bool = Field(default=False)
        status: NotificationStatus = Field(default=NotificationStatus.NOT_SENT)

    # Database Simulation
    notifications_db = [
        Notification(user_id="1", title="Welcome!", body="Thank you for joining us!", method="email"),
        Notification(user_id="2", title="Reminder", body="Your event is coming up soon.", method="SMS"),
    ]

    from fastapi import Query

    @notification_router.get("/notification-titles", response_model=List[NotificationTitle], tags=["notifications"])
    async def get_notification_titles(page: int = Query(1, example=1), per_page: int = Query(10, example=10)):
        """
        Retrieve a list of notifications titles with their current status and support pagination.

        Parameters:
        - **page** (int): The page number to retrieve. Defaults to 1.
        - **per_page** (int): The number of notifications to display per page. Defaults to 10.

        Returns:
        - A list of dictionaries, each containing the 'title' and 'status' of a notification.

        If the `page` or `per_page` parameters are less than 1, the endpoint returns an HTTP 400 error with a message indicating that the `page` or `per_page` value is invalid.
        """
        if page < 1 or per_page < 1:
            raise HTTPException(status_code=400, detail="Invalid page or per_page value")
        
        start = (page - 1) * per_page
        end = start + per_page

        # Update status to SENT where applicable and return title and status
        response_data = []
        for notification in notifications_db[start:end]:
            if notification.status == NotificationStatus.NOT_SENT:
                notification.status = NotificationStatus.SENT
            response_data.append({'title': notification.title, 'status': notification.status.value})

        return response_data

    # Endpoint to retrieve specific notification details
    @notification_router.get("/notification-details/{notification_id}", response_model=Notification, tags=["notifications"])
    async def get_notification_details(notification_id: int):
        """
        Retrieve all details for a specific notification by its ID.

        Parameters:
        - **notification_id** (int): The ID of the notification.

        Returns:
        - A Notification model object containing all details of the notification.

        If the notification ID is out of bounds or invalid, the endpoint returns an HTTP 404 error with a message indicating that the notification was not found.
        """
        if notification_id >= len(notifications_db) or notification_id < 0:
            raise HTTPException(status_code=404, detail="Notification not found")

        notification = notifications_db[notification_id]
        # Mark as OPENED if this is the first detailed access
        if not notification.seen:
            notification.seen = True
            notification.status = NotificationStatus.OPENED

        return notification
