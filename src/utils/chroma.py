"""
Docstring for utils.chroma
"""
import chromadb
import chromadb.utils.embedding_functions as ef

sentence_transformer_ef = ef.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.HttpClient(host="localhost", port=8080)

collection = client.get_or_create_collection(
    name="docs",
    embedding_function=sentence_transformer_ef
)
