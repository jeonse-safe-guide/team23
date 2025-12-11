# app/checklist_logic.py

import json
from pathlib import Path
from copy import deepcopy

from pydantic import ValidationError

from .models import ChecklistRequest, ChecklistResponse, ChecklistItem
from .llm_client import generate_llm_response


# ===== 0. risks가 비어 있을 때 & mock에서 쓸 기본 체크리스트 =====

_DEFAULT_ITEMS_NO_RISK = [
    ChecklistItem(
        id=1,
        category="registry",
        title="계약 당일 재발급한 등기부등본 최종 확인",
        description=(
            "전세금 보호를 위해 가장 중요한 행동입니다. 계약을 진행하는 당일(특히 잔금일) "
            "임대인에게 부탁하여 등기부등본을 다시 뽑아봅니다. 계약서를 쓴 이후에 집주인이 "
            "몰래 압류나 대출을 추가하지 않았는지 확인해야 안전합니다."
        ),
    ),
    ChecklistItem(
        id=2,
        category="registry",
        title="소유자와 임대인의 동일 여부 및 신분 확인 철저",
        description=(
            "계약 상대방(임대인)이 정말로 집주인(소유자)이 맞는지 신분증을 통해 직접 확인합니다. "
            "만약 대리인이 온다면, 집주인의 위임장, 인감증명서(3개월 이내 발급), 그리고 집주인과의 "
            "직접 통화 등을 통해 계약 권한이 있는지 철저히 확인해야 합니다."
        ),
    ),
    ChecklistItem(
        id=3,
        category="pre_contract",
        title="임대인 본인 명의 계좌로 계약금 및 잔금 송금",
        description=(
            "계약금, 잔금 등 돈을 보낼 때는 반드시 집주인의 이름으로 된 은행 계좌로 직접 송금해야 합니다. "
            "중개인이나 다른 사람의 계좌로 보내면 나중에 '집주인에게 돈을 주었다'는 증거가 불분명해질 수 있습니다."
        ),
    ),
    ChecklistItem(
        id=4,
        category="pre_contract",
        title="전세보증보험 가입 요건 및 가능 여부 사전 확인",
        description=(
            "전세금을 나라에서 대신 돌려주는 '전세보증보험'에 가입할 수 있는지 미리 알아봅니다. "
            "가입이 안 되는 집은 그만큼 위험하다는 뜻이므로 계약을 다시 생각해봐야 합니다. "
            "(HUG, SGI 등 보증기관을 미리 확인하세요.)"
        ),
    ),
    ChecklistItem(
        id=5,
        category="pre_contract",
        title="임대인의 국세 및 지방세 납세 증명서 요청",
        description=(
            "집주인에게 밀린 세금(국세/지방세)이 있는지 확인하기 위해 '완납 증명서'를 요청합니다. "
            "집주인의 체납된 세금은 나의 전세금보다 먼저 떼어갈 수 있으므로 반드시 확인해야 합니다."
        ),
    ),
    ChecklistItem(
        id=6,
        category="site",
        title="현장 방문 시 누수, 결로, 주요 시설물 작동 상태 확인",
        description=(
            "계약 전 집 내부에 물이 새는 곳(누수), 곰팡이가 생기는 곳(결로)은 없는지, "
            "보일러나 전기 시설은 잘 작동하는지 직접 눈으로 확인합니다. "
            "문제가 있다면 집주인과 누가 언제까지 고칠지 특약에 명확히 적어야 합니다."
        ),
    ),
    ChecklistItem(
        id=7,
        category="contract",
        title="전세 계약서에 '보증금 반환 확약' 특약 포함",
        description=(
            "나중에 계약이 끝났을 때 집주인이 전세금을 확실하게 돌려주겠다는 내용을 계약서 특약에 넣습니다. "
            "만약 돈을 늦게 돌려줄 경우 이자를 물어야 한다는 조항도 함께 넣는 것이 좋습니다."
        ),
    ),
    ChecklistItem(
        id=8,
        category="contract",
        title="계약서에 '선순위 권리 변동 금지' 특약 명시",
        description=(
            "잔금을 치르고 내가 전입신고를 마친 다음 날 0시가 되기 전까지, 집주인이 이 집에 "
            "추가로 은행 대출을 받거나(근저당 설정) 집을 팔지 않겠다는 약속을 계약서에 명확히 넣어야 합니다. "
            "이 약속을 어기면 계약을 해지할 수 있다는 내용도 함께 기재합니다."
        ),
    ),
    ChecklistItem(
        id=9,
        category="contract",
        title="계약서에 집주인의 전세보증보험 가입 협조 의무 명시",
        description=(
            "내가 전세보증보험에 가입할 때, 집주인이 필요한 서류(주택가격확인서 등)를 제때 발급해 주고 "
            "적극 협조한다는 내용을 계약서 특약에 적어둡니다."
        ),
    ),
]

_DEFAULT_RESPONSE_NO_RISK = ChecklistResponse(items=_DEFAULT_ITEMS_NO_RISK)


# ===== 1. 프롬프트 템플릿 로드 =====

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
TEMPLATE_PATH = PROMPTS_DIR / "template.txt"

if not TEMPLATE_PATH.exists():
    raise RuntimeError(f"프롬프트 템플릿 파일을 찾을 수 없습니다: {TEMPLATE_PATH}")

