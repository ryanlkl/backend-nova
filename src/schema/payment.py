"""
Payment Schemas

These are the shapes of data we send to the frontend.
We use Pydantic to make sure the data is always in the right format.
"""
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class TrendDirection(str, Enum):
    """Which way is the metric moving?"""
    up = "up"
    down = "down"
    stable = "stable"


# ============================================
# Response models for /market-pulse/stats
# ============================================

class StatItem(BaseModel):
    """
    One statistic to show on the dashboard.
    
    Example:
    {
        "value": "£4.2B",
        "raw_value": 4200,
        "change": 12.5,
        "trend": "up",
        "period": "vs last month"
    }
    """
    value: str  # Formatted for display (e.g., "£4.2B")
    raw_value: float  # Raw number for calculations
    change: float  # Percent change (e.g., 12.5 means +12.5%)
    trend: TrendDirection  # up, down, or stable
    period: str = "vs last month"  # What we're comparing to


class MarketPulseStatsResponse(BaseModel):
    """
    All the main stats for the market pulse dashboard.
    The frontend expects these specific fields.
    """
    total_consumer_credit: Optional[StatItem] = None
    credit_card_lending: Optional[StatItem] = None
    mortgage_approvals: Optional[StatItem] = None
    bank_rate: Optional[StatItem] = None
    last_updated: Optional[str] = None  # When we last fetched data


# ============================================
# Response models for /trend-alerts
# ============================================

class TrendAlert(BaseModel):
    """
    An alert about a significant change in a metric.
    
    Example: {"metric": "Open Banking", "change": 34, "direction": "up"}
    """
    metric: str
    change: float  # Percent change
    direction: TrendDirection
    message: Optional[str] = None  # Optional description


class TrendAlertsResponse(BaseModel):
    """List of notable trends to highlight"""
    alerts: List[TrendAlert]
    last_updated: Optional[str] = None


# ============================================
# Response models for /history (charts)
# ============================================

class HistoryDataPoint(BaseModel):
    """Single data point for a time series chart"""
    date: str  # YYYY-MM-DD format
    value: float


class MetricHistory(BaseModel):
    """Historical data for one metric"""
    metric_name: str
    unit: str  # "millions_gbp", "percent", "thousands"
    data: List[HistoryDataPoint]


class HistoryResponse(BaseModel):
    """Historical data for all metrics - for charts"""
    total_consumer_credit: Optional[MetricHistory] = None
    credit_card_lending: Optional[MetricHistory] = None
    mortgage_approvals: Optional[MetricHistory] = None
    bank_rate: Optional[MetricHistory] = None
    months_included: int
