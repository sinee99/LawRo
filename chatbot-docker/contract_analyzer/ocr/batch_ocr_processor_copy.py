import os
from ocr.upstage_ocr import extract_text_from_image
from utils.s3_utils import download_s3_files
from config.settings import TMP_DIR
import json

OCR_CACHE_DIR = os.path.join(TMP_DIR, "ocr_results")
os.makedirs(OCR_CACHE_DIR, exist_ok=True)

def ocr_pages_from_s3(bucket: str, s3_keys: list[str], user_id: str, contract_id: str) -> list[dict]:
    """
    S3에서 이미지 다운로드 후 페이지별 OCR 수행하여
    각 페이지 OCR 결과 리스트 반환
    """
    cache_file = os.path.join(OCR_CACHE_DIR, f"{user_id}_{contract_id}.json")

    # 1. 캐시 파일이 있으면 읽어서 반환
    if os.path.exists(cache_file):
        print(f"🔍 OCR 캐시 파일 발견: {cache_file} - 파일 로드")
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
        
    local_image_dir = os.path.join(TMP_DIR, "images")
    os.makedirs(local_image_dir, exist_ok=True)

    local_image_paths = download_s3_files(bucket, s3_keys, local_image_dir)

    page_results = []
    for idx, path in enumerate(local_image_paths):
        print(f"[{idx+1}/{len(local_image_paths)}] OCR 처리 중: {path}")
        result = extract_text_from_image(path)
        print("OCR API 응답:", result)  # 응답 원본 확인용
        
        page_results.append({
            "page": idx + 1,
            "html": result["content"]["html"],
            "raw_result": result
        })
        
    # 3. OCR 결과 캐시 파일로 저장
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(page_results, f, ensure_ascii=False, indent=2)
    print(f"✅ OCR 결과 캐시 저장 완료: {cache_file}")


    return page_results
