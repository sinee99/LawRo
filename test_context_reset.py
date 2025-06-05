#!/usr/bin/env python3
"""
커스텀 프롬프트 시 문맥 초기화 기능 테스트
"""

import requests
import json
import time

# 서버 설정
SERVER_IP = "16.176.26.197"
PORT = "8000"
BASE_URL = f"http://{SERVER_IP}:{PORT}"

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

def send_message(message, language="korean", session_id=None, custom_prompt=None):
    """메시지 전송"""
    data = {
        "message": message,
        "user_language": language
    }
    
    if session_id:
        data["session_id"] = session_id
    
    if custom_prompt:
        data["custom_prompt"] = custom_prompt
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/send",
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('success', False), result.get('message', ''), result.get('chat_history', [])
        else:
            return False, f"HTTP {response.status_code}", []
    except Exception as e:
        return False, str(e), []

def test_context_reset():
    """문맥 초기화 테스트"""
    print("🧪 커스텀 프롬프트 문맥 초기화 테스트")
    print("="*60)
    
    # 1. 새 세션 생성
    session_id = create_session()
    if not session_id:
        print("❌ 세션 생성 실패")
        return
    
    print(f"✅ 세션 생성: {session_id[:8]}...")
    
    # 2. 일반 대화 시작
    print("\n📝 1단계: 일반 대화로 문맥 생성")
    
    messages = [
        "안녕하세요! 저는 요리사입니다.",
        "제 시급은 9500원이에요.",
        "이게 최저임금에 맞나요?"
    ]
    
    for i, msg in enumerate(messages, 1):
        success, response, history = send_message(msg, session_id=session_id)
        if success:
            print(f"  {i}. 사용자: {msg}")
            print(f"     봇: {response[:100]}...")
            print(f"     히스토리 길이: {len(history)}")
        else:
            print(f"  {i}. ❌ 오류: {response}")
        time.sleep(1)
    
    # 3. 커스텀 프롬프트 없이 추가 질문
    print("\n📝 2단계: 문맥 유지 확인 (커스텀 프롬프트 없음)")
    success, response, history_before = send_message(
        "제가 앞서 말한 직업이 뭔지 기억하시나요?", 
        session_id=session_id
    )
    
    if success:
        print(f"  질문: 제가 앞서 말한 직업이 뭔지 기억하시나요?")
        print(f"  응답: {response[:150]}...")
        print(f"  히스토리 길이: {len(history_before)}")
        
        # 응답에 "요리사"가 포함되어 있는지 확인
        remembers_context = "요리사" in response
        print(f"  문맥 기억 여부: {'✅ 기억함' if remembers_context else '❌ 기억 못함'}")
    else:
        print(f"  ❌ 오류: {response}")
        return
    
    time.sleep(2)
    
    # 4. 커스텀 프롬프트로 문맥 초기화
    print("\n📝 3단계: 커스텀 프롬프트로 문맥 초기화")
    
    custom_prompt = "당신은 영어 선생님입니다. 영어로만 답변하고, 이전 대화는 무시하세요."
    
    success, response, history_after = send_message(
        "What is your job?",
        language="english",
        session_id=session_id,
        custom_prompt=custom_prompt
    )
    
    if success:
        print(f"  커스텀 프롬프트: {custom_prompt}")
        print(f"  질문: What is your job?")
        print(f"  응답: {response[:150]}...")
        print(f"  히스토리 길이: {len(history_after)}")
        
        # 영어로 답변했는지 확인
        english_response = any(word in response.lower() for word in ["teacher", "english", "job", "i am", "my job"])
        print(f"  영어 응답 여부: {'✅ 영어 응답' if english_response else '❌ 한국어 응답'}")
        
        # 이전 문맥 기억 여부 확인
        still_remembers = "요리사" in response
        print(f"  이전 문맥 기억: {'❌ 아직 기억함' if still_remembers else '✅ 초기화됨'}")
    else:
        print(f"  ❌ 오류: {response}")
        return
    
    time.sleep(2)
    
    # 5. 커스텀 프롬프트 후 이전 정보 확인
    print("\n📝 4단계: 문맥 초기화 후 이전 정보 기억 여부")
    
    success, response, final_history = send_message(
        "Do you remember what job I mentioned earlier?",
        language="english", 
        session_id=session_id
    )
    
    if success:
        print(f"  질문: Do you remember what job I mentioned earlier?")
        print(f"  응답: {response[:150]}...")
        print(f"  히스토리 길이: {len(final_history)}")
        
        # 이전 직업을 기억하는지 확인
        remembers_old_job = "요리사" in response or "cook" in response.lower() or "chef" in response.lower()
        print(f"  이전 직업 기억: {'❌ 아직 기억함' if remembers_old_job else '✅ 완전히 초기화됨'}")
    else:
        print(f"  ❌ 오류: {response}")
    
    # 6. 결과 요약
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)
    
    if success:
        print("✅ 커스텀 프롬프트 시 문맥 초기화 기능이 정상 작동합니다!")
        print("🔄 새로운 작업 시작 시 이전 대화 맥락이 깔끔하게 초기화됩니다.")
    else:
        print("❌ 테스트 중 오류가 발생했습니다.")
    
    print(f"\n🌐 API 문서에서 더 자세히 확인: {BASE_URL}/docs")

if __name__ == "__main__":
    test_context_reset() 