#!/usr/bin/env python3
"""
LawRo 챗봇 API 테스트 스크립트
EC2 서버: 16.176.26.197:8000
"""

import requests
import json
import time
from datetime import datetime

# 서버 설정
SERVER_IP = "16.176.26.197"
PORT = "8000"
BASE_URL = f"http://{SERVER_IP}:{PORT}"

def print_header(title):
    """테스트 섹션 헤더 출력"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_result(success, title, data=None, error=None):
    """테스트 결과 출력"""
    status = "✅ 성공" if success else "❌ 실패"
    print(f"{status} {title}")
    
    if data:
        if isinstance(data, dict):
            print(f"📊 응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"📊 응답: {data}")
    
    if error:
        print(f"⚠️ 오류: {error}")
    print("-" * 40)

def test_health_check():
    """헬스체크 테스트"""
    print_header("서버 헬스체크")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "헬스체크", data)
            return True
        else:
            print_result(False, "헬스체크", error=f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_result(False, "헬스체크", error="서버에 연결할 수 없습니다")
        return False
    except requests.exceptions.Timeout:
        print_result(False, "헬스체크", error="응답 시간 초과")
        return False
    except Exception as e:
        print_result(False, "헬스체크", error=str(e))
        return False

def test_api_docs():
    """API 문서 접근 테스트"""
    print_header("API 문서 접근 테스트")
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=10)
        
        if response.status_code == 200:
            print_result(True, "API 문서 접근")
            print(f"🌐 브라우저에서 확인: {BASE_URL}/docs")
            return True
        else:
            print_result(False, "API 문서 접근", error=f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, "API 문서 접근", error=str(e))
        return False

def test_chat_api():
    """채팅 API 테스트"""
    print_header("채팅 API 테스트")
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "한국어 기본 상담",
            "data": {
                "message": "안녕하세요! 근로계약서 관련 질문이 있습니다.",
                "user_language": "korean"
            }
        },
        {
            "name": "한국어 계약서 분석",
            "data": {
                "message": '{"직종": "요리사", "시급": "9000원", "근무시간": "주 40시간", "휴일": "주 1회", "4대보험": "가입"}',
                "user_language": "korean"
            }
        },
        {
            "name": "영어 상담",
            "data": {
                "message": "Hello! I have questions about my employment contract in Korea.",
                "user_language": "english"
            }
        },
        {
            "name": "베트남어 상담",
            "data": {
                "message": "Xin chào! Tôi có thắc mắc về hợp đồng lao động của mình.",
                "user_language": "vietnamese"
            }
        },
        {
            "name": "중국어 상담",
            "data": {
                "message": "你好！我对我的劳动合同有疑问。",
                "user_language": "chinese"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 테스트 {i}: {test_case['name']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/chat/send",
                json=test_case['data'],
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False)
                ai_response = result.get('message', '')
                api_processing_time = result.get('processing_time', 0)
                
                print(f"✅ 성공: {success}")
                print(f"⏱️ 총 시간: {processing_time:.2f}초 (API: {api_processing_time:.2f}초)")
                print(f"💬 AI 응답:")
                print(f"   {ai_response[:300]}{'...' if len(ai_response) > 300 else ''}")
                
            else:
                print_result(False, test_case['name'], error=f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print_result(False, test_case['name'], error="응답 시간 초과 (30초)")
        except Exception as e:
            print_result(False, test_case['name'], error=str(e))
        
        # 테스트 간 간격
        time.sleep(1)

def test_session_management():
    """세션 관리 테스트"""
    print_header("세션 관리 테스트")
    
    try:
        # 새 세션 생성
        response = requests.post(f"{BASE_URL}/chat/new-session", timeout=10)
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data.get('session_id')
            print_result(True, "새 세션 생성", {"session_id": session_id[:8] + "..."})
            
            # 세션을 사용한 채팅
            chat_response = requests.post(
                f"{BASE_URL}/chat/send",
                json={
                    "message": "안녕하세요!",
                    "session_id": session_id,
                    "user_language": "korean"
                },
                timeout=20
            )
            
            if chat_response.status_code == 200:
                print_result(True, "세션 기반 채팅")
            else:
                print_result(False, "세션 기반 채팅")
                
        else:
            print_result(False, "새 세션 생성")
            
    except Exception as e:
        print_result(False, "세션 관리", error=str(e))

def test_custom_prompt():
    """커스텀 프롬프트 테스트"""
    print_header("커스텀 프롬프트 테스트")
    
    # 여러 개의 커스텀 프롬프트 테스트
    test_prompts = [
        {
            "name": "간단한 답변 요청",
            "prompt": "간단하고 명확하게 20자 이내로 답변해주세요.",
            "message": "최저임금이 뭐예요?",
            "language": "korean"
        },
        {
            "name": "영어 답변 요청",
            "prompt": "Please respond in simple English with basic legal terms only.",
            "message": "What is minimum wage law?",
            "language": "english"
        },
        {
            "name": "친절한 상담사 역할",
            "prompt": "당신은 친절한 법률 상담사입니다. 따뜻하고 이해하기 쉽게 설명해주세요.",
            "message": "근로계약서에서 주의할 점이 뭔가요?",
            "language": "korean"
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_prompts, 1):
        print(f"\n📝 커스텀 프롬프트 테스트 {i}: {test_case['name']}")
        
        try:
            # 요청 데이터 준비
            request_data = {
                "message": test_case['message'],
                "user_language": test_case['language'],
                "custom_prompt": test_case['prompt']
            }
            
            # API 호출
            response = requests.post(
                f"{BASE_URL}/chat/send",
                json=request_data,
                timeout=45,  # 커스텀 프롬프트는 시간이 더 걸릴 수 있음
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success', False):
                    ai_response = result.get('message', '')
                    processing_time = result.get('processing_time', 0)
                    
                    print(f"✅ 성공")
                    print(f"⏱️ 처리시간: {processing_time:.2f}초")
                    print(f"💬 응답 미리보기:")
                    print(f"   {ai_response[:150]}{'...' if len(ai_response) > 150 else ''}")
                    success_count += 1
                else:
                    print(f"❌ API 성공하였으나 처리 실패")
                    print(f"   응답: {result.get('message', '')}")
                
            else:
                print(f"❌ HTTP 오류: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   오류 내용: {error_detail}")
                except:
                    print(f"   오류 내용: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ 타임아웃 (45초 초과)")
            
        except requests.exceptions.ConnectionError:
            print(f"❌ 연결 오류 - 서버가 응답하지 않습니다")
            
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {str(e)}")
        
        # 테스트 간 간격
        if i < len(test_prompts):
            time.sleep(2)
    
    # 결과 요약
    print(f"\n📊 커스텀 프롬프트 테스트 결과:")
    print(f"   성공: {success_count}/{len(test_prompts)}")
    
    if success_count == len(test_prompts):
        print("✅ 모든 커스텀 프롬프트 테스트 통과!")
    elif success_count > 0:
        print("⚠️ 일부 커스텀 프롬프트 테스트 성공")
    else:
        print("❌ 모든 커스텀 프롬프트 테스트 실패")
        print("   - 서버의 커스텀 프롬프트 기능을 확인해주세요")
        print("   - API 로그를 확인해보세요: docker logs lawro-chatbot")

def performance_test():
    """성능 테스트"""
    print_header("성능 테스트 (연속 5회 요청)")
    
    times = []
    for i in range(5):
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/chat/send",
                json={
                    "message": f"테스트 메시지 {i+1}",
                    "user_language": "korean"
                },
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = end_time - start_time
                times.append(response_time)
                print(f"✅ 요청 {i+1}: {response_time:.2f}초")
            else:
                print(f"❌ 요청 {i+1}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 요청 {i+1}: {e}")
        
        time.sleep(0.5)  # 짧은 간격
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        print(f"\n📊 성능 결과:")
        print(f"   평균 응답시간: {avg_time:.2f}초")
        print(f"   최소 응답시간: {min_time:.2f}초")
        print(f"   최대 응답시간: {max_time:.2f}초")

def main():
    """메인 테스트 함수"""
    print("🚀 LawRo 챗봇 API 테스트 시작")
    print(f"🌐 서버: {BASE_URL}")
    print(f"🕐 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 기본 연결 테스트
    if not test_health_check():
        print("\n❌ 서버 연결 실패! 다음을 확인해주세요:")
        print("   1. EC2 인스턴스가 실행 중인지 확인")
        print("   2. 보안 그룹에서 8000 포트가 열려있는지 확인")
        print("   3. Docker 컨테이너가 실행 중인지 확인: docker ps")
        return
    
    # API 문서 접근 테스트
    test_api_docs()
    
    # 채팅 API 테스트
    test_chat_api()
    
    # 세션 관리 테스트
    test_session_management()
    
    # 커스텀 프롬프트 테스트
    test_custom_prompt()
    
    # 성능 테스트
    performance_test()
    
    print("\n" + "="*60)
    print("🎉 모든 테스트 완료!")
    print(f"🌐 브라우저에서 확인: {BASE_URL}/docs")
    print("="*60)

if __name__ == "__main__":
    main() 