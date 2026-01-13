"""
Docstring for services.agent
"""
from ..agent.agent import init_agent

def exec_query(query):
    agent = init_agent()

    res = agent.invoke(
    {"messages": [{"role": "user", "content": query}]})
    
    return res["messages"][-1].content

print(exec_query("Hi, can you please tell me about DSBC?"))

'''
Answer:

(.venv) (base) dawidstepien@Dawids-MacBook-Pro backend-nova % python -m src.services.agent_service

DSBC operates with a global presence, having 18 offices across 44 markets. 
The company primarily generates its revenue from interest, with additional income from capital markets and fees.

'''
    
    