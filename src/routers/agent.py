"""
Docstring for routers.agent
"""
from fastapi import APIRouter, Depends
from src.schema.agent import AgentQuery
from src.utils.agent import agent 
from src.services.agent_service import exec_query

agent_router = APIRouter(prefix="/agent")


@agent_router.post("/") # Include appropriate schema
async def query_agent(query: AgentQuery):
    """
    Endpoint retrieves agent query for processing
    """
    res = exec_query(query.query, agent)
    return {"message": res}