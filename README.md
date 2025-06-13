# LawRo 마이크로서비스 아키텍처

LawRo는 법률 상담 및 계약서 분석을 위한 마이크로서비스 기반 애플리케이션입니다.

## 아키텍처 개요

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   main-docker   │    │ chatbot-docker  │    │contract_analyzer│
│   (Port 8000)   │────│   (Port 8001)   │    │   (Port 8002)   │
│                 │    │                 │    │                 │
│ - 사용자 관리    │    │ - 챗봇 서비스    │    │ - 계약서 분석    │
│ - 인증/JWT      │    │ - RAG 체인      │    │ - OCR 처리      │
│ - API 게이트웨이 │    │ - 세션 관리      │    │ - 문서 분석     │
│ - Firestore DB  │    │ - LLM 통합      │    │ - S3 연동       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Docker Network │
                    │  (lawro-network)│
                    └─────────────────┘
```

## 서비스 구성

### 1. Main API Service (Port 8000)
- **역할**: 메인 API 게이트웨이, 사용자 관리, 인증
- **기술스택**: FastAPI, Firebase Admin SDK, JWT
- **주요 기능**:
  - 회원가입/로그인
  - JWT 토큰 인증
  - 챗봇 서비스 프록시
  - 계약서 분석 서비스 프록시
  - Firestore를 통한 사용자 데이터 관리

### 2. Chatbot Service (Port 8001)
- **역할**: 법률 상담 챗봇
- **기술스택**: FastAPI, LangChain, Upstage API, ChromaDB
- **주요 기능**:
  - RAG 기반 법률 상담
  - 채팅 세션 관리
  - 벡터 데이터베이스 검색
  - 다국어 지원

### 3. Contract Analyzer Service (Port 8002)
- **역할**: 계약서 분석 및 처리
- **기술스택**: FastAPI, OCR, LLM, AWS S3
- **주요 기능**:
  - 계약서 업로드 및 OCR 처리
  - 계약서 분석 및 요약
  - 위험요소 탐지
  - 파일 저장 관리

## 설치 및 실행

### 필수 조건
- Docker
- Docker Compose
- Python 3.11+

### 환경 설정

1. **환경 변수 파일 생성**
```bash
cp .env.example .env
```

2. **환경 변수 설정**
```bash
# .env 파일에서 다음 값들을 설정하세요:
JWT_SECRET_KEY=your-jwt-secret-key
UPSTAGE_API_KEY=your-upstage-api-key
FIREBASE_PROJECT_ID=your-firebase-project-id
# ... 기타 Firebase 및 AWS 설정
```

3. **Firebase 서비스 계정 키 설정**
```bash
mkdir firebase-credentials
# firebase-service-account.json 파일을 firebase-credentials/ 디렉토리에 배치
```

### Docker Compose로 실행

```bash
# 모든 서비스 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build

# 특정 서비스만 실행
docker-compose up main-api
docker-compose up chatbot
docker-compose up contract
```

### 개별 서비스 실행

#### Main API Service
```bash
cd main-docker
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Chatbot Service
```bash
cd chatbot-docker
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

#### Contract Analyzer Service
```bash
cd contract_analyzer
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

## API 엔드포인트

### Main API (Port 8000)

#### 인증
- `POST /auth/signup` - 회원가입
- `POST /auth/login` - 로그인
- `GET /auth/profile` - 프로필 조회

#### 챗봇
- `POST /chat` - 챗봇 대화
- `POST /chat/new-session` - 새 세션 생성
- `GET /chat/history/{session_id}` - 채팅 히스토리

#### 계약서 분석
- `POST /contract/analyze` - 계약서 분석
- `POST /contract/upload` - 계약서 업로드
- `GET /contract/history` - 분석 히스토리

#### 시스템
- `GET /health` - 헬스 체크
- `GET /stats` - 시스템 통계

### 직접 서비스 접근 (개발용)
- Chatbot Service: http://localhost:8001/docs
- Contract Analyzer: http://localhost:8002/docs

## 모니터링

### 헬스 체크
```bash
# 전체 시스템 상태
curl http://localhost:8000/health

# 개별 서비스 상태
curl http://localhost:8001/health  # Chatbot
curl http://localhost:8002/health  # Contract Analyzer
```

### 로그 확인
```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f main-api
docker-compose logs -f chatbot
docker-compose logs -f contract
```

## 개발 환경

### 서비스 간 통신 테스트
```bash
# 챗봇 서비스 직접 테스트
curl -X POST http://localhost:8001/chat/send \
  -H "Content-Type: application/json" \
  -d '{"message": "계약서 관련 질문입니다"}'

# 계약서 분석 서비스 직접 테스트
curl -X POST http://localhost:8002/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"file_path": "test.pdf"}'
```

### 데이터베이스 관리
- **Firestore**: Firebase Console에서 관리
- **ChromaDB**: `chatbot-docker/chroma_db/` 디렉토리에 저장
- **업로드 파일**: `contract_analyzer/uploads/` 디렉토리에 저장

## 배포

### 프로덕션 배포
```bash
# 프로덕션 환경 변수 설정
export ENVIRONMENT=production
export DEBUG=false

# Docker Compose 프로덕션 실행
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 문제 해결

### 공통 문제
1. **포트 충돌**: 8000, 8001, 8002 포트가 사용 중인지 확인
2. **환경 변수**: .env 파일 설정 확인
3. **Firebase 인증**: 서비스 계정 키 파일 경로 확인
4. **네트워크**: Docker 네트워크 `lawro-network` 상태 확인

### 서비스별 문제
- **Main API**: Firestore 연결 및 JWT 설정 확인
- **Chatbot**: UPSTAGE_API_KEY 및 ChromaDB 파일 확인
- **Contract**: AWS 자격증명 및 S3 버킷 설정 확인

## 라이선스
이 프로젝트는 MIT 라이선스 하에 있습니다.

