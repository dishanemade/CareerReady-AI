"""
Builds (or loads) the Chroma vector database that stores the
knowledge base: skill synonyms, ATS best practices, industry keywords.

Run this file directly once to build the index:
    python -m app.rag.vectorstore
"""

import os
import json
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.embeddings import get_embeddings

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_base")
PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")
COLLECTION_NAME = "careerready_knowledge"


def _load_knowledge_base_documents() -> list[Document]:
    """Reads every file in knowledge_base/ and turns it into LangChain Documents."""
    documents = []

    # 1. Skills taxonomy (JSON: { "JavaScript": ["JS", "ECMAScript"], ... })
    taxonomy_path = os.path.join(KNOWLEDGE_BASE_DIR, "skills_taxonomy.json")
    if os.path.exists(taxonomy_path):
        with open(taxonomy_path, "r") as f:
            taxonomy = json.load(f)
        for canonical_skill, synonyms in taxonomy.items():
            content = f"Skill: {canonical_skill}. Known synonyms/aliases: {', '.join(synonyms)}."
            documents.append(Document(page_content=content, metadata={"source": "skills_taxonomy"}))

    # 2. ATS best practices (markdown)
    ats_path = os.path.join(KNOWLEDGE_BASE_DIR, "ats_best_practices.md")
    if os.path.exists(ats_path):
        with open(ats_path, "r") as f:
            documents.append(Document(page_content=f.read(), metadata={"source": "ats_best_practices"}))

    # 3. Industry keyword files (one .md/.txt per industry)
    keywords_dir = os.path.join(KNOWLEDGE_BASE_DIR, "industry_keywords")
    if os.path.isdir(keywords_dir):
        for fname in os.listdir(keywords_dir):
            fpath = os.path.join(keywords_dir, fname)
            with open(fpath, "r") as f:
                documents.append(
                    Document(page_content=f.read(), metadata={"source": f"industry_keywords/{fname}"})
                )

    return documents


def build_vectorstore() -> Chroma:
    """Builds the Chroma index from scratch and persists it to disk."""
    raw_documents = _load_knowledge_base_documents()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(raw_documents)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
    )
    print(f"Indexed {len(chunks)} knowledge base chunks into '{PERSIST_DIR}'.")
    return vectorstore


def load_vectorstore() -> Chroma:
    """Loads an already-built Chroma index from disk (fast, no re-embedding)."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=PERSIST_DIR,
    )


def get_vectorstore() -> Chroma:
    """Builds the index if it doesn't exist yet, otherwise loads it."""
    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
        return load_vectorstore()
    return build_vectorstore()


if __name__ == "__main__":
    build_vectorstore()
