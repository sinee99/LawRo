from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import time
import requests
import os
import tempfile
from typing import Dict, Any

from ..models.response_models import OCRResponse
from ..services.ocr_service import OCRService
from ..utils.text_preprocessing import preprocess_ocr_text

router = APIRouter()
ocr_service = OCRService()

@router.post("/extract", response_model=OCRResponse)
async def extract_text_from_image(file: UploadFile = File(...)):
    """
    이미지에서 텍스트를 추출합니다.
    
    Args:
        file: 업로드된 이미지 파일 (PNG, JPG, JPEG)
    
    Returns:
        OCRResponse: OCR 처리 결과
    """
    start_time = time.time()
    
    # 파일 형식 검증
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="이미지 파일만 업로드 가능합니다."
        )
    
    # 파일 크기 검증 (10MB 제한)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail="파일 크기는 10MB를 초과할 수 없습니다."
        )
    
    try:
        # OCR 처리
        original_text = await ocr_service.extract_text(file_content, file.filename)
        processed_text = preprocess_ocr_text(original_text)
        
        processing_time = time.time() - start_time
        
        return OCRResponse(
            success=True,
            original_text=original_text,
            processed_text=processed_text,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return OCRResponse(
            success=False,
            original_text="",
            processed_text="",
            processing_time=processing_time,
            error_message=str(e)
        )

@router.get("/health")
async def ocr_health_check():
    """OCR 서비스 상태 확인"""
    try:
        # Upstage API 연결 테스트
        is_healthy = await ocr_service.health_check()
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "OCR",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "OCR",
            "error": str(e),
            "timestamp": time.time()
        } 