"""
Docstring for agent.tools
"""
from langchain.tools import tool
from src.utils.chroma import chroma_client

@tool
def search_legislation(query: str) -> str:
    """Search legislative documents for relevant information and return the top 3 results with document IDs, titles, and dates"""
    
    collection = chroma_client.get_collection("legislation")
    
    if collection:
        results = collection.query(
            query_texts=[query],
            n_results=3,
            include=["documents", "metadatas"]
        )
        
        documents = results.get("documents")
        ids = results.get("ids")
        metadatas = results.get("metadatas")
        if not documents or not documents[0]:
            return "No relevant information was found"
        
        # Format results with IDs, titles, and dates
        formatted_results = []
        for i, doc in enumerate(documents[0]):
            doc_id = ids[0][i] if ids and i < len(ids[0]) else "Unknown"
            metadata = metadatas[0][i] if metadatas and i < len(metadatas[0]) else {}
            
            # Extract metadata fields
            title = metadata.get("title", "")
            created_at = metadata.get("created_at", "")
            source = metadata.get("source", "")
            
            # Build the result string
            result = f"[ID: {doc_id}]"
            if title:
                result += f"\nTitle: {title}"
            if created_at:
                result += f"\nDate: {created_at}"
            if source:
                result += f"\nSource: {source}"
            result += f"\n{doc}"
            
            formatted_results.append(result)
        
        return "\n\n".join(formatted_results)
    
    else: return "Could not connect to Chroma"
    
@tool
def search_market(query: str) -> str:
    """Search market documents for relevant information and return the top 3 results with document IDs, titles, and dates"""
    
    collection = chroma_client.get_collection("market_trends")
    
    if collection:
        results = collection.query(
            query_texts=[query],
            n_results=3,
            include=["documents", "metadatas"]
        )
        
        documents = results.get("documents")
        ids = results.get("ids")
        metadatas = results.get("metadatas")
        if not documents or not documents[0]:
            return "No relevant information was found"
        
        # Format results with IDs, titles, and dates
        formatted_results = []
        for i, doc in enumerate(documents[0]):
            doc_id = ids[0][i] if ids and i < len(ids[0]) else "Unknown"
            metadata = metadatas[0][i] if metadatas and i < len(metadatas[0]) else {}
            
            # Extract metadata fields
            title = metadata.get("title", "")
            created_at = metadata.get("created_at", "")
            source = metadata.get("source", "")
            
            # Build the result string
            result = f"[ID: {doc_id}]"
            if title:
                result += f"\nTitle: {title}"
            if created_at:
                result += f"\nDate: {created_at}"
            if source:
                result += f"\nSource: {source}"
            result += f"\n{doc}"
            
            formatted_results.append(result)
        
        return "\n\n".join(formatted_results)
    
    else: return "Could not connect to Chroma"
    
@tool
def search_payments(query: str) -> str:
    """Search payment documents for relevant information and return the top 3 results with document IDs, titles, and dates"""
    
    collection = chroma_client.get_collection("payments")
    
    if collection:
        results = collection.query(
            query_texts=[query],
            n_results=3,
            include=["documents", "metadatas"]
        )
        
        documents = results.get("documents")
        ids = results.get("ids")
        metadatas = results.get("metadatas")
        if not documents or not documents[0]:
            return "No relevant information was found"
        
        # Format results with IDs, titles, and dates
        formatted_results = []
        for i, doc in enumerate(documents[0]):
            doc_id = ids[0][i] if ids and i < len(ids[0]) else "Unknown"
            metadata = metadatas[0][i] if metadatas and i < len(metadatas[0]) else {}
            
            # Extract metadata fields
            title = metadata.get("title", "")
            created_at = metadata.get("created_at", "")
            source = metadata.get("source", "")
            
            # Build the result string
            result = f"[ID: {doc_id}]"
            if title:
                result += f"\nTitle: {title}"
            if created_at:
                result += f"\nDate: {created_at}"
            if source:
                result += f"\nSource: {source}"
            result += f"\n{doc}"
            
            formatted_results.append(result)
        
        return "\n\n".join(formatted_results)
    
    else: return "Could not connect to Chroma"


