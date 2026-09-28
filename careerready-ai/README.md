# CareerReady AI

AI-powered ATS Resume Analyzer using RAG + LangChain.

See `PROJECT_PLAN.md` for the full architecture and workflow explanation.

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set LLM_PROVIDER (openai or anthropic) and the matching API key
```

Build the knowledge base index (only needs to run once, or whenever you edit
files in `knowledge_base/`):

```bash
python -m app.rag.vectorstore
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

The API will be running at `http://localhost:8000`. Interactive docs at
`http://localhost:8000/docs`.

### 2. Frontend

In a second terminal:

```bash
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

streamlit run app.py
```

The app will open in your browser (usually `http://localhost:8501`).

## How It Works

1. Upload a resume + provide a job description
2. Both get parsed into plain text, then extracted into structured data by an LLM
3. Skills are compared using exact matching + RAG-grounded synonym resolution
   (the knowledge base in `backend/knowledge_base/` provides skill synonyms,
   ATS formatting rules, and industry keywords)
4. An ATS compatibility score is calculated with a transparent weighted formula
5. Personalized suggestions are generated, grounded in retrieved best-practice content

## Project Structure

```
careerready-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/analyze.py
│   │   ├── chains/            # extraction, comparison, scoring, suggestions
│   │   ├── rag/                # embeddings, vectorstore, retriever
│   │   ├── parsers/            # resume & JD file parsing
│   │   └── models/schemas.py
│   ├── knowledge_base/         # RAG source documents
│   └── requirements.txt
├── frontend/
│   └── app.py                  # Streamlit UI
└── PROJECT_PLAN.md
```

## Notes

- Embeddings use a free local model (`all-MiniLM-L6-v2`) — no API key or cost
  required for the RAG retrieval step.
- Only the LLM calls (extraction, comparison resolution, suggestions) require
  an API key — choose OpenAI or Anthropic in `.env`.
- Scanned/image-based PDFs are not supported yet (would need OCR).
