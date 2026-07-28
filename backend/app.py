from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import os
from dotenv import load_dotenv


load_dotenv()
# print(os.getenv("GEMINI_API_KEY"))
print("API key exists:", bool(os.getenv("GROQ_API_KEY")))

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
# for model in client_ai.models.list():
#     print(model.name)
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load ChromaDB

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="pdfs"
)


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask(question: Question):

    print("1. Question received:", question.question)

    embedding = model.encode(
        question.question
    ).tolist()

    print("2. Embedding created")


    result = collection.query(
        query_embeddings=[embedding],
        n_results=3
    )

    print("3. Chroma result:", result)


    context = "\n\n".join(
        result["documents"][0]
    )

    print("4. Context length:", len(context))


    prompt = f"""
You are a helpful assistant.
Answer the question using only the information from the PDF.

PDF Context:
{context}

Question:
{question.question}
"""


    try:
        print("5. Sending request to Groq")

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        print("6. Groq response received")

        answer = response.choices[0].message.content

        print("7. Groq answer:", answer)

    except Exception as e:
        print("GROQ ERROR:", e)

        return {
            "error": str(e)
        }


    return {
        "answer": answer
    }


    return {
        "answer": answer
    }