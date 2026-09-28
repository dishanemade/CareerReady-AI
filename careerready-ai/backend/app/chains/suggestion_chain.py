"""
Suggestion Chain: generates personalized resume improvement suggestions.

This is the second big RAG use case -- instead of letting the LLM
improvise generic advice ("add more keywords!"), we retrieve real
ATS best-practice content relevant to the specific gaps found, and
have the LLM write suggestions grounded in that retrieved material.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.llm_factory import get_llm
from app.models.schemas import ComparisonResult
from app.rag.retriever import retrieve_context


def generate_suggestions(comparison: ComparisonResult, jd_title: str) -> list[str]:
    # Build a retrieval query from the actual missing skills + ATS formatting topic
    query = (
        f"Resume best practices for a {jd_title} role, "
        f"missing skills: {', '.join(comparison.missing_skills) or 'none'}, "
        f"ATS formatting rules"
    )
    rag_context = retrieve_context(query, k=5)

    llm = get_llm(temperature=0.4)
    parser = StrOutputParser()

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a resume coach. Using ONLY the reference knowledge provided below, "
         "write 4-6 specific, actionable suggestions to improve this candidate's resume "
         "for the target role. Each suggestion should be one sentence, concrete, and tied "
         "to either a missing skill or a formatting/best-practice issue. Do not invent facts "
         "not supported by the reference knowledge or the given gaps. "
         "Return each suggestion on its own line, no numbering, no extra commentary.\n\n"
         "Reference knowledge:\n{rag_context}"),
        ("human",
         "Target role: {jd_title}\n"
         "Missing skills: {missing_skills}\n"
         "Partially matched skills (synonyms found but worth stating explicitly): {partial_matches}")
    ])

    chain = prompt | llm | parser
    raw_output = chain.invoke({
        "rag_context": rag_context,
        "jd_title": jd_title,
        "missing_skills": ", ".join(comparison.missing_skills) or "none",
        "partial_matches": ", ".join(
            f"{p.resume_term} -> {p.jd_term}" for p in comparison.partial_matches
        ) or "none",
    })

    suggestions = [line.strip("-• \t") for line in raw_output.split("\n") if line.strip()]
    return suggestions
