from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from config.settings import S3_BUCKET_NAME
from ocr.batch_ocr_processor_copy import ocr_pages_from_s3
from llm.gpt_summarizer import summarize_pages
from llm.gpt_parser import extract_contract_items_from_summaries
from services.chatbot_integration_service import ChatbotIntegrationService
import boto3
from typing import List, Dict, Optional

router = APIRouter()
s3 = boto3.client("s3")

class AnalyzeRequest(BaseModel):
    user_id: str
    contract_id: str

class AnalyzeResponse(BaseModel):
    message: str = Field(default="계약서 분석 완료")
    page_summaries: List[str]
    structured_result: Dict

class AnalyzeWithChatbotRequest(BaseModel):
    user_id: str
    contract_id: str
    use_chatbot: bool = True
    user_language: str = "korean"

class AnalyzeWithChatbotResponse(BaseModel):
    message: str = Field(default="계약서 분석 및 법률 상담 완료")
    page_summaries: List[str]
    structured_result: Dict
    chatbot_analysis: Optional[Dict] = None
    session_id: Optional[str] = None
    
@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_contract_images(req: AnalyzeRequest):
    try:
        prefix = f"user_{req.user_id}/contracts/{req.contract_id}/"
        paginator = s3.get_paginator("list_objects_v2")

        s3_keys = []
        for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix):
            contents = page.get("Contents", [])
            for obj in contents:
                s3_keys.append(obj["Key"])

        if not s3_keys:
            raise HTTPException(status_code=404, detail="해당 계약서 이미지가 없습니다.")

        # 1. 페이지별 OCR 수행
        page_ocr_results = ocr_pages_from_s3(S3_BUCKET_NAME, s3_keys, req.user_id, req.contract_id)

        # 2. 각 페이지 html 추출
        page_htmls = [page["html"] for page in page_ocr_results]

        # 3. 페이지별 요약 생성
        page_summaries = summarize_pages(page_htmls)

        # 4. 요약 기반 항목 추출
        structured_result = extract_contract_items_from_summaries(page_summaries)

        return AnalyzeResponse(
            page_summaries=page_summaries,
            structured_result=structured_result   
        )

    except Exception as e:
        print(f"ERROR: {str(e)}")  # 로그에 상세한 에러 메시지 출력
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-with-chatbot", response_model=AnalyzeWithChatbotResponse)
def analyze_contract_with_chatbot(req: AnalyzeWithChatbotRequest):
    """
    계약서 분석 + ChatBot 법률 상담 통합 엔드포인트
    """
    try:
        # 1. 기본 계약서 분석 (기존 로직과 동일)
        prefix = f"user_{req.user_id}/contracts/{req.contract_id}/"
        paginator = s3.get_paginator("list_objects_v2")

        s3_keys = []
        for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix):
            contents = page.get("Contents", [])
            for obj in contents:
                s3_keys.append(obj["Key"])

        if not s3_keys:
            raise HTTPException(status_code=404, detail="해당 계약서 이미지가 없습니다.")

        # OCR 수행
        page_ocr_results = ocr_pages_from_s3(S3_BUCKET_NAME, s3_keys, req.user_id, req.contract_id)
        page_htmls = [page["html"] for page in page_ocr_results]
        
        # 페이지별 요약 생성
        page_summaries = summarize_pages(page_htmls)
        
        # 요약 기반 항목 추출
        structured_result = extract_contract_items_from_summaries(page_summaries)
        
        print(f"✅ 계약서 기본 분석 완료 (사용자: {req.user_id}, 계약서: {req.contract_id})")
        
        # 2. ChatBot 법률 상담 (요청 시에만)
        chatbot_analysis = None
        session_id = None
        
        if req.use_chatbot:
            try:
                print(f"🤖 ChatBot 법률 분석 시작...")
                
                # ChatBot 통합 서비스 초기화
                chatbot_service = ChatbotIntegrationService()
                
                # 파싱된 계약서 데이터를 ChatBot으로 법률 분석 요청
                chatbot_result = chatbot_service.analyze_contract_with_chatbot(
                    parsed_contract_data=structured_result,
                    user_id=req.user_id,
                    user_language=req.user_language
                )
                
                if chatbot_result["success"]:
                    chatbot_analysis = {
                        "legal_analysis": chatbot_result["analysis"],
                        "processing_time": chatbot_result["processing_time"],
                        "timestamp": chatbot_result["timestamp"]
                    }
                    session_id = chatbot_result["session_id"]
                    
                    print(f"✅ ChatBot 법률 분석 완료 (세션: {session_id[:8]}...)")
                else:
                    print(f"❌ ChatBot 법률 분석 실패: {chatbot_result['error']}")
                    chatbot_analysis = {
                        "error": chatbot_result['error'],
                        "legal_analysis": "ChatBot 법률 분석에 실패했습니다. 기본 분석 결과를 참고해 주세요."
                    }
                    
            except Exception as chatbot_error:
                print(f"❌ ChatBot 통합 오류: {str(chatbot_error)}")
                chatbot_analysis = {
                    "error": str(chatbot_error),
                    "legal_analysis": "ChatBot 서비스 연결에 실패했습니다. 기본 분석 결과를 참고해 주세요."
                }

        return AnalyzeWithChatbotResponse(
            page_summaries=page_summaries,
            structured_result=structured_result,
            chatbot_analysis=chatbot_analysis,
            session_id=session_id
        )

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chatbot-status")
def check_chatbot_status():
    """ChatBot 서버 연결 상태 확인"""
    try:
        chatbot_service = ChatbotIntegrationService()
        health_check = chatbot_service.health_check()
        
        return {
            "chatbot_available": health_check["success"],
            "status": health_check.get("status", "unknown"),
            "details": health_check
        }
    except Exception as e:
        return {
            "chatbot_available": False,
            "status": "error",
            "error": str(e)
        }