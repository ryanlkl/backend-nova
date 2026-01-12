"""
Agent initialization module.
"""

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import tools

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def init_agent():
    """
    Docstring for init_agent
    """
    tool1 = tools.get_value
    tool2 = tools.search_documents

    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        max_tokens=1000,
        timeout=30
    )

    agent = create_agent(
        model=model,
        tools = [tool1, tool2],
        system_prompt="System prompt",
    )
    
    return agent
