import chromadb
import chromadb.utils.embedding_functions as embedding_functions

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=""
)

client = chromadb.HttpClient(host='localhost', port=8080)

collection = client.get_or_create_collection(
    name="docs",
    embedding_functions=sentence_transformer_ef
)

doc1_info = "info 1"
doc2_info = "info 2"
doc3_info = "info 3"

collection.upsert(
    documents = [doc1_info, doc2_info, doc3_info],
    metadatas = [{"source": "doc1 info"}, {"source": "doc2 info"}, {"source": "doc3 info"}],
    ids = ["id1", "id2", "id3"]
)

print(collection.get(include=["metadatas", "documents", "embedding"]))

print("Successfully upserted documents using the local model")