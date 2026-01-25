"""
Market database model
"""
from datetime import datetime
from sqlalchemy import Column, Text, Uuid, Enum
from src.utils.db import Base

class Market(Base):
    """
    id: Uuid - Unique identifier for the market
    title: Text - Title of the market
    description: Text - Description of the market
    source: Text - Source of the market data
    created_at: Text - Timestamp of market creation
    updated_at: Text - Timestamp of last market update

    Methods:
    --------
    __repr__: Returns a string representation of the Market instance
    to_dict: Converts the Market instance to a dictionary
    """
    __tablename__ = "markets"

    id = Column(Uuid, primary_key=True, index=True)
    title = Column(Text, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(Text, nullable=False)
    file_type = Column(Enum("pdf", "docx", "csv", "xlsx", "pptx", name="file_types"), nullable=False)
    created_at = Column(Text, default=datetime.now().isoformat())
    updated_at = Column(
        Text,
        default=datetime.now().isoformat(),
        onupdate=datetime.now().isoformat()
    )

    def __repr__(self):
        """
        Returns a string representation of the Market instance
        
        :param self: The Market instance
        """
        return f"<Market(title={self.title}, source={self.source})>"

    def to_dict(self):
        """
        Converts the Market instance to a dictionary
        
        :param self: The Market instance
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "file_type": self.file_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
