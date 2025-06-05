import requests
import time
import json

BASE_URL = "http://16.176.26.197:8000"  # 실제 서버 주소

def test_custom_prompt_auto_reset():
    """커스텀 프롬프트 사용 후 기본 프롬프트로 자동 복귀 테스트"""
    
    print("🧪 커스텀 프롬프트 자동 복귀 테스트")
    print("=" * 50)
    
    # 1. 새 세션 생성
    print("📋 1단계: 새 세션 생성")
    try:
        response = requests.post(f"{BASE_URL}/create_session")
        if response.status_code == 200:
            session_id = response.json()["session_id"]
            print(f"✅ 세션 생성 성공: {session_id[:8]}...")
        else:
            print(f"❌ 세션 생성 실패: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 세션 생성 오류: {str(e)}")
        return
    
    # 2. 기본 프롬프트로 첫 번째 질문
    print(f"\n📋 2단계: 기본 프롬프트로 첫 번째 질문")
    try:
        payload = {
            "message": "근로계약서에 대해 간단히 설명해주세요.",
            "session_id": session_id,
            "user_language": "korean"
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 기본 프롬프트 응답 (길이: {len(data['response'])})")
            print(f"📝 응답 미리보기: {data['response'][:100]}...")
        else:
            print(f"❌ 기본 프롬프트 요청 실패: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 기본 프롬프트 요청 오류: {str(e)}")
        return
    
    time.sleep(2)
    
    # 3. 커스텀 프롬프트로 질문
    print(f"\n📋 3단계: 커스텀 프롬프트 적용")
    custom_prompt = "당신은 계약서 분석 전문가입니다. 사용자의 질문에 대해 JSON 형태로 답변하고, 'analysis', 'recommendation', 'risk_score' 필드를 포함해주세요."
    
    try:
        payload = {
            "message": "이 계약서에서 문제가 될 수 있는 조항이 있나요?",
            "session_id": session_id,
            "custom_prompt": custom_prompt,
            "user_language": "korean"
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 커스텀 프롬프트 응답 (길이: {len(data['response'])})")
            print(f"📝 응답 미리보기: {data['response'][:100]}...")
            
            # JSON 형태인지 확인
            try:
                if '{' in data['response'] and '}' in data['response']:
                    print("✅ JSON 형태 응답 확인됨")
                else:
                    print("⚠️ JSON 형태가 아닌 응답")
            except:
                print("⚠️ JSON 파싱 불가")
        else:
            print(f"❌ 커스텀 프롬프트 요청 실패: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 커스텀 프롬프트 요청 오류: {str(e)}")
        return
    
    time.sleep(2)
    
    # 4. 커스텀 프롬프트 없이 다시 질문 (자동 복귀 테스트)
    print(f"\n📋 4단계: 기본 프롬프트로 자동 복귀 테스트")
    try:
        payload = {
            "message": "근로기준법에 대해 알려주세요.",
            "session_id": session_id,
            "user_language": "korean"
            # custom_prompt 필드 없음 - 자동으로 기본 프롬프트로 복귀해야 함
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 기본 프롬프트 복귀 응답 (길이: {len(data['response'])})")
            print(f"📝 응답 미리보기: {data['response'][:100]}...")
            
            # 기본 프롬프트 특징인 "📍" 마크가 있는지 확인
            if "📍" in data['response']:
                print("✅ 기본 프롬프트 특징 확인됨 (📍 마크 포함)")
            else:
                print("⚠️ 기본 프롬프트 특징이 보이지 않음")
                
            # JSON 형태가 아닌지 확인 (기본 프롬프트로 돌아갔다면 JSON이 아니어야 함)
            if not ('{' in data['response'] and '"analysis"' in data['response']):
                print("✅ JSON 형태가 아닌 일반 응답 확인 (기본 프롬프트로 복귀됨)")
            else:
                print("⚠️ 여전히 JSON 형태 응답 (커스텀 프롬프트가 유지됨)")
        else:
            print(f"❌ 자동 복귀 테스트 실패: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 자동 복귀 테스트 오류: {str(e)}")
        return
    
    time.sleep(2)
    
    # 5. 다시 한 번 더 기본 프롬프트로 질문해서 확실히 복귀되었는지 확인
    print(f"\n📋 5단계: 기본 프롬프트 지속 확인")
    try:
        payload = {
            "message": "퇴직금 계산 방법을 알려주세요.",
            "session_id": session_id,
            "user_language": "korean"
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 기본 프롬프트 지속 확인 (길이: {len(data['response'])})")
            print(f"📝 응답 미리보기: {data['response'][:100]}...")
            
            if "📍" in data['response']:
                print("✅ 기본 프롬프트가 지속적으로 사용됨")
            else:
                print("⚠️ 기본 프롬프트 특징이 보이지 않음")
        else:
            print(f"❌ 기본 프롬프트 지속 확인 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 기본 프롬프트 지속 확인 오류: {str(e)}")
    
    # 6. 마지막으로 다시 커스텀 프롬프트 테스트
    print(f"\n📋 6단계: 커스텀 프롬프트 재적용 테스트")
    try:
        new_custom_prompt = "당신은 친근한 법률 상담사입니다. 모든 답변 끝에 '도움이 되셨길 바랍니다!'를 추가해주세요."
        
        payload = {
            "message": "연차휴가에 대해 알려주세요.",
            "session_id": session_id,
            "custom_prompt": new_custom_prompt,
            "user_language": "korean"
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 새 커스텀 프롬프트 응답 (길이: {len(data['response'])})")
            print(f"📝 응답 미리보기: {data['response'][:100]}...")
            
            if "도움이 되셨길 바랍니다!" in data['response']:
                print("✅ 새로운 커스텀 프롬프트가 정상 적용됨")
            else:
                print("⚠️ 새로운 커스텀 프롬프트가 적용되지 않음")
        else:
            print(f"❌ 새 커스텀 프롬프트 테스트 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 새 커스텀 프롬프트 테스트 오류: {str(e)}")
    
    print(f"\n🎉 테스트 완료!")
    print(f"세션 ID: {session_id}")

def test_multiple_sessions():
    """여러 세션에서 독립적으로 커스텀 프롬프트가 작동하는지 테스트"""
    print(f"\n🔄 다중 세션 독립성 테스트")
    print("=" * 50)
    
    sessions = []
    
    # 3개의 세션 생성
    for i in range(3):
        try:
            response = requests.post(f"{BASE_URL}/create_session")
            if response.status_code == 200:
                session_id = response.json()["session_id"]
                sessions.append(session_id)
                print(f"✅ 세션 {i+1} 생성: {session_id[:8]}...")
            else:
                print(f"❌ 세션 {i+1} 생성 실패")
        except Exception as e:
            print(f"❌ 세션 {i+1} 생성 오류: {str(e)}")
    
    if len(sessions) < 3:
        print("❌ 세션 생성 부족으로 다중 세션 테스트 중단")
        return
    
    # 각 세션에 다른 커스텀 프롬프트 적용
    custom_prompts = [
        "JSON 형태로 답변해주세요.",
        "모든 답변을 영어로 해주세요. Please respond in English.",
        "답변 끝에 '감사합니다!'를 추가해주세요."
    ]
    
    for i, (session_id, custom_prompt) in enumerate(zip(sessions, custom_prompts)):
        print(f"\n📤 세션 {i+1}에 커스텀 프롬프트 적용...")
        try:
            payload = {
                "message": "근로계약서 작성 시 주의사항을 알려주세요.",
                "session_id": session_id,
                "custom_prompt": custom_prompt,
                "user_language": "korean"
            }
            
            response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 세션 {i+1} 응답 받음 (길이: {len(data['response'])})")
                print(f"📝 응답 시작: {data['response'][:50]}...")
            else:
                print(f"❌ 세션 {i+1} 요청 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 세션 {i+1} 요청 오류: {str(e)}")
        
        time.sleep(1)
    
    print(f"\n🎉 다중 세션 테스트 완료!")

if __name__ == "__main__":
    # 서버 상태 확인
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 서버 연결 확인")
        else:
            print(f"⚠️ 서버 응답: {response.status_code}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {str(e)}")
        print("⚠️ 테스트를 계속 진행하지만 결과가 부정확할 수 있습니다.")
    
    # 메인 테스트 실행
    test_custom_prompt_auto_reset()
    
    # 다중 세션 테스트 실행
    test_multiple_sessions() 