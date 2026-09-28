"""
Provides the embedding model used to turn text into vectors (numbers
representing meaning), for both indexing the knowledge base and
searching it later.

Using a local HuggingFace sentence-transformer model means this works
with ZERO API cost/key -- good for a competition build.
"""

from langchain_huggingface import HuggingFaceEmbeddings

_EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_embeddings_instance = None


def get_embeddings():
    """Returns a singleton embeddings instance (loading the model is slow, so reuse it)."""
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = HuggingFaceEmbeddings(model_name=_EMBEDDING_MODEL_NAME)
    return _embeddings_instance
