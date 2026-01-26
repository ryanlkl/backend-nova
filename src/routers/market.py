"""
Docstring for routers.market
"""

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from fastapi import Depends
from src.utils.db import get_db
from src.services.market import MarketService

market_router = APIRouter(prefix="/market")

## CRUD Endpoints for Market
@market_router.get("/")
async def list_market_items(db: Session = Depends(get_db)):
    """
    Docstring for list_market_items
    Additional filtering and pagination can be added as needed
    """
    return await MarketService.list_market_items(db)

@market_router.get("/{item_id}")
async def get_market_item(item_id: str, bucket: str = Query(...)):
    """
    Docstring for get_market_item
    
    :type item_id: str
    """
    return MarketService.get_market_object(item_id, bucket=bucket)

