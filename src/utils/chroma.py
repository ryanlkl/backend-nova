"""
Docstring for utils.chroma
"""
import chromadb
from app_config import CHROMA_API_KEY, CHROMA_TENANT_KEY


def chroma_init():
    """
    Docstring for connect_to_chroma
    """
    client = chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT_KEY,
        database='chroma-prod'
    )
    return client

chroma_client = chroma_init()
