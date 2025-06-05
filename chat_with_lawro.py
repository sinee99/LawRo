#!/usr/bin/env python3
"""
LawRo 챗봇과 대화하는 간단한 인터페이스
EC2 서버: 16.176.26.197:8000
"""

import requests
import json
from datetime import datetime

# 서버 설정
SERVER_IP = "16.176.26.197"
PORT = "8000"
BASE_URL = f"http://{SERVER_IP}:{PORT}"

def get_user_language():
    """사용자 언어 선택"""
    languages = {
        "1": ("korean", "한국어"),
        "2": ("english", "English"),
        "3": ("vietnamese", "Tiếng Việt"),
        "4": ("chinese", "中文"),
        "5": ("japanese", "日本語"),
        "6": ("thai", "ภาษาไทย")
    }
    
    print("\n🌍 답변받고 싶은 언어를 선택하세요:")
    for key, (code, name) in languages.items():
        print(f"  {key}. {name}")
    
    while True:
        choice = input("\n선택 (1-6): ").strip()
        if choice in languages:
            return languages[choice][0]
        print("❌ 잘못된 선택입니다. 1-6 중에서 선택해주세요.")

def send_message(message, language, session_id=None):
    """메시지 전송"""
    try:
        data = {
            "message": message,
            "user_language": language
        }
        
        if session_id:
            data["session_id"] = session_id
        
        response = requests.post(
            f"{BASE_URL}/chat/send",
            json=data,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('success', False), result.get('message', ''), result.get('processing_time', 0)
        else:
            return False, f"오류: HTTP {response.status_code}", 0
            
    except requests.exceptions.Timeout:
        return False, "응답 시간 초과 (30초)", 0
    except Exception as e:
        return False, f"연결 오류: {str(e)}", 0

def create_session():
    """새 세션 생성"""
    try:
        response = requests.post(f"{BASE_URL}/chat/new-session", timeout=10)
        if response.status_code == 200:
            session_data = response.json()
            return session_data.get('session_id')
    except:
        pass
    return None

def main():
    """메인 대화 루프"""
    print("🚀 LawRo 법률 상담 챗봇")
    print(f"🌐 서버: {BASE_URL}")
    print("="*60)
    
    # 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 서버에 연결할 수 없습니다.")
            print("EC2 서버와 Docker 컨테이너가 실행 중인지 확인해주세요.")
            return
    except:
        print("❌ 서버에 연결할 수 없습니다.")
        print("EC2 서버와 Docker 컨테이너가 실행 중인지 확인해주세요.")
        return
    
    print("✅ 서버 연결 성공!")
    
    # 언어 선택
    language = get_user_language()
    
    # 세션 생성
    session_id = create_session()
    if session_id:
        print(f"🔗 새 세션 생성됨: {session_id[:8]}...")
    
    print(f"\n💬 {language} 언어로 대화를 시작합니다!")
    print("📝 법률 관련 질문을 입력하세요. (종료하려면 'quit' 또는 'exit' 입력)")
    print("-"*60)
    
    conversation_count = 0
    
    while True:
        try:
            # 사용자 입력
            user_input = input("\n👤 질문: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료', '나가기']:
                print("\n👋 대화를 종료합니다. 감사합니다!")
                break
            
            if not user_input:
                print("❓ 질문을 입력해주세요.")
                continue
            
            print("🤖 답변 생성 중...")
            
            # 메시지 전송
            success, response, processing_time = send_message(user_input, language, session_id)
            
            if success:
                conversation_count += 1
                print(f"\n🤖 LawRo (처리시간: {processing_time:.2f}초):")
                print(f"{response}")
                
                if conversation_count == 1:
                    print(f"\n💡 팁: 계약서 내용을 JSON 형식으로 입력하면 더 정확한 분석을 받을 수 있습니다!")
                    print('예: {"직종": "요리사", "시급": "9000원", "근무시간": "주 40시간"}')
                
            else:
                print(f"\n❌ 오류 발생: {response}")
                
        except KeyboardInterrupt:
            print("\n\n👋 대화가 중단되었습니다. 감사합니다!")
            break
        except Exception as e:
            print(f"\n❌ 예상치 못한 오류: {e}")

if __name__ == "__main__":
    main() 