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
    allow_origins=[
        "https://chatbot-1-pi-liard.vercel.app"
    ],
    allow_credentials=True,
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
            "paraphrase-MiniLM-L3-v2",
            device="cpu"
        )
        print("SentenceTransformer model loaded.")

    return model


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask(question: Question):
    print("🔥 ASK API HIT")
    print("1. Question received:", question.question)

    cleaned_question = question.question.strip()

    if not cleaned_question:
        return {
            "answer": "Please enter a question."
        }

    try:
        embedding_model = get_model()
        print("✅ Model loaded")

        embedding = embedding_model.encode(
            cleaned_question
        ).tolist()

        print("✅ Embedding created")

        pdf_collection = get_collection()
        print("✅ Chroma loaded")

        result = pdf_collection.query(
            query_embeddings=[embedding],
            n_results=5
        )

        print("✅ Chroma query completed")

        documents = result.get("documents", [])

        if not documents or not documents[0]:
            return {
                "answer": "I couldn't find any relevant information in the PDF."
            }

        context = "\n\n".join(documents[0])

        print("4. Context length:", len(context))
        print("Retrieved context:", context[:1000])

        prompt = f"""
Answer the user's question directly using only the PDF context below.

Rules:
- Give the actual answer.
- Do not tell the user to visit or check a page.
- Do not only repeat a section title.
- Do not use information outside the supplied context.
- If the answer is unavailable, say:
  "I couldn't find enough information in the PDF to answer that question."
- Mention a page number only after providing the answer, if the page number
  exists in the context.

PDF Context:
{context}

User Question:
{cleaned_question}

Direct Answer:
"""

        print("5. Sending request to Groq")

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a PDF question-answering assistant. "
                        "Answer questions directly from the supplied context. "
                        "Never only direct the user to a page or section."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        print("6. Groq response received")

        answer = response.choices[0].message.content

        print("7. Groq answer:", answer)

        return {
            "answer": answer
        }

    except Exception as e:
        print("ASK API ERROR:", repr(e))

        return {
            "answer": "An error occurred while processing your question.",
            "error": str(e)
        }


    return {
        "answer": answer
    }

