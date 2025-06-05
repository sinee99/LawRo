import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config.settings import S3_BUCKET_NAME, TMP_DIR
from ocr.batch_ocr_processor import process_contract_images_from_s3
from llm.gpt_parser import extract_contract_items_from_summary
import boto3
import traceback

router = APIRouter()
s3 = boto3.client("s3")

class AnalyzeRequest(BaseModel):
    user_id: str
    contract_id: str

#@router.post("/analyze")
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

        os.makedirs(TMP_DIR, exist_ok=True)
        tmp_output = os.path.join(TMP_DIR, f"ocr_result_{req.user_id}_{req.contract_id}.json")

        process_contract_images_from_s3(
            bucket=S3_BUCKET_NAME,
            s3_keys=s3_keys,
            output_path=tmp_output
        )

        result = extract_contract_items_from_summary(tmp_output)

        return {
            "message": "계약서 분석 완료",
            "structured_result": result
        }

    except Exception as e:
        tb = traceback.format_exc()
        print(tb)  # 터미널에 전체 스택 트레이스 출력
        raise HTTPException(status_code=500, detail=str(e))
