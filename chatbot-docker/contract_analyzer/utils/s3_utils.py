import boto3
import os
import json
from uuid import uuid4
from config.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, TMP_DIR

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# ✅ 1. 이미지 업로드 (사용자 → S3)
def upload_image_to_s3(bucket: str, file, user_id: str, contract_id: str) -> str:
    ext = file.filename.split(".")[-1]
    key = f"user_{user_id}/contracts/{contract_id}/contract_{uuid4().hex[:8]}.{ext}"

    s3.upload_fileobj(
        file.file,
        bucket,
        key,
        ExtraArgs={"ContentType": file.content_type}
    )

    return key

# ✅ 2. 이미지 다운로드 (S3 → 임시 디렉토리)
def download_s3_files(bucket_name: str, s3_keys: list[str], local_dir: str) -> list[str]:
    if local_dir is None:
        local_dir = TMP_DIR
    os.makedirs(local_dir, exist_ok=True)

    local_paths = []

    for s3_key in s3_keys:
        filename = os.path.basename(s3_key)
        local_path = os.path.join(local_dir, filename)
        s3.download_file(bucket_name, s3_key, local_path)
        local_paths.append(local_path)

    return local_paths

# ✅ 3. JSON 데이터 업로드 (사용자 → S3)
def upload_json_to_s3(bucket: str, key: str, data: dict):
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, ensure_ascii=False, indent=2),
        ContentType="application/json"
    )