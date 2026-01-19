"""
Market database model
"""
from datetime import datetime
from sqlalchemy import Column, Text, Uuid
from src.utils.db import Base, engine

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
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

Base.metadata.create_all(bind=engine)
