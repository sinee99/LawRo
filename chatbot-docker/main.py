from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from typing import Dict, Any
import os
from dotenv import load_dotenv

from models import ChatRequest, ChatResponse, ChatMessage
from chat_service import ChatService

# 환경 변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="LawRo 챗봇 API",
    description="법률 상담 챗봇 서비스 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 챗봇 서비스 초기화
chat_service = ChatService()

@app.get("/")
async def root():
    """API 정보"""
    return {
        "message": "LawRo 챗봇 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "LawRo Chatbot",
        "timestamp": time.time(),
        "components": {
            "rag_chain": "operational",
            "llm": "operational",
            "vectorstore": "operational"
        }
    }

# 기존 /chat 엔드포인트는 /chat/send로 통합됨

@app.post("/chat/send", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """
    채팅 메시지를 보내고 AI 응답을 받습니다.
    """
    start_time = time.time()
    
    try:
        # 챗봇 응답 생성
        response_message, chat_history = await chat_service.process_message(
            message=request.message,
            session_id=request.session_id,
            context=request.context,
            custom_prompt=request.custom_prompt,
            user_language=request.user_language
        )
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            success=True,
            message=response_message,
            chat_history=chat_history,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return ChatResponse(
            success=False,
            message=f"오류가 발생했습니다: {str(e)}",
            chat_history=[],
            processing_time=processing_time
        )

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """특정 세션의 채팅 히스토리를 조회합니다."""
    try:
        history = await chat_service.get_chat_history(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "chat_history": history,
            "message_count": len(history)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"채팅 히스토리 조회 중 오류가 발생했습니다: {str(e)}"
        )

# 기존 /create_session 엔드포인트는 /chat/new-session으로 통합됨

@app.post("/chat/new-session")
async def create_new_chat_session():
    """새로운 채팅 세션을 생성합니다."""
    try:
        session_id = await chat_service.create_new_session()
        return {
            "success": True,
            "session_id": session_id,
            "message": "새로운 채팅 세션이 생성되었습니다."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"세션 생성 중 오류가 발생했습니다: {str(e)}"
        )

@app.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """특정 세션의 채팅 히스토리를 삭제합니다."""
    try:
        success = await chat_service.clear_chat_history(session_id)
        return {
            "success": success,
            "message": "채팅 히스토리가 삭제되었습니다." if success else "삭제에 실패했습니다.",
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"채팅 히스토리 삭제 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/stats")
async def get_server_stats():
    """서버 통계 정보를 조회합니다."""
    try:
        stats = chat_service.get_session_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    ) 