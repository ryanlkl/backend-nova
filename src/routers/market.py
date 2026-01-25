"""
Market Router - API endpoints for market trend data
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.utils.db import get_db
from src.services.market import MarketService

market_router = APIRouter(prefix="/market")


@market_router.get("/")
async def list_market_items(db: Session = Depends(get_db)):
    """
    Retrieves all market trend items from the database.

    Returns:
        List of all market items with their details

    Raises:
        500 error if database query fails
    """
    try:
        markets = MarketService.list_market_items(db)
        return {"data": markets, "count": len(markets)}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve market items from database"
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        ) from e


@market_router.get("/{item_id}")
async def get_market_item(item_id: str, db: Session = Depends(get_db)):
    """
    Retrieves a specific market item by its ID.

    Args:
        item_id: UUID of the market item to retrieve

    Returns:
        The market item details if found

    Raises:
        400 error if item_id is not a valid UUID format
        404 error if market item does not exist
        500 error if database query fails
    """
    # Validate UUID format
    try:
        from uuid import UUID
        UUID(item_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid ID format. Must be a valid UUID"
        )

    try:
        market = MarketService.get_market_item_by_id(db, item_id)

        if not market:
            raise HTTPException(
                status_code=404,
                detail=f"Market item with ID '{item_id}' not found"
            )

        return {"data": market}

    except HTTPException:
        # Re-raise HTTP exceptions (like 404) without wrapping them
        raise

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve market item from database"
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        ) from e
