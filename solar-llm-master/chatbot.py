import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import time
from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain_community.vectorstores import Chroma
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage

# ▶️ 벡터 저장된 디렉토리에서 불러오기
embedding = UpstageEmbeddings(
    model="solar-embedding-1-large",
    upstage_api_key=os.getenv("UPSTAGE_API_KEY")
)

vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding
)
retriever = vectorstore.as_retriever(k=2)

# ▶️ 챗봇 초기화
chat = ChatUpstage(
    model="solar-pro",
    upstage_api_key=os.getenv("UPSTAGE_API_KEY")
)

# ▶️ 문맥 재구성 프롬프트
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         "이전 대화 내용과 사용자 질문을 바탕으로, 문맥 없이도 이해할 수 있도록 질문을 다시 표현하세요."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    chat, retriever, contextualize_q_prompt
)

# ▶️ 문서 기반 QA 프롬프트
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

# ▶️ Streamlit 인터페이스
st.title("📚 LawRo 법률 상담 Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

MAX_MESSAGES = 4

if prompt := st.chat_input("법률 관련 질문을 입력하세요."):
    if len(st.session_state.messages) >= MAX_MESSAGES:
        del st.session_state.messages[0]
        del st.session_state.messages[0]

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        result = rag_chain.invoke({
            "input": prompt,
            "chat_history": st.session_state.messages
        })

        # ▶️ 문서 출처 추출
        sources = set()
        for doc in result.get("context", []):
            src = doc.metadata.get("source", "Unknown")
            sources.add(src)

        answer = result["answer"]
        sources_list = "\n".join(f"📄 {src}" for src in sources)
        final_response = f"{answer.strip()}\n\n🔎 **출처 문서:**\n{sources_list}"

        for chunk in final_response.split(" "):
            full_response += chunk + " "
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.02)
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
