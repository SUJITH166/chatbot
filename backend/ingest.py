from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
import os


# Read PDF
pdf_path = "uploads/hubblefocusgalaxies.pdf"

reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"


# Split text into chunks
def split_text(text, size=500):
    chunks = []
    for i in range(0, len(text), size):
        chunks.append(text[i:i+size])
    return chunks


chunks = split_text(text)

print("Chunks created:", len(chunks))


# Create embeddings
model = SentenceTransformer(
    "paraphrase-MiniLM-L3-v2",
    device="cpu"
)

embeddings = model.encode(chunks).tolist()


# Create ChromaDB
client = chromadb.PersistentClient(
    path="./chroma_db"
)


collection = client.get_or_create_collection(
    name="pdfs"
)


# Store data
collection.add(
    ids=[str(i) for i in range(len(chunks))],
    documents=chunks,
    embeddings=embeddings
)


print("PDF stored successfully!")