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
    persist_directory="storage/chroma_db",
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

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         """당신은 대한민국 근로기준법 및 외국인근로자고용 등에 관한 법률 해석(Labor Law Guidance, 이하 LAG)을 기반으로 근로계약서의 적법성 여부를 판단하는 전문가입니다.

질문에 검색된 문서 내용을 바탕으로 답변하세요. 답을 모르면 모른다고 하세요. 답변은 상세하고 명확하게 작성하세요. 법률과 관련된 질문에만 답변하세요. 관련되지 않을 경우 법률과 관련된 질문을 할 수 있도록 유도하는 말을 해주세요.

특히 다음 기준을 고려해 주세요:

1. 최저임금은 시간당 기준으로 판단해주세요.
2. 주 40시간 근무 기준으로 월 평균 근로시간은 209시간입니다.
3. 임금이 시급/일급/월급 중 어떤 형식이든 시급으로 환산하여 최저임금 충족 여부를 판단해 주세요.
4. 식대·유류비·숙소 등 복리후생비는 최저임금 산정에 포함되지 않습니다.
5. 수습기간 중에도 최저임금은 적용되며, 감액 시 근로기준법 제7조(차별 금지) 위반 소지가 있습니다.
6. 다음 항목이 누락되었거나 불명확하다면 지적해 주세요: 근로계약기간, 근로시간, 휴게시간, 휴일, 임금, 지급방법 및 시기
7. 외국인 근로자일 경우, 체류자격·숙소·통역 지원 등 고용허가제 관련 기준도 참고해 주세요.

📍 출처 문서: {context}"""),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(chat, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# ▶️ Streamlit UI
st.title("📚 LawRo 법률 상담 Chatbot")

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
