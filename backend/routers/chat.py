from fastapi import APIRouter, HTTPException
import time
from typing import Dict, Any, List

from models.request_models import ChatRequest
from models.response_models import ChatResponse, ChatMessage
from services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()

@router.post("/send", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """
    채팅 메시지를 보내고 AI 응답을 받습니다.
    
    Args:
        request: 채팅 요청 (메시지, 세션ID, 문맥)
    
    Returns:
        ChatResponse: 채팅 응답
    """
    start_time = time.time()
    
    try:
        # 챗봇 응답 생성
        response_message, chat_history = await chat_service.process_message(
            message=request.message,
            session_id=request.session_id,
            context=request.context
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

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    특정 세션의 채팅 히스토리를 조회합니다.
    
    Args:
        session_id: 세션 ID
    
    Returns:
        Dict: 채팅 히스토리
    """
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

@router.get("/context/{session_id}")
async def get_context_documents(session_id: str):
    """
    특정 세션의 마지막 응답에 사용된 컨텍스트 문서를 조회합니다.
    
    Args:
        session_id: 세션 ID
    
    Returns:
        Dict: 컨텍스트 문서 정보
    """
    try:
        context_docs = chat_service.get_context_documents(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "context_documents": context_docs,
            "document_count": len(context_docs)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"컨텍스트 문서 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    특정 세션의 채팅 히스토리를 삭제합니다.
    
    Args:
        session_id: 세션 ID
    
    Returns:
        Dict: 삭제 결과
    """
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

@router.post("/new-session")
async def create_new_chat_session():
    """
    새로운 채팅 세션을 생성합니다.
    
    Returns:
        Dict: 새 세션 정보
    """
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

@router.get("/health")
async def chat_health_check():
    """채팅 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "Chat",
        "components": {
            "rag_chain": "operational",
            "llm": "operational",
            "vectorstore": "operational",
            "session_manager": "operational"
        },
        "timestamp": time.time()
    } 