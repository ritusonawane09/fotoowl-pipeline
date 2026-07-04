"""
Builds our local vector store (Chroma) from the knowledge files.

We create TWO separate collections, not one combined pile of documents:
  - "style_guides"   : creative/style reference text, retrieved by the Storyboard Writer
  - "remotion_docs"  : Remotion code snippets, retrieved by the Script Generator / Fixer

Chunking strategy: each .txt file is already a short, single-topic, hand-written
unit (one style, or one code pattern) - so each FILE = ONE CHUNK. We deliberately
do NOT split these further, because splitting a style guide mid-sentence or a
code example mid-function would destroy the very context that makes it useful.

Run this file once (python -m rag.build_vectorstore) to create the local DB.
Re-run any time you edit the knowledge .txt files, to refresh the stored data.
"""

import os
import glob
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()

PERSIST_DIR = "rag/chroma_db"

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)


def _load_txt_files_as_documents(folder: str) -> list[Document]:
    docs = []
    for filepath in sorted(glob.glob(os.path.join(folder, "*.txt"))):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        name = os.path.splitext(os.path.basename(filepath))[0]
        docs.append(
            Document(
                page_content=text,
                metadata={"source": name, "filepath": filepath},
            )
        )
    return docs


def build():
    style_docs = _load_txt_files_as_documents("rag/knowledge/style_guides")
    remotion_docs = _load_txt_files_as_documents("rag/knowledge/remotion_docs")

    print(f"Loaded {len(style_docs)} style guide documents: {[d.metadata['source'] for d in style_docs]}")
    print(f"Loaded {len(remotion_docs)} Remotion doc documents: {[d.metadata['source'] for d in remotion_docs]}")

    Chroma.from_documents(
        documents=style_docs,
        embedding=embeddings,
        collection_name="style_guides",
        persist_directory=PERSIST_DIR,
    )
    print("Built 'style_guides' collection.")

    Chroma.from_documents(
        documents=remotion_docs,
        embedding=embeddings,
        collection_name="remotion_docs",
        persist_directory=PERSIST_DIR,
    )
    print("Built 'remotion_docs' collection.")

    print("\nVector store ready at:", PERSIST_DIR)


if __name__ == "__main__":
    build()