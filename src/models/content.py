from datetime import datetime, timezone
from sqlalchemy import Column, Text, Enum, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from src.utils.db import Base
import uuid

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "ppt", "pptx", "xls", "xlsx", "csv"}

class ContentHub(Base):
    """
    User-uploaded content table.

    Columns:
    --------
    id: UUID - Primary key
    title: Text - Title of the content
    description: Text - Optional description
    content_type: Text - 'market', 'legislation', 'insight', 'other'
    file_type: Enum - File type (pdf, docx, etc.)
    file_size: BigInteger - Size of the uploaded file in bytes
    created_at: Text - ISO timestamp of creation
    updated_at: Text - ISO timestamp of last update

    Methods:
    --------
    __repr__: Returns a string representation
    to_dict: Converts instance to dictionary
    """

    __tablename__ = "content_hub"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(
        Enum("market", "legislation", "insight", "other", name="content_type_enum"),
        nullable=False
    )
    file_type = Column(
        Enum(*ALLOWED_EXTENSIONS, name="file_type_enum"),
        nullable=False
    )
    file_size = Column(BigInteger, nullable=True)
    created_at = Column(Text, default=lambda: datetime.now(timezone.utc).isoformat())
    updated_at = Column(Text, default=lambda: datetime.now(timezone.utc).isoformat(), onupdate=lambda: datetime.now(timezone.utc).isoformat())

    def __repr__(self):
        return f"<ContentHub(title={self.title}, content_type={self.content_type})>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "content_type": self.content_type,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }