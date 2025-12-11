from typing import List, Optional, Any
from pydantic import BaseModel, Field

# ==========================================
# 1. 하위 데이터 모델 (Title, Gaggu, Eulgu)
# ==========================================

class TitleInfo(BaseModel):
    road_address: Optional[str] = Field(None, description="도로명 주소")
    jibun_address: Optional[str] = Field(None, description="지번 주소")
    building_name: Optional[str] = Field(None, description="건물명")
    exclusive_area: Optional[str] = Field(None, description="전유 면적")
    building_usage: Optional[str] = Field(None, description="건물 용도")
    dong: Optional[str] = Field(None, description="동")
    ho: Optional[str] = Field(None, description="호")

class GagguItem(BaseModel):
    type: str = Field(..., description="권리 유형 (ownership_transfer, provisional_seizure 등)")
    registration_purpose: Optional[str] = Field(None, description="등기 목적")
    # 소유권 이전 관련
    owner_name: Optional[str] = Field(None, description="소유자명")
    owner_ssn_prefix: Optional[str] = Field(None, description="주민번호 앞자리")
    # 권리 침해 관련 (가압류, 압류 등)
    rights_holder: Optional[str] = Field(None, description="채권자/권리자")
    debt_amount: Optional[int] = Field(None, description="청구 금액")

class EulguItem(BaseModel):
    type: str = Field(..., description="권리 유형 (mortgage 등)")
    registration_purpose: Optional[str] = Field(None, description="등기 목적")
    debt_max_amount: Optional[int] = Field(None, description="채권최고액")
    debtor: Optional[str] = Field(None, description="채무자")
    creditor: Optional[str] = Field(None, description="채권자(근저당권자)")

# ==========================================
# 2. 중간 데이터 래퍼 (Data)
# ==========================================

class OCRData(BaseModel):
    title: TitleInfo
    gaggu: List[GagguItem] = []
    eulgu: List[EulguItem] = []
    rawText: Optional[str] = Field(None, description="OCR 원본 텍스트")

# ==========================================
# 3. 최상위 응답 모델 (Response)
# ==========================================

class OCRResponse(BaseModel):
    data: OCRData