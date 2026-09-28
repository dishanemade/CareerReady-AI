"""
Extraction Chain: takes raw resume or JD text and asks the LLM to
return structured data (skills, experience, etc.) as clean JSON,
using LangChain's structured-output parsing so we get a Pydantic
object back instead of a free-text blob.
"""

from langchain_core.prompts import ChatPromptTemplate
from app.llm_factory import get_llm
from app.models.schemas import ResumeData, JobDescriptionData


def extract_resume_data(resume_text: str) -> ResumeData:
    llm = get_llm(temperature=0)
    structured_llm = llm.with_structured_output(ResumeData)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert resume parser. Extract structured information from the "
         "resume text below. Be thorough -- capture every skill mentioned, even if "
         "it's inside a sentence rather than a dedicated skills list."),
        ("human", "Resume text:\n\n{resume_text}")
    ])

    chain = prompt | structured_llm
    return chain.invoke({"resume_text": resume_text})


def extract_jd_data(jd_text: str) -> JobDescriptionData:
    llm = get_llm(temperature=0)
    structured_llm = llm.with_structured_output(JobDescriptionData)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert job description parser. Extract the required skills, "
         "preferred/nice-to-have skills, job title, and minimum years of experience "
         "from the job description below. Distinguish clearly between 'required' and "
         "'preferred' skills based on the language used (e.g. 'must have' vs 'a plus')."),
        ("human", "Job description text:\n\n{jd_text}")
    ])

    chain = prompt | structured_llm
    return chain.invoke({"jd_text": jd_text})
