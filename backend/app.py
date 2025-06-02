from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import tempfile
import shutil

from routers import ocr, analysis, chat
from models.response_models import (
    HealthResponse, 
    OCRResponse, 
    AnalysisResponse, 
    ViolationCheckResponse,
    LLMJudgmentResponse,
    RAGResponse
)

load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="LawRo API",
    description="근로계약서 분석을 위한 REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정 (안드로이드 앱에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])

# 헬스 체크 엔드포인트
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """API 서버 상태 확인"""
    return HealthResponse(
        status="healthy",
        message="LawRo API is running successfully",
        version="1.0.0"
    )

# 루트 엔드포인트
@app.get("/")
async def root():
    """API 정보"""
    return {
        "message": "LawRo API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 