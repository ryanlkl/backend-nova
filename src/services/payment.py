"""
Docstring for services.payment
"""

class PaymentService:
    """
    Docstring for PaymentService
    """
    @staticmethod
    def list_payment_data():
        """
        Docstring for list_payment_data
        """
        return [
            {"id": 1, "amount": 100.00, "currency": "USD", "status": "Completed"},
            {"id": 2, "amount": 250.50, "currency": "EUR", "status": "Pending"},
            {"id": 3, "amount": 75.25, "currency": "GBP", "status": "Failed"}
        ]

    @staticmethod
    def get_payment_info():
        """
        Docstring for get_payment_info
        """
        return {
            "provider": "Stripe",
            "currency": "USD",
        }