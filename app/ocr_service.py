from typing import List
from fastapi import UploadFile, HTTPException  # 에러 처리를 위해 HTTPException 추가

from .schemas import OCRResponse
from .core.ocr_engine import run_ocr_on_bytes
from .core.registry_parser import RegistryParser

# 파서는 상태가 없으므로 전역 재사용 가능
_PARSER = RegistryParser()

# 허용할 파일 확장자 목록
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/bmp", "image/tiff"}

async def run_registry_ocr_multi_files(files: List[UploadFile]) -> OCRResponse:
    """
    여러 장의 이미지를 받아 검증 후 OCR 및 파싱 수행
    """
    all_text_parts = []
    
    # 1. 파일별로 검증 및 OCR 수행
    for idx, file in enumerate(files, start=1):
        # (1) 파일 타입 검증 (여기서 처리)
        if file.content_type not in ALLOWED_TYPES:
            # 경고를 띄우거나 에러를 발생시킬 수 있습니다.
            # 지금은 에러를 발생시켜 잘못된 파일이 섞이는 것을 방지합니다.
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.content_type}. Only images are allowed."
            )

        # (2) 파일 읽기
        content = await file.read()
        
        # (3) 엔진 호출 (OCR)
        try:
            page_text = run_ocr_on_bytes(content)
        except Exception as e:
            # 이미지 디코딩 실패 등 엔진 에러 처리
            raise HTTPException(status_code=400, detail=f"OCR Error on file {file.filename}: {str(e)}")
        
        # (4) 텍스트 수집
        all_text_parts.append(f"[PAGE {idx}]")
        all_text_parts.append(page_text)

    # 2. 전체 텍스트 병합
    full_text = "\n".join(all_text_parts)

    # 3. 파싱 수행
    parsed_dict = _PARSER.run(full_text)
    
    # 4. 결과 반환
    return OCRResponse(**parsed_dict)