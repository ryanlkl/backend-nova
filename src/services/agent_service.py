"""
Docstring for services.agent
"""
from src.utils.agent import init_agent

def exec_query(query, agent):

    res = agent.invoke(
    {"messages": [{"role": "user", "content": query}]})
    
    return res["messages"][-1].content
    
    

'''
Answer:

(.venv) (base) dawidstepien@Dawids-MacBook-Pro backend-nova % python -m src.services.agent_service

DSBC operates with a global presence, having 18 offices across 44 markets. 
The company primarily generates its revenue from interest, with additional income from capital markets and fees.

'''
    
    