"""
Docstring for schema.content
"""
from pydantic import BaseModel

class ContentResponse(BaseModel):
    """
    Docstring for ContentResponse
    """
    title: str
    description: str
    source: str
    file_type: str
