# Contract Analyzer 로컬 실행 가이드

## 🚀 빠른 시작

### 방법 1: 자동 설정 및 실행 (권장)
```bash
cd contract_analyzer
python setup_and_run.py
```

### 방법 2: 수동 설정 및 실행
```bash
cd contract_analyzer

# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경변수 설정 (local_env.py 편집)
# 실제 API 키들로 변경 필요

# 5. 서버 실행
python run_local.py
```

### 방법 3: 직접 uvicorn 실행
```bash
# 가상환경 활성화 후
python local_env.py  # 환경변수 설정
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## ⚙️ 환경변수 설정

`local_env.py` 파일을 편집하여 실제 값으로 변경하세요:

```python
# 필수 설정 (실제 값으로 변경 필요)
os.environ["S3_BUCKET_NAME"] = "your-actual-bucket-name"
os.environ["AWS_ACCESS_KEY_ID"] = "AKIA..."  
os.environ["AWS_SECRET_ACCESS_KEY"] = "your-secret-key"
os.environ["UPSTAGE_API_KEY"] = "up_..."
os.environ["OPENAI_API_KEY"] = "sk-..."

# ChatBot 서버 (이미 설정됨)
os.environ["CHATBOT_URL"] = "http://16.176.26.197:8000"
```

## 🌐 접속 URL

서버 실행 후 다음 URL로 접속 가능:

- **메인 페이지**: http://localhost:8000/
- **API 문서**: http://localhost:8000/docs
- **ChatBot 상태**: http://localhost:8000/api/chatbot-status

## 🧪 테스트

### 전체 파이프라인 테스트 (실제 이미지 사용) ⭐
```bash
# 서버가 실행 중인 상태에서
python run_pipeline_test.py
```
이 테스트는 실제 `ex2.png` 이미지를 업로드하여 엔드유저가 받는 최종 출력 데이터를 확인합니다.

### ChatBot 연결 테스트
```bash
python test_server_communication.py
```

### 기본 기능 테스트
```bash
python test_integration.py
```

### 직접 파이프라인 테스트
```bash
python test_full_pipeline.py
```

### API 테스트 (curl)
```bash
# ChatBot 상태 확인
curl http://localhost:8000/api/chatbot-status

# 계약서 분석 (ChatBot 포함)
curl -X POST http://localhost:8000/api/analyze-with-chatbot \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "contract_id": "test_contract",
    "use_chatbot": true,
    "user_language": "korean"
  }'
```

## 📁 파일 구조

```
contract_analyzer/
├── main.py                        # FastAPI 메인 앱
├── run_local.py                    # 로컬 실행 스크립트
├── setup_and_run.py               # 자동 설정 및 실행
├── local_env.py                    # 환경변수 설정
├── requirements.txt                # Python 의존성
├── config/
│   └── chatbot_config.py          # ChatBot 서버 설정
├── services/
│   └── chatbot_integration_service.py  # ChatBot 통합 서비스
├── api/
│   ├── upload.py                  # 파일 업로드 API
│   └── analyze_copy.py            # 분석 API (ChatBot 통합)
├── ocr/                           # OCR 처리
├── llm/                           # LLM 처리
└── test_*.py                      # 테스트 스크립트
```

## 🔧 문제 해결

### 1. 패키지 설치 오류
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 2. ChatBot 연결 실패
- ChatBot 서버 상태 확인: http://16.176.26.197:8000/health
- 네트워크 연결 확인: `ping 16.176.26.197`

### 3. API 키 오류
- `local_env.py`에서 실제 API 키로 변경
- AWS 자격증명 확인: `aws configure list`

### 4. 포트 충돌
```bash
# 다른 포트로 실행
export PORT=8001
python run_local.py
```

## 💡 주요 기능

### 1. ChatBot 통합 분석
- 계약서 OCR → 구조화 → ChatBot 법률 분석
- 커스텀 프롬프트 자동 적용
- 사용자별 세션 관리

### 2. API 엔드포인트
- `/api/analyze`: 기본 계약서 분석
- `/api/analyze-with-chatbot`: ChatBot 통합 분석
- `/api/chatbot-status`: ChatBot 연결 상태

### 3. 다국어 지원
- 한국어, 영어, 일본어 등 10개 언어
- 언어별 법률 분석 제공

## 🎯 다음 단계

1. **실제 API 키 설정**: `local_env.py` 편집
2. **S3에 계약서 업로드**: 테스트용 계약서 이미지
3. **실제 분석 테스트**: 전체 파이프라인 확인
4. **성능 최적화**: 필요시 설정 조정

---

## 📞 도움말

문제가 발생하면:
1. 로그 확인: 터미널 출력 메시지
2. 테스트 실행: `python test_server_communication.py`
3. API 문서 확인: http://localhost:8000/docs 