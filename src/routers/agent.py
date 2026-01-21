"""
Docstring for routers.agent
"""
from fastapi import APIRouter
from src.schema.agent import AgentQuery

agent_router = APIRouter(prefix="/agent")


@agent_router.post("/") # Include appropriate schema
async def query_agent(query: AgentQuery):
    """
    Endpoint retrieves agent query for processing
    """
    return {"message": "Agent queried"}