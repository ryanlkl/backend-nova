"""
Market Service - Handles all database operations for market data
"""
from sqlalchemy.orm import Session
from src.models.market import Market


class MarketService:
    """
    Service class for market-related database operations.
    Provides methods to retrieve market trend data from PostgreSQL.
    """

    @staticmethod
    def list_market_items(db: Session) -> list[dict]:
        """
        Retrieves all market items from the database.

        Args:
            db: SQLAlchemy database session

        Returns:
            List of market items as dictionaries
        """
        markets = db.query(Market).all()
        return [market.to_dict() for market in markets]

    @staticmethod
    def get_market_item_by_id(db: Session, item_id: str) -> dict | None:
        """
        Retrieves a single market item by its unique ID.

        Args:
            db: SQLAlchemy database session
            item_id: UUID string of the market item

        Returns:
            Market item as dictionary if found, None otherwise
        """
        market = db.query(Market).filter(Market.id == item_id).first()
        if market:
            return market.to_dict()
        return None