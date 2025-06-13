FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 종속성 파일 복사 (requirements.txt가 있다면)
COPY requirements.txt* ./

# Python 패키지 설치 (requirements.txt가 있는 경우)
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# 추가 패키지 설치 (기본적으로 필요한 것들)
RUN pip install --no-cache-dir fastapi uvicorn python-multipart python-dotenv

# 애플리케이션 코드 복사
COPY . .

# 업로드 및 임시 디렉토리 생성
RUN mkdir -p /app/uploads /app/temp

# 포트 8002 노출
EXPOSE 8002

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"] 