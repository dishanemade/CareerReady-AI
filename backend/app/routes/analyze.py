"""
The main pipeline endpoint. This is where every piece from the plan
comes together in order:

  parse -> extract -> RAG-grounded compare -> score -> RAG-grounded suggest
"""
import traceback
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.parsers.resume_parser import parse_resume
from app.parsers.jd_parser import parse_job_description
from app.chains.extraction_chain import extract_resume_data, extract_jd_data
from app.chains.comparison_chain import compare_skills
from app.chains.scoring import calculate_ats_score
from app.chains.suggestion_chain import generate_suggestions
from app.models.schemas import AnalysisResponse

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    resume_file: UploadFile = File(...),
    jd_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
):
    try:
        # Step 1: Parse inputs into plain text
        resume_bytes = await resume_file.read()
        resume_text = parse_resume(resume_bytes, resume_file.filename)

        jd_file_bytes = await jd_file.read() if jd_file else None
        jd_filename = jd_file.filename if jd_file else None
        jd_plain_text = parse_job_description(jd_text, jd_file_bytes, jd_filename)

        # Step 2: Extract structured data from each
        resume_data = extract_resume_data(resume_text)
        jd_data = extract_jd_data(jd_plain_text)

        # Step 3: RAG-grounded comparison
        comparison = compare_skills(resume_data.skills, jd_data.required_skills)

        # Step 4: Score
        ats_score = calculate_ats_score(comparison, resume_data, jd_data)

        # Step 5: RAG-grounded suggestions
        suggestions = generate_suggestions(comparison, jd_data.job_title or "the target role")

        return AnalysisResponse(
            ats_score=ats_score,
            matched_skills=comparison.matched_skills,
            missing_skills=comparison.missing_skills,
            partial_matches=comparison.partial_matches,
            suggestions=suggestions,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
