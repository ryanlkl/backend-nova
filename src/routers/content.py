"""
Docstring for routers.content
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.schema.content import FilterParams, ContentType


from src.utils.db import get_db
from typing import Annotated
from src.services.content import ContentService

content_router = APIRouter(prefix="/content")


@content_router.get("/")
async def list_content(
    filter_query: FilterParams = Depends(FilterParams),
    db: Session = Depends(get_db)
):
    """
    Paginate and sort Market records
    """
    try:
        response = ContentService.list_all_content(db, filter_query)
        return response
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve content from database"
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        ) from e



@content_router.get("/{content_type}")
async def list_content(
    content_type: ContentType,
    filter_query: FilterParams = Depends(FilterParams),
    db: Session = Depends(get_db)
):
    """
    Paginate and sort Market records
    """
    filter_query = filter_query.model_copy(update={"content_type": content_type})
    
    try:
        response = ContentService.list_content(db, filter_query)
        return response
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve content from database"
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        ) from e

    


# @content_router.get("/{content_id}")
# async def get_content(
#     content_id: str,
#     db: Session = Depends(get_db)):
#     """
#     Retrieves details of a specific content item by its ID
    
#     :type content_id: str
#     """

#     market_data = db.get(Market, content_id)
#     if not market_data:
#         raise HTTPException(status_code=404, detail="Content not found")

#     return {
#         "message": "success",
#         "data": market_data.to_dict()
#     }

@content_router.post("/")
async def upload_market(
    content_type: Annotated[ContentType, Form()],
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    file: Annotated[UploadFile, File(description="content upload")],
    db: Session = Depends(get_db)
    ):
    try:
        return await ContentService.upload_content(
            db=db,
            title=title,
            description=description,
            file=file,
            content_type = content_type,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error") from e
   

@content_router.delete("/{content_id}")
async def delete_content(content_id: str):
    """
    Deletes a specific content item by its ID
    
    :type content_id: str
    """
    return {"message": f"Content {content_id} deleted"}
