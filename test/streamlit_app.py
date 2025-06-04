import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime
import streamlit as st

from review_and_edit_ui import review_and_edit_ui
from llm_utils import (
    PROMPT_TEMPLATE,
    call_llm_and_parse,
    get_llm_judgment
)
from ocr_utils import (
    process_ocr,
    get_full_text,
    create_highlighted_image,
    API_KEY
)

# 한글 폰트 설정
mpl.rcParams['font.family'] = 'AppleGothic'
mpl.rcParams['axes.unicode_minus'] = False

def process_single_image(image_bytes, image_type):
    """단일 이미지 처리 함수"""
    image_array = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

    with st.spinner("🔍 OCR 분석 중..."):
        try:
            ocr_data = process_ocr(image_bytes, image_type)
            full_text = get_full_text(ocr_data)
        except Exception as e:
            st.error(f"❌ {str(e)}")
            return None, None, None, None

    return full_text, image_array, ocr_data

def main():
    st.set_page_config(page_title="근로계약서 분석기", layout="wide")
    st.title("📁 근로계약서 자동 분석기")

    uploaded_files = st.file_uploader(
        "📄 분석할 근로계약서 이미지 업로드 (여러 페이지 선택 가능)", 
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.stop()

    # 모든 페이지의 텍스트와 이미지를 저장할 리스트
    all_texts = []
    all_images = []
    all_ocr_data = []
    
    # 각 이미지 OCR 처리
    with st.spinner("🔍 모든 페이지 OCR 처리 중..."):
        for idx, uploaded_file in enumerate(uploaded_files, 1):
            st.subheader(f"📄 {idx}페이지: {uploaded_file.name}")
            
            # 파일 내용을 바이트로 읽기
            image_bytes = uploaded_file.getvalue()
            
            full_text, image_array, ocr_data = process_single_image(
                image_bytes, 
                uploaded_file.type
            )
            
            if full_text is None:  # 에러 발생한 경우
                continue

            all_texts.append(full_text)
            all_images.append((image_array, ocr_data))

            # 이미지 표시
            col1, col2 = st.columns(2)
            with col1:
                st.image(image_array, caption=f"{idx}페이지 원본")
            with col2:
                highlighted = create_highlighted_image(image_array, ocr_data)
                st.image(highlighted, caption=f"{idx}페이지 OCR 결과")

    if not all_texts:  # OCR 처리된 텍스트가 없는 경우
        st.error("❌ 처리할 수 있는 이미지가 없습니다.")
        st.stop()

    # 전체 텍스트 결합
    combined_text = "\n\n=== 페이지 구분선 ===\n\n".join(all_texts)

    # OCR 결과 표시
    with st.expander("🖨️ 전체 OCR 결과 보기"):
        st.write(combined_text)

    # LLM 분석
    with st.spinner("🧠 계약서 내용 분석 중..."):
        prompt = PROMPT_TEMPLATE.format(text=combined_text)
        extracted_fields = call_llm_and_parse(prompt, API_KEY)

    # 추출된 필드 수정 UI
    st.subheader("✏️ 추출된 정보 확인 및 수정")
    updated_fields = review_and_edit_ui(extracted_fields)

    # 최종 결과 표시
    st.subheader("📊 분석 결과")
    st.json(updated_fields)

    # 법률 위반 판단
    if st.button("⚖️ 법률 위반 판단 요청"):
        with st.spinner("🧠 법률 위반 판단 중..."):
            judgment = get_llm_judgment(
                contract_json=updated_fields,
                api_key=API_KEY,
                year=datetime.now().year
            )
            st.subheader("⚖️ 법률 위반 판단 결과")
            st.write(judgment)

if __name__ == "__main__":
    main() 