import requests
from config.settings import UPSTAGE_OCR_API_KEY, UPSTAGE_OCR_ENDPOINT

def extract_text_from_image(image_path: str) -> dict:
    headers = {"Authorization": f"Bearer {UPSTAGE_OCR_API_KEY}"}
    
    with open(image_path, "rb") as img_file:
        files = {"document": img_file}  # 반드시 "document" 키 사용
        data = {
            "ocr": "force",
            "base64_encoding": "['table']",
            "model": "document-parse",
            "chart_recognition": True,
            "coordinates": True,
            "output_formats": '["html"]',
        }
        
        response = requests.post(
            UPSTAGE_OCR_ENDPOINT,
            headers=headers,
            files=files,
            data=data
        )

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"OCR 요청 실패: {response.status_code}, {response.text}")
