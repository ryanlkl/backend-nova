"""
Docstring for routers.legislation
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.db import get_db
from src.services.legislation import LegislationService

legislation_router = APIRouter(prefix="/legislation")

## CRUD Endpoints for Legislation
@legislation_router.get("/")
async def list_legislation(db: Session = Depends(get_db)):
    """
    Docstring for list_legislation
    """
    return {"message": "List of legislation"}

@legislation_router.get("/{legislation_id}")
async def get_legislation(legislation_id: str, db: Session = Depends(get_db)):
    """
    Docstring for get_legislation
    
    :type legislation_id: str
    """
    return {"message": f"Details of legislation {legislation_id}"}
