import re
import json
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage

# 최저임금 정보
MINIMUM_WAGE_BY_YEAR = {
    2023: 9620,
    2024: 9860,
    2025: 10030
}

def get_minimum_wage(year: int) -> int:
    return MINIMUM_WAGE_BY_YEAR.get(year, MINIMUM_WAGE_BY_YEAR[max(MINIMUM_WAGE_BY_YEAR)])

# 근로계약서 분석 프롬프트
PROMPT_TEMPLATE = """
근로계약서에서 아래 항목들을 JSON 형식으로 추출해주세요.
없거나 불명확한 항목은 "미기재"로 표시해주세요.

아래 동의어들도 같은 항목으로 처리해주세요:
- 성명: 이름, 근로자 성명, 직원 이름
- 사용자: 고용주, 고용자, 회사, 사업주
- 생년월일: 출생일, 주민등록번호의 생년월일
- 근로계약기간: 계약기간, 근무기간, 고용기간
- 근로시간: 근무시간, 소정근로시간
- 근무일: 출근일, 근무요일, 일하는 날
- 휴일: 유급휴일, 무급휴일, 주휴일, 공휴일
- 휴게시간: 쉬는시간, 브레이크타임
- 임금: 급여, 시급, 월급, 보수, 연봉, 소득
- 임금지급일: 급여일, 지급시기
- 숙소제공: 숙식제공, 숙소 여부, 기숙사

계약서 내용:
{text}
""".strip()

def call_llm_and_parse(prompt: str, api_key: str, model: str = "solar-pro") -> dict:
    chat = ChatUpstage(api_key=api_key, model=model)
    resp = chat.invoke([HumanMessage(content=prompt)])
    text = resp.content.strip()

    # JSON 형식 정제
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # JSON 파싱 실패시 기본 필드 반환
        return {
            "성명": "미기재",
            "사용자": "미기재",
            "생년월일": "미기재",
            "근로계약기간": "미기재",
            "근로시간": "미기재",
            "근무일": "미기재",
            "휴일": "미기재",
            "휴게시간": "미기재",
            "임금": "미기재",
            "임금지급일": "미기재",
            "숙소제공": "미기재"
        }

def get_llm_judgment(contract_json: dict, api_key: str, year: int, model: str="solar-pro") -> str:
    # 1) 연도별 최저임금 조회
    min_wage = get_minimum_wage(year)

    # 2) 계약서 JSON을 보기 좋게 문자열로 변환
    contract_text = json.dumps(contract_json, ensure_ascii=False, indent=2)

    # 3) 프롬프트 정의 (f-string 내부에 contract_text 포함)
    prompt = f"""
위반 여부를 분석하고 등급화해 주세요.  
특히 다음 기준을 반드시 고려하세요:
1. {year}년 기준 한국의 최저임금은 시간당 {min_wage:,}원입니다.
2. 최저임금 미달 시 근로기준법 제6조 및 제55조 위반입니다.
3. 주 40시간 근무 시 월 209시간으로 간주하며, 월급이 명시된 경우 시급 = 월급 ÷ 209로 계산합니다.
4. 중식보조비, 유류비 등은 최저임금 계산에서 제외됩니다.
5. 수습기간 감액은 차별로 간주될 수 있으며, 명확히 명시되어야 합니다.
6. 외국인 근로자의 경우 숙소 제공, 통역, 체류자격 정보 등도 포함되어야 합니다.

각 위반 항목별 가중치는 아래와 같습니다:
- 최저임금 미달: 3점
- 수습기간 중 감액: 2점
- 휴일 미기재: 2점
- 숙소제공 미기재(외국인): 2점
- 4대보험 미가입: 1.5점
- 임금지급일/지급방식 불명확: 1점
- 기타 조항 누락: 0.5점

#--- 아래 "총점 기준 등급" 및 "총점: [숫자]" 부분을 주석 처리했습니다. ---
# 총점 기준 등급은 다음과 같습니다:
# - 0 ~ 1점: ✅ 정상
# - 1.5 ~ 4점: 🟡 주의
# - 4.5점 이상: ⚠️ 위험

최종 결과는 반드시 아래 형식으로 출력해 주세요:

🧾 근로계약서 등급 평가 결과: [정상 / 주의 / 위험]
# 🧮 총점: [숫자]   ← 여기 부분을 주석 처리했습니다.
이유: [요약된 이유]

[계약서 내용]
{contract_text}

[근로계약서 항목]
{contract_text}

⚖️ 위반사항 및 조치 권고:
""".strip()

    # 4) LLM 호출
    chat = ChatUpstage(api_key=api_key, model=model)
    resp = chat.invoke([HumanMessage(content=prompt)])
    return resp.content.strip()
