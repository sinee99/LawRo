# 🤖 LawRo 챗봇 서비스 Docker 배포

## 📋 개요

이 디렉토리는 **LawRo 챗봇 서비스만**을 위한 독립적인 Docker 환경입니다.
`backend/services/chat_service.py`의 핵심 기능과 FastAPI 통신만 포함되어 있습니다.

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 환경 변수 파일 생성
cp env.example .env

# .env 파일에서 API 키 설정
nano .env
# UPSTAGE_API_KEY=up_XXXXXXXXXXXXXXXX 입력
```

### 2. 배포 실행
```bash
# 실행 권한 부여
chmod +x deploy-aws.sh

# AWS 서버에 배포
./deploy-aws.sh
```

## 📁 파일 구조

```
chatbot-service/
├── Dockerfile              # Docker 이미지 빌드 설정
├── requirements.txt         # Python 의존성 패키지
├── main.py                 # FastAPI 메인 애플리케이션
├── chat_service.py         # 챗봇 핵심 로직
├── models.py               # Pydantic 데이터 모델
├── env.example             # 환경 변수 예제
├── deploy-aws.sh           # AWS 배포 스크립트
└── README.md              # 이 파일
```

## 🔧 API 엔드포인트

배포 완료 후 다음 엔드포인트들을 사용할 수 있습니다:

### 📡 기본 정보
- `GET /` - API 정보
- `GET /health` - 서비스 상태 확인
- `GET /docs` - Swagger API 문서

### 💬 채팅 기능
- `POST /chat/send` - 메시지 전송
- `GET /chat/history/{session_id}` - 채팅 히스토리 조회
- `POST /chat/new-session` - 새 세션 생성
- `DELETE /chat/history/{session_id}` - 히스토리 삭제

## 📝 사용 예시

### 채팅 메시지 전송
```bash
curl -X POST "http://YOUR_SERVER_IP:8000/chat/send" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "근로계약서에서 최저임금 위반이 있나요?",
    "session_id": "user123"
  }'
```

### 응답 예시
```json
{
  "success": true,
  "message": "네, 근로계약서의 임금 조항을 검토하여 최저임금법 위반 여부를 확인해드릴 수 있습니다...",
  "chat_history": [
    {
      "role": "user",
      "content": "근로계약서에서 최저임금 위반이 있나요?",
      "timestamp": "2024-01-01T12:00:00"
    },
    {
      "role": "assistant", 
      "content": "네, 근로계약서의 임금 조항을 검토하여...",
      "timestamp": "2024-01-01T12:00:01"
    }
  ],
  "processing_time": 2.5
}
```

## ⚙️ 환경 변수

| 변수명 | 설명 | 필수 | 기본값 |
|--------|------|------|--------|
| `UPSTAGE_API_KEY` | Upstage API 키 | ✅ | - |
| `HOST` | 서버 호스트 | ❌ | 0.0.0.0 |
| `PORT` | 서버 포트 | ❌ | 8000 |
| `LOG_LEVEL` | 로그 레벨 | ❌ | INFO |

## 🔧 관리 명령어

### Docker 컨테이너 관리
```bash
# 컨테이너 상태 확인
sudo docker ps

# 로그 확인
sudo docker logs lawro-chatbot

# 컨테이너 재시작
sudo docker restart lawro-chatbot

# 컨테이너 중지
sudo docker stop lawro-chatbot

# 컨테이너 삭제
sudo docker rm lawro-chatbot
```

### 서비스 테스트
```bash
# 헬스체크
curl http://localhost:8000/health

# API 문서 접속
curl http://localhost:8000/docs
```

## 🛠️ 문제 해결

### 1. 컨테이너가 시작되지 않는 경우
```bash
# 로그 확인
sudo docker logs lawro-chatbot

# 환경 변수 확인
cat .env | grep UPSTAGE_API_KEY
```

### 2. API 키 오류
```bash
# .env 파일 수정
nano .env
# UPSTAGE_API_KEY 값 확인/수정

# 컨테이너 재시작
sudo docker restart lawro-chatbot
```

### 3. 포트 충돌
```bash
# 8000 포트 사용 중인 프로세스 확인
sudo netstat -tulpn | grep :8000

# 다른 포트로 실행
sudo docker run -d --name lawro-chatbot -p 8080:8000 --env-file .env lawro-chatbot:latest
```

### 4. 메모리 부족
```bash
# 시스템 리소스 확인
free -h
df -h

# 메모리 제한으로 실행
sudo docker run -d --name lawro-chatbot -p 8000:8000 --memory="1g" --env-file .env lawro-chatbot:latest
```

## 🔒 보안 고려사항

### AWS 보안 그룹 설정
1. EC2 인스턴스의 보안 그룹에서 8000 포트 개방
2. 필요한 IP만 허용하도록 설정

### SSL/HTTPS 설정 (권장)
```bash
# Nginx와 Let's Encrypt를 사용한 HTTPS 설정
sudo apt install nginx certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 성능 최적화

### 프로덕션 설정
```bash
# 리소스 제한으로 실행
sudo docker run -d \
  --name lawro-chatbot \
  --restart unless-stopped \
  -p 8000:8000 \
  --memory="2g" \
  --cpus="1.0" \
  --env-file .env \
  lawro-chatbot:latest
```

### 로그 로테이션
```bash
# 로그 크기 제한
sudo docker run -d \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  --name lawro-chatbot \
  -p 8000:8000 \
  --env-file .env \
  lawro-chatbot:latest
```

## 🔄 업데이트 방법

```bash
# 새 코드로 업데이트
git pull origin main

# 기존 컨테이너 중지 및 제거
sudo docker stop lawro-chatbot
sudo docker rm lawro-chatbot

# 새 이미지 빌드 및 실행
sudo docker build -t lawro-chatbot:latest .
./deploy-aws.sh
```

---

## 📞 지원

문제가 발생하면 다음을 확인해주세요:

1. **로그 확인**: `sudo docker logs lawro-chatbot`
2. **환경 변수**: `.env` 파일의 API 키 확인
3. **네트워크**: AWS 보안 그룹 포트 8000 개방
4. **리소스**: 서버의 메모리/CPU 사용량 확인

이 가이드로도 해결되지 않는 문제가 있다면 GitHub Issues에 문의해주세요! 🙌 