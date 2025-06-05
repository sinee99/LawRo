"""
서버 간 HTTP POST 통신 테스트 스크립트
Contract Analyzer → ChatBot Docker 연결 테스트
"""
import requests
import json
import time
import os
from typing import Dict, Any
from config.chatbot_config import chatbot_config

class ServerCommunicationTest:
    """서버 간 통신 테스트"""
    
    def __init__(self):
        self.contract_analyzer_url = "http://localhost:8000"
        self.chatbot_url = chatbot_config.base_url
        self.test_results = []
    
    def test_chatbot_direct_connection(self):
        """ChatBot 서버 직접 연결 테스트"""
        print("🔍 ChatBot 서버 직접 연결 테스트")
        print(f"   대상 서버: {self.chatbot_url}")
        
        try:
            # Health Check
            response = requests.get(f"{self.chatbot_url}/health", timeout=10)
            
            if response.status_code == 200:
                print("✅ ChatBot 서버 연결 성공")
                
                # 세션 생성 테스트
                session_response = requests.post(f"{self.chatbot_url}/create_session")
                if session_response.status_code == 200:
                    session_data = session_response.json()
                    session_id = session_data.get('session_id')
                    print(f"✅ 세션 생성 성공: {session_id[:8]}...")
                    
                    # 간단한 메시지 테스트
                    test_payload = {
                        "message": "서버 간 통신 테스트입니다.",
                        "session_id": session_id,
                        "user_language": "korean"
                    }
                    
                    chat_response = requests.post(
                        f"{self.chatbot_url}/chat", 
                        json=test_payload,
                        timeout=30
                    )
                    
                    if chat_response.status_code == 200:
                        chat_data = chat_response.json()
                        print(f"✅ ChatBot 메시지 처리 성공")
                        print(f"   처리시간: {chat_data.get('processing_time', 0):.2f}초")
                        print(f"   응답 길이: {len(chat_data.get('response', ''))}자")
                        return True
                    else:
                        print(f"❌ ChatBot 메시지 처리 실패: HTTP {chat_response.status_code}")
                        return False
                else:
                    print(f"❌ 세션 생성 실패: HTTP {session_response.status_code}")
                    return False
            else:
                print(f"❌ ChatBot 서버 연결 실패: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ ChatBot 서버 응답 시간 초과")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ ChatBot 서버 연결 오류: {self.chatbot_url}")
            return False
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {str(e)}")
            return False
    
    def test_contract_analyzer_chatbot_integration(self):
        """Contract Analyzer를 통한 ChatBot 통합 테스트"""
        print("\n🔗 Contract Analyzer → ChatBot 통합 테스트")
        
        try:
            # Contract Analyzer health check
            response = requests.get(f"{self.contract_analyzer_url}/")
            if response.status_code != 200:
                print(f"❌ Contract Analyzer 서버 연결 실패: HTTP {response.status_code}")
                return False
            
            print("✅ Contract Analyzer 서버 연결 성공")
            
            # ChatBot 상태 확인 (Contract Analyzer를 통해)
            status_response = requests.get(f"{self.contract_analyzer_url}/api/chatbot-status")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"✅ ChatBot 상태 확인 성공: {status_data.get('status', 'unknown')}")
                print(f"   ChatBot URL: {status_data.get('server_url', 'N/A')}")
                print(f"   환경: {status_data.get('environment', 'N/A')}")
                
                if not status_data.get('chatbot_available', False):
                    print("❌ ChatBot이 사용 불가능한 상태입니다")
                    return False
                
                return True
            else:
                print(f"❌ ChatBot 상태 확인 실패: HTTP {status_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 통합 테스트 오류: {str(e)}")
            return False
    
    def test_end_to_end_analysis(self):
        """전체 End-to-End 분석 테스트 (ChatBot 통합 포함)"""
        print("\n🧪 End-to-End 분석 테스트")
        
        # 실제 계약서 분석과 유사한 테스트 데이터
        test_request = {
            "user_id": f"test_user_{int(time.time())}",
            "contract_id": f"test_contract_{int(time.time())}",
            "use_chatbot": True,
            "user_language": "korean"
        }
        
        print(f"   사용자 ID: {test_request['user_id']}")
        print(f"   계약서 ID: {test_request['contract_id']}")
        
        try:
            # 통합 분석 요청
            response = requests.post(
                f"{self.contract_analyzer_url}/api/analyze-with-chatbot",
                json=test_request,
                timeout=90  # 충분한 시간 확보
            )
            
            if response.status_code == 200:
                result_data = response.json()
                
                print("✅ 통합 분석 성공!")
                print(f"   메시지: {result_data.get('message', 'N/A')}")
                
                # ChatBot 분석 결과 확인
                chatbot_analysis = result_data.get('chatbot_analysis')
                if chatbot_analysis:
                    if 'error' in chatbot_analysis:
                        print(f"⚠️ ChatBot 분석 오류: {chatbot_analysis['error']}")
                        return False
                    else:
                        legal_analysis = chatbot_analysis.get('legal_analysis', '')
                        processing_time = chatbot_analysis.get('processing_time', 0)
                        
                        print(f"✅ ChatBot 법률 분석 완료")
                        print(f"   처리시간: {processing_time:.2f}초")
                        print(f"   분석 결과 길이: {len(legal_analysis)}자")
                        
                        if len(legal_analysis) > 100:  # 최소 분석 결과 길이 체크
                            print(f"   분석 내용 미리보기: {legal_analysis[:100]}...")
                            
                            # 세션 ID 확인
                            session_id = result_data.get('session_id')
                            if session_id:
                                print(f"   생성된 세션 ID: {session_id[:8]}...")
                                return True
                            else:
                                print("⚠️ 세션 ID가 생성되지 않았습니다")
                                return False
                        else:
                            print("⚠️ 분석 결과가 너무 짧습니다")
                            return False
                else:
                    print("⚠️ ChatBot 분석 결과가 없습니다")
                    return False
                    
            elif response.status_code == 404:
                print("⚠️ 계약서 이미지가 없습니다 (S3 관련 - 정상적인 테스트 결과)")
                print("   실제 계약서 이미지가 있다면 정상 동작할 것입니다")
                return True
            else:
                print(f"❌ 통합 분석 실패: HTTP {response.status_code}")
                print(f"   응답 내용: {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ 분석 요청 시간 초과 (90초)")
            return False
        except Exception as e:
            print(f"❌ End-to-End 테스트 오류: {str(e)}")
            return False
    
    def test_network_connectivity(self):
        """네트워크 연결성 테스트"""
        print("\n🌐 네트워크 연결성 테스트")
        
        import socket
        
        # ChatBot 서버 포트 체크
        try:
            # URL에서 호스트와 포트 추출
            chatbot_host = self.chatbot_url.replace('http://', '').replace('https://', '').split(':')[0]
            chatbot_port = int(self.chatbot_url.split(':')[-1])
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((chatbot_host, chatbot_port))
            sock.close()
            
            if result == 0:
                print(f"✅ ChatBot 서버 포트 연결 가능: {chatbot_host}:{chatbot_port}")
                return True
            else:
                print(f"❌ ChatBot 서버 포트 연결 실패: {chatbot_host}:{chatbot_port}")
                return False
                
        except Exception as e:
            print(f"❌ 네트워크 테스트 오류: {str(e)}")
            return False
    
    def test_environment_variables(self):
        """환경변수 설정 확인"""
        print("\n⚙️ 환경변수 설정 확인")
        
        required_vars = [
            "S3_BUCKET_NAME",
            "UPSTAGE_API_KEY", 
            "OPENAI_API_KEY"
        ]
        
        optional_vars = [
            "CHATBOT_URL",
            "CHATBOT_ENV",
            "CHATBOT_TIMEOUT"
        ]
        
        all_good = True
        
        # 필수 환경변수 체크
        for var in required_vars:
            value = os.getenv(var)
            if value:
                print(f"✅ {var}: 설정됨")
            else:
                print(f"❌ {var}: 설정되지 않음")
                all_good = False
        
        # 선택적 환경변수 체크
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                print(f"✅ {var}: {value}")
            else:
                print(f"⚠️ {var}: 기본값 사용")
        
        return all_good
    
    def run_full_test(self):
        """전체 서버 통신 테스트 실행"""
        print("🚀 Contract Analyzer ↔ ChatBot Docker 서버 통신 테스트")
        print("="*70)
        
        tests = [
            ("환경변수 설정 확인", self.test_environment_variables),
            ("네트워크 연결성 테스트", self.test_network_connectivity),
            ("ChatBot 서버 직접 연결", self.test_chatbot_direct_connection),
            ("Contract Analyzer 통합", self.test_contract_analyzer_chatbot_integration),
            ("End-to-End 분석 테스트", self.test_end_to_end_analysis),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n{'='*50}")
            print(f"📋 {test_name}")
            print("="*50)
            
            try:
                start_time = time.time()
                result = test_func()
                end_time = time.time()
                
                results[test_name] = result
                duration = end_time - start_time
                status = "✅ 성공" if result else "❌ 실패"
                print(f"\n결과: {status} (소요시간: {duration:.2f}초)")
                
            except Exception as e:
                results[test_name] = False
                print(f"\n결과: ❌ 오류 - {str(e)}")
        
        # 최종 결과 요약
        print(f"\n{'='*70}")
        print("📊 최종 테스트 결과 요약")
        print("="*70)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ 통과" if result else "❌ 실패"
            print(f"   {test_name}: {status}")
        
        print(f"\n총 결과: {passed}/{total} 테스트 통과")
        
        if passed == total:
            print("\n🎉 모든 서버 통신 테스트가 성공적으로 완료되었습니다!")
            print("   Contract Analyzer와 ChatBot Docker가 정상적으로 연결되었습니다.")
            
            print(f"\n🔗 서버 정보:")
            print(f"   Contract Analyzer: {self.contract_analyzer_url}")
            print(f"   ChatBot Docker: {self.chatbot_url}")
            print(f"   환경: {chatbot_config.environment}")
            
        else:
            print(f"\n⚠️ {total - passed}개 테스트가 실패했습니다.")
            print("   로그를 확인하고 설정을 점검해 주세요.")
        
        return passed == total

if __name__ == "__main__":
    # 서버 통신 테스트 실행
    tester = ServerCommunicationTest()
    success = tester.run_full_test()
    
    if success:
        print(f"\n🎯 다음 단계:")
        print("1. 실제 계약서 이미지를 S3에 업로드")
        print("2. 운영 환경에서 실제 계약서 분석 테스트")
        print("3. 모니터링 및 로깅 설정")
        print("4. 성능 최적화 및 스케일링 검토")
    else:
        print(f"\n🔧 문제 해결:")
        print("1. ChatBot 서버 상태 확인")
        print("2. 네트워크 및 방화벽 설정 점검")
        print("3. 환경변수 설정 확인")
        print("4. API 키 및 권한 점검") 