
from fastembed import TextEmbedding

print("Loading embedding model...")

model = TextEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

texts = [
    "What is cloud computing?",
    "Azure virtual machines are cloud resources."
]

embeddings = list(model.embed(texts))

print("Embedding model loaded successfully!")
print("Number of vectors:", len(embeddings))
print("Vector dimensions:", len(embeddings[0]))
