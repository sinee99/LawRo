from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from config.settings import S3_BUCKET_NAME
from ocr.batch_ocr_processor_copy import ocr_pages_from_s3
from llm.gpt_summarizer import summarize_pages
from llm.gpt_parser import extract_contract_items_from_summaries
import boto3
from typing import List, Dict

router = APIRouter()
s3 = boto3.client("s3")

class AnalyzeRequest(BaseModel):
    user_id: str
    contract_id: str

class AnalyzeResponse(BaseModel):
    message: str = Field(default="계약서 분석 완료")
    page_summaries: List[str]
    structured_result: Dict
    
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