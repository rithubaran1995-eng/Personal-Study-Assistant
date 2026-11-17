
import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path("study_assistant.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():

    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_hash TEXT UNIQUE NOT NULL,
                page_count INTEGER DEFAULT 0,
                chunk_count INTEGER DEFAULT 0,
                uploaded_at TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                title TEXT,
                created_at TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(conversation_id)
                    ON DELETE CASCADE
            )
        """)

        conn.commit()


def get_document_by_hash(file_hash):

    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM documents WHERE file_hash = ?",
            (file_hash,)
        ).fetchone()


def add_document(doc_id, filename, file_hash, pages, chunks):

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO documents
            (doc_id, filename, file_hash, page_count,
             chunk_count, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            filename,
            file_hash,
            pages,
            chunks,
            datetime.now().isoformat()
        ))


def get_all_documents():

    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM documents ORDER BY uploaded_at DESC"
        ).fetchall()


def delete_document(doc_id):

    with get_connection() as conn:
        conn.execute(
            "DELETE FROM documents WHERE doc_id = ?",
            (doc_id,)
        )


def create_conversation(conversation_id, title):

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO conversations
            (conversation_id, title, created_at)
            VALUES (?, ?, ?)
        """, (
            conversation_id,
            title,
            datetime.now().isoformat()
        ))


def save_message(conversation_id, role, content):

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO messages
            (conversation_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            conversation_id,
            role,
            content,
            datetime.now().isoformat()
        ))


def get_conversation_messages(conversation_id):

    with get_connection() as conn:
        return conn.execute("""
            SELECT role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY message_id ASC
        """, (conversation_id,)).fetchall()


def get_all_conversations():

    with get_connection() as conn:
        return conn.execute("""
            SELECT c.conversation_id, c.title, c.created_at,
                   COUNT(m.message_id) AS message_count
            FROM conversations c
            LEFT JOIN messages m
                ON c.conversation_id = m.conversation_id
            GROUP BY c.conversation_id
            ORDER BY c.created_at DESC
        """).fetchall()


def delete_conversation(conversation_id):

    with get_connection() as conn:
        conn.execute(
            "DELETE FROM conversations WHERE conversation_id = ?",
            (conversation_id,)
        )
