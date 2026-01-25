"""
Legislation database model
"""
from datetime import datetime
from sqlalchemy import Column, Text, Uuid, Enum
from src.utils.db import Base

class Legislation(Base):
    """
    id: Uuid - Unique identifier for the legislation
    title: Text - Title of the legislation
    description: Text - Description of the legislation
    source_url: Text - URL source of the legislation
    created_at: Text - Timestamp of legislation creation
    updated_at: Text - Timestamp of last legislation update

    Methods:
    --------
    __repr__: Returns a string representation of the Legislation instance
    to_dict: Converts the Legislation instance to a dictionary
    """
    __tablename__ = "legislations"

    id = Column(Uuid, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(Text, nullable=False)
    file_type = Column(
        Enum(
            "pdf",
            "docx",
            "csv",
            "xlsx",
            "pptx",
            name="file_types"
        ),
        nullable=False
    )
    created_at = Column(Text, default=datetime.now().isoformat())
    updated_at = Column(
        Text,
        default=datetime.now().isoformat(),
        onupdate=datetime.now().isoformat()
    )
    def __repr__(self):
        """
        Returns a string representation of the Legislation instance
        
        :param self: The Legislation instance
        """
        return f"<Legislation(title={self.title}, source={self.source})>"

    def to_dict(self):
        """
        Converts the Legislation instance to a dictionary
        
        :param self: The Legislation instance
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
