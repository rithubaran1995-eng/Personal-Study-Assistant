
from src.database import (
    initialize_database,
    create_conversation,
    save_message,
    get_conversation_messages,
    get_all_conversations,
    delete_conversation
)

import uuid


# Initialize database
initialize_database()

# Create a test conversation
conversation_id = str(uuid.uuid4())

create_conversation(
    conversation_id,
    "Python Learning"
)

print("Conversation created!")

# Save messages
save_message(
    conversation_id,
    "user",
    "What are Python functions?"
)

save_message(
    conversation_id,
    "assistant",
    "Python functions are reusable blocks of code."
)

print("Messages saved!")

# Retrieve messages
messages = get_conversation_messages(conversation_id)

print("\nConversation messages:")

for message in messages:
    print(f"{message['role']}: {message['content']}")

# List conversations
conversations = get_all_conversations()

print("\nConversation history:")

for conversation in conversations:
    print(
        conversation["title"],
        "- Messages:",
        conversation["message_count"]
    )

# Delete test conversation
delete_conversation(conversation_id)

print("\nTest conversation deleted!")
