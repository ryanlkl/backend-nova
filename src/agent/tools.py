"""
agent/tools.py
"""
from langchain.tools import tool
from src.utils.chroma import chroma_client

def _format_results(documents: list, metadatas: list) -> str:
    """Zip docs with their metadata and format as a readable string with sources."""
    formatted = []
    for doc, meta in zip(documents[0], metadatas[0]):
        source = meta.get("source", "unknown")
        formatted.append(f"[Source: {source}]\n{doc}")
    return "\n\n---\n\n".join(formatted)

@tool
def search_legislation(query: str) -> str:
    """Search legislative documents for relevant information and return the top 3 results."""
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
    """Search market documents for relevant information and return the top 3 results."""
    collection = chroma_client.get_collection("market")
    if not collection:
        return "Could not connect to Chroma"

    results = collection.query(query_texts=[query], n_results=3)
    documents = results.get("documents")
    metadatas = results.get("metadatas", [[]])

    if not documents or not documents[0]:
        return "No relevant information was found"

    return _format_results(documents, metadatas)