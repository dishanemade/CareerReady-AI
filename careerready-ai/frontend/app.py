"""
CareerReady AI - Streamlit Frontend

Run with: streamlit run app.py
Make sure the backend is running first: uvicorn app.main:app --reload (from backend/)
"""

import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000/api/analyze"

st.set_page_config(page_title="CareerReady AI", page_icon="📄", layout="centered")

st.title("📄 CareerReady AI")
st.caption("AI-powered ATS Resume Analyzer — RAG + LangChain")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload your resume")
    resume_file = st.file_uploader("Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

with col2:
    st.subheader("2. Provide the job description")
    jd_input_mode = st.radio("Input method", ["Paste text", "Upload file"], horizontal=True)

    jd_text = None
    jd_file = None
    if jd_input_mode == "Paste text":
        jd_text = st.text_area("Paste the job description here", height=200)
    else:
        jd_file = st.file_uploader("Job description file", type=["pdf", "docx", "txt"], key="jd_file")

st.divider()

if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
    if not resume_file:
        st.error("Please upload a resume first.")
    elif not jd_text and not jd_file:
        st.error("Please paste or upload a job description.")
    else:
        with st.spinner("Parsing, retrieving context, and analyzing... this may take a moment"):
            files = {"resume_file": (resume_file.name, resume_file.getvalue())}
            data = {}
            if jd_text:
                data["jd_text"] = jd_text
            if jd_file:
                files["jd_file"] = (jd_file.name, jd_file.getvalue())

            try:
                response = requests.post(BACKEND_URL, files=files, data=data, timeout=120)
                response.raise_for_status()
                result = response.json()
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the backend: {e}")
                st.stop()

        st.success("Analysis complete!")

        st.subheader("📊 ATS Compatibility Score")
        st.metric(label="Score", value=f"{result['ats_score']} / 100")
        st.progress(result["ats_score"] / 100)

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("✅ Matched Skills")
            if result["matched_skills"]:
                for skill in result["matched_skills"]:
                    st.markdown(f"- {skill}")
            else:
                st.write("None found.")

        with col_b:
            st.subheader("❌ Missing Skills")
            if result["missing_skills"]:
                for skill in result["missing_skills"]:
                    st.markdown(f"- {skill}")
            else:
                st.write("None — great coverage!")

        if result["partial_matches"]:
            st.subheader("🟡 Partial / Synonym Matches")
            for match in result["partial_matches"]:
                st.markdown(f"- Your **{match['resume_term']}** ≈ their **{match['jd_term']}**")

        st.subheader("💡 Personalized Suggestions")
        for suggestion in result["suggestions"]:
            st.markdown(f"- {suggestion}")
