"""
Comparison Chain: matches resume skills against JD skills.

Uses a two-layer approach:
1. Exact/case-insensitive matching (fast, free, no LLM needed)
2. For everything NOT exactly matched, ask the LLM to resolve partial/synonym
   matches -- grounded with RAG context pulled from the skills taxonomy
   knowledge base, so it doesn't have to guess whether "JS" == "JavaScript".
"""

from langchain_core.prompts import ChatPromptTemplate
from app.llm_factory import get_llm
from app.models.schemas import ComparisonResult
from app.rag.retriever import retrieve_context_for_skills


def compare_skills(resume_skills: list[str], jd_required_skills: list[str]) -> ComparisonResult:
    resume_lower = {s.lower().strip(): s for s in resume_skills}
    jd_lower = {s.lower().strip(): s for s in jd_required_skills}

    # Layer 1: exact matches
    exact_matches = [jd_lower[k] for k in jd_lower if k in resume_lower]
    remaining_jd_skills = [jd_lower[k] for k in jd_lower if k not in resume_lower]

    if not remaining_jd_skills:
        return ComparisonResult(matched_skills=exact_matches, missing_skills=[], partial_matches=[])

    # Layer 2: RAG-grounded synonym resolution for whatever didn't exactly match
    rag_context = retrieve_context_for_skills(remaining_jd_skills + resume_skills)

    llm = get_llm(temperature=0)
    structured_llm = llm.with_structured_output(ComparisonResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are comparing a candidate's resume skills against a job's required skills. "
         "Some of the job's required skills may already be covered by resume skills under "
         "a different name (synonyms, abbreviations, or closely related tools). Use the "
         "reference knowledge below to resolve these cases correctly.\n\n"
         "Reference knowledge (skill synonyms, may be partially relevant):\n{rag_context}\n\n"
         "Return: matched_skills (JD skills the resume already covers, including via synonym), "
         "missing_skills (JD skills the resume does NOT cover at all), and partial_matches "
         "(pairs where a resume term is a synonym/near-match for a JD term)."),
        ("human",
         "Resume skills: {resume_skills}\n\n"
         "Remaining JD required skills to resolve: {remaining_jd_skills}")
    ])

    chain = prompt | structured_llm
    llm_result = chain.invoke({
        "rag_context": rag_context,
        "resume_skills": ", ".join(resume_skills),
        "remaining_jd_skills": ", ".join(remaining_jd_skills),
    })

    return ComparisonResult(
        matched_skills=exact_matches + llm_result.matched_skills,
        missing_skills=llm_result.missing_skills,
        partial_matches=llm_result.partial_matches,
    )
