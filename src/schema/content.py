"""
Docstring for schema.content
"""
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class ContentRequestSchema(BaseModel):
    """
    Docstring for ContentRequestSchema
    """
    title: str
    description: str
    source: str
    file_type: str

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class ContentType(str, Enum):
    market = "market"
    legislation = "legislation"
    insight = "insight"
    other = "other"

# set of values acceptable to sort records by 
class SortField(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"
    title = "title"
    source = "source"
    file_type = "file_type"
    content_type ="content_type"

class FilterParams(BaseModel):
    page: int = Field(0, ge=0)
    page_size: int = Field(10, ge=1, le=100)
    sort_by: SortField = SortField.created_at
    order: SortOrder = SortOrder.desc
    content_type: Optional[ContentType] = None
    user_only: bool = False
    search: Optional[str] = None
