
import chromadb
from fastembed import TextEmbedding

# 1. Load our selected local embedding model
print("Loading BGE embedding model...")

model = TextEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

# 2. Connect to persistent ChromaDB
client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="study_materials"
)

# 3. Prepare sample document
documents = [
    "Azure is Microsoft's cloud computing platform."
]

ids = ["test1"]

# 4. Generate embeddings locally using FastEmbed
document_embeddings = list(model.embed(documents))

# 5. Store documents and their vectors
collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=[document_embeddings[0].tolist()]
)

print("Document successfully stored!")

# 6. Search using a question
question = "What is Azure?"

query_embedding = list(model.query_embed([question]))[0]

results = collection.query(
    query_embeddings=[query_embedding.tolist()],
    n_results=1
)

# 7. Display results
print("\nSearch successful!")
print("Question:", question)
print("Retrieved document:", results["documents"][0][0])
print("Document ID:", results["ids"][0][0])

print("\nChromaDB + FastEmbed working successfully!")
