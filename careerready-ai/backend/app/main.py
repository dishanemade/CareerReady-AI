from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analyze import router as analyze_router

app = FastAPI(
    title="CareerReady AI",
    description="AI-powered ATS Resume Analyzer using RAG + LangChain",
    version="1.0.0",
)

# Allow the frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before deploying publicly
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/api", tags=["analysis"])


@app.get("/")
def health_check():
    return {"status": "ok", "message": "CareerReady AI backend is running"}
