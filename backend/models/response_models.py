from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class HealthResponse(BaseModel):
    """헬스 체크 응답 모델"""
    status: str = Field(..., description="서버 상태")
    message: str = Field(..., description="상태 메시지")
    version: str = Field(..., description="API 버전")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")

class OCRResponse(BaseModel):
    """OCR 처리 응답 모델"""
    success: bool = Field(..., description="처리 성공 여부")
    original_text: str = Field(..., description="원본 OCR 텍스트")
    processed_text: str = Field(..., description="전처리된 텍스트")
    processing_time: float = Field(..., description="처리 시간(초)")
    error_message: Optional[str] = Field(None, description="오류 메시지")

class RequiredFieldsResult(BaseModel):
    """필수 항목 검사 결과"""
    found_fields: Dict[str, List[str]] = Field(..., description="발견된 필수 항목들")
    missing_fields: Dict[str, List[str]] = Field(..., description="누락된 필수 항목들")
    completion_rate: float = Field(..., description="완성도 비율 (0-100)")

class ViolationItem(BaseModel):
    """법 위반 항목"""
    rule_name: str = Field(..., description="위반 규칙명")
    description: str = Field(..., description="위반 내용 설명")
    severity: str = Field(..., description="심각도 (low, medium, high)")

class ViolationCheckResponse(BaseModel):
    """법 위반 검사 응답 모델"""
    success: bool = Field(..., description="처리 성공 여부")
    violations: List[ViolationItem] = Field(..., description="위반 항목들")
    violation_count: int = Field(..., description="위반 항목 수")
    risk_level: str = Field(..., description="전체 위험도 (safe, caution, danger)")

class AnalysisResponse(BaseModel):
    """종합 분석 응답 모델"""
    success: bool = Field(..., description="처리 성공 여부")
    ocr_result: OCRResponse = Field(..., description="OCR 처리 결과")
    required_fields: RequiredFieldsResult = Field(..., description="필수 항목 검사 결과")
    violations: ViolationCheckResponse = Field(..., description="법 위반 검사 결과")
    overall_score: float = Field(..., description="전체 점수 (0-100)")
    recommendations: List[str] = Field(..., description="개선 권장사항")

class LLMJudgmentResponse(BaseModel):
    """LLM 판단 응답 모델"""
    success: bool = Field(..., description="처리 성공 여부")
    judgment: str = Field(..., description="LLM 판단 결과")
    confidence_score: float = Field(..., description="신뢰도 점수 (0-1)")
    processing_time: float = Field(..., description="처리 시간(초)")

class RAGDocument(BaseModel):
    """RAG 문서 모델"""
    content: str = Field(..., description="문서 내용")
    source: str = Field(..., description="문서 출처")
    relevance_score: float = Field(..., description="관련성 점수")

class RAGResponse(BaseModel):
    """RAG 검색 응답 모델"""
    success: bool = Field(..., description="처리 성공 여부")
    query: str = Field(..., description="검색 쿼리")
    result: str = Field(..., description="RAG 검색 결과")
    source_documents: List[RAGDocument] = Field(..., description="참조 문서들")
    processing_time: float = Field(..., description="처리 시간(초)")

class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    role: str = Field(..., description="메시지 역할 (user, assistant)")
    content: str = Field(..., description="메시지 내용")
    timestamp: datetime = Field(default_factory=datetime.now, description="메시지 시간")

class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="응답 메시지")
    chat_history: List[ChatMessage] = Field(..., description="대화 히스토리")
    processing_time: float = Field(..., description="처리 시간(초)")

class PDFExportResponse(BaseModel):
    """PDF 내보내기 응답 모델"""
    success: bool = Field(..., description="처리 성공 여부")
    download_url: str = Field(..., description="다운로드 URL")
    file_size: int = Field(..., description="파일 크기(바이트)")
    expires_at: datetime = Field(..., description="링크 만료 시간") 