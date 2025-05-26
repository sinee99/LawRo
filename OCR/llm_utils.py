# OCR/llm_utils.py
import os
from langchain_upstage import ChatUpstage
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("UPSTAGE_API_KEY")

llm = ChatUpstage(
    model="solar-pro",
    upstage_api_key=API_KEY,
    temperature=0.2
)

def get_llm_judgment(text: str) -> str:
    prompt = f"""
다음은 근로계약서에서 추출한 전체 내용입니다. 근로기준법 또는 외국인근로자보호 관련 법률을 위반하고 있는 조항이 있는지 판단해주세요.
위반이 있다면 어떤 내용이 위반인지, 어떤 조항을 위반하는지 설명해주세요.

[계약서 내용]
{text}

당신의 판단:
"""
    response = llm.invoke(prompt)
    return response.content.strip()
