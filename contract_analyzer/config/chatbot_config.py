"""
ChatBot 서버 연결 설정
"""
import os
from typing import Dict, Any

class ChatBotConfig:
    """ChatBot 서버 연결 설정"""
    
    # 환경별 ChatBot 서버 URL 설정
    CHATBOT_SERVERS = {
        "development": "http://localhost:8001",  # 로컬 개발
        "docker": "http://chatbot:8000",  # Docker 컨테이너 간 통신
        "aws": "http://localhost:8000",  # AWS ECS Task 내 컨테이너 간 통신
        "staging": "http://staging-chatbot.example.com:8000",  # 스테이징
        "production": "http://16.176.26.197:8000"  # 운영 서버
    }
    
    def __init__(self):
        # 환경변수에서 설정 읽기
        self.environment = os.getenv("CHATBOT_ENV", "aws")
        self.custom_url = os.getenv("CHATBOT_URL")
        self.timeout = int(os.getenv("CHATBOT_TIMEOUT", "60"))
        self.max_retries = int(os.getenv("CHATBOT_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("CHATBOT_RETRY_DELAY", "2.0"))
        
    @property
    def base_url(self) -> str:
        """ChatBot 서버 기본 URL"""
        if self.custom_url:
            return self.custom_url.rstrip('/')
        
        return self.CHATBOT_SERVERS.get(self.environment, self.CHATBOT_SERVERS["aws"])
    
    @property 
    def endpoints(self) -> Dict[str, str]:
        """ChatBot API 엔드포인트"""
        base = self.base_url
        return {
            "health": f"{base}/health",
            "create_session": f"{base}/create_session", 
            "chat": f"{base}/chat",
            "history": f"{base}/chat/history",
            "stats": f"{base}/stats"
        }
    
    def get_connection_config(self) -> Dict[str, Any]:
        """연결 설정 반환"""
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "environment": self.environment
        }
    
    def validate_config(self) -> bool:
        """설정 유효성 검사"""
        try:
            import requests
            response = requests.get(self.endpoints["health"], timeout=10)
            return response.status_code == 200
        except:
            return False

# 전역 설정 인스턴스
chatbot_config = ChatBotConfig()

# 편의 함수들
def get_chatbot_url() -> str:
    """ChatBot 서버 URL 반환"""
    return chatbot_config.base_url

def get_chatbot_endpoints() -> Dict[str, str]:
    """ChatBot API 엔드포인트 반환"""
    return chatbot_config.endpoints

def is_chatbot_available() -> bool:
    """ChatBot 서버 연결 가능 여부 확인"""
    return chatbot_config.validate_config()

if __name__ == "__main__":
    # 설정 테스트
    print("ChatBot 설정 정보:")
    print(f"  환경: {chatbot_config.environment}")
    print(f"  서버 URL: {chatbot_config.base_url}")
    print(f"  타임아웃: {chatbot_config.timeout}초")
    print(f"  최대 재시도: {chatbot_config.max_retries}회")
    
    print("\nAPI 엔드포인트:")
    for name, url in chatbot_config.endpoints.items():
        print(f"  {name}: {url}")
    
    print(f"\n연결 테스트: {'✅ 성공' if is_chatbot_available() else '❌ 실패'}") 