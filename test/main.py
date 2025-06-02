import os
import cv2
import json
import requests
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage
from llm_utils import (
    build_prompt,
    call_llm_and_parse,
    get_llm_judgment
)

# 한글 폰트 설정
import matplotlib as mpl
mpl.rcParams['font.family'] = 'AppleGothic'
mpl.rcParams['axes.unicode_minus'] = False

# 환경변수에서 API 키 로드
load_dotenv()
API_KEY = os.getenv("API_KEY")
OCR_URL = "https://ap-northeast-2.apistage.ai/v1/document-ai/ocr"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


def review_and_edit(fields: dict) -> dict:
    """
    추출된 JSON 항목을 사용자에게 보여주고 잘못된 값을
    직접 수정할 수 있도록 대화형 입력을 받습니다.
    엔터만 누르면 기존 값을 유지합니다.
    """
    print("\n📋 추출된 항목을 검토하고 잘못된 값은 수정하세요. 엔터는 그대로 유지:")
    def _recursive_edit(d, parent_key="") -> dict:
        for k, v in d.items():
            if isinstance(v, dict):
                print(f"\n-- {k} (하위 항목) --")
                d[k] = _recursive_edit(v, k)
            else:
                prompt = f"{parent_key + '.' if parent_key else ''}{k} [{v}]: "
                user_input = input(prompt).strip()
                if user_input:
                    d[k] = user_input
        return d

    return _recursive_edit(fields)


def main():
    # 이미지 경로 입력
    image_path = input("📁 분석할 근로계약서 이미지 경로를 입력하세요: ").strip()
    if not os.path.exists(image_path):
        print(f"❌ 파일이 존재하지 않습니다: {image_path}")
        return

    # 이미지 읽기
    image = cv2.imread(image_path)

    # OCR 요청
    with open(image_path, "rb") as img_file:
        files = {"image": img_file}
        resp = requests.post(OCR_URL, headers=HEADERS, files=files)
    if resp.status_code != 200:
        print(f"❌ OCR 실패: {resp.status_code}\n{resp.text}")
        return

    # OCR 결과 텍스트 합치기
    ocr_data = resp.json()
    full_text = " ".join(p.get("text", "") for p in ocr_data.get("pages", []))
    print("\n📄 OCR 결과 일부:")
    print((full_text[:500] + '...') if len(full_text) > 500 else full_text)

    # LLM 프롬프트 생성 및 핵심 정보 추출
    prompt = build_prompt(full_text)
    extracted_fields = call_llm_and_parse(prompt, API_KEY)

    # 사용자 검토 및 수정
    extracted_fields = review_and_edit(extracted_fields)

    # 최종 결과 출력
    print("\n📝 최종 확인된 결과:")
    print(json.dumps(extracted_fields, indent=2, ensure_ascii=False))

    # 법률 위반 판단 추가 호출
    print("\n 법률 위반 판단 중…")
    judgment = get_llm_judgment(full_text, API_KEY)
    print("⚖️ 법률 위반 판단 결과:\n", judgment)

    # OCR 박스 강조 이미지 만들기
    highlighted = image.copy()
    for page in ocr_data.get("pages", []):
        for word in page.get("words", []):
            v = word["boundingBox"]["vertices"]
            cv2.rectangle(highlighted, (v[0]["x"], v[0]["y"]), (v[2]["x"], v[2]["y"]), (0, 0, 255), 2)

    # 결과 이미지 저장
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    axs[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    axs[0].set_title("원본 이미지")
    axs[0].axis("off")

    axs[1].imshow(cv2.cvtColor(highlighted, cv2.COLOR_BGR2RGB))
    axs[1].set_title("OCR 강조 이미지")
    axs[1].axis("off")

    plt.tight_layout()
    plt.savefig("ocr_highlighted.png", dpi=150)
    print("➜ 강조 이미지가 ocr_highlighted.png에 저장되었습니다.")

if __name__ == "__main__":
    main()
