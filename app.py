
import streamlit as st
import os
import uuid

from dotenv import load_dotenv
from groq import Groq

from src.database import (
    initialize_database,
    create_conversation,
    save_message,
    get_conversation_messages,
    get_all_conversations,
    delete_conversation
)

from src.rag_pipeline import RAGPipeline


# =====================================
# 1. INITIALIZATION
# =====================================

st.set_page_config(
    page_title="Study Assistant",
    page_icon="📚",
    layout="wide"
)

load_dotenv()
initialize_database()


@st.cache_resource
def get_pipeline():
    return RAGPipeline()


@st.cache_resource
def get_groq():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


pipeline = get_pipeline()


if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None


# =====================================
# 2. CUSTOM STYLING
# =====================================

st.markdown("""
<style>

/* Main application */
.stApp {
    background-color: #212121;
    color: #ececec;
}

/* Main content width */
.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #171717;
    border-right: 1px solid #303030;
}

/* Sidebar text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #d1d5db;
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
    border: 1px solid #383838;
    background-color: transparent;
    color: #eeeeee;
    transition: background-color 0.2s ease;
}

.stButton > button:hover {
    background-color: #303030;
    border-color: #505050;
    color: white;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background-color: transparent;
    border: none;
    padding: 1rem 0;
}

/* Chat input */
[data-testid="stChatInput"] {
    background-color: #303030;
    border: 1px solid #505050;
    border-radius: 16px;
}

/* Input text */
.stChatInput textarea {
    color: #ffffff;
}

/* Expanders */
[data-testid="stExpander"] {
    border: 1px solid #383838;
    border-radius: 10px;
}

/* Divider */
hr {
    border-color: #383838;
}

/* Hide Streamlit footer */
footer {
    visibility: hidden;
}

/* Hide top decoration */
[data-testid="stHeader"] {
    background-color: transparent;
}

</style>
""", unsafe_allow_html=True)


# =====================================
# 3. SIDEBAR
# =====================================

with st.sidebar:

    st.markdown("## 📚 Study Assistant")

    st.caption("Your personal AI study companion")

    st.divider()

    # New chat
    if st.button("＋  New Chat", use_container_width=True):

        st.session_state.current_conversation_id = None
        st.rerun()

    st.divider()

    # PDF upload
    with st.expander("📎  Add study materials"):

        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            key="pdf_uploader"
        )

        if st.button(
            "Process PDFs",
            use_container_width=True,
            type="primary"
        ):

            if not uploaded_files:

                st.warning("Please select a PDF first.")

            else:

                for uploaded_file in uploaded_files:

                    try:

                        with st.spinner(
                            f"Processing {uploaded_file.name}..."
                        ):

                            result = pipeline.process_pdf(uploaded_file)

                        if result["status"] == "success":

                            st.success(
                                f"{uploaded_file.name} indexed successfully."
                            )

                        elif result["status"] == "duplicate":

                            st.warning(
                                f"{uploaded_file.name} is already indexed."
                            )

                        elif result["status"] == "empty":

                            st.warning(
                                f"No extractable text in {uploaded_file.name}."
                            )

                    except Exception as e:

                        st.error(f"Processing failed: {e}")

    # Document library
    with st.expander("📚  My Documents"):

        documents = pipeline.get_documents()

        if documents:

            st.caption(f"{len(documents)} documents indexed")

            for document in documents:

                st.markdown(f"**{document['filename']}**")

                st.caption(
                    f"{document['page_count']} pages · "
                    f"{document['chunk_count']} chunks"
                )

                if st.button(
                    "Delete",
                    key=f"delete_{document['doc_id']}",
                    use_container_width=True
                ):

                    try:

                        pipeline.delete_pdf(document["doc_id"])

                        st.success("Document deleted.")
                        st.rerun()

                    except Exception as e:

                        st.error(f"Deletion failed: {e}")

                st.divider()

        else:

            st.caption("No documents uploaded yet.")

    st.divider()

    # Conversation history
    st.markdown("### Your chats")

    conversations = get_all_conversations()

    if conversations:

        for conversation in conversations:

            conversation_id = conversation["conversation_id"]

            col1, col2 = st.columns([5, 1])

            with col1:

                is_active = (
                    st.session_state.current_conversation_id
                    == conversation_id
                )

                label = (
                    f"● {conversation['title']}"
                    if is_active
                    else conversation["title"]
                )

                if st.button(
                    label,
                    key=f"chat_{conversation_id}",
                    use_container_width=True
                ):

                    st.session_state.current_conversation_id = (
                        conversation_id
                    )

                    st.rerun()

            with col2:

                if st.button(
                    "×",
                    key=f"delete_chat_{conversation_id}"
                ):

                    delete_conversation(conversation_id)

                    if (
                        st.session_state.current_conversation_id
                        == conversation_id
                    ):

                        st.session_state.current_conversation_id = None

                    st.rerun()

    else:

        st.caption("Your conversations will appear here.")


# =====================================
# 4. MAIN CHAT AREA
# =====================================

current_id = st.session_state.current_conversation_id

if current_id:

    messages = get_conversation_messages(current_id)

    # Display existing conversation
    for message in messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

else:

    # Welcome screen
    st.markdown(
        "<div style='text-align:center; padding-top:100px;'>"
        "<h1 style='font-size:32px; color:#eeeeee;'>"
        "What are you studying today?"
        "</h1>"
        "<p style='color:#999999; font-size:16px;'>"
        "Ask questions about your uploaded study materials."
        "</p>"
        "</div>",
        unsafe_allow_html=True
    )


# =====================================
# 5. CHAT INPUT
# =====================================

question = st.chat_input(
    "Ask anything about your study materials..."
)


# =====================================
# 6. PROCESS USER QUESTION
# =====================================

if question:

    if not pipeline.get_documents():

        st.warning(
            "Please upload and process a study PDF first."
        )

    else:

        try:

            # Create conversation if needed
            if not st.session_state.current_conversation_id:

                conversation_id = str(uuid.uuid4())

                title = question[:50]

                create_conversation(
                    conversation_id,
                    title
                )

                st.session_state.current_conversation_id = (
                    conversation_id
                )

            current_id = st.session_state.current_conversation_id

            # Save user message
            save_message(
                current_id,
                "user",
                question
            )

            # Search study materials
            with st.spinner("Thinking..."):

                results = pipeline.search(question)

                if not results:

                    answer = (
                        "I couldn't find relevant information "
                        "about this topic in your uploaded study PDFs."
                    )

                else:

                    context = "\n\n".join(
                        [
                            f"Source: {r['source']}, "
                            f"Page: {r['page']}\n{r['text']}"
                            for r in results
                        ]
                    )

                    client = get_groq()

                    response = client.chat.completions.create(

                        model=os.getenv("GROQ_MODEL"),

                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a beginner-friendly study tutor. "
                                    "Answer using only the supplied study context. "
                                    "Do not use outside knowledge. If the context "
                                    "does not contain the answer, clearly say so. "
                                    "Explain concepts simply."
                                )
                            },
                            {
                                "role": "user",
                                "content": (
                                    f"Study context:\n{context}\n\n"
                                    f"Question: {question}"
                                )
                            }
                        ]
                    )

                    answer = response.choices[0].message.content

                    # Add source references
                    answer += "\n\n**Sources:**\n"

                    for result in results:

                        answer += (
                            f"- {result['source']} "
                            f"(Page {result['page']})\n"
                        )

            # Save assistant response
            save_message(
                current_id,
                "assistant",
                answer
            )

            st.rerun()

        except Exception as e:

            st.error(f"Something went wrong: {e}")
