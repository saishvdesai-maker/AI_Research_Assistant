import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="papers"
)


def add_chunks(chunks):

    ids = []
    documents = []

    for i, chunk in enumerate(chunks):
        ids.append(str(i))
        documents.append(chunk)

    collection.add(
        ids=ids,
        documents=documents
    )


def search(query):

    return collection.query(
        query_texts=[query],
        n_results=3
    )