
import hashlib
import chromadb
import pymupdf

from src.database import (
    get_document_by_hash,
    add_document,
    get_all_documents,
    delete_document
)

from fastembed import TextEmbedding


class RAGPipeline:

    def __init__(self):

        self.model = TextEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )

        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="study_materials",
            metadata={"hnsw:space": "cosine"}
        )

    def process_pdf(self, uploaded_file):

        file_bytes = uploaded_file.getvalue()

        # 1. Generate document hash
        file_hash = hashlib.sha256(
            file_bytes
        ).hexdigest()

        # 2. Check duplicate
        existing = get_document_by_hash(file_hash)

        if existing:
            return {
                "status": "duplicate",
                "message": "This PDF is already indexed."
            }

        # 3. Extract PDF text
        pdf = pymupdf.open(
            stream=file_bytes,
            filetype="pdf"
        )

        chunks = []
        metadatas = []
        ids = []

        for page_number, page in enumerate(pdf, start=1):

            text = " ".join(
                page.get_text("text").split()
            )

            if not text:
                continue

            start = 0
            chunk_index = 0

            while start < len(text):

                end = min(start + 1000, len(text))

                if end < len(text):
                    boundary = text.rfind(" ", start, end)

                    if boundary > start:
                        end = boundary + 1

                chunk = text[start:end].strip()

                if chunk:

                    chunk_id = hashlib.sha256(
                        f"{file_hash}|{page_number}|{chunk_index}".encode()
                    ).hexdigest()

                    ids.append(chunk_id)
                    chunks.append(chunk)

                    metadatas.append({
                        "source": uploaded_file.name,
                        "page": page_number,
                        "chunk_index": chunk_index,
                        "doc_id": file_hash
                    })

                    chunk_index += 1

                if end >= len(text):
                    break

                start = end - 150

        page_count = len(pdf)
        pdf.close()

        if not chunks:
            return {
                "status": "empty",
                "message": "No extractable text found."
            }

        # 4. Generate embeddings
        embeddings = [
            vector.tolist()
            for vector in self.model.embed(chunks)
        ]

        # 5. Store in ChromaDB in batches
        batch_size = 64

        try:
            for start in range(0, len(chunks), batch_size):

                end = start + batch_size

                self.collection.upsert(
                    ids=ids[start:end],
                    documents=chunks[start:end],
                    embeddings=embeddings[start:end],
                    metadatas=metadatas[start:end]
                )

            # 6. Register document in SQLite
            add_document(
                doc_id=file_hash,
                filename=uploaded_file.name,
                file_hash=file_hash,
                pages=page_count,
                chunks=len(chunks)
            )

        except Exception:
            self.collection.delete(
                where={"doc_id": file_hash}
            )
            raise

        return {
            "status": "success",
            "chunks": len(chunks),
            "pages": page_count
        }

    def get_documents(self):
        return get_all_documents()

    def delete_pdf(self, doc_id):

        # Delete all chunks belonging to this PDF
        self.collection.delete(
            where={"doc_id": doc_id}
        )

        # Remove document registry entry
        delete_document(doc_id)

        return True


    def search(self, question, top_k=4):

        # Get currently active documents from SQLite
        documents = self.get_documents()

        active_doc_ids = [
            doc["doc_id"] for doc in documents
        ]

        # No active documents
        if not active_doc_ids:
            return []

        # Generate question embedding
        query_vector = list(
            self.model.query_embed([question])
        )[0].tolist()

        # Search only active documents
        results = self.collection.query(
            query_embeddings=[query_vector],

            n_results=min(
                top_k,
                self.collection.count()
            ),

            where={
                "doc_id": {
                    "$in": active_doc_ids
                }
            },

            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        matches = []

        for i in range(len(results["ids"][0])):

            matches.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "page": results["metadatas"][0][i]["page"],
                "distance": results["distances"][0][i]
            })

        return matches
