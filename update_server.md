# 🔄 LawRo 서버 업데이트 가이드

## 📋 변경사항
- 커스텀 프롬프트에서 `{context}` 변수 자동 추가 기능 구현
- 커스텀 프롬프트 오류 "Prompt must accept context as an input variable" 해결

## 🚀 EC2에서 서버 업데이트 방법

### 1단계: EC2 접속
```bash
ssh -i your-key.pem ec2-user@16.176.26.197
cd ~/chatbot-docker
```

### 2단계: 수정된 파일 업로드
**로컬에서 수정된 chat_service.py 파일을 업로드:**

```bash
# 로컬에서 실행 (Windows)
scp -i C:\path\to\your-key.pem .\chatbot-docker\chat_service.py ec2-user@16.176.26.197:~/chatbot-docker/
```

### 3단계: 컨테이너 재시작
```bash
# 기존 컨테이너 중지 및 제거
sudo docker stop lawro-chatbot
sudo docker rm lawro-chatbot

# 새 이미지 빌드
sudo docker build -t lawro-chatbot:latest .

# 컨테이너 재시작
sudo docker run -d \
    --name lawro-chatbot \
    --restart unless-stopped \
    -p 8000:8000 \
    --env-file .env \
    -v $(pwd)/chroma_db:/app/chroma_db \
    lawro-chatbot:latest
```

### 4단계: 서비스 확인
```bash
# 컨테이너 상태 확인
sudo docker ps

# 로그 확인
sudo docker logs lawro-chatbot

# 헬스체크
curl http://localhost:8000/health
```

## ✅ 테스트 방법

업데이트 완료 후 커스텀 프롬프트 테스트:

```bash
# 로컬에서 테스트
python test_lawro_api.py
```

또는 curl로 직접 테스트:

```bash
curl -X POST "http://16.176.26.197:8000/chat/send" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "최저임금이 뭐예요?",
       "user_language": "korean",
       "custom_prompt": "간단하고 명확하게 20자 이내로 답변해주세요."
     }'
```

## 🔍 문제 해결

만약 여전히 오류가 발생한다면:

1. **Docker 로그 확인:**
   ```bash
   sudo docker logs lawro-chatbot --tail 50
   ```

2. **컨테이너 재빌드:**
   ```bash
   sudo docker system prune -f
   sudo docker build --no-cache -t lawro-chatbot:latest .
   ```

3. **환경변수 확인:**
   ```bash
   cat .env
   ``` 