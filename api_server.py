"""
GVPCEW Connect - Backend API Server
FastAPI backend service powering the GVPCEW Connect Academic Portal.
Enforces strict website-only boundaries, 5-intent classification,
and institutional knowledge retrieval.
"""

import os
import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pdf_knowledge import get_categorized_documents
from website_ai import generate_ai_response, classify_user_intent, IntentType, WEBSITE_INFO

app = FastAPI(
    title="GVPCEW Connect Backend API",
    description="Backend API for GVPCEW Connect Academic Portal",
    version="2.1.0"
)

# Enable CORS for frontend clients (Live Server port 5500, localhost, and file origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "question_classifier.joblib")

_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None and os.path.exists(MODEL_PATH):
        try:
            _classifier = joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"Error loading classifier: {e}")
    return _classifier


class ChatRequest(BaseModel):
    question: str


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "GVPCEW Connect Backend",
        "port": 8000,
        "model_loaded": get_classifier() is not None,
        "website_scope": "strictly_enforced"
    }


@app.get("/api/documents")
def list_documents():
    return get_categorized_documents()


@app.post("/api/chat")
def chat_endpoint(payload: ChatRequest):
    query = payload.question.strip()
    if not query:
        return {
            "title": "GVPCEW Assistant",
            "answer": "Please ask a question about this website or GVPCEW academics, exams, syllabus, attendance, and placements.",
            "source": "GVPCEW Assistant",
            "page": 1,
            "intent": IntentType.UNCLEAR.value,
            "score": 0.0,
            "detected_category": "unclear",
            "related": []
        }

    # Generate strictly website-focused response via website AI engine
    response = generate_ai_response(query)

    return {
        "title": response.get("title", "GVPCEW Connect"),
        "answer": response["answer"],
        "source": response.get("source", "Verified College Academic Record"),
        "page": response.get("page", 1),
        "intent": response.get("intent", IntentType.WEBSITE_QUESTION.value),
        "score": response.get("score", 1.0),
        "detected_category": response.get("detected_category", "general"),
        "related": []
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting GVPCEW Connect Backend API on http://localhost:8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
