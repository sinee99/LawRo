import uuid
import time
import os
from typing import List, Tuple, Optional, Dict
from dotenv import load_dotenv

from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain_chroma import Chroma
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from models.response_models import ChatMessage

load_dotenv()

class ChatService:
    """RAG 기반 법률 상담 채팅 서비스"""
    
    def __init__(self):
        self.chat_sessions: Dict[str, List[ChatMessage]] = {}
        self.api_key = os.getenv("UPSTAGE_API_KEY")
        
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY 환경변수가 설정되지 않았습니다.")
        
        # RAG 체인 초기화
        self._initialize_rag_chain()
        
    def _initialize_rag_chain(self):
        """RAG 체인을 초기화합니다."""
        try:
            # 임베딩 모델 초기화
            self.embedding = UpstageEmbeddings(
                model="solar-embedding-1-large",
                upstage_api_key=self.api_key
            )
            
            # 벡터스토어 로딩
            self.vectorstore = Chroma(
                persist_directory="../storage/chroma_db",  # 프로젝트 루트의 chroma_db 사용
                embedding_function=self.embedding
            )
            self.retriever = self.vectorstore.as_retriever(k=2)
            
            # LLM 초기화
            self.chat_llm = ChatUpstage(
                model="solar-pro",
                upstage_api_key=self.api_key
            )
            
            # 컨텍스트 인식 프롬프트
            contextualize_q_prompt = ChatPromptTemplate.from_messages([
                ("system", "이전 대화 내용과 사용자 질문을 바탕으로, 문맥 없이도 이해할 수 있도록 질문을 다시 표현하세요."),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            # 히스토리 인식 리트리버 생성
            self.history_aware_retriever = create_history_aware_retriever(
                self.chat_llm, self.retriever, contextualize_q_prompt
            )
            
            # 기본 QA 프롬프트 정의
            self.default_qa_prompt_text = """질문에 검색된 문서 내용을 바탕으로 답변하세요. 답을 모르면 모른다고 하세요. 답변은 20자 이내로 간결하고 명확하게 작성하세요. 법률과 관련된 질문에만 답변하세요. 관련되지 않을 경우 법률과 관련된 질문을 할 수 있도록 유도하는 말을 해주세요.

📍답변 내용:  
📍출처 문서: {context}"""
            
            print("✅ RAG 체인 초기화 완료")
            
        except Exception as e:
            print(f"❌ RAG 체인 초기화 오류: {e}")
            # RAG가 실패하면 기본 LLM만 사용
            self.rag_chain = None
            try:
                self.chat_llm = ChatUpstage(
                    model="solar-pro", 
                    upstage_api_key=self.api_key
                )
                print("⚠️ 기본 LLM만 사용합니다")
            except Exception as llm_error:
                print(f"❌ LLM 초기화도 실패: {llm_error}")
                self.chat_llm = None

    def _create_rag_chain_with_prompt(self, custom_prompt: Optional[str] = None):
        """커스텀 프롬프트로 RAG 체인을 동적 생성합니다."""
        if not hasattr(self, 'history_aware_retriever') or not self.history_aware_retriever:
            return None
            
        # 프롬프트 선택 (커스텀 또는 기본)
        prompt_text = custom_prompt if custom_prompt else self.default_qa_prompt_text
        
        # QA 프롬프트 생성
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_text),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # QA 체인 생성
        question_answer_chain = create_stuff_documents_chain(self.chat_llm, qa_prompt)
        
        # RAG 체인 반환
        return create_retrieval_chain(self.history_aware_retriever, question_answer_chain)

    async def process_message(
        self, 
        message: str, 
        session_id: Optional[str] = None,
        context: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> Tuple[str, List[ChatMessage]]:
        """채팅 메시지를 처리하고 응답을 생성합니다."""
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = []
        
        # 사용자 메시지 추가
        user_message = ChatMessage(
            role="user",
            content=message
        )
        self.chat_sessions[session_id].append(user_message)
        
        # 대화 히스토리를 LangChain 형식으로 변환
        chat_history = []
        for msg in self.chat_sessions[session_id][:-1]:  # 마지막 메시지 제외
            chat_history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        try:
            # 커스텀 프롬프트가 있으면 동적으로 RAG 체인 생성
            if custom_prompt:
                rag_chain = self._create_rag_chain_with_prompt(custom_prompt)
                if rag_chain:
                    result = rag_chain.invoke({
                        "input": message,
                        "chat_history": chat_history
                    })
                    response_text = result["answer"]
                else:
                    response_text = "RAG 체인 생성에 실패했습니다."
            elif hasattr(self, 'history_aware_retriever') and self.history_aware_retriever:
                # 기본 RAG 체인 사용
                default_rag_chain = self._create_rag_chain_with_prompt()
                if default_rag_chain:
                    result = default_rag_chain.invoke({
                        "input": message,
                        "chat_history": chat_history
                    })
                    response_text = result["answer"]
                else:
                    response_text = "기본 RAG 체인 생성에 실패했습니다."
            elif self.chat_llm:
                # 기본 LLM만 사용
                prompt = f"법률 상담 질문에 답변해주세요: {message}"
                response = self.chat_llm.invoke(prompt)
                response_text = response.content
            else:
                response_text = "죄송합니다. 현재 시스템에 문제가 있어 답변을 제공할 수 없습니다. 시스템 관리자에게 문의해주세요."
                
        except Exception as e:
            response_text = f"답변 생성 중 오류가 발생했습니다: {str(e)}"
        
        # AI 응답 메시지 추가
        assistant_message = ChatMessage(
            role="assistant",
            content=response_text
        )
        self.chat_sessions[session_id].append(assistant_message)
        
        # 최대 메시지 수 제한 (6개)
        MAX_MESSAGES = 6
        if len(self.chat_sessions[session_id]) > MAX_MESSAGES:
            self.chat_sessions[session_id] = self.chat_sessions[session_id][-MAX_MESSAGES:]
        
        return response_text, self.chat_sessions[session_id]
    
    async def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """채팅 히스토리를 조회합니다."""
        return self.chat_sessions.get(session_id, [])
    
    async def clear_chat_history(self, session_id: str) -> bool:
        """채팅 히스토리를 삭제합니다."""
        if session_id in self.chat_sessions:
            del self.chat_sessions[session_id]
            return True
        return False
    
    async def create_new_session(self) -> str:
        """새로운 채팅 세션을 생성합니다."""
        session_id = str(uuid.uuid4())
        self.chat_sessions[session_id] = []
        return session_id
    
    def get_context_documents(self, session_id: str) -> List[Dict]:
        """마지막 응답의 컨텍스트 문서를 반환합니다."""
        # 실제 구현에서는 마지막 RAG 결과의 context를 저장/반환
        # 현재는 기본 구현만 제공
        return [] 