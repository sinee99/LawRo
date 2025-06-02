from pydantic import BaseModel, Field
from typing import List, Optional

class TextAnalysisRequest(BaseModel):
    """텍스트 분석 요청 모델"""
    text: str = Field(..., description="분석할 텍스트", min_length=1)
    include_llm_judgment: bool = Field(True, description="LLM 판단 포함 여부")
    include_rag_search: bool = Field(True, description="RAG 검색 포함 여부")

class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str = Field(..., description="사용자 메시지", min_length=1)
    session_id: Optional[str] = Field(None, description="세션 ID")
    context: Optional[str] = Field(None, description="문맥 정보 (계약서 내용)")
    custom_prompt: Optional[str] = Field(None, description="커스텀 QA 프롬프트 (설정하지 않으면 기본 프롬프트 사용)")

class RAGSearchRequest(BaseModel):
    """RAG 검색 요청 모델"""
    query: str = Field(..., description="검색 쿼리", min_length=1)
    max_results: int = Field(4, description="최대 결과 수", ge=1, le=10)

class LLMJudgmentRequest(BaseModel):
    """LLM 판단 요청 모델"""
    text: str = Field(..., description="판단할 텍스트", min_length=1)
    focus_areas: Optional[List[str]] = Field(None, description="중점 검토 영역")

class PDFExportRequest(BaseModel):
    """PDF 내보내기 요청 모델"""
    contract_text: str = Field(..., description="계약서 텍스트")
    analysis_results: dict = Field(..., description="분석 결과")
    include_recommendations: bool = Field(True, description="권장사항 포함 여부") 