"""
agent/tools.py
"""
from langchain.tools import tool
from src.utils.chroma import chroma_client

@tool
def search_legislation(query: str) -> str:
    """
    Search legislation and regulatory documents relevant to the user's query.
    Use this tool for questions about laws, regulation, compliance, reporting requirements, or legal changes affecting payments.
    Do not use this tool for general market, company, or economic trend questions.
    Returns up to 3 relevant results with source tags.
    """
    collection = chroma_client.get_collection("legislation")
    if not collection:
        return "Could not connect to Chroma"

    results = collection.query(query_texts=[query], n_results=3)
    documents = results.get("documents")
    metadatas = results.get("metadatas", [[]])

    if not documents or not documents[0]:
        return "No relevant information was found"
    
    return _format_results(documents, metadatas)

@tool
def search_market(query: str) -> str:
    """
    Search market trend documents relevant to the user's query.
    Use this tool for questions about payments market trends, industry developments, companies, competition, or the economy.
    Do not use this tool for legal or regulatory questions.
    Returns up to 3 relevant results with source tags.
    """
    collection = chroma_client.get_collection("market_trends")
    if not collection:
        return "Could not connect to Chroma"

    results = collection.query(query_texts=[query], n_results=3)
    documents = results.get("documents")
    metadatas = results.get("metadatas", [[]])

    if not documents or not documents[0]:
        return "No relevant information was found"

    return _format_results(documents, metadatas)

def _format_results(documents: list, metadatas: list) -> str:
    formatted = []
    for doc, meta in zip(documents[0], metadatas[0]):
        source = meta.get("source", "unknown")
        formatted.append(f"[Source: {source}]\n{doc}")
    return "\n\n---\n\n".join(formatted)