PROMPT_TEMPLATE = TEMPLATE_PATH.read_text(encoding="utf-8")


def build_prompt(req: ChecklistRequest) -> str:
    """
    ChecklistRequest -> 템플릿에 박아서 LLM 프롬프트 생성
    """
    if "{analysis_json}" not in PROMPT_TEMPLATE:
        raise RuntimeError("프롬프트 템플릿에 {analysis_json} 플레이스홀더가 없습니다.")

    data_dict = req.dict()
    analysis_json = json.dumps(data_dict, ensure_ascii=False, indent=2)
    return PROMPT_TEMPLATE.replace("{analysis_json}", analysis_json)


def _strip_code_block(raw: str) -> str:
    """
    LLM이 ```json ... ``` 형태로 줄 때 코드블록 제거
    """
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines).strip()
    return raw


def _normalize_items(items: list[ChecklistItem]) -> list[ChecklistItem]:
    """
    LLM이 만든 items를 최종 스펙에 맞게 정리:
    - id는 1부터 다시 부여
    - title이 비어있으면 해당 항목 삭제
    - description None → ""로 통일
    - category가 이상하면 'contract'로 fallback
    """
    valid_categories = {"registry", "contract", "site", "pre_contract"}
    normalized: list[ChecklistItem] = []
    next_id = 1

    for item in items:
        category = item.category
        if category not in valid_categories:
            category = "contract"

        title = item.title.strip()
        if not title:
            continue

        desc = (item.description or "").strip()

        normalized.append(
            ChecklistItem(
                id=next_id,
                category=category,  # type: ignore[arg-type]
                title=title,
                description=desc,
            )
        )
        next_id += 1

    if not normalized:
        raise RuntimeError("LLM 응답에서 유효한 체크리스트 항목이 없습니다.")

    return normalized


def generate_checklist_llm(req: ChecklistRequest) -> ChecklistResponse:
    """
    1) risks가 비어 있으면: 기본 체크리스트(_DEFAULT_RESPONSE_NO_RISK) 반환
    2) risks가 있으면: LLM 호출 → JSON 파싱 → 후처리
       (기본적으로 실제 LLM, LLM_MOCK_MODE=true면 전역 mock)
    """
    # 1. risks가 비어있는 경우 → 기본 체크리스트 반환 (LLM 호출 X)
    if not req.risks:
        return deepcopy(_DEFAULT_RESPONSE_NO_RISK)

    # 2. LLM 프롬프트 구성
    prompt = build_prompt(req)

    # 3. LLM 호출 (force_mock=False → 기본은 실제 LLM)
    try:
        response = generate_llm_response(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": ChecklistResponse.model_json_schema(),
            },
            force_mock=False,  # /generate 엔드포인트는 기본적으로 실제 LLM
        )
    except Exception as e:
        raise RuntimeError(f"Gemini API 호출 오류: {e}")

    # 4. 원시 응답 텍스트
    raw = (getattr(response, "text", None) or "").strip()
    if not raw:
        raise RuntimeError("Gemini 응답이 비어 있습니다.")

    raw = _strip_code_block(raw)

    # 5. JSON 파싱 + 검증
    try:
        parsed = ChecklistResponse.model_validate_json(raw)
    except ValidationError as e:
        snippet = raw[:300]
        raise RuntimeError(f"LLM JSON 파싱 실패: {e}\n원본 응답 일부: {snippet}")

    # 6. 후처리
    parsed.items = _normalize_items(parsed.items)
    return parsed


def generate_checklist_mock(req: ChecklistRequest) -> ChecklistResponse:
    """
    /generate_mock 엔드포인트용:
    - risks가 비어 있으면: 기본 체크리스트(_DEFAULT_RESPONSE_NO_RISK) 반환
    - risks가 있으면: LLM mock 호출(generate_llm_response(force_mock=True)) 후
      JSON 파싱 + 후처리
    """
    # 1. risks가 비어 있을 때 → 기본 체크리스트
    if not req.risks:
        return deepcopy(_DEFAULT_RESPONSE_NO_RISK)

    # 2. 프롬프트 구성
    prompt = build_prompt(req)

    # 3. mock LLM 호출 (실제 API 안 타고 wrapper의 mock JSON 사용)
    try:
        response = generate_llm_response(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": ChecklistResponse.model_json_schema(),
            },
            force_mock=True,  # 이 엔드포인트는 무조건 mock
        )
    except Exception as e:
        raise RuntimeError(f"Gemini MOCK 호출 오류: {e}")

    # 4. response가 dict(mock)인지, 실제 LLM 객체인지 구분해서 처리
    if isinstance(response, dict):
        raw = (response.get("text") or "").strip()
    else:
        raw = (getattr(response, "text", None) or "").strip()

    if not raw:
        raise RuntimeError("Gemini MOCK 응답이 비어 있습니다.")

    raw = _strip_code_block(raw)

    # 5. JSON 파싱 + Pydantic 검증
    try:
        parsed = ChecklistResponse.model_validate_json(raw)
    except ValidationError as e:
        snippet = raw[:300]
        raise RuntimeError(f"MOCK JSON 파싱 실패: {e}\n원본 응답 일부: {snippet}")

    # 6. id/카테고리/description 정리
    parsed.items = _normalize_items(parsed.items)
    return parsed