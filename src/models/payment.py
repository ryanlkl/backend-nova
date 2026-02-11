"""
Payment Statistics Model

This model stores payment data fetched from the Bank of England API.
We store each data point (like credit card lending, mortgage approvals, etc.)
as a separate row so we can track changes over time.
"""
from datetime import datetime
from sqlalchemy import Column, Text, Float, Date, Uuid
from src.utils.db import Base
import uuid


class PaymentStatistic(Base):
    """
    Stores payment statistics from the Bank of England.
    
    Each row represents one data point for a specific metric on a specific date.
    For example: "Credit card lending was £1.2B on 2024-01-01"
    
    Fields:
    -------
    id: Unique identifier for this record
    series_code: The BoE code (e.g., LPMAUYN for credit card lending)
    metric_name: Human readable name (e.g., "Credit Card Lending")
    date: The date this data point is for
    value: The numeric value (in millions GBP)
    unit: What the value represents (e.g., "millions_gbp", "percent")
    source: Where we got this data from
    created_at: When we saved this record
    updated_at: When we last updated this record
    """
    __tablename__ = "payment_statistics"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    series_code = Column(Text, nullable=False, index=True)  # BoE series code
    metric_name = Column(Text, nullable=False)  # Human readable name
    date = Column(Date, nullable=False, index=True)  # Date of the data point
    value = Column(Float, nullable=False)  # The actual value
    unit = Column(Text, default="millions_gbp")  # What the value means
    source = Column(Text, default="Bank of England")
    created_at = Column(Text, default=datetime.now().isoformat())
    updated_at = Column(
        Text,
        default=datetime.now().isoformat(),
        onupdate=datetime.now().isoformat()
    )

    def __repr__(self):
        return f"<PaymentStatistic({self.metric_name}: {self.value} on {self.date})>"

    def to_dict(self):
        """Convert this record to a dictionary for API responses"""
        return {
            "id": str(self.id),
            "series_code": self.series_code,
            "metric_name": self.metric_name,
            "date": str(self.date),
            "value": self.value,
            "unit": self.unit,
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
