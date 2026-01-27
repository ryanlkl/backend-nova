"""
Legislation router module
"""
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from src.utils.db import get_db
from src.services.legislation import LegislationService

legislation_router = APIRouter(prefix="/legislation")

## CRUD Endpoints for Legislation
@legislation_router.get("/")
async def list_legislation(db: Session = Depends(get_db)):
    """
    Lists all legislation entries
    Additional filtering and pagination can be added as needed
    """
    response = await LegislationService.list_legislation(db)
    return response

@legislation_router.get("/{legislation_id}")
async def get_legislation(legislation_id: str, db: Session = Depends(get_db)):
    """
    Retrieves details of a specific legislation entry
    
    :type legislation_id: str
    """
    try:
        result = await LegislationService.get_legislation_info(legislation_id, db)

        file_stream = io.BytesIO(result["data"])

        filename = result["filename"]

        return StreamingResponse(
            file_stream,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
