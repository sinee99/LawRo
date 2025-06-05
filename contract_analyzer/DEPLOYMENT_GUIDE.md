# Contract Analyzer 서버 배포 가이드

## 🎯 개요

Contract Analyzer를 독립된 서버에 배포하고 ChatBot Docker 서버와 HTTP POST 통신하는 방법을 설명합니다.

## 🏗️ 아키텍처

```
[Contract Analyzer Server]  ----HTTP POST----> [ChatBot Docker Server]
      (Port: 8000)                                  (16.176.26.197:8000)
```

## 📋 필수 준비사항

### 1. 서버 요구사항
- **OS**: Ubuntu 20.04+ / CentOS 7+ / Amazon Linux 2
- **CPU**: 2 Core 이상
- **RAM**: 4GB 이상 
- **Disk**: 20GB 이상
- **Network**: ChatBot 서버(16.176.26.197:8000)로 HTTP 통신 가능

### 2. 필수 서비스
- **Docker & Docker Compose**: 컨테이너 실행
- **AWS S3**: 계약서 이미지 저장
- **Upstage OCR API**: 문서 OCR 처리
- **OpenAI API**: 텍스트 분석 및 파싱

## 🚀 배포 방법

### 방법 1: Docker Compose 배포 (권장)

#### 1단계: 코드 다운로드
```bash
# 서버에 접속 후
cd /opt
sudo git clone https://github.com/your-repo/LawRo.git
cd LawRo/contract_analyzer
```

#### 2단계: 환경변수 설정
```bash
# 환경변수 파일 복사 및 수정
cp env.example .env
sudo nano .env
```

**`.env` 파일 설정:**
```bash
# ChatBot 서버 설정
CHATBOT_ENV=production
CHATBOT_URL=http://16.176.26.197:8000
CHATBOT_TIMEOUT=60
CHATBOT_MAX_RETRIES=3
CHATBOT_RETRY_DELAY=2.0

# AWS S3 설정 (실제 값으로 변경)
S3_BUCKET_NAME=your-contract-bucket
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-northeast-2

# API 키 설정 (실제 값으로 변경)
UPSTAGE_API_KEY=up_...
OPENAI_API_KEY=sk-...
```

#### 3단계: 서비스 실행
```bash
# Docker Compose로 실행
sudo docker-compose up -d

# 로그 확인
sudo docker-compose logs -f contract-analyzer
```

#### 4단계: 연결 테스트
```bash
# 서버 상태 확인
curl http://localhost:8000/

# ChatBot 연결 테스트
curl http://localhost:8000/api/chatbot-status
```

### 방법 2: 수동 Docker 배포

```bash
# 1. Docker 이미지 빌드
sudo docker build -t contract-analyzer:latest .

# 2. 컨테이너 실행
sudo docker run -d \
  --name contract-analyzer \
  --restart unless-stopped \
  -p 8000:8000 \
  -e CHATBOT_URL=http://16.176.26.197:8000 \
  -e S3_BUCKET_NAME=your-bucket \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  -e UPSTAGE_API_KEY=your-upstage-key \
  -e OPENAI_API_KEY=your-openai-key \
  -v ./tmp:/app/tmp \
  -v ./logs:/app/logs \
  contract-analyzer:latest

# 3. 상태 확인
sudo docker ps
sudo docker logs contract-analyzer
```

### 방법 3: 직접 Python 실행

```bash
# 1. Python 환경 설정
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 환경변수 설정
export CHATBOT_URL=http://16.176.26.197:8000
export S3_BUCKET_NAME=your-bucket
# ... 기타 환경변수

# 3. 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🔧 환경별 설정

### 개발 환경
```bash
CHATBOT_ENV=development
CHATBOT_URL=http://localhost:8001  # 로컬 ChatBot 서버
```

### 스테이징 환경
```bash
CHATBOT_ENV=staging
CHATBOT_URL=http://staging-chatbot.example.com:8000
```

### 운영 환경
```bash
CHATBOT_ENV=production
CHATBOT_URL=http://16.176.26.197:8000
```

## 🔍 연결 테스트

### 1. 기본 서버 상태 확인
```bash
curl -X GET http://your-server:8000/
```

### 2. ChatBot 연결 상태 확인
```bash
curl -X GET http://your-server:8000/api/chatbot-status
```

### 3. 통합 분석 테스트
```bash
curl -X POST http://your-server:8000/api/analyze-with-chatbot \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "contract_id": "test_contract",
    "use_chatbot": true,
    "user_language": "korean"
  }'
```

### 4. 포괄적 통합 테스트
```bash
cd /opt/LawRo/contract_analyzer
python test_integration.py
```

## 🚨 문제 해결

### ChatBot 연결 실패
```bash
# 1. 네트워크 연결 확인
ping 16.176.26.197
telnet 16.176.26.197 8000

# 2. ChatBot 서버 상태 확인
curl http://16.176.26.197:8000/health

# 3. 방화벽 확인
sudo ufw status
sudo iptables -L
```

### S3 연결 실패
```bash
# AWS 자격증명 확인
aws s3 ls s3://your-bucket-name
aws configure list
```

### OCR/LLM API 실패
```bash
# API 키 확인
echo $UPSTAGE_API_KEY
echo $OPENAI_API_KEY

# API 할당량 확인 (OpenAI 대시보드)
```

## 📊 모니터링

### 로그 확인
```bash
# Docker Compose 로그
sudo docker-compose logs -f

# 직접 실행 로그
tail -f logs/contract_analyzer.log
```

### 성능 모니터링
```bash
# 컨테이너 리소스 사용량
sudo docker stats contract-analyzer

# 시스템 리소스
htop
df -h
```

### Health Check
```bash
# Docker health check
sudo docker inspect contract-analyzer | grep Health -A 10

# 수동 health check
curl http://localhost:8000/api/chatbot-status
```

## 🔒 보안 고려사항

### 환경변수 보안
```bash
# .env 파일 권한 설정
chmod 600 .env
sudo chown root:root .env
```

### 방화벽 설정
```bash
# 필요한 포트만 개방
sudo ufw allow 8000/tcp
sudo ufw enable
```

### API 키 관리
- 환경변수로만 관리, 코드에 하드코딩 금지
- 정기적인 API 키 로테이션
- AWS IAM 최소 권한 원칙 적용

## 🔄 업데이트 방법

### Docker Compose 업데이트
```bash
cd /opt/LawRo/contract_analyzer
sudo git pull
sudo docker-compose down
sudo docker-compose build --no-cache
sudo docker-compose up -d
```

### 무중단 배포
```bash
# Blue-Green 배포 예시
sudo docker-compose -f docker-compose.blue.yml up -d
# 테스트 후
sudo docker-compose -f docker-compose.green.yml down
```

## 📞 지원

문제 발생 시:
1. **로그 확인**: `sudo docker-compose logs -f`
2. **연결 테스트**: `python test_integration.py`
3. **네트워크 확인**: `ping 16.176.26.197`
4. **API 키 확인**: 환경변수 및 할당량 점검

---

## ✅ 배포 완료 체크리스트

- [ ] 서버 요구사항 확인
- [ ] Docker & Docker Compose 설치
- [ ] 환경변수 설정 (`.env` 파일)
- [ ] AWS S3 연결 테스트
- [ ] API 키 설정 및 테스트
- [ ] ChatBot 서버 연결 확인
- [ ] Docker Compose 실행
- [ ] 통합 테스트 실행
- [ ] 모니터링 설정
- [ ] 보안 설정 확인

🎉 **배포 완료! Contract Analyzer가 ChatBot과 HTTP POST 통신으로 연결되었습니다!** 