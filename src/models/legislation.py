"""
Docstring for models.legislation
"""
from datetime import datetime
from sqlalchemy import Column, String, Uuid
from src.utils.db import Base, engine

class Legislation(Base):
    """
    Docstring for Legislation
    """
    __tablename__ = "legislations"

    id = Column(Uuid, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    created_at = Column(String, default=datetime.now().isoformat())
    updated_at = Column(String, default=datetime.now().isoformat(), onupdate=datetime.now().isoformat())

    def __repr__(self):
        """
        Docstring for __repr__
        
        :param self: Description
        """
        return f"<Legislation(title={self.title}, version={self.version})>"
    
    def to_dict(self):
        """
        Docstring for to_dict
        
        :param self: Description
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "effective_date": self.effective_date,
            "version": self.version,
            "source_url": self.source_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
Base.metadata.create_all(bind=engine)
