"""
Payment Router

API endpoints for UK payment statistics from the Bank of England.

Endpoints:
- GET /payment/stats - Main dashboard stats (consumer credit, mortgages, etc.)
- GET /payment/payment-methods - Payment method breakdown
- GET /payment/trend-alerts - Notable trends
- POST /payment/refresh - Manually trigger data refresh from BoE
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.utils.db import get_db
from src.services.payment import PaymentService
from src.schema.payment import (
    MarketPulseStatsResponse,
    PaymentMethodsResponse,
    TrendAlertsResponse
)

payment_router = APIRouter(prefix="/payment")


@payment_router.get("/stats", response_model=MarketPulseStatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """
    Get main dashboard statistics.
    
    Returns the latest values for:
    - Total consumer credit
    - Credit card lending
    - Mortgage approvals
    - Bank rate
    
    Each stat includes the current value, change vs last month, and trend direction.
    """
    return await PaymentService.get_market_pulse_stats(db)


@payment_router.get("/payment-methods", response_model=PaymentMethodsResponse)
async def get_payment_methods():
    """
    Get payment method market share breakdown.
    
    Returns percentage breakdown of payment methods in the UK:
    - Debit Cards, Credit Cards, Faster Payments, Direct Debit, Cash, Other
    
    Note: This is manually updated data from UK Finance reports.
    """
    return await PaymentService.get_payment_methods()


@payment_router.get("/trend-alerts", response_model=TrendAlertsResponse)
async def get_trend_alerts(db: Session = Depends(get_db)):
    """
    Get notable trends worth highlighting.
    
    Returns alerts for metrics that have changed by more than 5%
    compared to the previous month.
    """
    return await PaymentService.get_trend_alerts(db)


@payment_router.post("/refresh")
async def refresh_boe_data(db: Session = Depends(get_db)):
    """
    Manually trigger a data refresh from the Bank of England API.
    
    This fetches the latest data for all tracked metrics and saves
    it to the database. Use this to update data on demand.
    
    In production, you might want to:
    - Add authentication (only admins can trigger refresh)
    - Set up a scheduled job to run this daily
    """
    result = await PaymentService.fetch_boe_data(db)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return result

