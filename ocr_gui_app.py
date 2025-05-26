import streamlit as st
import requests
import cv2
import numpy as np
import json
from PIL import Image
from rapidfuzz import fuzz
import re

# --- 설정 ---
API_KEY = "up_KvE6eQR9HV5o3NAUoRNCITGI9s63v"
API_URL = "https://ap-northeast-2.apistage.ai/v1/document-ai/ocr"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# --- 필수 키워드 ---
required_fields = {
    "사용자 정보": ["성명", "업체명", "소재지", "전화번호", "사업자등록번호", "주민등록번호"],
    "근로자 정보": ["근로자", "성명", "생년월일", "본국주소"],
    "근로계약기간": ["근로계약기간", "수습기간", "신규", "재입국"],
    "근로장소": ["근로장소", "장소"],
    "업무내용": ["업종", "사업내용", "직무내용"],
    "근로시간": ["근로시간", "시", "분", "교대제"],
    "휴게시간": ["휴게시간", "분"],
    "휴일": ["휴일", "일요일", "토요일", "공휴일", "유급", "무급"],
    "임금": ["통상임금", "기본급", "수당", "상여금", "수습", "가산수당"],
    "임금지급일": ["매월", "매주", "지급일", "요일", "공휴일", "전일"],
    "지급방법": ["계좌지급", "현금지급", "통장", "도장", "직접지급"],
    "숙식제공": ["숙소", "제공", "미제공", "자비", "식사", "숙소제공", "식사제공", "조식", "중식", "석식"],
    "규정준수": ["취업규칙", "단체협약", "성실", "이행"],
    "기타조항": ["협의", "기타사항", "추가", "자유협의"]
}

# --- 법 위반 룰 ---
law_violation_rules = {
    "수습기간 6개월 초과": r"수습.*(6개월|180일|이상)",
    "주 52시간 초과 근로": r"(52시간|하루\s?10시간\s?초과|연장근로.*무제한)",
    "휴일 무급 처리": r"무급.*(휴일|공휴일)",
    "임금 미지급 언급": r"(임금.*지급하지.*않는다|무급근로|지연지급)"
}

def is_similar(word, keyword, threshold=85):
    return fuzz.ratio(word, keyword) >= threshold

def analyze_text(text):
    found_fields = {}
    lowered_text = text.lower()
    words = lowered_text.split()

    for category, keywords in required_fields.items():
        found = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # 1. 문자열 포함 여부 우선 검사
            if keyword_lower in lowered_text:
                found.append(keyword)
            else:
                # 2. 유사도 판단
                for word in words:
                    if is_similar(word, keyword_lower):
                        found.append(keyword)
                        break
        if found:
            found_fields[category] = found

    missing_fields = {}
    for category, keywords in required_fields.items():
        found = found_fields.get(category, [])
        missing = list(set(keywords) - set(found))
        if missing:
            missing_fields[category] = missing

    violations = []
    for label, pattern in law_violation_rules.items():
        if re.search(pattern, lowered_text):
            violations.append(label)

    return found_fields, missing_fields, violations

def highlight_boxes(image, ocr_data):
    for page in ocr_data.get("pages", []):
        for word in page.get("words", []):
            vertices = word["boundingBox"]["vertices"]
            pt1 = (vertices[0]["x"], vertices[0]["y"])
            pt2 = (vertices[2]["x"], vertices[2]["y"])
            cv2.rectangle(image, pt1, pt2, (0, 0, 255), 2)
    return image

# --- Streamlit UI ---
st.title("📄 근로계약서 OCR & 분석")

uploaded_file = st.file_uploader("이미지를 업로드하세요 (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    np_image = np.array(image)
    st.image(image, caption="원본 이미지", use_column_width=True)

    with st.spinner("🧠 OCR 분석 중..."):
        files = {"image": (uploaded_file.name, uploaded_file.getvalue())}
        response = requests.post(API_URL, headers=HEADERS, files=files)

        if response.status_code == 200:
            ocr_result = response.json()
            full_text = " ".join([p.get("text", "") for p in ocr_result.get("pages", [])])
            analyzed_image = highlight_boxes(np_image.copy(), ocr_result)

            st.image(analyzed_image, caption="텍스트 강조 이미지", use_column_width=True)

            st.subheader("📄 OCR 전체 텍스트")
            st.text(full_text)

            found, missing, violations = analyze_text(full_text)

            st.subheader("✅ 포함된 필수 항목")
            st.json(found)

            if missing:
                st.subheader("⚠️ 누락된 필수 항목")
                st.json(missing)
            else:
                st.success("모든 필수 항목이 포함되어 있습니다.")

            if violations:
                st.subheader("❌ 근로기준법 위반 가능 조항")
                st.json(violations)
            else:
                st.success("근로기준법 위반 조항이 감지되지 않았습니다.")
        else:
            st.error(f"OCR 실패: {response.status_code}")
            st.text(response.text)
