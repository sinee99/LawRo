import os
import time
import warnings
from dotenv import load_dotenv

# LangChain deprecation warnings 무시
warnings.filterwarnings("ignore", category=DeprecationWarning)

import streamlit as st
from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain_chroma import Chroma
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

# ▶️ API 키 확인
api_key = os.getenv("UPSTAGE_API_KEY")
if not api_key:
    st.error("❗️Upstage API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    st.stop()

# ▶️ 벡터스토어 로딩
embedding = UpstageEmbeddings(
    model="solar-embedding-1-large",
    upstage_api_key=api_key
)

vectorstore = Chroma(
    persist_directory="../storage/chroma_db",
    embedding_function=embedding
)
retriever = vectorstore.as_retriever(k=2)

# ▶️ 챗봇 초기화
chat = ChatUpstage(
    model="solar-pro",
    upstage_api_key=api_key
)

# ▶️ 프롬프트 구성
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "이전 대화 내용과 사용자 질문을 바탕으로, 문맥 없이도 이해할 수 있도록 질문을 다시 표현하세요."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(chat, retriever, contextualize_q_prompt)

def create_qa_prompt_with_language(language_code: str):
    """언어별 QA 프롬프트를 생성합니다."""
    language_instruction = get_language_instruction(language_code)
    
    system_prompt = f"""사용자의 질문은 json 형식으로 된 법률 분석 자료입니다. 양식에 맞게 항목 별로 위반 여부를 분석하고 등급화해 주세요.  
         최저임금 정보는 다음과 같습니다 년 : 원
    2023: 9620,
    2024: 9860,
    2025: 10030
당신은 노동법 전문가입니다. 아래는 OCR로 추출된 근로계약서 항목입니다.
이를 바탕으로 "전체 분석 결과(총점 포함)", "하이라이트 항목", "법률 해석" 세 가지 섹션을 반드시 순수 텍스트로 구분하여 출력해 주세요.
JSON이나 코드 펜스는 사용하지 말고, 다음의 예시 형식을 참고하여 작성하십시오.

예시 출력 형식:
—
전체 분석 결과:
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

전체 심층 분석:
[여기에 최소 5~6문장 이상의 길고 상세한 분석을 작성하세요. 
예: 계약서의 어떤 조항이 노동법상 왜 문제가 되는지, 외국인 근로자 관점에서 추가 리스크는 무엇인지, 향후 개선 방안과 예방법 등에 대해 구체적으로 기술]
—

추가로 반드시 고려해야 할 기준은 다음과 같습니다:
1. %%년 기준 한국의 최저임금은 시간당 %%원입니다.
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

{language_instruction}

📍 출처 문서: {{context}}"""
    
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

# RAG 체인은 사용자 입력 시 동적으로 생성됩니다

# ▶️ Streamlit UI
st.title("📚 LawRo 법률 상담 Chatbot")

# ▶️ 언어 선택 옵션 추가
language_options = {
    "한국어": "korean",
    "English": "english", 
    "中文": "chinese",
    "Tiếng Việt": "vietnamese",
    "日本語": "japanese",
    "ภาษาไทย": "thai",
    "Bahasa Indonesia": "indonesian",
    "Filipino": "tagalog",
    "Español": "spanish",
    "Français": "french"
}

selected_language_display = st.selectbox(
    "🌍 답변 언어 선택",
    options=list(language_options.keys()),
    index=0
)
selected_language = language_options[selected_language_display]

# 언어별 프롬프트 지시사항
def get_language_instruction(language_code: str) -> str:
    """언어별 프롬프트 지시사항을 반환합니다."""
    language_prompts = {
        "korean": "답변은 반드시 한국어로 해주세요.",
        "english": "Please respond in English only.",
        "chinese": "请只用中文回答。",
        "vietnamese": "Vui lòng chỉ trả lời bằng tiếng Việt.",
        "japanese": "日本語のみで答えてください。",
        "thai": "กรุณาตอบเป็นภาษาไทยเท่านั้น",
        "indonesian": "Silakan jawab hanya dalam bahasa Indonesia.",
        "tagalog": "Mangyaring sumagot sa wikang Filipino lamang.",
        "spanish": "Por favor responde solo en español.",
        "french": "Veuillez répondre uniquement en français."
    }
    return language_prompts.get(language_code, "답변은 반드시 한국어로 해주세요.")

# ▶️ 대화 상태 관리
if "messages" not in st.session_state:
    st.session_state.messages = []

# ▶️ 이전 메시지 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ▶️ 입력 처리
MAX_MESSAGES = 6

if prompt := st.chat_input("법률 관련 질문을 입력하세요."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ▶️ 최근 N개만 유지
    if len(st.session_state.messages) > MAX_MESSAGES:
        st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # 선택된 언어로 QA 프롬프트 생성
        qa_prompt = create_qa_prompt_with_language(selected_language)
        question_answer_chain = create_stuff_documents_chain(chat, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        result = rag_chain.invoke({
            "input": prompt,
            "chat_history": st.session_state.messages
        })

        # ▶️ 증거자료 내용 출력
        docs = result.get("context", [])
        with st.expander("📂 관련 문서"):
            if isinstance(docs, list):
                for i, doc in enumerate(docs, 1):
                    content = getattr(doc, "page_content", "출처 없음")
                    st.markdown(f"**[{i}]** {content.strip()[:500]}...")  # 최대 500자

        # ▶️ 답변 애니메이션 출력
        for chunk in result["answer"].split(" "):
            full_response += chunk + " "
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.02)
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
