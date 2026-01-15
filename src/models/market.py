"""
Docstring for models.market
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String
from src.utils.db import Base

class Market(Base):
    """
    Docstring for Market
    """
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    source = Column(String, nullable=False)
    created_at = Column(String, default=datetime.now().isoformat())
    updated_at = Column(String, default=datetime.now().isoformat(), onupdate=datetime.now().isoformat())

    def __repr__(self):
        """
        Docstring for __repr__
        
        :param self: Description
        """
        return f"<Market(title={self.title}, source={self.source})>"
    
    def to_dict(self):
        """
        Docstring for to_dict
        
        :param self: Description
        """
        return {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    