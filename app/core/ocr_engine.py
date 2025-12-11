import easyocr
import torch
import numpy as np
import cv2

# 전역 변수로 Reader를 캐싱하여 요청마다 로딩하지 않도록 함
_READER = None

def get_reader() -> easyocr.Reader:
    global _READER
    if _READER is None:
        use_gpu = torch.cuda.is_available()
        print(f"[INFO] EasyOCR Reader 로딩 시작 (GPU: {use_gpu})...")
        _READER = easyocr.Reader(['ko', 'en'], gpu=use_gpu)
        print("[INFO] EasyOCR Reader 로딩 완료.")
    return _READER

def preprocess_image_bytes(image_bytes: bytes) -> np.ndarray:
    """
    bytes -> numpy array -> grayscale -> denoise -> upscale
    """
    # 1. bytes -> numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("이미지 디코딩 실패. 손상된 파일이거나 지원하지 않는 형식입니다.")

    # 2. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

    # 4. Upscaling (x2.0)
    scale_factor = 2.0
    upscaled = cv2.resize(denoised, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

    return upscaled

def run_ocr_on_bytes(image_bytes: bytes) -> str:
    """
    단일 이미지 바이트를 받아 텍스트를 반환
    """
    reader = get_reader()
    preprocessed_img = preprocess_image_bytes(image_bytes)
    
    result = reader.readtext(
        preprocessed_img,
        detail=0,
        paragraph=True,
        batch_size=4,
        contrast_ths=0.1,
        adjust_contrast=0.5
    )
    
    return "\n".join(result)