import os
import cv2
import numpy as np
import requests
from dotenv import load_dotenv

# 환경변수에서 API 키 로드
load_dotenv()
API_KEY = os.getenv("UPSTAGE_API_KEY")
OCR_URL = "https://ap-northeast-2.apistage.ai/v1/document-ai/ocr"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def process_ocr(image_bytes, image_type: str):
    """
    이미지를 OCR 처리하고 결과를 반환.
    """
    files = {"image": ("uploaded.png", image_bytes, image_type)}
    resp = requests.post(OCR_URL, headers=HEADERS, files=files)
    if resp.status_code != 200:
        raise Exception(f"OCR 실패: {resp.status_code}\n{resp.text}")
    
    return resp.json()

def get_full_text(ocr_data: dict) -> str:
    """
    OCR 결과에서 전체 텍스트를 추출.
    """
    return " ".join(p.get("text", "") for p in ocr_data.get("pages", []))

def create_highlighted_image(image_array: np.ndarray, ocr_data: dict) -> np.ndarray:
    """
    OCR 결과를 시각화한 이미지를 생성.
    """
    highlighted = image_array.copy()
    for page in ocr_data.get("pages", []):
        for word in page.get("words", []):
            v = word["boundingBox"]["vertices"]
            cv2.rectangle(highlighted, (v[0]["x"], v[0]["y"]), (v[2]["x"], v[2]["y"]), (0, 0, 255), 2)
    return highlighted 