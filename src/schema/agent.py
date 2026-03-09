"""
Docstring for services.agent
"""
from pydantic import BaseModel

class AgentQuery(BaseModel):
    """
    Docstring for AgentQuery schema
    """
    query: str
    history: list

    def __repr__(self):
        """
        Returns a string representation of the AgentQuery instance
        
        :param self: The AgentQuery instance
        """
        print(f"<AgentQuery(query={self.query})>")
        return f"<AgentQuery(query={self.query})>"