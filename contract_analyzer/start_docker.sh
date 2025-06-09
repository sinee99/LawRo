#!/bin/bash

# Docker 환경에서 LawRo Contract Analyzer 시작 스크립트

echo "🚀 LawRo Contract Analyzer Docker 환경 시작"

# .env 파일 확인
if [ ! -f .env ]; then
    echo "⚠️ .env 파일이 없습니다. env.example을 참고하여 .env 파일을 생성해주세요."
    echo "📝 cp env.example .env"
    exit 1
fi

# Docker 및 docker-compose 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose가 설치되지 않았습니다."
    exit 1
fi

# 기존 컨테이너 중지 및 제거
echo "🧹 기존 컨테이너 정리..."
docker-compose down

# 이미지 빌드 및 컨테이너 시작
echo "🔨 Docker 이미지 빌드 및 컨테이너 시작..."
docker-compose up --build -d

# 서비스 상태 확인
echo "⏳ 서비스 시작 대기 중..."
sleep 10

echo "🔍 서비스 상태 확인..."
docker-compose ps

echo ""
echo "✅ LawRo Contract Analyzer가 Docker 환경에서 실행 중입니다!"
echo "📍 Contract Analyzer: http://localhost:8000"
echo "📍 ChatBot: http://localhost:8001"
echo ""
echo "📊 로그 확인: docker-compose logs -f"
echo "🛑 중지: docker-compose down" 