"""
Pydantic models used to:
1. Force LLM output into a predictable structure (extraction results)
2. Define the shape of API responses
"""

from pydantic import BaseModel, Field
from typing import List


class ResumeData(BaseModel):
    name: str = Field(default="", description="Candidate's full name if present")
    skills: List[str] = Field(default_factory=list, description="All technical and soft skills mentioned")
    experience_years: float = Field(default=0, description="Approximate total years of professional experience")
    job_titles: List[str] = Field(default_factory=list, description="Past job titles held")
    education: List[str] = Field(default_factory=list, description="Degrees / institutions mentioned")
    certifications: List[str] = Field(default_factory=list, description="Certifications mentioned")


class JobDescriptionData(BaseModel):
    job_title: str = Field(default="", description="Title of the role")
    required_skills: List[str] = Field(default_factory=list, description="Must-have skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have skills")
    min_experience_years: float = Field(default=0, description="Minimum years of experience required")


class SkillMatch(BaseModel):
    resume_term: str
    jd_term: str


class ComparisonResult(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    partial_matches: List[SkillMatch]


class AnalysisResponse(BaseModel):
    ats_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    partial_matches: List[SkillMatch]
    suggestions: List[str]
