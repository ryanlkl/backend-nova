"""
Docstring for routers.content
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from src.models.market import Market
from src.utils.db import get_db
from src.utils.s3 import upload_to_s3

from enum import Enum
from typing import Annotated
from datetime import datetime
import uuid

content_router = APIRouter(prefix="/content")

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class SortField(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"
    title = "title"
    source = "source"


@content_router.get("/")
async def list_content(
    db: Session = Depends(get_db),
    page: int = Query(0, ge=0),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: SortField = SortField.created_at,
    order: SortOrder = SortOrder.desc,
):
    """
    Paginate and sort Market records
    """
    columns_map = {
        SortField.created_at: Market.created_at,
        SortField.updated_at: Market.updated_at,
        SortField.title: Market.title,
        SortField.source: Market.source,
    }

    sort_column = columns_map[sort_by]

    sort_expression = (
        asc(sort_column) if order == SortOrder.asc else desc(sort_column)
    )

    offset = page * page_size

    try:
        markets = (
            db.query(Market)
            .order_by(sort_expression)
            .offset(offset)
            .limit(page_size)
            .all()
        )

        total = db.query(Market).count()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error when fetching items from database: {str(e)}")

    

    return {
        "message": "success",
        "page": page,
        "page_size": page_size,
        "total": total,
        "sort_by": sort_by.value,
        "order": order.value,
        "data": [m.to_dict() for m in markets],
    }


@content_router.get("/{content_id}")
async def get_content(
    content_id: str,
    db: Session = Depends(get_db)):
    """
    Docstring for get_content
    
    :type content_id: str
    """

    market_data = db.get(Market, content_id)
    if not market_data:
        raise HTTPException(status_code=404, detail="Content not found")

    return {
        "message": "success",
        "data": market_data.to_dict()
    }

@content_router.post("/nova")
async def upload_market(
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    file: Annotated[UploadFile, File(description="content upload")],
    db: Session = Depends(get_db)
    ):
    """
    Docstring for upload_market
    
    :param title: Description
    :type title: Annotated[str, Form()]
    :param description: Description
    :type description: Annotated[str, Form()]
    :param file: Description
    :type file: Annotated[UploadFile, File(description="content upload")]
    :param db: Description
    :type db: Session
    """
    
    # some validation stuff for file extension and file size (max 10mb for now)
    ALLOWED_EXTENSIONS = {"pdf", "docx", "csv", "xlsx", "pptx"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  

    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file_extension}. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {MAX_FILE_SIZE // (1024*1024)} MB")

    file.file.seek(0)

    try:
        market_entry = Market(
            id=uuid.uuid4(),
            title=title,
            description=description,
            source="user",
            file_type=file_extension,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        # uploading the metdata
        db.add(market_entry)
        db.commit()
        db.refresh(market_entry)

        # upload file to s3
        upload_to_s3(contents, file_extension, "nova-content-bucket", f"{market_entry.id}.{file_extension}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database insert failed: {str(e)}")
    
    return {
        "message": "Market data uploaded successfully",
        "id": str(market_entry.id),
        "file_type": file_extension,
        "file_size_bytes": len(contents)
    }

@content_router.delete("/{content_id}")
async def delete_content(content_id: str):
    """
    Docstring for delete_content
    
    :type content_id: str
    """
    return {"message": f"Content {content_id} deleted"}
