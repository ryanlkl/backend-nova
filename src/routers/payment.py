"""
Docstring for routers.payment
"""
from fastapi import APIRouter

payment_router = APIRouter(prefix="/payment")

## CRUD Endpoints for Payment
@payment_router.get("/")
async def list_payments():
    """
    Docstring for list_payments
    """
    return {"message": "List of payments"}

@payment_router.get("/{payment_id}")
async def get_payment(payment_id: str):
    """
    Docstring for get_payment
    
    :type payment_id: str
    """
    return {"message": f"Details of payment {payment_id}"}

@payment_router.post("/") # Include appropriate schema
async def create_payment():
    """
    Docstring for create_payment
    """
    return {"message": "Payment created"}

@payment_router.put("/{payment_id}") # Include appropriate schema
async def update_payment(payment_data: dict, payment_id: str):
    """
    Docstring for update_payment
    
    :param payment_data: Description
    :type payment_data: dict
    :param payment_id: Description
    :type payment_id: str
    """
    return {
        "message": f"Payment {payment_id} updated",
        "data": payment_data
        }

@payment_router.delete("/{payment_id}")
async def delete_payment(payment_id: str):
    """
    Docstring for delete_payment
    
    :type payment_id: str
    """
    return {"message": f"Payment {payment_id} deleted"}
