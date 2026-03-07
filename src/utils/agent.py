"""
utils/agent.py
"""
import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
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

    prompt = (
        "You are a research assistant for the payments solution team with access to market trends "
        f"and legislation databases. The date today is: {datetime.now().strftime('%Y-%m-%d')}. "
        "When answering, if you called any tools, cite your sources using the [Source: ...] tags "
        "from tool outputs. For questions that are not applicable to markets or legislation, do not call any tools. "
        "Use a formal and professional tone. Overall, answer the question to the best of your ability, calling tools if necessary."
    )
    structure = (
            "Format your final answer as:\n\n"
            "Answer: <your answer>\n\n"
            "Sources:\n- <source 1>\n- <source 2>"
        )

    initialised_agent = create_agent(
        model=model,
        tools=[leg_tool, mar_tool],
        system_prompt=f"{prompt}\n\n{structure}"
    )

    return initialised_agent

agent = init_agent()
