"""
Scoring module: calculates the final ATS compatibility score.

This is deliberately NOT an LLM call -- a score should be consistent,
explainable, and reproducible. We use a transparent weighted formula
instead of asking the AI to "guess" a number.
"""

from app.models.schemas import ComparisonResult, ResumeData, JobDescriptionData

# Weights should sum to 1.0
WEIGHT_REQUIRED_SKILLS = 0.55
WEIGHT_EXPERIENCE = 0.20
WEIGHT_PARTIAL_MATCH_BONUS = 0.15
WEIGHT_FORMAT_COMPLETENESS = 0.10


def calculate_ats_score(
    comparison: ComparisonResult,
    resume_data: ResumeData,
    jd_data: JobDescriptionData,
) -> int:
    total_required = len(jd_data.required_skills) or 1  # avoid divide-by-zero

    # 1. Required skill coverage
    matched_count = len(comparison.matched_skills)
    skill_score = min(matched_count / total_required, 1.0) * WEIGHT_REQUIRED_SKILLS

    # 2. Partial match bonus (synonym matches count for something, but less than exact)
    partial_score = (
        min(len(comparison.partial_matches) / total_required, 1.0) * WEIGHT_PARTIAL_MATCH_BONUS
    )

    # 3. Experience alignment
    if jd_data.min_experience_years <= 0:
        experience_score = WEIGHT_EXPERIENCE  # no requirement stated, full credit
    else:
        ratio = resume_data.experience_years / jd_data.min_experience_years
        experience_score = min(ratio, 1.0) * WEIGHT_EXPERIENCE

    # 4. Resume "completeness" as a proxy for ATS formatting friendliness
    completeness_checks = [
        bool(resume_data.skills),
        bool(resume_data.education),
        bool(resume_data.job_titles),
        resume_data.experience_years > 0,
    ]
    completeness_score = (sum(completeness_checks) / len(completeness_checks)) * WEIGHT_FORMAT_COMPLETENESS

    total = skill_score + partial_score + experience_score + completeness_score
    return round(total * 100)
