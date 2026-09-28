"""
This is the "R" in RAG: given a query, fetch the most relevant
knowledge base chunks so the LLM can use them as grounding context.
"""

from app.rag.vectorstore import get_vectorstore

_vectorstore = None


def _get_store():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = get_vectorstore()
    return _vectorstore


def retrieve_context(query: str, k: int = 4) -> str:
    """
    Searches the knowledge base for the top-k chunks most relevant to `query`,
    and returns them joined as a single context string ready to inject into a prompt.
    """
    store = _get_store()
    results = store.similarity_search(query, k=k)

    if not results:
        return "No additional context found."

    return "\n---\n".join(doc.page_content for doc in results)


def retrieve_context_for_skills(skills: list[str], k_per_skill: int = 2) -> str:
    """
    Convenience helper: builds a combined retrieval query from a list of
    skill terms (e.g. skills found in the resume or JD) and retrieves context
    for all of them at once.
    """
    query = "Skill synonyms and relevance for: " + ", ".join(skills)
    return retrieve_context(query, k=k_per_skill * max(len(skills), 1))
