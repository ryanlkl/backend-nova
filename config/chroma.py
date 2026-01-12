import chromadb
import chromadb.utils.embedding_functions as embedding_functions

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.HttpClient(host='localhost', port=8080)

collection = client.get_or_create_collection(
    name="docs",
    embedding_function=sentence_transformer_ef 
)

doc1_info = "DSBC has 18 offices."
doc2_info = "DSBC makes most of its revenue from interest alongside some from capital markets and fees"
doc3_info = "DSBC has global presents, operating within 44 markets."

collection.upsert(
    documents=[doc1_info, doc2_info, doc3_info],
    metadatas=[{"source": "BBC"}, {"source": "GOVUK"}, {"source": "WORLDGOV"}],
    ids=["id1", "id2", "id3"]
)

print(collection.get(include=["metadatas", "documents", "embeddings"]))

print("Successfully upserted documents using the local model")