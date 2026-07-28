from fastapi import FastAPI
from pydantic import BaseModel
import chromadb

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

client = None
collection = None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHROMA_PATH = os.path.join(
    BASE_DIR,
    "chroma_db"
)

def get_collection():
    global client, collection

    if collection is None:
        client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )   

        collection = client.get_or_create_collection(
            name="pdfs"
        )

    return collection


model = None


def get_model():
    global model

    if model is None:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            device="cpu"
        )

    return model


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask(question: Question):

    print("1. Question received:", question.question)

    embedding_model = get_model()

    embedding = embedding_model.encode(
        question.question
    ).tolist()

    print("2. Embedding created")


    pdf_collection = get_collection()

    result = pdf_collection.query(
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

