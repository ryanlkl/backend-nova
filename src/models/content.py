"""
Market database model
"""
from datetime import datetime
from sqlalchemy import Column, Text, Uuid, Enum, Float
from src.utils.db import Base

class Content(Base):
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
    __tablename__ = "content"

    id = Column(Uuid, primary_key=True, index=True)
    title = Column(Text, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(Enum("legislation", "market", "insight", name="content_types"), nullable=False)
    file_type = Column(Enum("pdf", "docx", "csv", "xlsx", "xls", "pptx", "ppt", "txt", name="file_types"), nullable=False)
    uploaded_by = Column(Text, nullable=False)
    source = Column(Text)
    file_size = Column(Float)
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
            "updated_at": self.updated_at,
            "uploaded_by": self.uploaded_by,
            "file_size": self.file_size
        }
    