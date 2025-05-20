# app.py (최종 Streamlit 앱)
import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import time
import uuid
from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# 세션 초기화
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.messages = []

# 저장된 벡터스토어 로드
@st.cache_resource(show_spinner="📂 저장된 문서 로딩 중...")
def load_vectorstore():
    return Chroma(
        persist_directory="chroma_db",
        embedding_function=UpstageEmbeddings(model="solar-embedding-1-large")
    ).as_retriever(k=2)

retriever = load_vectorstore()
chat = ChatUpstage(upstage_api_key=os.getenv("UPSTAGE_API_KEY"), model="solar-pro")

# 체인 구성
contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", """이전 대화 내용과 최신 사용자 질문이 있을 때, 이 질문이 이전 대화 내용과 관련이 있을 수 있습니다. 
    이런 경우, 대화 내용을 알 필요 없이 독립적으로 이해할 수 있는 질문으로 바꾸세요. 
    질문에 답할 필요는 없고, 필요하다면 그저 다시 구성하거나 그대로 두세요."""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])
history_aware_retriever = create_history_aware_retriever(chat, retriever, contextualize_q_prompt)

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", """질문-답변 업무를 돕는 보조원입니다. 
질문에 답하기 위해 검색된 내용을 사용하세요. 
답을 모르면 모른다고 말하세요. 
답변은 세 문장 이내로 간결하게 유지하세요.

## 답변 예시
📍답변 내용: 
📍증거: 

{context}"""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])
question_answer_chain = create_stuff_documents_chain(chat, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# 제목 표시
st.title("📚 LawRo 법률 챗봇")

# 이전 대화 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

MAX_MESSAGES_BEFORE_DELETION = 4

if prompt := st.chat_input("법률 관련 질문을 입력하세요!"):
    if len(st.session_state.messages) >= MAX_MESSAGES_BEFORE_DELETION:
        del st.session_state.messages[0:2]

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        result = rag_chain.invoke({
            "input": prompt,
            "chat_history": st.session_state.messages
        })

        with st.expander("📌 참고 문서"):
            st.write(result["context"])

        for chunk in result["answer"].split(" "):
            full_response += chunk + " "
            time.sleep(0.02)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
