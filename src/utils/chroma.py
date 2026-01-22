import chromadb
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("CHROMA_API_KEY")
tenant_key = os.getenv("CHROMA_TENANT_KEY")


def connect_to_chroma():
    client = chromadb.CloudClient(
        api_key=api_key,
        tenant=tenant_key,
        database='chroma-prod'
    )
    return client
