import os
import time
from dotenv import load_dotenv

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
    persist_directory="chroma_db",
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
         """질문에 검색된 문서 내용을 바탕으로 답변하세요. 답을 모르면 모른다고 하세요. 답변은 간결하고 명확하게 작성하세요. 법률과 관련된 질문에만 답변하세요. 관련되지 않을경우 법률과 관련된 질문을 할 수 있도록 유도하는 말을 해주세요.

📍답변 내용:  
📍출처 문서: {context}"""),
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
