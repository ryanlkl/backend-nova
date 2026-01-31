"""
Docstring for routers.payment
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.db import get_db

payment_router = APIRouter(prefix="/payment")

## CRUD Endpoints for Payment
@payment_router.get("/")
async def list_payments(db: Session = Depends(get_db)):
    """
    Docstring for list_payments
    Additional filtering and pagination can be added as needed
    """
    return {"message": "List of payments"}

@payment_router.get("/{payment_id}")
async def get_payment(payment_id: str, db: Session = Depends(get_db)):
    """
    Docstring for get_payment
    
    :type payment_id: str
    """
    return {"message": f"Details of payment {payment_id}"}
