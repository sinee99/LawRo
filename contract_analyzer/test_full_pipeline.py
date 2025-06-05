"""
전체 파이프라인 테스트: ex2.png 이미지 업로드부터 최종 법률 분석까지
실제 엔드유저가 받게 되는 최종 출력 데이터를 확인하는 테스트
"""
import requests
import json
import os
import time
import boto3
from datetime import datetime
from typing import Dict, Any
import shutil
from pathlib import Path

# 환경변수 설정
import local_env

class FullPipelineTest:
    """전체 파이프라인 테스트 클래스"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.environ.get('S3_BUCKET_NAME')
        self.test_user_id = f"test_user_{int(time.time())}"
        self.test_contract_id = f"contract_{int(time.time())}"
        self.test_image_path = "../test/ex2.png"
        
        print(f"🧪 전체 파이프라인 테스트 초기화")
        print(f"   사용자 ID: {self.test_user_id}")
        print(f"   계약서 ID: {self.test_contract_id}")
        print(f"   S3 버킷: {self.bucket_name}")
        
    def check_image_file(self):
        """테스트 이미지 파일 확인"""
        print("\n📁 테스트 이미지 파일 확인")
        
        if not os.path.exists(self.test_image_path):
            print(f"❌ 이미지 파일을 찾을 수 없습니다: {self.test_image_path}")
            return False
        
        file_size = os.path.getsize(self.test_image_path) / 1024  # KB
        print(f"✅ 이미지 파일 확인: {self.test_image_path}")
        print(f"   파일 크기: {file_size:.1f} KB")
        
        return True
    
    def upload_image_to_s3(self):
        """이미지를 S3에 업로드"""
        print("\n☁️ S3에 이미지 업로드")
        
        try:
            # S3 키 생성 (contract_analyzer의 예상 경로)
            s3_key = f"user_{self.test_user_id}/contracts/{self.test_contract_id}/page_1.png"
            
            print(f"   업로드 경로: s3://{self.bucket_name}/{s3_key}")
            
            # 파일 업로드
            self.s3_client.upload_file(
                self.test_image_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': 'image/png'}
            )
            
            print(f"✅ S3 업로드 성공")
            print(f"   S3 키: {s3_key}")
            
            return True
            
        except Exception as e:
            print(f"❌ S3 업로드 실패: {str(e)}")
            return False
    
    def test_basic_analysis(self):
        """기본 계약서 분석 테스트 (ChatBot 없이)"""
        print("\n🔍 기본 계약서 분석 테스트")
        
        payload = {
            "user_id": self.test_user_id,
            "contract_id": self.test_contract_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/analyze",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ 기본 분석 성공")
                print(f"   메시지: {result.get('message', 'N/A')}")
                print(f"   페이지 요약 수: {len(result.get('page_summaries', []))}")
                
                # 구조화된 결과 확인
                structured_result = result.get('structured_result', {})
                if structured_result:
                    print(f"   구조화된 데이터 키: {list(structured_result.keys())}")
                    
                return result
            else:
                print(f"❌ 기본 분석 실패: HTTP {response.status_code}")
                print(f"   응답: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ 기본 분석 오류: {str(e)}")
            return None
    
    def test_chatbot_integration_analysis(self):
        """ChatBot 통합 분석 테스트 (최종 엔드유저 출력)"""
        print("\n🤖 ChatBot 통합 분석 테스트 (최종 결과)")
        
        payload = {
            "user_id": self.test_user_id,
            "contract_id": self.test_contract_id,
            "use_chatbot": True,
            "user_language": "korean"
        }
        
        try:
            print(f"📤 ChatBot 통합 분석 요청 전송...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/analyze-with-chatbot",
                json=payload,
                timeout=180  # 충분한 시간 확보
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ ChatBot 통합 분석 성공!")
                print(f"   총 처리시간: {processing_time:.2f}초")
                print(f"   메시지: {result.get('message', 'N/A')}")
                
                # 세션 ID 확인
                session_id = result.get('session_id')
                if session_id:
                    print(f"   생성된 세션 ID: {session_id[:8]}...")
                
                return result
                
            else:
                print(f"❌ ChatBot 통합 분석 실패: HTTP {response.status_code}")
                error_details = response.text[:500] if response.text else "응답 없음"
                print(f"   오류 상세: {error_details}")
                return None
                
        except Exception as e:
            print(f"❌ ChatBot 통합 분석 오류: {str(e)}")
            return None
    
    def display_final_results(self, result: Dict[str, Any]):
        """최종 결과 데이터 출력 (엔드유저가 받는 데이터)"""
        print("\n" + "="*80)
        print("📋 최종 엔드유저 출력 데이터")
        print("="*80)
        
        # 1. 기본 정보
        print(f"\n📄 계약서 분석 결과")
        print(f"   사용자 ID: {result.get('user_id', self.test_user_id)}")
        print(f"   계약서 ID: {self.test_contract_id}")
        print(f"   처리 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 2. 페이지별 요약
        page_summaries = result.get('page_summaries', [])
        print(f"\n📝 페이지별 요약 ({len(page_summaries)}개)")
        for i, summary in enumerate(page_summaries, 1):
            print(f"   페이지 {i}: {summary[:100]}..." if len(summary) > 100 else f"   페이지 {i}: {summary}")
        
        # 3. 구조화된 계약서 데이터
        structured_result = result.get('structured_result', {})
        print(f"\n📊 구조화된 계약서 데이터")
        self._display_structured_data(structured_result)
        
        # 4. ChatBot 법률 분석 (핵심!)
        chatbot_analysis = result.get('chatbot_analysis')
        if chatbot_analysis:
            if 'error' in chatbot_analysis:
                print(f"\n⚠️ ChatBot 분석 오류")
                print(f"   오류: {chatbot_analysis['error']}")
            else:
                print(f"\n⚖️ 전문 법률 분석")
                legal_analysis = chatbot_analysis.get('legal_analysis', '')
                processing_time = chatbot_analysis.get('processing_time', 0)
                
                print(f"   분석 처리시간: {processing_time:.2f}초")
                print(f"   분석 내용 길이: {len(legal_analysis)}자")
                print(f"\n📋 법률 분석 내용:")
                print("-" * 60)
                print(legal_analysis)
                print("-" * 60)
        else:
            print(f"\n⚠️ ChatBot 법률 분석 결과 없음")
        
        # 5. 세션 정보
        session_id = result.get('session_id')
        if session_id:
            print(f"\n🔐 세션 정보")
            print(f"   세션 ID: {session_id}")
            print(f"   추가 질문 가능: ✅")
    
    def _display_structured_data(self, data: Dict[str, Any], indent: int = 0):
        """구조화된 데이터를 보기 좋게 출력"""
        if not data:
            print("   (구조화된 데이터 없음)")
            return
        
        for key, value in data.items():
            spaces = "   " + "  " * indent
            
            if isinstance(value, dict):
                print(f"{spaces}{key}:")
                self._display_structured_data(value, indent + 1)
            elif isinstance(value, list):
                print(f"{spaces}{key}: [{len(value)}개 항목]")
                for i, item in enumerate(value[:3]):  # 처음 3개만 표시
                    print(f"{spaces}  - {item}")
                if len(value) > 3:
                    print(f"{spaces}  ... (총 {len(value)}개)")
            else:
                # 길이가 긴 문자열은 축약
                if isinstance(value, str) and len(value) > 100:
                    print(f"{spaces}{key}: {value[:100]}...")
                else:
                    print(f"{spaces}{key}: {value}")
    
    def save_results_to_file(self, result: Dict[str, Any]):
        """결과를 파일로 저장"""
        print(f"\n💾 결과 파일 저장")
        
        try:
            # 결과 디렉토리 생성
            results_dir = Path("test_results")
            results_dir.mkdir(exist_ok=True)
            
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pipeline_test_{timestamp}.json"
            filepath = results_dir / filename
            
            # JSON 파일로 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 결과 저장 완료: {filepath}")
            
            # 법률 분석만 별도 텍스트 파일로 저장
            chatbot_analysis = result.get('chatbot_analysis', {})
            legal_analysis = chatbot_analysis.get('legal_analysis', '')
            
            if legal_analysis:
                text_filename = f"legal_analysis_{timestamp}.txt"
                text_filepath = results_dir / text_filename
                
                with open(text_filepath, 'w', encoding='utf-8') as f:
                    f.write("=" * 50 + "\n")
                    f.write("전문 법률 분석 결과\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"사용자 ID: {self.test_user_id}\n")
                    f.write(f"계약서 ID: {self.test_contract_id}\n\n")
                    f.write(legal_analysis)
                
                print(f"✅ 법률 분석 텍스트 저장: {text_filepath}")
            
            return str(filepath)
            
        except Exception as e:
            print(f"❌ 파일 저장 실패: {str(e)}")
            return None
    
    def cleanup_s3_files(self):
        """테스트 후 S3 파일 정리"""
        print(f"\n🧹 S3 테스트 파일 정리")
        
        try:
            # 테스트로 업로드한 파일들 삭제
            prefix = f"user_{self.test_user_id}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                delete_objects = [{'Key': obj['Key']} for obj in response['Contents']]
                
                self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': delete_objects}
                )
                
                print(f"✅ {len(delete_objects)}개 파일 삭제 완료")
            else:
                print(f"   삭제할 파일 없음")
                
        except Exception as e:
            print(f"⚠️ S3 정리 실패: {str(e)}")
    
    def run_full_test(self):
        """전체 파이프라인 테스트 실행"""
        print("🚀 전체 파이프라인 테스트 시작")
        print("="*80)
        print("실제 이미지 → S3 업로드 → OCR → 파싱 → ChatBot 법률 분석 → 최종 결과")
        print("="*80)
        
        try:
            # 1. 이미지 파일 확인
            if not self.check_image_file():
                return False
            
            # 2. S3 업로드
            if not self.upload_image_to_s3():
                return False
            
            # 3. 기본 분석 테스트 (선택사항)
            print(f"\n⚠️ 기본 분석 테스트를 실행하시겠습니까? (y/n): ", end="")
            run_basic = input().lower() == 'y'
            
            if run_basic:
                basic_result = self.test_basic_analysis()
                if basic_result:
                    print(f"✅ 기본 분석 완료")
            
            # 4. ChatBot 통합 분석 (메인 테스트)
            final_result = self.test_chatbot_integration_analysis()
            
            if final_result:
                # 5. 최종 결과 출력
                self.display_final_results(final_result)
                
                # 6. 결과 파일 저장
                saved_file = self.save_results_to_file(final_result)
                
                print(f"\n🎉 전체 파이프라인 테스트 성공!")
                if saved_file:
                    print(f"📄 상세 결과는 다음 파일에서 확인: {saved_file}")
                
                return True
            else:
                print(f"\n❌ 전체 파이프라인 테스트 실패")
                return False
                
        except KeyboardInterrupt:
            print(f"\n⏹️ 테스트가 중단되었습니다.")
            return False
        except Exception as e:
            print(f"\n❌ 예상치 못한 오류: {str(e)}")
            return False
        finally:
            # 7. 정리 작업
            cleanup = input(f"\nS3 테스트 파일을 삭제하시겠습니까? (y/n): ").lower() == 'y'
            if cleanup:
                self.cleanup_s3_files()

if __name__ == "__main__":
    # 전체 파이프라인 테스트 실행
    tester = FullPipelineTest()
    success = tester.run_full_test()
    
    if success:
        print(f"\n✅ 테스트 완료! 엔드유저가 받는 최종 데이터를 확인했습니다.")
        print(f"📁 결과 파일들이 'test_results/' 디렉토리에 저장되었습니다.")
    else:
        print(f"\n❌ 테스트 실패. 로그를 확인해 주세요.") 