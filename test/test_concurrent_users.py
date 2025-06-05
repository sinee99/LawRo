import asyncio
import time
import requests
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

BASE_URL = "http://16.176.26.197:8000"  # 실제 서버 주소로 변경

class ConcurrentUserTest:
    """동시 사용자 테스트 클래스"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []
        self.errors = []
    
    def create_session(self) -> str:
        """새 세션 생성"""
        try:
            response = requests.post(f"{self.base_url}/create_session")
            if response.status_code == 200:
                data = response.json()
                return data.get('session_id')
            else:
                self.errors.append(f"세션 생성 실패: {response.status_code}")
                return None
        except Exception as e:
            self.errors.append(f"세션 생성 예외: {str(e)}")
            return None
    
    def send_message(self, session_id: str, message: str, user_id: str, language: str = "korean") -> dict:
        """메시지 전송"""
        try:
            payload = {
                "message": message,
                "session_id": session_id,
                "user_language": language
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "user_id": user_id,
                    "session_id": session_id,
                    "message": message,
                    "response": data.get('response', ''),
                    "chat_history": data.get('chat_history', []),
                    "success": True,
                    "timestamp": time.time()
                }
            else:
                return {
                    "user_id": user_id,
                    "session_id": session_id,
                    "message": message,
                    "error": f"HTTP {response.status_code}",
                    "success": False,
                    "timestamp": time.time()
                }
                
        except Exception as e:
            return {
                "user_id": user_id,
                "session_id": session_id,
                "message": message,
                "error": str(e),
                "success": False,
                "timestamp": time.time()
            }
    
    def simulate_user_conversation(self, user_id: str, num_messages: int = 5) -> list:
        """사용자 대화 시뮬레이션"""
        session_id = self.create_session()
        if not session_id:
            return [{"user_id": user_id, "error": "세션 생성 실패", "success": False}]
        
        messages = [
            f"안녕하세요! 저는 사용자 {user_id}입니다.",
            f"근로계약서에 대해 궁금한 점이 있습니다. (사용자 {user_id})",
            f"외국인 근로자의 권리에 대해 알려주세요. (사용자 {user_id})",
            f"임금 체불 시 어떻게 해야 하나요? (사용자 {user_id})",
            f"감사합니다. (사용자 {user_id})"
        ]
        
        results = []
        for i, message in enumerate(messages[:num_messages]):
            print(f"👤 사용자 {user_id}: 메시지 {i+1}/{num_messages} 전송")
            
            result = self.send_message(session_id, message, user_id)
            results.append(result)
            
            if result['success']:
                print(f"✅ 사용자 {user_id}: 응답 받음 (길이: {len(result['response'])})")
            else:
                print(f"❌ 사용자 {user_id}: 오류 - {result.get('error', 'Unknown')}")
            
            # 실제 사용자처럼 약간의 지연
            time.sleep(random.uniform(1, 3))
        
        return results
    
    def test_concurrent_users(self, num_users: int = 5, messages_per_user: int = 3):
        """동시 사용자 테스트"""
        print(f"🚀 {num_users}명의 동시 사용자 테스트 시작")
        print(f"   - 사용자당 메시지 수: {messages_per_user}")
        print(f"   - 총 예상 메시지 수: {num_users * messages_per_user}")
        print()
        
        start_time = time.time()
        
        # ThreadPoolExecutor로 동시 실행
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            # 각 사용자별로 작업 제출
            future_to_user = {
                executor.submit(self.simulate_user_conversation, f"USER_{i:02d}", messages_per_user): f"USER_{i:02d}"
                for i in range(1, num_users + 1)
            }
            
            # 결과 수집
            all_results = []
            for future in as_completed(future_to_user):
                user_id = future_to_user[future]
                try:
                    user_results = future.result()
                    all_results.extend(user_results)
                    print(f"✅ 사용자 {user_id} 완료")
                except Exception as e:
                    print(f"❌ 사용자 {user_id} 실패: {str(e)}")
                    self.errors.append(f"사용자 {user_id} 실패: {str(e)}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 결과 분석
        self.analyze_results(all_results, duration)
    
    def analyze_results(self, results: list, duration: float):
        """결과 분석"""
        print(f"\n📊 테스트 결과 분석")
        print(f"=" * 50)
        print(f"⏱️  총 소요 시간: {duration:.2f}초")
        print(f"📝 총 메시지 수: {len(results)}")
        
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]
        
        print(f"✅ 성공한 메시지: {len(successful)}")
        print(f"❌ 실패한 메시지: {len(failed)}")
        print(f"📈 성공률: {len(successful)/len(results)*100:.1f}%")
        
        if failed:
            print(f"\n❌ 실패 원인:")
            error_counts = {}
            for f in failed:
                error = f.get('error', 'Unknown')
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in error_counts.items():
                print(f"   - {error}: {count}회")
        
        # 세션 격리 검증
        print(f"\n🔍 세션 격리 검증")
        self.verify_session_isolation(successful)
        
        # 응답 시간 분석
        if successful:
            response_times = []
            for r in successful:
                if 'timestamp' in r:
                    response_times.append(r['timestamp'])
            
            if len(response_times) > 1:
                print(f"\n⏱️  응답 시간 분석:")
                print(f"   - 평균 응답 간격: {(max(response_times) - min(response_times))/len(response_times):.2f}초")
    
    def verify_session_isolation(self, successful_results: list):
        """세션 격리 검증"""
        session_messages = {}
        
        # 세션별로 메시지 그룹화
        for result in successful_results:
            session_id = result.get('session_id')
            user_id = result.get('user_id')
            
            if session_id:
                if session_id not in session_messages:
                    session_messages[session_id] = []
                
                session_messages[session_id].append({
                    'user_id': user_id,
                    'message': result.get('message', ''),
                    'response': result.get('response', '')
                })
        
        print(f"   - 총 세션 수: {len(session_messages)}")
        
        # 교차 오염 검사
        contamination_found = False
        for session_id, messages in session_messages.items():
            user_ids = set(msg['user_id'] for msg in messages)
            
            if len(user_ids) > 1:
                print(f"   ⚠️  세션 {session_id[:8]}...에서 여러 사용자 감지: {user_ids}")
                contamination_found = True
            
            # 응답에서 다른 사용자 ID 언급 검사
            for msg in messages:
                response = msg['response'].lower()
                current_user = msg['user_id']
                
                # 다른 사용자 ID가 응답에 언급되었는지 확인
                for other_user in [f"user_{i:02d}" for i in range(1, 21)]:
                    if other_user != current_user.lower() and other_user in response:
                        print(f"   ⚠️  사용자 {current_user}의 응답에서 {other_user} 언급 감지")
                        contamination_found = True
        
        if not contamination_found:
            print(f"   ✅ 세션 격리 정상 - 교차 오염 없음")
        else:
            print(f"   ❌ 세션 격리 문제 발견!")
    
    def test_different_languages(self):
        """다국어 동시 테스트"""
        print(f"\n🌍 다국어 동시 사용자 테스트")
        
        languages = ["korean", "english", "chinese", "vietnamese", "japanese"]
        messages = {
            "korean": "근로계약서에 대해 알려주세요.",
            "english": "Tell me about employment contracts.",
            "chinese": "请告诉我关于劳动合同的信息。",
            "vietnamese": "Hãy cho tôi biết về hợp đồng lao động.",
            "japanese": "労働契約について教えてください。"
        }
        
        with ThreadPoolExecutor(max_workers=len(languages)) as executor:
            futures = []
            
            for lang in languages:
                session_id = self.create_session()
                if session_id:
                    future = executor.submit(
                        self.send_message,
                        session_id,
                        messages[lang],
                        f"USER_{lang.upper()}",
                        lang
                    )
                    futures.append((future, lang))
            
            print(f"📤 {len(futures)}개 언어로 동시 메시지 전송...")
            
            for future, lang in futures:
                try:
                    result = future.result(timeout=30)
                    if result['success']:
                        print(f"✅ {lang}: 응답 길이 {len(result['response'])}")
                    else:
                        print(f"❌ {lang}: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"❌ {lang}: 예외 발생 - {str(e)}")

def main():
    print("🤖 LawRo 동시 사용자 테스트")
    print("=" * 50)
    
    # 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 서버 연결 확인")
        else:
            print(f"⚠️  서버 응답: {response.status_code}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {str(e)}")
        print("⚠️  테스트를 계속 진행하지만 결과가 부정확할 수 있습니다.")
    
    tester = ConcurrentUserTest()
    
    # 테스트 시나리오들
    print(f"\n📋 테스트 시나리오:")
    print(f"1. 소규모 동시 사용자 테스트 (5명)")
    print(f"2. 중간 규모 동시 사용자 테스트 (10명)")
    print(f"3. 다국어 동시 테스트")
    
    # 1. 소규모 테스트
    print(f"\n" + "="*50)
    print(f"📋 시나리오 1: 소규모 동시 사용자 테스트")
    tester.test_concurrent_users(num_users=5, messages_per_user=3)
    
    time.sleep(2)
    
    # 2. 중간 규모 테스트
    print(f"\n" + "="*50)
    print(f"📋 시나리오 2: 중간 규모 동시 사용자 테스트")
    tester.test_concurrent_users(num_users=10, messages_per_user=2)
    
    time.sleep(2)
    
    # 3. 다국어 테스트
    print(f"\n" + "="*50)
    print(f"📋 시나리오 3: 다국어 동시 테스트")
    tester.test_different_languages()
    
    # 최종 오류 요약
    if tester.errors:
        print(f"\n❌ 발생한 오류들:")
        for error in tester.errors[-10:]:  # 최근 10개만 표시
            print(f"   - {error}")
    else:
        print(f"\n✅ 모든 테스트가 오류 없이 완료되었습니다!")

if __name__ == "__main__":
    main() 