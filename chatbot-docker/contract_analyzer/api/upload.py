from fastapi import APIRouter, File, UploadFile, Form
from typing import List
from utils.s3_utils import upload_image_to_s3
from config.settings import S3_BUCKET_NAME

router = APIRouter()

@router.post("/upload")
async def upload_contract_images(
    user_id: str = Form(...),
    contract_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    uploaded_keys = []
    for file in files:
        s3_key = upload_image_to_s3(S3_BUCKET_NAME, file, user_id, contract_id)
        uploaded_keys.append(s3_key)

    return {
        "message": "이미지 업로드 완료",
        "s3_keys": uploaded_keys
    }
