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
import traceback

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



@content_router.get("/data/{content_type}")
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
    



#############################################
#                                           #   
#                                           #   
#                CONTENT_HUB                #   
#                                           #
#                                           #
#############################################

@content_router.get("/hub")
async def list_content_hub(
    filter_query: FilterParams = Depends(FilterParams),
    db: Session = Depends(get_db)
):
    """
    List Content Hub records with pagination, search, and sorting.
    """
    try:
        response = ContentService.list_content_hub(db=db, filters=filter_query)
        return response
    except SQLAlchemyError as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
    
    
@content_router.post("/")
async def upload_content(
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
    
    
@content_router.patch("/hub/{content_id}")
async def patch_content_hub(
    content_id: str,
    content_type: ContentType | None = Form(None),
    title: str | None = Form(None),
    description: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    # background_tasks: BackgroundTasks = BackgroundTasks(),
    """
    Patch ContentHub record: metadata and optional file replacement
    """
    try:
        response = await ContentService.update_content_hub(
            db=db,
            content_id=content_id,
            title=title,
            description=description,
            content_type=content_type,
            file=file,
            # background_tasks=background_tasks
        )
        return response

    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

    except SQLAlchemyError as e:
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error") from e

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e
    


@content_router.get("/hub/{content_id}")
def download_content(
    content_id: str,
    db: Session = Depends(get_db),
):
    """
    Downloads a content item file
    """
    try:
        return ContentService.download_contenthub(
            db=db,
            content_id=content_id,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error") from e
    


@content_router.delete("/hub/{content_id}")
async def delete_content(
    content_id: str,
    db: Session = Depends(get_db),
    
    ):
    """
    Deletes a specific content item by its ID
    
    :type content_id: str
    """
    # TODO: if we delete are we deleting from s3 and chroma
    try:
        return ContentService.delete_contenthub_item(db=db, content_id=content_id)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error") from e
    
    