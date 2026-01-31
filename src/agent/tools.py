"""
Docstring for agent.tools
"""
from langchain.tools import tool
from src.utils.chroma import chroma_client

@tool
def search_legislation(query: str) -> str:
    """Search legislative documents for relevant information and return the top 3 results"""
    
    collection = chroma_client.get_collection("legislation")
    
    if collection:
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        
        documents = results.get("documents")
        if not documents or not documents[0]:
            return "No relevant information was found"
        
        return "\n".join(documents[0])
    
    else: return "Could not connect to Chroma"
    
@tool
def search_market(query: str) -> str:
    """Search market documents for relevant information and return the top 3 results"""
    
    collection = chroma_client.get_collection("market")
    
    if collection:
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        
        documents = results.get("documents")
        if not documents or not documents[0]:
            return "No relevant information was found"
        
        return "\n".join(documents[0])
    
    else: return "Could not connect to Chroma"
    
@tool
def search_payments(query: str) -> str:
    """Search payment documents for relevant information and return the top 3 results"""
    
    collection = chroma_client.get_collection("payments")
    
    if collection:
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        
        documents = results.get("documents")
        if not documents or not documents[0]:
            return "No relevant information was found"
        
        return "\n".join(documents[0])
    
    else: return "Could not connect to Chroma"


