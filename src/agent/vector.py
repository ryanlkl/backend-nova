import chromadb

client = chromadb.HttpClient(host="localhost", port=8080)

collection = client.get_or_create_collection(
    name="docs"
)

doc1 = "hi"
doc2 = "hello"
doc3 = "yo"

collection.upsert(
    documents = [doc1, doc2, doc3],
    metadatas = [{"source": "doc1 info"}, {"source": "doc2 info"}, {"source": "doc3 info"}],
    ids = ["id1", "id2", "id3"]
)

results = collection.get()
print(results)