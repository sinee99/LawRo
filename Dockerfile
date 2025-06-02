FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY backend/ ./backend/
COPY chatbot/ ./chatbot/
COPY law_data/ ./law_data/

# 벡터 데이터베이스 생성
WORKDIR /app/chatbot
RUN python chroma_db_embeddings.py

WORKDIR /app/backend

# 포트 노출
EXPOSE 8000

# 앱 실행
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 