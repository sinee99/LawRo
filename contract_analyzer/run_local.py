"""
Contract Analyzer 로컬 실행 스크립트
"""
import uvicorn
import os
import sys

# 환경변수 설정
import local_env

# FastAPI 앱 import
from main import app

def main():
    """Contract Analyzer 로컬 실행"""
    print("🚀 Contract Analyzer 로컬 서버 시작")
    print("="*50)
    
    # 환경변수 확인
    print("📋 환경 설정:")
    print(f"   ChatBot 서버: {os.environ.get('CHATBOT_URL')}")
    print(f"   환경: {os.environ.get('CHATBOT_ENV')}")
    print(f"   포트: {os.environ.get('PORT', '8000')}")
    
    # 필수 환경변수 체크
    required_vars = ["S3_BUCKET_NAME", "UPSTAGE_API_KEY", "OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        value = os.environ.get(var)
        if not value or value.startswith("your-"):
            missing_vars.append(var)
    
    if missing_vars:
        print("\n⚠️ 다음 환경변수들을 실제 값으로 설정해 주세요:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n설정 방법:")
        print(f"   1. local_env.py 파일을 편집하여 실제 값으로 변경")
        print(f"   2. 또는 환경변수로 직접 설정")
        print("\n현재는 테스트 모드로 실행됩니다 (실제 분석은 실패할 수 있음)")
    
    print(f"\n🌐 서버 실행 중...")
    print(f"   URL: http://localhost:{os.environ.get('PORT', '8000')}")
    print(f"   API 문서: http://localhost:{os.environ.get('PORT', '8000')}/docs")
    print(f"   ChatBot 상태: http://localhost:{os.environ.get('PORT', '8000')}/api/chatbot-status")
    print("\n💡 종료하려면 Ctrl+C를 누르세요")
    print("="*50)
    
    # uvicorn으로 서버 실행
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get('PORT', '8000')),
        reload=True,  # 코드 변경 시 자동 재시작
        log_level="info"
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Contract Analyzer 서버가 종료되었습니다.")
    except Exception as e:
        print(f"\n❌ 서버 실행 오류: {str(e)}")
        sys.exit(1) 