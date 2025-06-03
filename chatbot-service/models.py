from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    role: str = Field(..., description="메시지 역할 (user, assistant)")
    content: str = Field(..., description="메시지 내용")
    timestamp: datetime = Field(default_factory=datetime.now, description="메시지 시간")

class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str = Field(..., description="사용자 메시지", min_length=1)
    session_id: Optional[str] = Field(None, description="세션 ID")
    context: Optional[str] = Field(None, description="문맥 정보 (계약서 내용)")
    custom_prompt: Optional[str] = Field(None, description="커스텀 QA 프롬프트")

class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="응답 메시지")
    chat_history: List[ChatMessage] = Field(..., description="대화 히스토리")
    processing_time: float = Field(..., description="처리 시간(초)") 