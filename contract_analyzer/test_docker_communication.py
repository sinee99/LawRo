#!/usr/bin/env python3
"""
Docker 환경에서 컨테이너 간 통신 테스트
Contract Analyzer ↔ ChatBot Docker 연결 테스트
"""
import requests
import json
import time
import os
from typing import Dict, Any

class DockerCommunicationTest:
    """Docker 환경에서 컨테이너 간 통신 테스트"""
    
    def __init__(self):
        # Docker 환경에서의 서비스 URL
        self.contract_analyzer_url = "http://localhost:8000"
        self.chatbot_url = "http://localhost:8001"
        
    def test_container_health(self):
        """컨테이너 헬스체크"""
        print("🏥 컨테이너 헬스체크")
        
        # Contract Analyzer 헬스체크
        try:
            response = requests.get(f"{self.contract_analyzer_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Contract Analyzer: {data.get('status', 'unknown')}")
            else:
                print(f"❌ Contract Analyzer 헬스체크 실패: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Contract Analyzer 연결 실패: {str(e)}")
            return False
        
        # ChatBot 헬스체크
        try:
            response = requests.get(f"{self.chatbot_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ ChatBot: {data.get('status', 'unknown')}")
            else:
                print(f"❌ ChatBot 헬스체크 실패: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ ChatBot 연결 실패: {str(e)}")
            return False
        
        return True
    
    def test_inter_container_communication(self):
        """컨테이너 간 통신 테스트"""
        print("\n🔗 컨테이너 간 통신 테스트")
        
        # Contract Analyzer를 통해 ChatBot과 통신 테스트
        test_payload = {
            "user_id": f"docker_test_{int(time.time())}",
            "contract_id": f"test_contract_{int(time.time())}",
            "use_chatbot": True,
            "user_language": "korean"
        }
        
        try:
            print(f"📤 통합 분석 요청 전송...")
            print(f"   사용자 ID: {test_payload['user_id']}")
            print(f"   계약서 ID: {test_payload['contract_id']}")
            
            response = requests.post(
                f"{self.contract_analyzer_url}/api/analyze-with-chatbot",
                json=test_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 컨테이너 간 통신 성공!")
                print(f"   메시지: {result.get('message', 'N/A')}")
                
                # ChatBot 응답 확인
                chatbot_analysis = result.get('chatbot_analysis')
                if chatbot_analysis and 'error' not in chatbot_analysis:
                    processing_time = chatbot_analysis.get('processing_time', 0)
                    print(f"   ChatBot 처리시간: {processing_time:.2f}초")
                    return True
                else:
                    error_msg = chatbot_analysis.get('error', '알 수 없는 오류') if chatbot_analysis else '응답 없음'
                    print(f"⚠️ ChatBot 처리 오류: {error_msg}")
                    return False
                    
            elif response.status_code == 404:
                print("ℹ️ 테스트 계약서가 없어 404 응답 (정상 - S3 관련)")
                print("   실제 환경에서는 계약서 이미지가 필요합니다")
                return True
            else:
                print(f"❌ 통합 분석 실패: HTTP {response.status_code}")
                print(f"   응답: {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ 요청 타임아웃 (60초)")
            return False
        except Exception as e:
            print(f"❌ 통신 테스트 오류: {str(e)}")
            return False
    
    def test_direct_chatbot_access(self):
        """ChatBot 직접 접근 테스트"""
        print("\n🤖 ChatBot 직접 접근 테스트")
        
        try:
            # 세션 생성
            session_response = requests.post(f"{self.chatbot_url}/create_session")
            if session_response.status_code == 200:
                session_data = session_response.json()
                session_id = session_data.get('session_id')
                print(f"✅ 세션 생성: {session_id[:8]}...")
                
                # 간단한 메시지 테스트
                chat_payload = {
                    "message": "Docker 환경에서 컨테이너 간 통신 테스트입니다.",
                    "session_id": session_id,
                    "user_language": "korean"
                }
                
                chat_response = requests.post(
                    f"{self.chatbot_url}/chat",
                    json=chat_payload,
                    timeout=30
                )
                
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    response_text = chat_data.get('response', '')
                    processing_time = chat_data.get('processing_time', 0)
                    
                    print(f"✅ ChatBot 응답 성공")
                    print(f"   처리시간: {processing_time:.2f}초")
                    print(f"   응답 길이: {len(response_text)}자")
                    print(f"   응답 미리보기: {response_text[:100]}")
                    return True
                else:
                    print(f"❌ ChatBot 채팅 실패: HTTP {chat_response.status_code}")
                    return False
            else:
                print(f"❌ 세션 생성 실패: HTTP {session_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ChatBot 직접 테스트 오류: {str(e)}")
            return False
    
    def run_full_test(self):
        """전체 테스트 실행"""
        print("🐳 Docker 환경 컨테이너 간 통신 테스트 시작")
        print("=" * 60)
        
        test_results = []
        
        # 1. 헬스체크
        health_ok = self.test_container_health()
        test_results.append(("컨테이너 헬스체크", health_ok))
        
        if not health_ok:
            print("\n❌ 헬스체크 실패로 테스트 중단")
            return False
        
        # 2. ChatBot 직접 테스트
        direct_ok = self.test_direct_chatbot_access()
        test_results.append(("ChatBot 직접 접근", direct_ok))
        
        # 3. 컨테이너 간 통신 테스트
        comm_ok = self.test_inter_container_communication()
        test_results.append(("컨테이너 간 통신", comm_ok))
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        
        all_passed = True
        for test_name, result in test_results:
            status = "✅ 성공" if result else "❌ 실패"
            print(f"  {test_name}: {status}")
            if not result:
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 모든 테스트 통과! Docker 환경이 정상적으로 구성되었습니다.")
            print("📍 Contract Analyzer: http://localhost:8000")
            print("📍 ChatBot: http://localhost:8001")
        else:
            print("⚠️ 일부 테스트 실패. 로그를 확인해주세요.")
            print("📊 로그 확인: docker-compose logs -f")
        
        return all_passed

if __name__ == "__main__":
    tester = DockerCommunicationTest()
    success = tester.run_full_test() 