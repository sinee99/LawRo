import streamlit as st
import requests
import json
import re
from rapidfuzz import fuzz

# ────────────────────────────────────────
# 🔐 Upstage OCR API 설정
API_KEY = "up_KvE6eQR9HV5o3NAUoRNCITGI9s63v"  # ← 여기에 본인 키 입력 또는 환경변수 처리
OCR_URL = "https://ap-northeast-2.apistage.ai/v1/document-ai/ocr"
OCR_HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# ────────────────────────────────────────
# 전처리 함수
def preprocess_ocr_text(raw_text):
    lines = raw_text.splitlines()
    cleaned = []

    for line in lines:
        line = re.sub(r"[■●☑️✔️]", "[X]", line)
        line = re.sub(r"[□⬜️☐]", "[ ]", line)
        line = line.strip()

        if not line or re.match(r"^[-=]{3,}$", line):
            continue
        cleaned.append(line)

    return "\n".join(cleaned)

# ────────────────────────────────────────
# 유사도 비교
def is_similar(word, keyword, threshold=85):
    return fuzz.ratio(word.lower(), keyword.lower()) >= threshold or keyword.lower() in word.lower()

# ────────────────────────────────────────
# 키워드 정의
required_fields = {
    "사용자 정보": ["성명", "업체명", "소재지", "전화번호", "사업자등록번호", "주민등록번호"],
    "근로자 정보": ["근로자", "성명", "생년월일", "본국주소"],
    "근로계약기간": ["근로계약기간", "수습기간", "신규", "재입국"],
    "근로장소": ["근로장소", "장소"],
    "업무내용": ["업종", "사업내용", "직무내용"],
    "근로시간": ["근로시간", "시", "분", "교대제"],
    "휴게시간": ["휴게시간", "분"],
    "휴일": ["휴일", "일요일", "토요일", "공휴일", "유급", "무급"]
}

law_violation_rules = {
    "수습기간 6개월 이상": lambda text: re.search(r"수습.*(6개월|180일|이상)", text),
    "주 52시간 초과 근무": lambda text: re.search(r"(52시간|하루\s?10시간\s?초과|연장근로.*무제한)", text),
    "무급 휴일": lambda text: "무급" in text and "휴일" in text,
    "임금 미지급 가능성": lambda text: re.search(r"(임금.*지급하지.*않는다|무급근로|지연지급)", text)
}

# ────────────────────────────────────────
# 분석 함수
def analyze_contract_text(text):
    extracted_keywords = {}
    words = text.split()

    for category, keywords in required_fields.items():
        found = []
        for keyword in keywords:
            for word in words:
                if is_similar(word, keyword):
                    found.append(keyword)
                    break
        if found:
            extracted_keywords[category] = found

    missing_fields = {}
    for category, keywords in required_fields.items():
        found = extracted_keywords.get(category, [])
        missing = list(set(keywords) - set(found))
        if missing:
            missing_fields[category] = missing

    violations = []
    for label, rule in law_violation_rules.items():
        if rule(text):
            violations.append(label)

    return extracted_keywords, missing_fields, violations

# ────────────────────────────────────────
# OCR 함수
def call_ocr_api(file):
    files = {"image": (file.name, file.getvalue())}
    response = requests.post(OCR_URL, headers=OCR_HEADERS, files=files)
    if response.status_code == 200:
        result = response.json()
        text = " ".join([p.get("text", "") for p in result.get("pages", [])])
        return preprocess_ocr_text(text)
    else:
        raise ValueError(f"OCR 실패: {response.status_code}\n{response.text}")

# ────────────────────────────────────────
# Streamlit UI
st.set_page_config(page_title="근로계약서 분석기", layout="wide")
st.title("📄 근로계약서 자동 분석기 (이미지 업로드 + OCR + 법 위반 감지)")

uploaded_file = st.file_uploader("📤 근로계약서 이미지를 업로드하세요 (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="업로드된 계약서 이미지", use_column_width=True)
    with st.spinner("🔍 OCR 분석 및 전처리 중..."):
        try:
            clean_text = call_ocr_api(uploaded_file)

            st.subheader("🧾 전처리된 계약서 텍스트 (요약)")
            st.text(clean_text[:1000] + "..." if len(clean_text) > 1000 else clean_text)

            found, missing, violations = analyze_contract_text(clean_text)

            st.subheader("✅ 포함된 필수 항목")
            st.json(found)

            st.subheader("⚠️ 누락된 필수 항목")
            if missing:
                st.json(missing)
            else:
                st.success("모든 항목이 포함되어 있습니다.")

            st.subheader("❌ 근로기준법 위반 가능 조항")
            if violations:
                for v in violations:
                    st.error(f"🚨 {v}")
            else:
                st.success("감지된 위반 조항 없음")

        except Exception as e:
            st.error(f"분석 중 오류 발생: {e}")
