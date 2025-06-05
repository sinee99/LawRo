# 🚀 LawRo 챗봇 EC2 배포 가이드

## 📋 사전 준비사항

### 1. AWS EC2 인스턴스 설정
- **인스턴스 타입**: t3.medium 이상 권장 (메모리 4GB+)
- **OS**: Ubuntu 20.04 LTS 또는 Amazon Linux 2
- **스토리지**: 20GB 이상
- **보안 그룹**: 다음 포트 열기
  - SSH (22)
  - HTTP (80) - 선택사항
  - Custom TCP (8000) - **필수**

### 2. 로컬에서 파일 준비
```bash
# .env 파일 생성
cp env.example .env

# .env 파일에서 본인의 UPSTAGE_API_KEY 설정
UPSTAGE_API_KEY=up_여기에_본인의_API_키_입력
```

## 🚀 배포 단계

### 1단계: EC2 인스턴스 접속
```bash
# SSH로 EC2 접속
ssh -i your-key.pem ubuntu@your-ec2-ip
# 또는 Amazon Linux의 경우
ssh -i your-key.pem ec2-user@your-ec2-ip
```

### 2단계: 시스템 업데이트
```bash
# Ubuntu
sudo apt update && sudo apt upgrade -y

# Amazon Linux
sudo yum update -y
```

### 3단계: Git 설치 및 프로젝트 클론
```bash
# Git 설치
sudo apt install git -y  # Ubuntu
# sudo yum install git -y  # Amazon Linux

# 프로젝트 클론 (GitHub에 업로드된 경우)
git clone https://github.com/your-username/LawRo.git
cd LawRo/chatbot-docker

# 또는 파일 직접 업로드 (scp 사용)
# scp -i your-key.pem -r ./chatbot-docker ubuntu@your-ec2-ip:~/
```

### 4단계: 환경 설정
```bash
# .env 파일 생성 및 편집
cp env.example .env
nano .env  # 또는 vim .env

# API 키 설정 확인
cat .env
```

### 5단계: 배포 스크립트 실행
```bash
# 실행 권한 부여
chmod +x deploy-aws.sh

# 배포 실행
./deploy-aws.sh
```

## 🔧 수동 배포 방법 (스크립트 실행이 안되는 경우)

### Docker 수동 설치
```bash
# Ubuntu
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker $USER

# Amazon Linux
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker $USER

# 새 그룹 권한 적용
newgrp docker
```

### 수동 배포
```bash
# Docker 이미지 빌드
docker build -t lawro-chatbot:latest .

# 컨테이너 실행
docker run -d \
    --name lawro-chatbot \
    --restart unless-stopped \
    -p 8000:8000 \
    --env-file .env \
    -v $(pwd)/chroma_db:/app/chroma_db \
    lawro-chatbot:latest
```

## ✅ 배포 확인

### 1. 서비스 상태 확인
```bash
# 컨테이너 상태 확인
docker ps

# 로그 확인
docker logs lawro-chatbot

# 헬스체크 (EC2 내부에서)
curl http://localhost:8000/health
```

### 2. 외부 접속 테스트
```bash
# 외부 IP 확인
curl ifconfig.me

# 브라우저에서 접속
# http://your-ec2-ip:8000/docs
# http://your-ec2-ip:8000/health
```

### 3. API 테스트
```bash
# curl로 테스트
curl -X POST "http://your-ec2-ip:8000/chat/send" \
     -H "Content-Type: application/json" \
     -d '{"message": "근로계약서 분석 도와주세요", "user_language": "korean"}'
```

## 🛠️ 관리 명령어

```bash
# 서비스 상태 확인
docker ps

# 로그 확인
docker logs lawro-chatbot

# 컨테이너 재시작
docker restart lawro-chatbot

# 컨테이너 중지
docker stop lawro-chatbot

# 컨테이너 삭제 (중지 후)
docker rm lawro-chatbot

# 이미지 재빌드 (코드 변경 시)
docker build -t lawro-chatbot:latest .
docker stop lawro-chatbot
docker rm lawro-chatbot
docker run -d --name lawro-chatbot --restart unless-stopped -p 8000:8000 --env-file .env -v $(pwd)/chroma_db:/app/chroma_db lawro-chatbot:latest
```

## 🔒 보안 설정

### 1. 방화벽 설정 (선택사항)
```bash
# Ubuntu UFW
sudo ufw allow ssh
sudo ufw allow 8000
sudo ufw enable

# Amazon Linux iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo service iptables save
```

### 2. HTTPS 설정 (고급)
- Let's Encrypt SSL 인증서 적용
- Nginx 리버스 프록시 설정
- 도메인 연결

## 🔍 문제 해결

### 포트 접속 안되는 경우
1. AWS 보안 그룹에서 8000 포트 열렸는지 확인
2. EC2 인스턴스 방화벽 설정 확인
3. 컨테이너가 정상 실행되고 있는지 확인: `docker ps`

### API 키 오류
1. .env 파일에 올바른 UPSTAGE_API_KEY 설정 확인
2. 컨테이너 재시작: `docker restart lawro-chatbot`

### 메모리 부족
1. 더 큰 인스턴스 타입으로 변경 (t3.medium → t3.large)
2. 스왑 파일 생성

## 📊 모니터링

### 리소스 사용량 확인
```bash
# 시스템 리소스
htop
df -h

# Docker 컨테이너 리소스
docker stats lawro-chatbot
```

### 로그 모니터링
```bash
# 실시간 로그
docker logs -f lawro-chatbot

# 최근 100줄
docker logs --tail 100 lawro-chatbot
```

## 🎯 성공 지표

배포가 성공적으로 완료되면:
- ✅ `http://your-ec2-ip:8000/health` 에서 상태 확인
- ✅ `http://your-ec2-ip:8000/docs` 에서 API 문서 접근
- ✅ 한국어, 영어, 베트남어 등 다국어 응답 생성
- ✅ 컨테이너가 자동 재시작되도록 설정됨

---

**🔥 팁**: EC2 요금 절약을 위해 개발/테스트 후에는 인스턴스를 중지해두세요! 