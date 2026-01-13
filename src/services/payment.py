"""
Docstring for services.payment
"""

class PaymentService:
    @staticmethod
    def get_payment_info():
        return {
            "provider": "Stripe",
            "currency": "USD",
            "transaction_fee": "2.9% + 30¢ per transaction"
        }