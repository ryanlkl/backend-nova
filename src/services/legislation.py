"""
Docstring for services.legislation
"""

class LegislationService:
    """
    Docstring for LegislationService
    """
    @staticmethod
    def list_legislation():
        """
        Docstring for list_legislation
        """
        return [
            {"id": 1, "title": "Data Protection Act", "year": 2018},
            {"id": 2, "title": "Freedom of Information Act", "year": 2000}
        ]

    @staticmethod
    def get_legislation_info():
        """
        Docstring for get_legislation_info
        """
        return {
            "name": "Data Protection Act",
            "year": 2018,
            "description": "An act to make provision for the regulation of the processing of personal data."
        }
    
