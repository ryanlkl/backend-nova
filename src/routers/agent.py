"""
Docstring for routers.agent
"""
from fastapi import APIRouter

agent_router = APIRouter(prefix="/agent")

## CRUD Endpoints for Agent
@agent_router.get("/")
async def list_agents():
    """
    Docstring for list_agents
    """
    return {"message": "List of agents"}

@agent_router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """
    Docstring for get_agent
    
    :type agent_id: str
    """
    return {"message": f"Details of agent {agent_id}"}

@agent_router.post("/") # Include appropriate schema
async def create_agent():
    """
    Docstring for create_agent
    """
    return {"message": "Agent created"}

@agent_router.put("/{agent_id}") # Include appropriate schema
async def update_agent(agent_data: dict, agent_id: str):
    """
    Docstring for update_agent
    
    :param agent_data: Description
    :type agent_data: dict
    :param agent_id: Description
    :type agent_id: str
    """
    return {
        "message": f"Agent {agent_id} updated",
        "data": agent_data
        }

@agent_router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """
    Docstring for delete_agent
    
    :type agent_id: str
    """
    return {"message": f"Agent {agent_id} deleted"}
