"""
전체 파이프라인 테스트 실행 스크립트
Contract Analyzer 서버가 실행 중이어야 합니다.
"""
import subprocess
import sys
import time
import requests
import os

def check_server_running():
    """Contract Analyzer 서버 실행 상태 확인"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_chatbot_connection():
    """ChatBot 서버 연결 확인"""
    try:
        response = requests.get("http://localhost:8000/api/chatbot-status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('chatbot_available', False)
        return False
    except:
        return False

def main():
    print("🧪 전체 파이프라인 테스트 준비")
    print("="*50)
    
    # 1. Contract Analyzer 서버 확인
    print("🔍 Contract Analyzer 서버 상태 확인...")
    if not check_server_running():
        print("❌ Contract Analyzer 서버가 실행되지 않았습니다!")
        print("\n다음 명령으로 서버를 먼저 실행해 주세요:")
        print("  python run_local.py")
        print("  또는")
        print("  python setup_and_run.py")
        return False
    
    print("✅ Contract Analyzer 서버 실행 중")
    
    # 2. ChatBot 연결 확인
    print("🔍 ChatBot 서버 연결 확인...")
    if not check_chatbot_connection():
        print("⚠️ ChatBot 서버 연결에 문제가 있습니다.")
        print("   테스트는 계속 진행되지만 법률 분석이 제한될 수 있습니다.")
    else:
        print("✅ ChatBot 서버 연결 정상")
    
    # 3. 테스트 이미지 확인
    test_image = "../test/ex2.png"
    if not os.path.exists(test_image):
        print(f"❌ 테스트 이미지를 찾을 수 없습니다: {test_image}")
        return False
    
    print(f"✅ 테스트 이미지 확인: {test_image}")
    
    # 4. 환경변수 확인
    required_env = ["S3_BUCKET_NAME", "AWS_ACCESS_KEY_ID", "UPSTAGE_OCR_API_KEY", "OPENAI_API_KEY"]
    missing_env = []
    
    for env_var in required_env:
        if not os.environ.get(env_var) or os.environ.get(env_var).startswith("your-"):
            missing_env.append(env_var)
    
    if missing_env:
        print("⚠️ 다음 환경변수가 설정되지 않았습니다:")
        for env_var in missing_env:
            print(f"   - {env_var}")
        print("   local_env.py에서 실제 값으로 설정해 주세요.")
        
        proceed = input("\n계속 진행하시겠습니까? (일부 기능이 실패할 수 있음) (y/n): ")
        if proceed.lower() != 'y':
            return False
    else:
        print("✅ 모든 환경변수 설정 완료")
    
    print("\n🚀 전체 파이프라인 테스트를 시작합니다!")
    print("=" * 50)
    print("테스트 과정:")
    print("1. ex2.png 이미지를 S3에 업로드")
    print("2. OCR로 텍스트 추출")
    print("3. LLM으로 계약서 데이터 구조화")
    print("4. ChatBot으로 전문 법률 분석")
    print("5. 최종 결과 출력 및 파일 저장")
    print("=" * 50)
    
    proceed = input("\n진행하시겠습니까? (y/n): ")
    if proceed.lower() != 'y':
        print("테스트가 취소되었습니다.")
        return False
    
    # 5. 테스트 실행
    try:
        print("\n📋 전체 파이프라인 테스트 실행 중...")
        
        # 환경변수 설정 후 테스트 모듈 import
        import local_env
        from test_full_pipeline import FullPipelineTest
        
        # 테스트 실행
        tester = FullPipelineTest()
        success = tester.run_full_test()
        
        return success
        
    except ImportError as e:
        print(f"❌ 모듈 import 오류: {str(e)}")
        print("필요한 의존성이 설치되지 않았을 수 있습니다.")
        print("다음 명령으로 설치해 주세요: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ 테스트 실행 오류: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        
        if success:
            print("\n🎉 전체 파이프라인 테스트 완료!")
            print("📁 결과 파일들이 'test_results/' 디렉토리에 저장되었습니다.")
            print("\n📋 다음 단계:")
            print("   1. test_results/ 폴더에서 상세 결과 확인")
            print("   2. 법률 분석 텍스트 파일 검토")
            print("   3. JSON 파일로 전체 데이터 구조 확인")
        else:
            print("\n❌ 테스트가 실패했습니다.")
            print("로그를 확인하고 설정을 점검해 주세요.")
            
    except KeyboardInterrupt:
        print("\n⏹️ 테스트가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {str(e)}")
        sys.exit(1) 