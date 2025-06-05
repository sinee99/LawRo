import json
import os
from ocr.upstage_ocr import extract_text_from_image
from utils.s3_utils import download_s3_files
from config.settings import TMP_DIR

def process_contract_images_from_s3(bucket: str, s3_keys: list[str], output_path: str):
    merged_result = {
        "pages": [],
        "full_html": ""
    }

    local_image_dir = os.path.join(TMP_DIR, "images")
    os.makedirs(local_image_dir, exist_ok=True)

    local_image_paths = download_s3_files(bucket, s3_keys, local_image_dir)

    for idx, path in enumerate(local_image_paths):
        print(f"[{idx+1}/{len(local_image_paths)}] OCR 처리 중: {path}")
        result = extract_text_from_image(path)
        print("OCR API 응답:", result)  # 응답 원본 확인용
        
        page_html = result["content"]["html"]
        merged_result["pages"].append({
            "page": idx + 1,
            "html": page_html
        })
        merged_result["full_html"] += f"\n<!-- Page {idx+1} -->\n" + page_html

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_result, f, ensure_ascii=False, indent=2)

    print(f"✅ 병합 OCR 결과가 {output_path}에 저장되었습니다.")
