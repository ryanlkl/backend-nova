"""
Docstring for services.agent
"""
from src.utils.agent import init_agent
import re

def exec_query(query, history, agent):
    prompt = f"""
    Here are the last 15 messages in the conversation:

    {history}

    and here is the next message:

    {query}

    Respond to the query using your knowledge as a payments market trends and legislation expert.
    """
    result = agent.invoke({"input": prompt})

    # Parse sources from intermediate steps as a fallback / for structured access
    # sources = []
    # for _, tool_output in result["intermediate_steps"]:
    #     sources.extend(re.findall(r'\[Source: (.+?)\]', tool_output))

    message = result["messages"][-1].content
    tools = result["messages"][0].tool_calls
    legislation_tool_response = result["messages"][1]
    market_tool_response = result["messages"][2]

    return {
        "message": message,
        "tools": tools,
        "legislation_tool_response": legislation_tool_response,
        "market_tool_response": market_tool_response
    }
    
    

'''
Answer:

(.venv) (base) dawidstepien@Dawids-MacBook-Pro backend-nova % python -m src.services.agent_service

DSBC operates with a global presence, having 18 offices across 44 markets. 
The company primarily generates its revenue from interest, with additional income from capital markets and fees.

'''
    
    