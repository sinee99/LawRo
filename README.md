# LawRo
# 📝 근로계약서 분석 시스템 (OCR + LLM + RAG)

AI 기반으로 근로계약서 이미지를 분석하여 필수 항목 누락 여부, 근로기준법 위반 가능성 등을 자동 판단하고, PDF 보고서로 저장할 수 있는 통합 시스템입니다.



## 📦 주요 기능

- 📸 **OCR 기반 계약서 인식** (`Upstage OCR API`)
- 🔎 **필수 항목 누락 탐지** (`정규식 + RapidFuzz`)
- ❗ **근로기준법 위반 조항 감지** (`룰 기반 + solar-pro`)
- 💬 **의미 기반 법률 판단** (`Upstage LLM`)
- 📚 **법률 문서 RAG 기반 판단** (`Chroma + solar-embedding`)
- 🧾 **PDF 리포트 저장 및 다운로드**
- 🖼️ **Streamlit 기반 UI 제공**



## 🖥️ 실행 화면

<p float="left">
  <img src="screenshots/upload.png" width="45%">
  <img src="screenshots/analysis.png" width="45%">
</p>
<p float="left">
  <img src="screenshots/violation.png" width="45%">
  <img src="screenshots/pdf.png" width="45%">
</p>



## 🚀 실행 방법

```
bash
# 필수 라이브러리 설치
pip install -r requirements.txt
```

# 환경 변수 설정
```
cp .env.example .env
```
또는 .env 파일에 아래처럼 작성
UPSTAGE_API_KEY=up_XXXXXXXXXXXXXXXX

# 앱 실행
```
cd OCR
streamlit run app.py
```

🗂️ 폴더 구조
OCR/
├── app.py                 # Streamlit 메인 앱
├── llm_utils.py           # solar-pro 의미 기반 판단
├── rag_utils.py           # 법률 문서 RAG 검색
├── pdf_export.py          # 분석 결과 PDF 저장
├── ocr_result.json        # (샘플) OCR 결과 JSON
├── .env                   # API 키 보관
├── law_data/              # 내장된 법률 PDF
├── chroma_db/             # 임베딩 벡터 저장소
└── screenshots/           # 실행 화면 캡처


⚙️ 기술 스택

| 기능       | 기술                                                                           |
| -------- | ---------------------------------------------------------------------------- |
| OCR      | [Upstage OCR API](https://console.upstage.ai/docs/capabilities/document-ocr) |
| LLM 판단   | `solar-pro`, Upstage API                                                     |
| 임베딩 RAG  | `solar-embedding-1-large`, LangChain + Chroma                                |
| 유사도 분석   | `RapidFuzz`                                                                  |
| 보고서 생성   | `fpdf`                                                                       |
| UI       | `Streamlit`                                                                  |
| 환경 변수 관리 | `dotenv`                                                                     |

---
📄 분석 보고서 예시
분석된 결과는 문서 형식으로 자동 생성됩니다.

필수 항목 누락 여부, 법 위반 추정 조항, 법률 해석 요약이 포함됩니다.

---
📬 문의 / 기여
해당 프로젝트는 근로계약의 공정성 향상과 외국인 근로자 보호를 목표로 합니다.
개선 제안이나 기여는 언제든지 환영입니다! 🙌

