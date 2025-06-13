from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import asyncio
from typing import Dict, Any, Optional, List
import time
import os
from dotenv import load_dotenv

from models import (
    ChatRequest, ChatResponse, 
    UserSignupRequest, UserSignupResponse, UserLoginRequest, UserLoginResponse,
    ContractAnalyzeRequest, ContractAnalyzeResponse
)
from services.user_service import UserService
from services.external_service import ExternalService

# 환경 변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="LawRo 메인 API",
    description="LawRo 앱의 메인 API 서버 - 챗봇, 계약서 분석, 사용자 관리",
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

# 보안 설정
security = HTTPBearer()

# 서비스 초기화
user_service = UserService()
external_service = ExternalService()

@app.get("/")
async def root():
    """API 정보"""
    return {
        "message": "LawRo 메인 API",
        "version": "1.0.0",
        "docs": "/docs",
        "services": {
            "chatbot": "http://chatbot:8001",
            "contract_analyzer": "http://contract:8002"
        }
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    # 외부 서비스 상태 확인
    chatbot_status = await external_service.check_chatbot_health()
    contract_status = await external_service.check_contract_health()
    
    return {
        "status": "healthy",
        "service": "LawRo Main API",
        "timestamp": time.time(),
        "external_services": {
            "chatbot": chatbot_status,
            "contract_analyzer": contract_status
        }
    }

# 사용자 관리 엔드포인트
@app.post("/auth/signup", response_model=UserSignupResponse)
async def user_signup(request: UserSignupRequest):
    """사용자 회원가입"""
    try:
        result = await user_service.create_user(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"회원가입 중 오류가 발생했습니다: {str(e)}")

@app.post("/auth/login", response_model=UserLoginResponse)
async def user_login(request: UserLoginRequest):
    """사용자 로그인"""
    try:
        result = await user_service.authenticate_user(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그인 중 오류가 발생했습니다: {str(e)}")

@app.get("/auth/profile")
async def get_user_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """사용자 프로필 조회"""
    try:
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        return {
            "success": True,
            "user": user_data
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 조회 중 오류가 발생했습니다: {str(e)}")

# 챗봇 관련 엔드포인트
@app.post("/chat/send", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """챗봇과 대화"""
    try:
        # 사용자 인증
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        
        # 챗봇 서비스로 요청 전달
        response = await external_service.send_chat_message(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"챗봇 요청 중 오류가 발생했습니다: {str(e)}")

@app.post("/chat/new-session")
async def create_chat_session(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """새로운 채팅 세션 생성"""
    try:
        # 사용자 인증
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        
        # 챗봇 서비스로 요청 전달
        response = await external_service.create_chat_session()
        return response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 생성 중 오류가 발생했습니다: {str(e)}")

@app.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """채팅 히스토리 조회"""
    try:
        # 사용자 인증
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        
        # 챗봇 서비스로 요청 전달
        response = await external_service.get_chat_history(session_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 조회 중 오류가 발생했습니다: {str(e)}")

@app.delete("/chat/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """채팅 히스토리 삭제"""
    try:
        # 사용자 인증
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        
        # 챗봇 서비스로 요청 전달
        response = await external_service.clear_chat_history(session_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 삭제 중 오류가 발생했습니다: {str(e)}")

# 계약서 분석 관련 엔드포인트
@app.post("/contract/analyze", response_model=ContractAnalyzeResponse)
async def analyze_contract(
    request: ContractAnalyzeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """계약서 분석"""
    try:
        # 사용자 인증
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        
        # 계약서 분석 서비스로 요청 전달
        response = await external_service.analyze_contract(request)
        
        # 분석 결과를 사용자와 연결하여 저장 (선택사항)
        await user_service.save_contract_analysis(user_data["user_id"], response)
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"계약서 분석 중 오류가 발생했습니다: {str(e)}")

@app.post("/contract/upload")
async def upload_contract(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """계약서 업로드"""
    try:
        # 사용자 인증
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        
        # 계약서 업로드 서비스로 요청 전달
        response = await external_service.upload_contract()
        return response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"계약서 업로드 중 오류가 발생했습니다: {str(e)}")

@app.get("/contract/history")
async def get_contract_history(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """사용자의 계약서 분석 히스토리 조회"""
    try:
        # 사용자 인증
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        
        # 사용자의 계약서 분석 히스토리 조회
        history = await user_service.get_contract_history(user_data["user_id"])
        return {
            "success": True,
            "history": history
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 조회 중 오류가 발생했습니다: {str(e)}")

# 서버 상태 정보
@app.get("/stats")
async def get_server_stats():
    """서버 통계 정보"""
    try:
        # 전체 서비스 통계 수집
        chatbot_stats = await external_service.get_chatbot_stats()
        user_stats = await user_service.get_user_stats()
        
        return {
            "success": True,
            "stats": {
                "users": user_stats,
                "chatbot": chatbot_stats,
                "timestamp": time.time()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 