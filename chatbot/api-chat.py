# solar-llm-master/chatbot.py

import os
from dotenv import load_dotenv

from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain_community.vectorstores import Chroma
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

# ▶️ 임베딩 & 벡터 DB
embedding = UpstageEmbeddings(
    model="solar-embedding-1-large",
    upstage_api_key=os.getenv("UPSTAGE_API_KEY")
)
vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding
)
retriever = vectorstore.as_retriever(k=2)

# ▶️ Upstage 챗 모델
chat = ChatUpstage(
    model="solar-pro",
    upstage_api_key=os.getenv("UPSTAGE_API_KEY")
)

# ▶️ 프롬프트 구성
contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", "이전 대화 내용과 사용자 질문을 바탕으로, 문맥 없이도 이해할 수 있도록 질문을 다시 표현하세요."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     """질문에 검색된 문서 내용을 바탕으로 답변하세요. 답을 모르면 모른다고 하세요. 답변은 간결하고 명확하게 작성하세요. 법률과 관련된 질문에만 답변하세요. 관련되지 않을경우 법률과 관련된 질문을 할 수 있도록 유도하는 말을 해주세요.

📍답변 내용:  
📍출처 문서: {context}"""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# ▶️ RAG 체인 생성
history_aware_retriever = create_history_aware_retriever(chat, retriever, contextualize_q_prompt)
question_answer_chain = create_stuff_documents_chain(chat, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# ▶️ 질문 처리 함수
def ask_chatbot(question: str, history: list):
    result = rag_chain.invoke({
        "input": question,
        "chat_history": history
    })

    docs = result.get("context", [])
    sources = [getattr(doc, "page_content", "")[:300] for doc in docs]

    return {
        "answer": result.get("answer", ""),
        "evidence": sources
    }
