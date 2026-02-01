"""
Docstring for routers.notification
"""
from fastapi import APIRouter
notif_router = APIRouter(prefix="/notification")

@notif_router.get("/")
async def list_all_notifications():
    """
    Docstring for list_all_notifications
    """
    return {"message": "List of notifications"}

@notif_router.get("/{notification_id}")
async def get_notification(notification_id: str):
    """
    Docstring for get_notification
    
    :type notification_id: str
    """
    return {"message": f"Details of content {notification_id}"}


@notif_router.patch("/{notification_id}")
async def read_notification(notification_id: str):
    """
    Docstring for read_notification
    
    :type notification_id: str
    """
    return {"message": f"Details of content {notification_id}"}


@notif_router.patch("/{notification_id}")
async def unread_notification(notification_id: str):
    """
    Docstring for read_notification
    
    :type notification_id: str
    """
    return {"message": f"Details of content {notification_id}"}


@notif_router.delete("/{content_id}")
async def delete_notification(content_id: str):
    """
    Docstring for delete_notification
    
    :type content_id: str
    """
    return {"message": f"Content {content_id} deleted"}




