#!/bin/bash

# AWS 서버 배포 스크립트 for LawRo 챗봇 서비스

echo "🚀 LawRo 챗봇 서비스 AWS 배포 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 환경 변수 확인
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env 파일이 없습니다.${NC}"
    echo "env.example을 참고하여 .env 파일을 생성해주세요:"
    echo "cp env.example .env"
    echo "그 후 .env 파일에서 UPSTAGE_API_KEY를 설정해주세요."
    exit 1
fi

# Docker 설치 여부 확인
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️ Docker가 설치되지 않았습니다. 설치를 시작합니다...${NC}"
    
    # Docker 설치 (Ubuntu/Amazon Linux)
    if [ -f /etc/ubuntu-release ] || [ -f /etc/debian_version ]; then
        # Ubuntu/Debian
        sudo apt update
        sudo apt install -y docker.io
        sudo systemctl start docker
        sudo systemctl enable docker
    elif [ -f /etc/amazon-linux-release ] || [ -f /etc/system-release ]; then
        # Amazon Linux
        sudo yum update -y
        sudo yum install -y docker
        sudo systemctl start docker
        sudo systemctl enable docker
    else
        echo -e "${RED}❌ 지원하지 않는 OS입니다. Docker를 수동으로 설치해주세요.${NC}"
        exit 1
    fi
    
    # 현재 사용자를 docker 그룹에 추가
    sudo usermod -a -G docker $USER
    echo -e "${YELLOW}⚠️ 로그아웃 후 다시 로그인하거나 다음 명령을 실행하세요:${NC}"
    echo "newgrp docker"
fi

# 기존 컨테이너 중지 및 제거
echo -e "${YELLOW}🛑 기존 컨테이너 정리 중...${NC}"
sudo docker stop lawro-chatbot 2>/dev/null || true
sudo docker rm lawro-chatbot 2>/dev/null || true

# 이미지 빌드
echo -e "${YELLOW}🔨 Docker 이미지 빌드 중...${NC}"
sudo docker build -t lawro-chatbot:latest .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker 이미지 빌드에 실패했습니다.${NC}"
    exit 1
fi

# 컨테이너 실행
echo -e "${YELLOW}🚀 컨테이너 실행 중...${NC}"
sudo docker run -d \
    --name lawro-chatbot \
    --restart unless-stopped \
    -p 8000:8000 \
    --env-file .env \
    -v $(pwd)/storage:/app/storage \
    lawro-chatbot:latest

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 컨테이너 실행에 실패했습니다.${NC}"
    exit 1
fi

# 헬스체크
echo -e "${YELLOW}🔍 서비스 상태 확인 중...${NC}"
sleep 5

# 최대 30초 동안 헬스체크 시도
for i in {1..6}; do
    if curl -f http://localhost:8000/health &>/dev/null; then
        echo -e "${GREEN}✅ 서비스가 정상적으로 시작되었습니다!${NC}"
        break
    else
        echo "헬스체크 시도 $i/6..."
        sleep 5
    fi
    
    if [ $i -eq 6 ]; then
        echo -e "${RED}❌ 서비스 시작에 실패했습니다. 로그를 확인해주세요:${NC}"
        echo "sudo docker logs lawro-chatbot"
        exit 1
    fi
done

echo ""
echo -e "${GREEN}🎉 배포가 완료되었습니다!${NC}"
echo ""
echo "📊 서비스 정보:"
echo "  🌐 API 문서: http://$(curl -s ifconfig.me):8000/docs"
echo "  🏥 헬스체크: http://$(curl -s ifconfig.me):8000/health"
echo "  💬 채팅 엔드포인트: http://$(curl -s ifconfig.me):8000/chat/send"
echo ""
echo "📝 관리 명령어:"
echo "  상태 확인: sudo docker ps"
echo "  로그 확인: sudo docker logs lawro-chatbot"
echo "  중지: sudo docker stop lawro-chatbot"
echo "  재시작: sudo docker restart lawro-chatbot"
echo "  완전 삭제: sudo docker stop lawro-chatbot && sudo docker rm lawro-chatbot"
echo ""
echo -e "${GREEN}✅ AWS 보안 그룹에서 8000 포트를 열어주세요!${NC}" 