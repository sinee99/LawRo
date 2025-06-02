from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import time
import tempfile
import os
from typing import Dict, Any

from ..models.request_models import TextAnalysisRequest, LLMJudgmentRequest, RAGSearchRequest, PDFExportRequest
from ..models.response_models import (
    AnalysisResponse, 
    ViolationCheckResponse, 
    LLMJudgmentResponse, 
    RAGResponse,
    PDFExportResponse,
    RequiredFieldsResult,
    OCRResponse
)
from ..services.analysis_service import AnalysisService
from ..services.ocr_service import OCRService
from ..services.llm_service import LLMService
from ..services.rag_service import RAGService
from ..services.pdf_service import PDFService

router = APIRouter()

# 서비스 인스턴스 생성
analysis_service = AnalysisService()
ocr_service = OCRService()
llm_service = LLMService()
rag_service = RAGService()
pdf_service = PDFService()

@router.post("/full-analysis", response_model=AnalysisResponse)
async def full_contract_analysis(file: UploadFile = File(...)):
    """
    이미지 업로드부터 전체 분석까지 원스톱으로 처리합니다.
    
    Args:
        file: 근로계약서 이미지 파일
    
    Returns:
        AnalysisResponse: 종합 분석 결과
    """
    start_time = time.time()
    
    try:
        # 1. OCR 처리
        file_content = await file.read()
        original_text = await ocr_service.extract_text(file_content, file.filename)
        processed_text = analysis_service.preprocess_text(original_text)
        
        ocr_result = OCRResponse(
            success=True,
            original_text=original_text,
            processed_text=processed_text,
            processing_time=time.time() - start_time
        )
        
        # 2. 필수 항목 분석
        required_fields = analysis_service.analyze_required_fields(processed_text)
        
        # 3. 법 위반 검사
        violations = analysis_service.check_violations(processed_text)
        
        # 4. 전체 점수 계산
        overall_score = analysis_service.calculate_overall_score(
            required_fields, violations
        )
        
        # 5. 권장사항 생성
        recommendations = analysis_service.generate_recommendations(
            required_fields, violations
        )
        
        processing_time = time.time() - start_time
        
        return AnalysisResponse(
            success=True,
            ocr_result=ocr_result,
            required_fields=required_fields,
            violations=violations,
            overall_score=overall_score,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")

@router.post("/text-analysis", response_model=RequiredFieldsResult)
async def analyze_text(request: TextAnalysisRequest):
    """
    텍스트에서 필수 항목을 분석합니다.
    
    Args:
        request: 텍스트 분석 요청
    
    Returns:
        RequiredFieldsResult: 필수 항목 분석 결과
    """
    try:
        processed_text = analysis_service.preprocess_text(request.text)
        result = analysis_service.analyze_required_fields(processed_text)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트 분석 중 오류가 발생했습니다: {str(e)}")

@router.post("/violations", response_model=ViolationCheckResponse)
async def check_violations(request: TextAnalysisRequest):
    """
    근로기준법 위반 사항을 검사합니다.
    
    Args:
        request: 텍스트 분석 요청
    
    Returns:
        ViolationCheckResponse: 위반 검사 결과
    """
    try:
        processed_text = analysis_service.preprocess_text(request.text)
        result = analysis_service.check_violations(processed_text)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"위반 검사 중 오류가 발생했습니다: {str(e)}")

@router.post("/llm-judgment", response_model=LLMJudgmentResponse)
async def get_llm_judgment(request: LLMJudgmentRequest):
    """
    LLM을 사용하여 계약서 내용을 판단합니다.
    
    Args:
        request: LLM 판단 요청
    
    Returns:
        LLMJudgmentResponse: LLM 판단 결과
    """
    try:
        result = await llm_service.get_judgment(request.text, request.focus_areas)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM 판단 중 오류가 발생했습니다: {str(e)}")

@router.post("/rag-search", response_model=RAGResponse)
async def rag_search(request: RAGSearchRequest):
    """
    RAG를 사용하여 법률 문서를 검색하고 판단합니다.
    
    Args:
        request: RAG 검색 요청
    
    Returns:
        RAGResponse: RAG 검색 결과
    """
    try:
        result = await rag_service.search_and_analyze(request.query, request.max_results)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG 검색 중 오류가 발생했습니다: {str(e)}")

@router.post("/export-pdf")
async def export_analysis_pdf(request: PDFExportRequest):
    """
    분석 결과를 PDF로 내보냅니다.
    
    Args:
        request: PDF 내보내기 요청
    
    Returns:
        FileResponse: PDF 파일
    """
    try:
        pdf_path = await pdf_service.generate_analysis_report(
            request.contract_text,
            request.analysis_results,
            request.include_recommendations
        )
        
        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename='contract_analysis_report.pdf'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 생성 중 오류가 발생했습니다: {str(e)}")

@router.get("/health")
async def analysis_health_check():
    """분석 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "Analysis",
        "components": {
            "text_analysis": "operational",
            "violation_check": "operational",
            "llm_service": "operational",
            "rag_service": "operational"
        },
        "timestamp": time.time()
    } 