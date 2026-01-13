import chromadb
from langchain.tools import tool

def connect_to_chroma():
    try:
        client = chromadb.HttpClient(host="localhost", port=8080)
        collection = client.get_collection(name="docs")
        return collection
    except Exception as e:
        return None

@tool
def search_documents(query: str) -> str:
    """Search documents for relevant information and return the top 3 results"""
    
    collection = connect_to_chroma()
    
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
    