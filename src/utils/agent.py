"""
Docstring for utils.agent
"""
import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from src.agent import tools
from app_config import OPENAI_API_KEY

# update all the prompts & context
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    
def init_agent():
    """
    Docstring for init_agent
    """
    leg_tool = tools.search_legislation
    mar_tool = tools.search_market
    pay_tool = tools.search_payments

    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        max_tokens=1000,
        timeout=30
    )

    initialised_agent = create_agent(
        model=model,
        tools = [leg_tool, mar_tool, pay_tool],
        system_prompt="You are an assistant, helping users with their queries.",
    )

    return initialised_agent

agent = init_agent()


# # limit of 16384 words/chars?
# import pdfplumber
# def upload_document(pdf_path: str) -> str:
#     client = connect_to_chroma()

#     if not client:
#         return "Could not connect to Chroma"

#     legislation_col = client.get_or_create_collection(name="legislation")

#     try:
#         text = ""
#         with pdfplumber.open(pdf_path) as pdf:
#             for page in pdf.pages:
#                 text += page.extract_text() or ""
#         print("text created: " + str(len(text)))

#         # Upload the extracted text to Chroma
#         legislation_col.add(documents=[text], metadatas=[{"source": pdf_path}], ids=["2"])
#         return "Document uploaded successfully"
    
#     except Exception as e:
#         return f"An error occurred: {str(e)}"
