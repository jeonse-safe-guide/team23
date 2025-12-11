from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import OCRResponse
from .ocr_service import run_registry_ocr_multi_files

app = FastAPI(
    title="Registry OCR Service",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "OCR Server"}

# ★ 메인 OCR 엔드포인트
@app.post(
    "/ocr",
    response_model=OCRResponse,
    summary="등기부등본 OCR",
    description="여러 장의 등기부 이미지를 업로드하여 파싱된 JSON 결과를 반환합니다."
)
async def ocr_registry(documents: List[UploadFile] = File(...)):
    """
    documents: multipart/form-data로 전송된 파일 리스트
    """
    # 파일이 없는 경우만 여기서 빠르게 거르고, 나머지 복잡한 검사는 서비스 계층으로 위임합니다.
    if not documents:
        raise HTTPException(status_code=400, detail="No files provided")

    # 모든 처리를 서비스 함수에 위임
    return await run_registry_ocr_multi_files(documents)