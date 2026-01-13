"""
Agent initialization module.
"""

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from src.agent import tools

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def init_agent():

    search_document_tool = tools.search_documents

    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        max_tokens=1000,
        timeout=30
    )

    agent = create_agent(
        model=model,
        tools = [search_document_tool],
        system_prompt="You are an assistant, helping users with their queries.",
    )
    
    return agent
