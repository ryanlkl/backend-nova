"""
utils/agent.py
"""
import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.agent import tools
from app_config import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def init_agent():
    leg_tool = tools.search_legislation
    mar_tool = tools.search_market
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        max_tokens=1000,
        timeout=30,
    )

    # System message is a plain string here — datetime is eagerly evaluated at
    # init time. If you need it per-request, move agent init into a factory function
    # or use a RunnableLambda to inject it dynamically.
    prompt = (
            f"You are a research assistant for the payments solution team with access to market trends and legislation databases. "
            f"The date today is: {datetime.now().strftime('%Y-%m-%d')}.\n\n"
            "When answering, cite your sources using the [Source: ...] tags from tool outputs. "
            "Format your final answer as:\n\n"
            "Answer: <your answer>\n\n"
            "Sources:\n- <source 1>\n- <source 2>"
        )

    intialised_agent = create_agent(
        model=model,
        tools = [leg_tool, mar_tool],
        system_prompt=prompt
    )

    return intialised_agent

agent = init_agent()
