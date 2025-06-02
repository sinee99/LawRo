import re
import json
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage


def build_prompt(full_text: str) -> str:
    """
    OCR로 추출된 전체 텍스트(full_text)를 입력받아
    LLM에게 보낼 프롬프트 문장을 완성해 돌려줍니다.
    """
    return f"""
다음은 근로계약서 OCR 결과입니다.
주요 항목을 반드시 “JSON only” 형식으로, 코드 펜스 없이 출력해주세요.
만약 항목이 없거나 명확하지 않으면 “미기재”로 표시해주세요.

- 성명
- 사용자
- 생년월일
- 근로계약기간
- 근로시간
- 휴게시간
- 임금
- 임금지급일
- 숙소제공

OCR 내용:
{full_text}
""".strip()


def call_llm_and_parse(prompt: str, api_key: str, model: str = "solar-pro") -> dict:
    """
    prompt를 가지고 LLM(solar-pro)을 호출한 뒤,
    ```json ... ``` 펜스를 제거하고 json.loads()로 파싱하여 dict를 반환합니다.
    """
    chat = ChatUpstage(api_key=api_key, model=model)
    resp = chat.invoke([HumanMessage(content=prompt)])
    text = resp.content.strip()

    # ``` 또는 ```json 제거
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 파싱 실패 시 raw text 반환
        return {"raw_response": text}


def get_llm_judgment(text: str, api_key: str, model: str="solar-pro") -> str:
    """
    계약서 전체 텍스트를 입력받아 위반 여부와 위반 조항을 설명합니다.
    """
    prompt = f"""
다음은 근로계약서에서 추출한 전체 내용입니다. 
근로기준법 또는 외국인근로자보호 관련 법률을 위반하고 있는 조항이 있는지 판단해주세요.
위반이 있다면 어떤 내용이 위반인지, 어떤 조항을 위반하는지 설명해주세요.

[계약서 내용]
{text}

당신의 판단:
""".strip()

    chat = ChatUpstage(api_key=api_key, model=model)
    resp = chat.invoke([HumanMessage(content=prompt)])
    return resp.content.strip()
