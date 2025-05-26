import streamlit as st
import requests
import cv2
import numpy as np
import json
import os
from PIL import Image
from dotenv import load_dotenv
from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# 환경변수 로드
load_dotenv()

# 설정
API_KEY = os.getenv("UPSTAGE_API_KEY")
OCR_URL = "https://ap-northeast-2.apistage.ai/v1/document-ai/ocr"
OCR_HEADERS = {"Authorization": f"Bearer {API_KEY}"}


# ✅ OCR 요청
def run_ocr(uploaded_file):
    files = {"image": (uploaded_file.name, uploaded_file.getvalue())}
    response = requests.post(OCR_URL, headers=OCR_HEADERS, files=files)
    return response


# ✅ 박스 시각화
def highlight_boxes(image, ocr_data):
    for page in ocr_data.get("pages", []):
        for word in page.get("words", []):
            vertices = word["boundingBox"]["vertices"]
            pt1 = (vertices[0]["x"], vertices[0]["y"])
            pt2 = (vertices[2]["x"], vertices[2]["y"])
            cv2.rectangle(image, pt1, pt2, (0, 0, 255), 2)
    return image


# ✅ 벡터DB + LLM RAG 구성
@st.cache_resource
def setup_rag():
    embedding = UpstageEmbeddings(model="solar-embedding-1-large", upstage_api_key=API_KEY)
    vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embedding)

    llm = ChatUpstage(model="solar-pro", upstage_api_key=API_KEY, temperature=0.2)

    prompt = PromptTemplate(
        template="""
다음은 OCR로 추출된 근로계약서 내용입니다. 아래 법률 근거와 비교하여
위반 여부를 판단해주세요. 위반이라면 어떤 조항을 위반했는지 설명해주세요.

[계약서 내용]
{question}

[법률 근거]
{context}

당신의 판단:
""",
        input_variables=["question", "context"]
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )
    return qa


# ✅ Streamlit 앱 시작
st.set_page_config(page_title="근로계약서 위반 분석 (RAG)", layout="wide")
st.title("📄 근로계약서 법률 위반 분석 (Upstage OCR + RAG)")

uploaded_file = st.file_uploader("📤 근로계약서 이미지를 업로드하세요 (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    np_image = np.array(image)
    st.image(image, caption="원본 이미지", use_column_width=True)

    with st.spinner("🧠 OCR 수행 중..."):
        response = run_ocr(uploaded_file)

        if response.status_code == 200:
            ocr_result = response.json()
            full_text = " ".join([p.get("text", "") for p in ocr_result.get("pages", [])])

            annotated_image = highlight_boxes(np_image.copy(), ocr_result)
            st.image(annotated_image, caption="🔴 텍스트 강조 이미지", use_column_width=True)

            # ✅ 법률 근거 기반 분석 (RAG)
            with st.spinner("⚖️ 법률 근거 기반 위반 분석 중..."):
                rag_chain = setup_rag()
                result = rag_chain({"query": full_text})

                st.subheader("🧠 판단 결과")
                st.markdown(result["result"])

                st.subheader("📚 참조한 법률 조항들")
                for i, doc in enumerate(result["source_documents"]):
                    st.markdown(f"**{i+1}. {doc.metadata.get('source', '알 수 없음')}**")
                    st.code(doc.page_content.strip(), language="markdown")
        else:
            st.error(f"OCR 실패: {response.status_code}")
            st.text(response.text)
