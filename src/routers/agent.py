"""
Docstring for routers.agent
"""
from fastapi import APIRouter

agent_router = APIRouter(prefix="/agent")


@agent_router.post("/") # Include appropriate schema
async def query_agent():
    """
    Docstring for query_agent
    """
    return {"message": "Agent queried"}