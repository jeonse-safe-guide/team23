# app/main.py

from fastapi import FastAPI, HTTPException
from .models import ChecklistRequest, ChecklistResponse
from .checklist_logic import generate_checklist_llm, generate_checklist_mock

app = FastAPI(
    title="Checklist Server",
    version="0.1.0",
    description="전세 위험 분석 기반 체크리스트 생성 API 서버"
)


# -------------------------
# 1. Health Check
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "Checklist Server"}


# -------------------------
# 2. LLM 기반 체크리스트 생성
# -------------------------
@app.post("/generate", response_model=ChecklistResponse)
def generate(req: ChecklistRequest):
    try:
        return generate_checklist_llm(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# 3. MOCK 체크리스트 생성
# -------------------------
@app.post("/generate_mock", response_model=ChecklistResponse)
def generate_mock(req: ChecklistRequest):
    try:
        return generate_checklist_mock(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
