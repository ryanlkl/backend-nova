"""
Docstring for services.market
"""

class MarketService:
    """
    Docstring for MarketService
    """
    @staticmethod
    def list_market_items():
        """
        Docstring for list_market_items
        """
        return [
            {"id": 1, "name": "Tech Stocks", "value": "1.5 Trillion USD"},
            {"id": 2, "name": "Real Estate", "value": "2 Trillion USD"},
            {"id": 3, "name": "Commodities", "value": "500 Billion USD"}
        ]

    @staticmethod
    def get_market_info():
        """
        Docstring for get_market_info
        """
        return {
            "name": "Global Tech Market",
            "size": "5 Trillion USD",
            "growth_rate": "8% annually"
        }