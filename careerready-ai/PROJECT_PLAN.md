# CareerReady AI — Project Plan
### AI-Powered ATS Resume Analyzer using RAG + LangChain

---

## 1. Overview

**CareerReady AI** is an intelligent resume analysis tool that compares a user's resume against a target job description, identifies matching and missing skills, generates an ATS compatibility score, and produces personalized improvement suggestions — all grounded using Retrieval-Augmented Generation (RAG) over a curated career/skills knowledge base, orchestrated with LangChain.

---

## 2. Core Features

1. Resume upload (PDF/DOCX)
2. Job description input (paste text or upload file)
3. Structured information extraction from resume
4. Structured requirement extraction from job description
5. RAG-based retrieval of skills taxonomy, ATS best practices, and industry keyword knowledge
6. Skill matching (exact + semantic) → matched / missing / partial skills
7. ATS compatibility score (weighted, explainable)
8. Personalized, RAG-grounded improvement suggestions
9. Result presentation (dashboard-style output)

---

## 3. System Architecture

```
┌─────────────┐      ┌──────────────────┐      ┌────────────────────────┐
│  Frontend   │─────▶│   Backend API     │─────▶│  LangChain Orchestrator │
│ (React/     │◀─────│   (FastAPI)       │◀─────│  (Extraction/Compare/   │
│  Streamlit) │      └──────────────────┘      │   Score/Suggest Chains) │
└─────────────┘                                └───────────┬────────────┘
                                                            │
                                          ┌─────────────────┼─────────────────┐
                                          ▼                 ▼                 ▼
                                   ┌────────────┐   ┌───────────────┐  ┌─────────────┐
                                   │  LLM API   │   │  Vector Store  │  │   Parsers    │
                                   │ (GPT-4 /   │   │ (Chroma/FAISS) │  │ (PDF/DOCX →  │
                                   │  Claude)   │   │  + Embeddings  │  │  raw text)   │
                                   └────────────┘   └───────────────┘  └─────────────┘
                                                            │
                                                   ┌────────────────┐
                                                   │ Knowledge Base │
                                                   │ (skills, ATS   │
                                                   │  rules, guides)│
                                                   └────────────────┘
```

---

## 4. End-to-End Data Flow

1. User uploads resume + provides JD via frontend
2. Backend parses both into raw text (PDF/DOCX loaders)
3. LangChain **Extraction Chain** converts resume text → structured JSON (skills, experience, education, certifications)
4. LangChain **Extraction Chain** converts JD text → structured JSON (required skills, preferred skills, experience level)
5. A retrieval query is built from the extracted skills/JD terms
6. **RAG Retriever** queries the vector DB for relevant knowledge chunks (skill synonyms, industry keywords, ATS rules)
7. LangChain **Comparison Chain** matches resume skills vs JD skills (keyword + embedding similarity), using retrieved context to resolve synonyms
8. **Scoring module** computes a weighted ATS compatibility score
9. LangChain **Suggestion Chain** (RAG-grounded on resume best-practice docs) generates specific, actionable suggestions tied to the identified gaps
10. Backend returns a structured JSON result to the frontend for display

---

## 5. Role of RAG

RAG is used wherever the system needs **grounded external knowledge** rather than relying on the LLM's raw parametric knowledge:

| Retrieval Use Case | Knowledge Base Content |
|---|---|
| Skill synonym resolution | Skill taxonomy / alias mappings (e.g. "JS" = "JavaScript") |
| Industry keyword awareness | Curated keyword banks per job domain |
| ATS formatting compliance | ATS parsing rules & formatting pitfalls |
| Resume improvement suggestions | Resume-writing best practice guides |

**Retrieval pipeline:** query → embed (sentence-transformer / OpenAI embeddings) → similarity search in vector store → top-k chunks → injected into LLM prompt context.

---

## 6. Role of LangChain

| Component | LangChain Piece Used |
|---|---|
| Resume/JD ingestion | Document Loaders (PDF, DOCX) |
| Knowledge base prep | Text Splitters + Embeddings + VectorStore wrappers |
| Retrieval | Retriever interface over Chroma/FAISS |
| Info extraction | LLM Chain / LCEL pipeline + structured Output Parser (JSON) |
| Comparison logic | Chain combining structured data + retrieved context |
| Suggestion generation | RAG chain (retriever + LLM + prompt template) |

---

