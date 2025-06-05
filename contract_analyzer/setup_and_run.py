"""
Contract Analyzer 자동 설정 및 실행 스크립트
Python 가상환경 설정부터 서버 실행까지 한 번에 처리
"""
import subprocess
import sys
import os
import platform

def run_command(command, cwd=None):
    """명령어 실행"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ 명령어 실행 실패: {command}")
            print(f"오류: {result.stderr}")
            return False
        print(f"✅ 명령어 실행 성공: {command}")
        return True
    except Exception as e:
        print(f"❌ 명령어 실행 오류: {str(e)}")
        return False

def check_python():
    """Python 버전 확인"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        print(f"현재 버전: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python 버전 확인 완료: {version.major}.{version.minor}.{version.micro}")
    return True

def setup_virtual_environment():
    """가상환경 설정"""
    print("📦 Python 가상환경 설정 중...")
    
    # 가상환경 존재 확인
    if os.path.exists("venv"):
        print("⚠️ 기존 가상환경이 존재합니다. 삭제 후 새로 생성하시겠습니까? (y/n): ", end="")
        response = input().lower()
        if response == 'y':
            if platform.system() == "Windows":
                run_command("rmdir /s /q venv")
            else:
                run_command("rm -rf venv")
        else:
            print("기존 가상환경을 사용합니다.")
            return True
    
    # 가상환경 생성
    if not run_command(f"{sys.executable} -m venv venv"):
        return False
    
    print("✅ 가상환경 생성 완료")
    return True

def install_dependencies():
    """의존성 설치"""
    print("📚 의존성 패키지 설치 중...")
    
    # 가상환경의 pip 경로 확인
    if platform.system() == "Windows":
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # pip 업그레이드
    if not run_command(f"{pip_path} install --upgrade pip"):
        return False
    
    # requirements.txt 설치
    if not run_command(f"{pip_path} install -r requirements.txt"):
        return False
    
    print("✅ 의존성 설치 완료")
    return True

def setup_environment():
    """환경변수 설정"""
    print("⚙️ 환경변수 설정...")
    
    # local_env.py 파일 확인
    if not os.path.exists("local_env.py"):
        print("❌ local_env.py 파일이 없습니다.")
        return False
    
    print("✅ 환경변수 설정 파일 확인 완료")
    print("⚠️ local_env.py 파일에서 실제 API 키들을 설정해 주세요!")
    return True

def run_server():
    """서버 실행"""
    print("🚀 Contract Analyzer 서버 실행 중...")
    
    # 가상환경의 python 경로
    if platform.system() == "Windows":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    # 서버 실행
    try:
        subprocess.run([python_path, "run_local.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 오류: {str(e)}")
        return False
    
    return True

def main():
    """메인 함수"""
    print("🔧 Contract Analyzer 자동 설정 및 실행")
    print("="*60)
    
    # Python 버전 확인
    if not check_python():
        sys.exit(1)
    
    # 현재 디렉토리 확인
    if not os.path.exists("main.py"):
        print("❌ contract_analyzer 디렉토리에서 실행해 주세요.")
        print("현재 위치:", os.getcwd())
        sys.exit(1)
    
    steps = [
        ("가상환경 설정", setup_virtual_environment),
        ("의존성 설치", install_dependencies),
        ("환경변수 설정", setup_environment),
        ("서버 실행", run_server)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 단계: {step_name}")
        print("-" * 40)
        
        if not step_func():
            print(f"❌ {step_name} 실패")
            sys.exit(1)
        
        print(f"✅ {step_name} 완료")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 설정이 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {str(e)}")
        sys.exit(1) 