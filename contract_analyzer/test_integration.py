"""
계약서 분석 + ChatBot 법률 상담 통합 시스템 테스트
"""
import requests
import json
import time
from typing import Dict, Any

class ContractAnalyzerIntegrationTest:
    def __init__(self, 
                 contract_analyzer_url: str = "http://localhost:8000",
                 chatbot_url: str = "http://16.176.26.197:8000"):
        self.contract_analyzer_url = contract_analyzer_url.rstrip('/')
        self.chatbot_url = chatbot_url.rstrip('/')
        
    def test_chatbot_status(self):
        """ChatBot 서버 상태 확인"""
        print("🔍 ChatBot 서버 상태 확인 중...")
        
        try:
            # Contract Analyzer를 통한 ChatBot 상태 확인
            response = requests.get(f"{self.contract_analyzer_url}/api/chatbot-status")
            
            if response.status_code == 200:
                status_data = response.json()
                print(f"✅ ChatBot 상태: {status_data}")
                return status_data["chatbot_available"]
            else:
                print(f"❌ ChatBot 상태 확인 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ChatBot 상태 확인 오류: {str(e)}")
            return False
    
    def test_direct_chatbot_connection(self):
        """직접 ChatBot 서버 연결 테스트"""
        print("🔍 ChatBot 서버 직접 연결 테스트...")
        
        try:
            # 1. 세션 생성 테스트
            response = requests.post(f"{self.chatbot_url}/create_session")
            
            if response.status_code == 200:
                session_data = response.json()
                session_id = session_data.get('session_id')
                print(f"✅ 세션 생성 성공: {session_id[:8]}...")
                
                # 2. 간단한 메시지 테스트
                test_message = {
                    "message": "안녕하세요. 테스트 메시지입니다.",
                    "session_id": session_id,
                    "user_language": "korean"
                }
                
                chat_response = requests.post(f"{self.chatbot_url}/chat", json=test_message)
                
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    print(f"✅ ChatBot 응답 테스트 성공 (처리시간: {chat_data.get('processing_time', 0):.2f}초)")
                    print(f"   응답 길이: {len(chat_data.get('response', ''))}자")
                    return True
                else:
                    print(f"❌ ChatBot 메시지 테스트 실패: HTTP {chat_response.status_code}")
                    return False
            else:
                print(f"❌ 세션 생성 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 직접 연결 테스트 오류: {str(e)}")
            return False
    
    def test_integration_with_sample_data(self):
        """샘플 데이터로 통합 시스템 테스트"""
        print("🧪 샘플 데이터로 통합 시스템 테스트...")
        
        # 실제 계약서 분석 결과와 유사한 샘플 데이터
        sample_request = {
            "user_id": "test_user_integration",
            "contract_id": "sample_contract_001",
            "use_chatbot": True,
            "user_language": "korean"
        }
        
        # 실제로는 S3에서 이미지를 가져오겠지만, 
        # 테스트용으로는 ChatBot 통합 서비스를 직접 테스트
        from services.chatbot_integration_service import ChatbotIntegrationService
        
        sample_contract_data = {
            "contract_info": {
                "employer_name": "주식회사 테스트컴퍼니",
                "employee_name": "김○○",
                "employee_nationality": "네팔",
                "position": "제조업 생산직",
                "work_location": "경기도 안산시 단원구",
                "contract_period": {
                    "start_date": "2024-01-01",
                    "end_date": "2026-12-31",
                    "duration": "3년"
                }
            },
            "work_conditions": {
                "working_hours": {
                    "daily": "8시간",
                    "weekly": "주 5일",
                    "total_weekly": "40시간"
                },
                "salary": {
                    "type": "월급",
                    "amount": 2100000,
                    "currency": "KRW",
                    "hourly_rate": 10047.8,  # 2100000 / 209시간
                    "payment_date": "매월 25일",
                    "payment_method": "계좌이체"
                },
                "overtime": {
                    "rate": "1.5배",
                    "weekend_rate": "1.5배"
                }
            },
            "benefits": {
                "insurance": ["국민연금", "건강보험", "고용보험", "산재보험"],
                "vacation": {
                    "annual_leave": "15일",
                    "sick_leave": "명시되지 않음"
                },
                "allowances": {
                    "meal": "월 100,000원",
                    "transportation": "월 50,000원",
                    "accommodation": "회사 기숙사 제공"
                }
            },
            "foreign_worker_specific": {
                "visa_type": "E-9",
                "accommodation_provided": True,
                "korean_language_support": "미명시",
                "work_permit_details": "회사에서 관리"
            },
            "potential_issues": [
                "최저임금 위반 가능성 (2024년 기준 9,860원/시간)",
                "수습기간 감액 조항 불분명",
                "휴일 및 휴가 규정 미흡",
                "외국인 근로자 지원 사항 불충분"
            ]
        }
        
        try:
            print("📤 ChatBot 통합 서비스 테스트 시작...")
            
            chatbot_service = ChatbotIntegrationService()
            
            result = chatbot_service.analyze_contract_with_chatbot(
                parsed_contract_data=sample_contract_data,
                user_id=sample_request["user_id"],
                user_language=sample_request["user_language"]
            )
            
            print("\n" + "="*60)
            print("📋 통합 시스템 테스트 결과:")
            print("="*60)
            
            if result["success"]:
                print(f"✅ 분석 성공!")
                print(f"   세션 ID: {result['session_id'][:8]}...")
                print(f"   처리 시간: {result['processing_time']:.2f}초")
                print(f"   분석 결과 길이: {len(result['analysis'])}자")
                print(f"   사용자 ID: {result['user_id']}")
                
                print(f"\n📝 법률 분석 결과 (처음 300자):")
                print("-" * 40)
                print(result['analysis'][:300] + "..." if len(result['analysis']) > 300 else result['analysis'])
                
                return True
            else:
                print(f"❌ 분석 실패: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ 통합 테스트 오류: {str(e)}")
            return False
    
    def test_multiple_users(self):
        """다중 사용자 동시 처리 테스트"""
        print("👥 다중 사용자 동시 처리 테스트...")
        
        from services.chatbot_integration_service import ChatbotIntegrationService
        import threading
        
        def test_user_analysis(user_id: str, results: dict):
            """개별 사용자 분석 테스트"""
            try:
                chatbot_service = ChatbotIntegrationService()
                
                sample_data = {
                    "user_info": {"user_id": user_id},
                    "contract_summary": "간단한 테스트 계약서",
                    "test_timestamp": time.time()
                }
                
                result = chatbot_service.analyze_contract_with_chatbot(
                    parsed_contract_data=sample_data,
                    user_id=user_id,
                    user_language="korean"
                )
                
                results[user_id] = result
                print(f"   {user_id}: {'✅ 성공' if result['success'] else '❌ 실패'}")
                
            except Exception as e:
                results[user_id] = {"success": False, "error": str(e)}
                print(f"   {user_id}: ❌ 오류 - {str(e)}")
        
        # 5명의 사용자로 동시 테스트
        users = [f"test_user_{i:03d}" for i in range(1, 6)]
        results = {}
        threads = []
        
        start_time = time.time()
        
        for user_id in users:
            thread = threading.Thread(target=test_user_analysis, args=(user_id, results))
            threads.append(thread)
            thread.start()
        
        # 모든 스레드 완료 대기
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        successful = [user for user, result in results.items() if result.get("success", False)]
        
        print(f"\n📊 다중 사용자 테스트 결과:")
        print(f"   총 사용자: {len(users)}명")
        print(f"   성공: {len(successful)}명")
        print(f"   실패: {len(users) - len(successful)}명")
        print(f"   총 소요시간: {end_time - start_time:.2f}초")
        
        return len(successful) == len(users)
    
    def run_full_test(self):
        """전체 통합 테스트 실행"""
        print("🚀 계약서 분석 + ChatBot 법률 상담 통합 시스템 테스트 시작")
        print("="*70)
        
        tests = [
            ("ChatBot 서버 상태 확인", self.test_chatbot_status),
            ("직접 ChatBot 연결 테스트", self.test_direct_chatbot_connection),
            ("샘플 데이터 통합 테스트", self.test_integration_with_sample_data),
            ("다중 사용자 동시 처리 테스트", self.test_multiple_users),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}")
            print("-" * 50)
            
            try:
                result = test_func()
                results[test_name] = result
                status = "✅ 통과" if result else "❌ 실패"
                print(f"결과: {status}")
                
            except Exception as e:
                results[test_name] = False
                print(f"결과: ❌ 오류 - {str(e)}")
        
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
            print("🎉 모든 통합 테스트가 성공적으로 완료되었습니다!")
        else:
            print("⚠️ 일부 테스트가 실패했습니다. 로그를 확인해 주세요.")
        
        return passed == total

if __name__ == "__main__":
    # 통합 테스트 실행
    tester = ContractAnalyzerIntegrationTest()
    success = tester.run_full_test()
    
    if success:
        print("\n🔧 통합 시스템 사용 방법:")
        print("-" * 30)
        print("1. 계약서 이미지를 S3에 업로드")
        print("2. POST /api/analyze-with-chatbot 호출")
        print("   - user_id: 사용자 ID")
        print("   - contract_id: 계약서 ID") 
        print("   - use_chatbot: true (ChatBot 분석 사용)")
        print("   - user_language: 'korean' (응답 언어)")
        print("3. 응답에서 structured_result와 chatbot_analysis 확인")
        print("4. session_id로 추가 대화 가능")
        
        print(f"\n🌐 API 엔드포인트:")
        print(f"   - 통합 분석: POST /api/analyze-with-chatbot")
        print(f"   - ChatBot 상태: GET /api/chatbot-status")
        print(f"   - ChatBot 서버: http://16.176.26.197:8000/docs")
    else:
        print("\n❌ 통합 시스템에 문제가 있습니다. 설정을 확인해 주세요.") 