import requests
import json
from typing import Optional, Dict, List, Tuple
import time
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ChatMessage:
    """채팅 메시지 클래스"""
    role: str
    content: str
    timestamp: Optional[str] = None

@dataclass
class ChatResponse:
    """채팅 응답 클래스"""
    response: str
    chat_history: List[ChatMessage]
    processing_time: float
    success: bool = True
    error: Optional[str] = None

class LawRoClient:
    """LawRo 챗봇 서버 클라이언트"""
    
    def __init__(self, base_url: str = "http://16.176.26.197:8000", timeout: int = 30):
        """
        클라이언트 초기화
        
        Args:
            base_url: LawRo 서버 주소
            timeout: 요청 타임아웃 (초)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session_id = None
        
    def health_check(self) -> Dict:
        """서버 상태 확인"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "data": response.json(),
                    "success": True
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "success": False
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "success": False
            }
    
    def create_session(self) -> Optional[str]:
        """새로운 채팅 세션 생성"""
        try:
            response = requests.post(f"{self.base_url}/create_session", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                session_id = data.get('session_id')
                self.session_id = session_id  # 자동으로 현재 세션 설정
                return session_id
            else:
                print(f"❌ 세션 생성 실패: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 세션 생성 오류: {str(e)}")
            return None
    
    def send_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        user_language: str = "korean",
        context: Optional[str] = None
    ) -> ChatResponse:
        """
        메시지 전송
        
        Args:
            message: 사용자 메시지
            session_id: 세션 ID (None이면 자동 생성)
            custom_prompt: 커스텀 프롬프트
            user_language: 응답 언어
            context: 문맥 정보
        """
        # 세션 ID가 없으면 자동 생성
        if not session_id and not self.session_id:
            session_id = self.create_session()
        elif not session_id:
            session_id = self.session_id
            
        if not session_id:
            return ChatResponse(
                response="",
                chat_history=[],
                processing_time=0,
                success=False,
                error="세션 생성에 실패했습니다."
            )
        
        payload = {
            "message": message,
            "session_id": session_id,
            "user_language": user_language
        }
        
        if custom_prompt:
            payload["custom_prompt"] = custom_prompt
        if context:
            payload["context"] = context
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=self.timeout
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # 채팅 히스토리 변환
                chat_history = []
                for msg in data.get('chat_history', []):
                    chat_history.append(ChatMessage(
                        role=msg.get('role', ''),
                        content=msg.get('content', ''),
                        timestamp=msg.get('timestamp')
                    ))
                
                return ChatResponse(
                    response=data.get('response', ''),
                    chat_history=chat_history,
                    processing_time=processing_time,
                    success=True
                )
            else:
                return ChatResponse(
                    response="",
                    chat_history=[],
                    processing_time=processing_time,
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return ChatResponse(
                response="",
                chat_history=[],
                processing_time=0,
                success=False,
                error=str(e)
            )
    
    def get_chat_history(self, session_id: Optional[str] = None) -> List[ChatMessage]:
        """채팅 히스토리 조회"""
        if not session_id:
            session_id = self.session_id
            
        if not session_id:
            print("❌ 세션 ID가 없습니다.")
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/chat/history/{session_id}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                chat_history = []
                
                for msg in data.get('chat_history', []):
                    chat_history.append(ChatMessage(
                        role=msg.get('role', ''),
                        content=msg.get('content', ''),
                        timestamp=msg.get('timestamp')
                    ))
                
                return chat_history
            else:
                print(f"❌ 히스토리 조회 실패: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 히스토리 조회 오류: {str(e)}")
            return []
    
    def clear_chat_history(self, session_id: Optional[str] = None) -> bool:
        """채팅 히스토리 삭제"""
        if not session_id:
            session_id = self.session_id
            
        if not session_id:
            print("❌ 세션 ID가 없습니다.")
            return False
        
        try:
            response = requests.delete(
                f"{self.base_url}/chat/history/{session_id}",
                timeout=self.timeout
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ 히스토리 삭제 오류: {str(e)}")
            return False
    
    def get_server_stats(self) -> Dict:
        """서버 통계 정보 조회"""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def chat_conversation(
        self,
        messages: List[str],
        custom_prompt: Optional[str] = None,
        user_language: str = "korean",
        delay_between_messages: float = 1.0
    ) -> List[ChatResponse]:
        """
        연속 대화 수행
        
        Args:
            messages: 메시지 리스트
            custom_prompt: 커스텀 프롬프트 (첫 번째 메시지에만 적용)
            user_language: 응답 언어
            delay_between_messages: 메시지 간 지연 시간 (초)
        """
        # 새 세션 생성
        session_id = self.create_session()
        if not session_id:
            return []
        
        responses = []
        
        for i, message in enumerate(messages):
            print(f"📤 메시지 {i+1}/{len(messages)}: {message[:50]}...")
            
            # 첫 번째 메시지에만 커스텀 프롬프트 적용
            prompt = custom_prompt if i == 0 else None
            
            response = self.send_message(
                message=message,
                session_id=session_id,
                custom_prompt=prompt,
                user_language=user_language
            )
            
            responses.append(response)
            
            if response.success:
                print(f"✅ 응답 받음 (길이: {len(response.response)})")
            else:
                print(f"❌ 응답 실패: {response.error}")
            
            # 마지막 메시지가 아니면 지연
            if i < len(messages) - 1:
                time.sleep(delay_between_messages)
        
        return responses

# 편의 함수들
def quick_chat(message: str, server_url: str = "http://16.176.26.197:8000") -> str:
    """빠른 일회성 채팅"""
    client = LawRoClient(server_url)
    response = client.send_message(message)
    return response.response if response.success else f"오류: {response.error}"

def analyze_contract_with_custom_prompt(
    contract_text: str,
    analysis_prompt: str,
    server_url: str = "http://16.176.26.197:8000"
) -> str:
    """커스텀 프롬프트로 계약서 분석"""
    client = LawRoClient(server_url)
    response = client.send_message(
        message=contract_text,
        custom_prompt=analysis_prompt
    )
    return response.response if response.success else f"오류: {response.error}"

def multi_language_chat(
    message: str,
    language: str = "english",
    server_url: str = "http://16.176.26.197:8000"
) -> str:
    """다국어 채팅"""
    client = LawRoClient(server_url)
    response = client.send_message(message, user_language=language)
    return response.response if response.success else f"오류: {response.error}"

# 사용 예제
if __name__ == "__main__":
    # 기본 사용법
    print("🤖 LawRo 클라이언트 테스트")
    print("=" * 50)
    
    # 1. 클라이언트 생성 및 서버 상태 확인
    client = LawRoClient()
    
    health = client.health_check()
    if health["success"]:
        print("✅ 서버 상태 정상")
    else:
        print(f"❌ 서버 상태 오류: {health['error']}")
        exit(1)
    
    # 2. 간단한 질문
    print(f"\n📋 간단한 질문 테스트")
    response = client.send_message("근로계약서란 무엇인가요?")
    if response.success:
        print(f"응답: {response.response[:100]}...")
    else:
        print(f"오류: {response.error}")
    
    # 3. 커스텀 프롬프트 사용
    print(f"\n📋 커스텀 프롬프트 테스트")
    custom_prompt = "JSON 형태로 답변해주세요. 'summary', 'key_points', 'recommendation' 필드를 포함해주세요."
    
    response = client.send_message(
        message="외국인 근로자의 권리에 대해 알려주세요.",
        custom_prompt=custom_prompt
    )
    
    if response.success:
        print(f"JSON 응답: {response.response[:200]}...")
    else:
        print(f"오류: {response.error}")
    
    # 4. 다국어 테스트
    print(f"\n📋 다국어 테스트")
    response = client.send_message(
        message="Tell me about employment contracts in Korea.",
        user_language="english"
    )
    
    if response.success:
        print(f"영어 응답: {response.response[:100]}...")
    else:
        print(f"오류: {response.error}")
    
    # 5. 히스토리 조회
    print(f"\n📋 히스토리 조회")
    history = client.get_chat_history()
    print(f"총 {len(history)}개의 메시지")
    
    # 6. 서버 통계
    print(f"\n📋 서버 통계")
    stats = client.get_server_stats()
    if "stats" in stats:
        print(f"활성 세션: {stats['stats'].get('total_sessions', 0)}개")
        print(f"총 메시지: {stats['stats'].get('total_messages', 0)}개")
    
    print(f"\n🎉 테스트 완료!") 