## 7. Vector Database & Embeddings

- **Vector DB:** Chroma (embedded, no separate server — ideal for a competition build) or FAISS
- **Embedding model options:**
  - `all-MiniLM-L6-v2` (HuggingFace sentence-transformers) — free, local, no API cost
  - OpenAI `text-embedding-3-small` — higher quality, requires API key
- **What gets embedded:**
  - Knowledge base documents (skills taxonomy, ATS guides, keyword banks)
  - Optionally, resume/JD skill phrases (for semantic similarity matching, separate from the RAG knowledge base)

---

## 8. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React (or Streamlit for faster competition build) |
| Backend | Python + FastAPI |
| Orchestration | LangChain (LCEL chains) |
| LLM | OpenAI GPT-4 / Anthropic Claude API |
| Vector DB | Chroma (or FAISS) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) or OpenAI embeddings |
| Resume/JD Parsing | `pypdf` / `pdfplumber`, `python-docx`, LangChain document loaders |
| Database (results/history) | SQLite (simple) or PostgreSQL |
| Deployment | Local / Streamlit Cloud / Render / Vercel (frontend) |

---

## 9. API Design

| Endpoint | Method | Purpose |
|---|---|---|
| `/upload-resume` | POST | Upload & parse resume file |
| `/upload-jd` | POST | Upload or submit pasted JD text |
| `/analyze` | POST | Run full pipeline (extraction → RAG → matching → scoring → suggestions) |
| `/result/{id}` | GET | Retrieve a past analysis result |
| `/knowledge-base/status` | GET | (optional) Check vector DB health/stats |

**Example `/analyze` response shape:**
```json
{
  "ats_score": 78,
  "matched_skills": ["Python", "SQL", "Machine Learning"],
  "missing_skills": ["Docker", "Kubernetes"],
  "partial_matches": [{"resume": "JS", "jd": "JavaScript"}],
  "suggestions": [
    "Add a 'Skills' section listing containerization tools like Docker.",
    "Quantify your project impact (e.g., 'reduced processing time by 30%')."
  ]
}
```

---

## 10. Folder Structure

```
careerready-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entrypoint
│   │   ├── routes/
│   │   │   ├── upload.py
│   │   │   └── analyze.py
│   │   ├── chains/
│   │   │   ├── extraction_chain.py
│   │   │   ├── comparison_chain.py
│   │   │   ├── scoring.py
│   │   │   └── suggestion_chain.py
│   │   ├── rag/
│   │   │   ├── vectorstore.py
│   │   │   ├── embeddings.py
│   │   │   └── retriever.py
│   │   ├── parsers/
│   │   │   ├── resume_parser.py
│   │   │   └── jd_parser.py
│   │   ├── models/                  # Pydantic schemas
│   │   └── db/
│   ├── knowledge_base/
│   │   ├── skills_taxonomy.json
│   │   ├── ats_best_practices.md
│   │   └── industry_keywords/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   └── package.json
├── PROJECT_PLAN.md
└── README.md
```

---

## 11. Development Phases

**Phase 1 — Setup & Ingestion**
- Project scaffolding (backend + frontend)
- Resume/JD file upload + parsing (PDF/DOCX → text)

**Phase 2 — Knowledge Base & RAG**
- Curate skills taxonomy, ATS guides, keyword banks
- Chunk + embed knowledge base into Chroma/FAISS
- Build retriever

**Phase 3 — LangChain Extraction Pipeline**
- Extraction chain for resume → structured JSON
- Extraction chain for JD → structured JSON

**Phase 4 — Matching & Scoring**
- Keyword + semantic similarity matching
- ATS score calculation logic

**Phase 5 — Suggestion Generation**
- RAG-grounded suggestion chain
- Prompt engineering for actionable, specific feedback

**Phase 6 — Integration & UI**
- Connect frontend to backend APIs
- Build results dashboard (score, skills, suggestions)

**Phase 7 — Testing & Polish**
- Test with varied resume formats
- Edge cases (poorly formatted resumes, sparse JDs)
- Demo prep for competition

---

## 12. Open Decisions (to confirm before implementation)

- Frontend: React vs Streamlit (Streamlit is faster to build for a competition demo)
- LLM: OpenAI vs Anthropic Claude API
- Embeddings: local (free, no key) vs OpenAI (higher quality, costs money)
- Persistence: do we need to store analysis history, or is single-session enough?
