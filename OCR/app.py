import streamlit as st
import requests
import json
import re
from rapidfuzz import fuzz
from rag_utils import get_rag_result
from llm_utils import get_llm_judgment
from pdf_export import export_pdf
from dotenv import load_dotenv
import os
load_dotenv()

# 해당 .env 파일에 UPSTAGE_API_KEY 해당 
API_KEY = os.getenv("UPSTAGE_API_KEY")
OCR_URL = "https://ap-northeast-2.apistage.ai/v1/document-ai/ocr"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# ---- 가장 기본적인 정규식 기본 형식 방식 ----
def preprocess(text):
    lines = text.splitlines()
    out = []
    for line in lines:
        line = re.sub(r"[■●☑️✔️]", "[X]", line)
        line = re.sub(r"[□⬜️☐]", "[ ]", line)
        line = line.strip()
        if line and not re.match(r"^[-=]{3,}$", line):
            out.append(line)
    return "\n".join(out)

def is_similar(word, keyword, threshold=85):
    return fuzz.ratio(word.lower(), keyword.lower()) >= threshold or keyword.lower() in word.lower()

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
    "수습기간 6개월 이상": lambda t: re.search(r"수습.*(6개월|180일|이상)", t),
    "주 52시간 초과 근무": lambda t: re.search(r"(52시간|하루\s?10시간\s?초과|연장근로.*무제한)", t),
    "무급 휴일": lambda t: "무급" in t and "휴일" in t,
    "임금 미지급 가능성": lambda t: re.search(r"(임금.*지급하지.*않는다|무급근로|지연지급)", t)
}

def analyze(text):
    results = {}
    words = text.split()
    for category, keywords in required_fields.items():
        found = []
        for keyword in keywords:
            if any(is_similar(word, keyword) for word in words):
                found.append(keyword)
        if found:
            results[category] = found
    return results

def detect_missing(found):
    missing = {}
    for cat, keywords in required_fields.items():
        included = found.get(cat, [])
        remain = list(set(keywords) - set(included))
        if remain:
            missing[cat] = remain
    return missing

def detect_violations(text):
    return [label for label, rule in law_violation_rules.items() if rule(text)]

# ★ Streamlit App
st.set_page_config(page_title="근로계약서 자동 분석기", layout="wide")
st.title("📄 근로계약서 자동 분석기 (OCR + 전처리 + 위반 판단)")

uploaded_file = st.file_uploader("📤 계약서 이미지 업로드 (.png, .jpg)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="업로드된 이미지", use_column_width=True)
    with st.spinner("🧠 OCR 분석 중..."):
        files = {"image": (uploaded_file.name, uploaded_file.getvalue())}
        response = requests.post("https://ap-northeast-2.apistage.ai/v1/document-ai/ocr", headers=HEADERS, files=files)

        if response.status_code == 200:
            ocr_result = response.json()
            text = " ".join([p.get("text", "") for p in ocr_result.get("pages", [])])
            clean_text = preprocess(text)

            st.subheader("🧾 전처리된 텍스트")
            st.text(clean_text[:1000] + "..." if len(clean_text) > 1000 else clean_text)

            found = analyze(clean_text)
            missing = detect_missing(found)
            violations = detect_violations(clean_text)

            st.subheader("✅ 포함된 필수 항목")
            st.json(found)

            st.subheader("⚠️ 누락된 항목")
            if missing:
                st.json(missing)
            else:
                st.success("모든 항목 포함")

            st.subheader("❌ 정규식 기반 위반 감지")
            if violations:
                for v in violations:
                    st.error(f"🚨 {v}")
            else:
                st.success("명시적 위반 없음")

            with st.expander("🔎 Upstage Embedding 기반 법률 조항 검색(RAG)"):
                rag_result = get_rag_result(clean_text)
                st.markdown(rag_result["result"])
                for i, doc in enumerate(rag_result["source_documents"]):
                    st.code(doc.page_content.strip(), language="markdown")
                    st.caption(f"출처: {doc.metadata.get('source', '알 수 없음')}")

            with st.expander("🧠 solar-pro 모델 기반 위반 의미 분석"):
                llm_result = get_llm_judgment(clean_text)
                st.markdown(llm_result)

            st.download_button("📥 분석 결과 PDF 저장", data=export_pdf(clean_text, found, missing, violations, rag_result, llm_result), file_name="분석결과.pdf")

        else:
            st.error(f"❌ OCR 실패: {response.status_code}")
            st.text(response.text)
