"""
Docstring for routers.content
"""
from fastapi import APIRouter

content_router = APIRouter(prefix="/content")

@content_router.get("/")
async def list_content():
    """
    Docstring for list_content
    """
    return {"message": "List of content"}

@content_router.get("/{content_id}")
async def get_content(content_id: str):
    """
    Docstring for get_content
    
    :type content_id: str
    """
    return {"message": f"Details of content {content_id}"}

@content_router.post("/") # Include appropriate schema
async def upload_content():
    """
    Docstring for upload_content
    """
    return {"message": "Content uploaded"}

@content_router.delete("/{content_id}")
async def delete_content(content_id: str):
    """
    Docstring for delete_content
    
    :type content_id: str
    """
    return {"message": f"Content {content_id} deleted"}
