"""
Docstring for routers.content
"""
from fastapi import APIRouter
from src.schema.content import ContentRequestSchema

content_router = APIRouter(prefix="/content")

@content_router.get("/")
async def list_content():
    """
    Lists all content stored in sql db e.g. market trends, legislation, insights
    Additional filtering and pagination can be added as needed
    """
    return {"message": "List of content"}

@content_router.get("/{content_id}")
async def get_content(content_id: str):
    """
    Retrieves details of a specific content item by its ID
    
    :type content_id: str
    """
    return {"message": f"Details of content {content_id}"}

@content_router.get("/{content_id}/download")
async def download_content(content_id: str):
    """
    Downloads a specific content item by its ID
    
    :type content_id: str
    """
    return {"message": f"Content {content_id} downloaded"}

@content_router.post("/") # Include appropriate schema
async def upload_content(request: ContentRequestSchema):
    """
    Uploads new content to the system
    """
    return {"message": "Content uploaded"}

@content_router.delete("/{content_id}")
async def delete_content(content_id: str):
    """
    Deletes a specific content item by its ID
    
    :type content_id: str
    """
    return {"message": f"Content {content_id} deleted"}
