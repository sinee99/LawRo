import os
import cv2
import json
import requests
import matplotlib.pyplot as plt
import pandas as pd

from PIL import Image

# Pandas 출력 설정
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 5000)

# --- 설정값 ---
API_KEY = "up_KvE6eQR9HV5o3NAUoRNCITGI9s63v"
API_URL = "https://ap-northeast-2.apistage.ai/v1/document-ai/ocr"
IMAGE_PATH = r"C:\Users\sinee\Documents\VSCODE\LawRo\test.png"

HEADERS = {"Authorization": f"Bearer {API_KEY}"}


def load_image(path: str):
    """이미지 파일을 OpenCV로 로드"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
    return cv2.imread(path)


def request_ocr_api(image_path: str):
    """OCR API 요청 보내기"""
    with open(image_path, "rb") as image_file:
        files = {"image": image_file}
        response = requests.post(API_URL, headers=HEADERS, files=files)
    return response


def draw_bounding_boxes(image, ocr_result):
    """OCR 결과 기반으로 텍스트 박스 표시"""
    annotated = image.copy()
    for page in ocr_result.get("pages", []):
        for word in page.get("words", []):
            vertices = word["boundingBox"]["vertices"]
            start_point = (vertices[0]["x"], vertices[0]["y"])
            end_point = (vertices[2]["x"], vertices[2]["y"])
            cv2.rectangle(annotated, start_point, end_point, (0, 0, 255), 2)
    return annotated


def show_images(original, annotated):
    """원본 및 OCR 박스 이미지 시각화"""
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    axs[0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    axs[0].set_title("Original Image")
    axs[0].axis("off")

    axs[1].imshow(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
    axs[1].set_title("OCR Highlighted Image")
    axs[1].axis("off")

    plt.tight_layout()
    plt.show()


def save_result_json(result: dict, filename: str = "ocr_result.json"):
    """OCR 결과를 JSON 파일로 저장"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def main():
    try:
        print("🔍 이미지 로드 중...")
        image = load_image(IMAGE_PATH)

        print("📤 OCR API 요청 중...")
        response = request_ocr_api(IMAGE_PATH)

        if response.status_code == 200:
            print("✅ OCR 성공!")
            result = response.json()

            print("📄 OCR 결과 (요약):")
            print(json.dumps(result["pages"], indent=2, ensure_ascii=False))

            save_result_json(result)

            print("🎨 박스 시각화 중...")
            annotated_image = draw_bounding_boxes(image, result)
            show_images(image, annotated_image)

        else:
            print(f"❌ OCR 요청 실패: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"🚨 오류 발생: {e}")


if __name__ == "__main__":
    main()
