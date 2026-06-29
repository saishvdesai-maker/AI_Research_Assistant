import chromadb

client = None


def get_client():
    global client

    if client is None:
        client = chromadb.PersistentClient(
            path="./chroma_db"
        )

    return client
collection = get_client().get_or_create_collection(...)


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