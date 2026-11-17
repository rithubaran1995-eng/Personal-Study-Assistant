# Personal Study Assistant

A personal AI-powered study assistant that helps you understand your study materials by asking questions about uploaded PDF documents.

Built using Python, Streamlit, Retrieval-Augmented Generation (RAG), ChromaDB, FastEmbed, and Groq.

## Features

- Upload and process PDF documents.
- Extract text and split it into smaller chunks.
- Generate embeddings locally using FastEmbed.
- Store and search document embeddings using ChromaDB.
- Ask questions about uploaded study materials.
- Generate beginner-friendly answers using Groq AI.
- Display source PDF filenames and page numbers.
- Detect duplicate PDF uploads.
- Delete indexed documents.
- Save and manage conversation history using SQLite.
- ChatGPT-inspired dark user interface.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Programming language |
| Streamlit | Web interface |
| ChromaDB | Vector database |
| FastEmbed | Text embeddings |
| PyMuPDF | PDF text extraction |
| Groq API | AI answer generation |
| SQLite | Conversation and document records |

## Project Structure

```text
Personal-RAG/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── database.py
│   └── rag_pipeline.py
│
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_chroma.py
│   ├── test_embeddings.py
│   ├── test_groq.py
│   └── test_pdf.py
│
├── documents/       # Local PDF files
├── chroma_db/       # Local vector database
├── study_assistant.db
└── .venv/
```

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Personal-RAG
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a template.

Add your Groq API key and model:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_groq_model_name
```

Keep your actual `.env` file private. Never upload your API key to GitHub.

## Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

```text
http://localhost:8501
```

## How It Works

1. Upload a study PDF.
2. Extract text from the PDF using PyMuPDF.
3. Split the extracted text into chunks.
4. Generate embeddings using FastEmbed.
5. Store embeddings in ChromaDB.
6. Ask a question through the chat interface.
7. Retrieve relevant document chunks.
8. Send the retrieved context to Groq.
9. Display the generated answer with source references.

## Future Improvements

- Improve retrieval accuracy.
- Add streaming AI responses.
- Improve source citation presentation.
- Add more document formats.

## Author

**Rithubaran G**

Personal learning project built to explore Python, RAG, vector databases, embeddings, and AI application development.