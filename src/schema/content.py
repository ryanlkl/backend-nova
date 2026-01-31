"""
Docstring for schema.content
"""
from pydantic import BaseModel

class ContentRequestSchema(BaseModel):
    """
    Docstring for ContentRequestSchema
    """
    title: str
    description: str
    source: str
    file_type: str
