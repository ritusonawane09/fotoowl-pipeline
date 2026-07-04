"""
Standalone sanity check: proves retrieval actually finds relevant documents,
before we trust it inside a real agent.

Run: python -m rag.test_retrieval
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

PERSIST_DIR = "rag/chroma_db"

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

style_store = Chroma(
    collection_name="style_guides",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)

remotion_store = Chroma(
    collection_name="remotion_docs",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)


def demo_query(store, query, label):
    print(f"\nQuery [{label}]: '{query}'")
    results = store.similarity_search(query, k=2)
    for i, doc in enumerate(results, 1):
        print(f"  #{i} -> source: {doc.metadata['source']}")
        print(f"       preview: {doc.page_content[:80].strip()}...")


if __name__ == "__main__":
    print("=== Testing style_guides collection ===")
    demo_query(style_store, "slow emotional wedding video with warm colors", "cinematic-ish prompt")
    demo_query(style_store, "fast energetic birthday party highlight reel", "upbeat-ish prompt")

    print("\n=== Testing remotion_docs collection ===")
    demo_query(remotion_store, "how do I fade an image in and out", "fade transition")
    demo_query(remotion_store, "how do I show text captions on screen", "captions")
