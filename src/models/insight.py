"""
Docstring for models.content
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Text, Enum
from src.utils.db import Base, engine

class Insight(Base):
    """
    Docstring for Insight model
    """
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
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
        Returns a string representation of the Insight instance
        
        :param self: The Insight instance
        """
        return f"<Insight(title={self.title}, source={self.source}, file_type={self.file_type})>"

    def to_dict(self):
        """
        Converts the Insight instance to a dictionary
        
        :param self: The Insight instance
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "file_type": self.file_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

Base.metadata.create_all(bind=engine)
