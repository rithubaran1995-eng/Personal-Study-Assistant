
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL")

if not api_key:
    raise ValueError("GROQ_API_KEY missing in .env")

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model=model_name,
    messages=[
        {
            "role": "user",
            "content": "Explain cloud computing in two sentences."
        }
    ]
)

print(response.choices[0].message.content)
