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

    # 3) 프롬프트 정의 (총점 포함, 순수 텍스트 출력)
    prompt = f"""
당신은 노동법 전문가입니다. 아래는 OCR로 추출된 근로계약서 항목입니다.
이를 바탕으로 “전체 분석 결과(총점 포함)”, “하이라이트 항목”, “법률 해석” 세 가지 섹션을 반드시 순수 텍스트로 구분하여 출력해 주세요.
JSON이나 코드 펜스는 사용하지 말고, 다음의 예시 형식을 참고하여 작성하십시오.

전체 분석 결과
총점: [여기에 계산된 숫자(소수점 가능)]  
[간략한 요약문을 작성하세요]

하이라이트 항목
1. [첫 번째 핵심 위반 요소 또는 주의 사항]
2. [두 번째 핵심 위반 요소 또는 주의 사항]
3. ...

법률 해석
1. [첫 번째 위반 요소에 대한 법적 근거와 설명]
2. [두 번째 위반 요소에 대한 법적 근거와 설명]
3. ...

전체 심층 분석
[여기에 최소 5~6문장 이상의 길고 상세한 분석을 작성하세요. 
예: 계약서의 어떤 조항이 노동법상 왜 문제가 되는지, 외국인 근로자 관점에서 추가 리스크는 무엇인지, 향후 개선 방안과 예방법 등에 대해 구체적으로 기술]
---

추가로 반드시 고려해야 할 기준은 다음과 같습니다:
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

[계약서 내용]
{contract_text}
""".strip()

    # 4) LLM 호출
    chat = ChatUpstage(api_key=api_key, model=model)
    resp = chat.invoke([HumanMessage(content=prompt)])
    return resp.content.strip()
