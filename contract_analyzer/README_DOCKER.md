# LawRo Contract Analyzer - Docker 환경 가이드

## 🐳 Docker 환경 개요

이 프로젝트는 Docker Compose를 사용하여 두 개의 주요 서비스를 컨테이너로 실행합니다:

- **contract-analyzer**: 계약서 분석 API 서버 (포트: 8000)
- **chatbot**: 법률 상담 ChatBot 서버 (포트: 8001)

## 📋 사전 요구사항

- Docker 20.10 이상
- Docker Compose 2.0 이상
- 최소 4GB RAM
- 최소 2GB 여유 디스크 공간

## 🚀 빠른 시작

### 1. 환경변수 설정

```bash
# env.example을 복사하여 .env 파일 생성
cp env.example .env

# .env 파일을 편집하여 필요한 API 키와 설정 입력
nano .env
```

필수 환경변수:
```env
UPSTAGE_API_KEY=your_upstage_api_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=ap-northeast-2
```

### 2. Docker 컨테이너 실행

```bash
# 자동 스크립트 사용 (권장)
chmod +x start_docker.sh
./start_docker.sh

# 또는 수동 실행
docker-compose up --build -d
```

### 3. 서비스 확인

```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f
```

### 4. 통신 테스트

```bash
# Docker 환경에서 컨테이너 간 통신 테스트
python test_docker_communication.py
```

## 📡 API 엔드포인트

### Contract Analyzer (포트: 8000)
- `GET /` - 서비스 상태 확인
- `GET /health` - 헬스체크
- `POST /api/upload` - 계약서 이미지 업로드
- `POST /api/analyze-with-chatbot` - ChatBot 통합 분석

### ChatBot (포트: 8001)
- `GET /health` - 헬스체크
- `POST /create_session` - 세션 생성
- `POST /chat` - 채팅 요청

## 🔧 개발 환경 설정

### 로컬 개발을 위한 설정

```bash
# 개발 모드로 실행 (코드 변경 시 자동 재시작)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### 디버깅

```bash
# 특정 컨테이너 로그 확인
docker-compose logs -f contract-analyzer
docker-compose logs -f chatbot

# 컨테이너 내부 접근
docker-compose exec contract-analyzer bash
docker-compose exec chatbot bash
```

## 🌐 네트워크 구성

컨테이너들은 `lawro-network` 브리지 네트워크를 통해 통신합니다:

- `contract-analyzer` → `chatbot:8000` (내부 통신)
- 외부 접근: `localhost:8000`, `localhost:8001`

## 📊 모니터링

### 헬스체크

```bash
# Contract Analyzer 헬스체크
curl http://localhost:8000/health

# ChatBot 헬스체크  
curl http://localhost:8001/health
```

### 리소스 사용량 확인

```bash
# 컨테이너 리소스 사용량
docker stats

# 디스크 사용량
docker system df
```

## 🛠️ 문제 해결

### 일반적인 문제

1. **포트 충돌**
   ```bash
   # 포트 사용 확인
   netstat -tulpn | grep :8000
   netstat -tulpn | grep :8001
   ```

2. **메모리 부족**
   ```bash
   # Docker 메모리 사용량 확인
   docker system prune -f
   docker volume prune -f
   ```

3. **컨테이너 간 통신 실패**
   ```bash
   # 네트워크 상태 확인
   docker network ls
   docker network inspect lawro-network
   ```

### 로그 레벨 조정

환경변수를 통해 로그 레벨을 조정할 수 있습니다:

```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## 🔄 업데이트 및 배포

### 이미지 업데이트

```bash
# 새 이미지 빌드 및 배포
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 백업

```bash
# 데이터 볼륨 백업
docker run --rm -v contract_analyzer_chroma_db:/data -v $(pwd):/backup alpine tar czf /backup/chroma_db_backup.tar.gz /data
```

## 📈 성능 최적화

### 리소스 제한 설정

`docker-compose.yml`에서 리소스 제한을 설정할 수 있습니다:

```yaml
services:
  contract-analyzer:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

## 🔒 보안 고려사항

1. **환경변수 보안**
   - `.env` 파일을 Git에 커밋하지 마세요
   - 프로덕션에서는 Docker Secrets 사용 권장

2. **네트워크 보안**
   - 필요한 포트만 외부에 노출
   - 프로덕션에서는 HTTPS 사용

3. **이미지 보안**
   - 정기적인 베이스 이미지 업데이트
   - 취약점 스캔 수행

## 📞 지원

문제가 발생하면 다음을 확인해주세요:

1. `docker-compose logs -f`로 전체 로그 확인
2. `python test_docker_communication.py`로 통신 테스트
3. 환경변수 설정 재확인
4. Docker 및 Docker Compose 버전 확인

---

**참고**: 이 문서는 Docker 환경에서의 실행을 다룹니다. 로컬 개발 환경은 `README_LOCAL.md`를 참조하세요. 