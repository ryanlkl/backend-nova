"""
Docstring for services.legislation
"""
from sqlalchemy.orm import Session
from src.utils.crud import get_with_filters, get_by_id
from src.models.legislation import Legislation

class LegislationService:
    """
    Docstring for LegislationService
    """
    @staticmethod
    async def list_legislation(db: Session):
        """
        Retrieves all legislation entries in the database
        """
        legislation = await get_with_filters(Legislation, db, filters={})
        return legislation

    @staticmethod
    async def get_legislation_info(legislation_id, db: Session):
        """
        Retrieves detailed information about a specific legislation entry
        :param legislation_id: The ID of the legislation entry

        """
        legislation = await get_by_id(Legislation, db, legislation_id)
        return legislation
