"""
Docstring for routers.content
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query, BackgroundTasks
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
async def list_content_by_content_type(
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

    
@content_router.get("/item/{content_id}")
async def get_content(
    content_id: str,
    content_type: ContentType = Query(...),  
    db: Session = Depends(get_db),
):
    try:
        return ContentService.get_content(db, content_id, content_type)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error") from e

@content_router.post("/")
async def upload_market(
    content_type: Annotated[ContentType, Form()],
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    file: Annotated[UploadFile, File(description="content upload")],
    background_tasks:BackgroundTasks,
    db: Session = Depends(get_db)
    ):
    try:
        return await ContentService.upload_content(
            db=db,
            title=title,
            description=description,
            file=file,
            content_type = content_type,
            background_tasks=background_tasks
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error") from e
   

@content_router.delete("/item/{content_id}")
async def delete_content(
    content_id: str,
    background_tasks : BackgroundTasks,
    content_type: ContentType = Query(...),
    db: Session = Depends(get_db),
    
    ):
    """
    Deletes a specific content item by its ID
    
    :type content_id: str
    """
    # TODO: if we delete are we deleting from s3 and chroma
    try:
        return ContentService.delete_content(db=db, content_id=content_id, content_type=content_type, background_tasks=background_tasks)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error") from e
    

@content_router.get("/item/{content_id}/download")
def download_content(
    content_id: str,
    content_type: ContentType = Query(...),
    db: Session = Depends(get_db),
):
    """
    Downloads a content item file
    """
    try:
        return ContentService.download_content(
            db=db,
            content_id=content_id,
            content_type=content_type,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error") from e