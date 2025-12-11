# app/llm_client.py

import os
from typing import Any, Optional

from google import genai
from dotenv import load_dotenv

# 1) .env 읽기
load_dotenv()

# 2) MOCK 모드 여부 (원하면 계속 사용, 아니면 항상 false로 둬도 됨)
MOCK_MODE = os.getenv("LLM_MOCK_MODE", "false").lower() == "true"

# 3) 실제 API 키 읽기
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY and not MOCK_MODE:
    raise RuntimeError(
        "GEMINI_API_KEY 환경변수가 설정되어 있지 않습니다. "
        "또는 LLM_MOCK_MODE=true 로 설정하여 mock 모드를 사용하십시오."
    )

# 4) Gemini Client 초기화
client: Optional[genai.Client] = None
if not MOCK_MODE:
    # gemini_test.py와 완전히 같은 패턴
    client = genai.Client(api_key=API_KEY)


def generate_llm_response(
    model: str,
    contents: str,
    config: Optional[dict] = None,
    *,
    force_mock: bool = False,
) -> Any:
    """
    LLM 호출 wrapper.
    - force_mock=True 이거나 환경변수 LLM_MOCK_MODE=true 이면,
      실제 API 호출 대신 mock JSON을 반환.
    """
    # ------------------ 1) Mock 모드 ------------------
    if force_mock or MOCK_MODE:
        return {
            "text": """
            {
                "items": [
                    {
                        "id": 1,
                        "category": "registry",
                        "title": "MOCK: 계약 당일 재발급한 등기부등본 최종 확인",
                        "description": "MOCK 모드: 전세금 보호를 위해 계약 당일 등기부등본을 재발급 받아 소유자·권리 변동 여부를 최종 확인하세요."
                    },
                    {
                        "id": 2,
                        "category": "pre_contract",
                        "title": "MOCK: 임대인 본인 계좌로만 계약금 송금",
                        "description": "MOCK 모드: 계약 전, 임대인의 명의와 동일한 계좌인지 확인하고 제3자 계좌 송금은 절대 금지하세요."
                    },
                    {
                        "id": 3,
                        "category": "site",
                        "title": "MOCK: 현장 방문 시 누수·결로 점검",
                        "description": "MOCK 모드: 집 내부의 누수, 결로, 곰팡이 여부를 직접 확인하고 문제 있으면 특약에 보수 기한을 명시하세요."
                    },
                    {
                        "id": 4,
                        "category": "contract",
                        "title": "MOCK: 보증금 반환 확약 특약 추가",
                        "description": "MOCK 모드: 전세계약서에 보증금 반환 기한 및 지연 시 이자 지급 등의 보호 특약을 반드시 포함하세요."
                    }
                ]
            }
            """
        }

    # ------------------ 2) 실제 LLM 호출 ------------------
    if client is None:
        raise RuntimeError("Gemini client가 초기화되지 않았습니다.")

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config or {},
        )
        return response
    except Exception as e:
        # 여기까지 오면 진짜 네트워크/API레벨 에러
        raise RuntimeError(f"Gemini API 호출 실패: {e}")
