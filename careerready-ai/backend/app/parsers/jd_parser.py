"""
Handles job description input, which can be either:
- pasted plain text
- an uploaded file (PDF/DOCX/TXT)

Reuses the resume parser's file-reading logic since the underlying
file formats are identical.
"""

from app.parsers.resume_parser import parse_resume


def parse_job_description(text: str | None, file_bytes: bytes | None, filename: str | None) -> str:
    """
    Returns plain text for the job description, from whichever input was provided.
    """
    if text and text.strip():
        return text.strip()

    if file_bytes and filename:
        return parse_resume(file_bytes, filename)  # same file-parsing logic applies

    raise ValueError("No job description provided. Paste text or upload a file.")
