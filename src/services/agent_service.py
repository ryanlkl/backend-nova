"""
Docstring for services.agent
"""
from src.utils.agent import init_agent
import re

def exec_query(query, agent):
    result = agent.invoke({"input": query})

    # Parse sources from intermediate steps as a fallback / for structured access
    # sources = []
    # for _, tool_output in result["intermediate_steps"]:
    #     sources.extend(re.findall(r'\[Source: (.+?)\]', tool_output))

    return result
    
    

'''
Answer:

(.venv) (base) dawidstepien@Dawids-MacBook-Pro backend-nova % python -m src.services.agent_service

DSBC operates with a global presence, having 18 offices across 44 markets. 
The company primarily generates its revenue from interest, with additional income from capital markets and fees.

'''
    
    