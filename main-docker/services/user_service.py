import os
import hashlib
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from models import UserSignupRequest, UserSignupResponse, UserLoginRequest, UserLoginResponse, ContractAnalyzeResponse

class UserService:
    """Firestore를 사용한 사용자 관리 서비스"""
    
    def __init__(self):
        # Firebase 초기화
        self._initialize_firebase()
        
        # JWT 설정
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "lawro-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
        self.jwt_expiration_hours = 24
        
        # Firestore 컬렉션 이름
        self.users_collection = "users"
        self.contracts_collection = "contract_analyses"
    
    def _initialize_firebase(self):
        """Firebase 초기화"""
        try:
            # Firebase 서비스 계정 키 파일 경로
            service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "firebase-service-account.json")
            
            if not firebase_admin._apps:
                if os.path.exists(service_account_path):
                    # 서비스 계정 키 파일 사용
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # 환경 변수에서 직접 설정 (Docker 환경에서 유용)
                    firebase_config = {
                        "type": "service_account",
                        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                        "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
                        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                    cred = credentials.Certificate(firebase_config)
                    firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            print("✅ Firebase 초기화 완료")
            
        except Exception as e:
            print(f"❌ Firebase 초기화 실패: {e}")
            # 테스트 환경에서는 Mock 사용
            self.db = None
    
    def _hash_password(self, password: str) -> str:
        """비밀번호 해시화"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_jwt_token(self, user_id: str) -> str:
        """JWT 토큰 생성"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expiration_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("토큰이 만료되었습니다")
        except jwt.InvalidTokenError:
            raise ValueError("유효하지 않은 토큰입니다")
    
    async def create_user(self, request: UserSignupRequest) -> UserSignupResponse:
        """사용자 회원가입"""
        try:
            if not self.db:
                raise Exception("Firestore 연결이 없습니다")
            
            # 사용자 ID 중복 확인
            user_ref = self.db.collection(self.users_collection).document(request.user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                return UserSignupResponse(
                    success=False,
                    message="이미 존재하는 사용자 ID입니다",
                    user_id=None,
                    token=None
                )
            
            # 이메일 중복 확인
            users_ref = self.db.collection(self.users_collection)
            email_query = users_ref.where(filter=FieldFilter("email", "==", request.email))
            email_docs = email_query.get()
            
            if email_docs:
                return UserSignupResponse(
                    success=False,
                    message="이미 사용 중인 이메일입니다",
                    user_id=None,
                    token=None
                )
            
            # 비밀번호 해시화
            hashed_password = self._hash_password(request.password)
            
            # 사용자 데이터 생성
            user_data = {
                "user_id": request.user_id,
                "password": hashed_password,
                "email": request.email,
                "name": request.name,
                "phone": request.phone,
                "created_at": datetime.now(),
                "last_login": None,
                "is_active": True
            }
            
            # Firestore에 저장
            user_ref.set(user_data)
            
            # JWT 토큰 생성
            token = self._generate_jwt_token(request.user_id)
            
            return UserSignupResponse(
                success=True,
                message="회원가입이 완료되었습니다",
                user_id=request.user_id,
                token=token
            )
            
        except Exception as e:
            return UserSignupResponse(
                success=False,
                message=f"회원가입 중 오류가 발생했습니다: {str(e)}",
                user_id=None,
                token=None
            )
    
    async def authenticate_user(self, request: UserLoginRequest) -> UserLoginResponse:
        """사용자 로그인"""
        try:
            if not self.db:
                raise Exception("Firestore 연결이 없습니다")
            
            # 사용자 조회
            user_ref = self.db.collection(self.users_collection).document(request.user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return UserLoginResponse(
                    success=False,
                    message="존재하지 않는 사용자입니다",
                    token=None,
                    user_data=None
                )
            
            user_data = user_doc.to_dict()
            
            # 비밀번호 확인
            hashed_password = self._hash_password(request.password)
            if user_data["password"] != hashed_password:
                return UserLoginResponse(
                    success=False,
                    message="비밀번호가 틀렸습니다",
                    token=None,
                    user_data=None
                )
            
            # 활성 사용자 확인
            if not user_data.get("is_active", True):
                return UserLoginResponse(
                    success=False,
                    message="비활성화된 계정입니다",
                    token=None,
                    user_data=None
                )
            
            # 마지막 로그인 시간 업데이트
            user_ref.update({"last_login": datetime.now()})
            
            # JWT 토큰 생성
            token = self._generate_jwt_token(request.user_id)
            
            # 민감한 정보 제거
            safe_user_data = {
                "user_id": user_data["user_id"],
                "email": user_data["email"],
                "name": user_data.get("name"),
                "phone": user_data.get("phone"),
                "created_at": user_data["created_at"]
            }
            
            return UserLoginResponse(
                success=True,
                message="로그인에 성공했습니다",
                token=token,
                user_data=safe_user_data
            )
            
        except Exception as e:
            return UserLoginResponse(
                success=False,
                message=f"로그인 중 오류가 발생했습니다: {str(e)}",
                token=None,
                user_data=None
            )
    
    async def get_user_by_token(self, token: str) -> Dict[str, Any]:
        """토큰으로 사용자 정보 조회"""
        try:
            if not self.db:
                raise Exception("Firestore 연결이 없습니다")
            
            # 토큰 검증
            payload = self._verify_jwt_token(token)
            user_id = payload["user_id"]
            
            # 사용자 조회
            user_ref = self.db.collection(self.users_collection).document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                raise ValueError("존재하지 않는 사용자입니다")
            
            user_data = user_doc.to_dict()
            
            # 민감한 정보 제거
            safe_user_data = {
                "user_id": user_data["user_id"],
                "email": user_data["email"],
                "name": user_data.get("name"),
                "phone": user_data.get("phone"),
                "created_at": user_data["created_at"],
                "last_login": user_data.get("last_login")
            }
            
            return safe_user_data
            
        except Exception as e:
            raise ValueError(f"사용자 조회 실패: {str(e)}")
    
    async def save_contract_analysis(self, user_id: str, analysis_response: ContractAnalyzeResponse):
        """계약서 분석 결과 저장"""
        try:
            if not self.db or not analysis_response.success:
                return
            
            # 분석 히스토리 데이터 생성
            analysis_data = {
                "analysis_id": analysis_response.analysis_id or str(uuid.uuid4()),
                "user_id": user_id,
                "analysis_result": analysis_response.analysis_result,
                "processing_time": analysis_response.processing_time,
                "created_at": datetime.now()
            }
            
            # Firestore에 저장
            self.db.collection(self.contracts_collection).add(analysis_data)
            
        except Exception as e:
            print(f"⚠️ 계약서 분석 결과 저장 실패: {e}")
    
    async def get_contract_history(self, user_id: str) -> List[Dict[str, Any]]:
        """사용자의 계약서 분석 히스토리 조회"""
        try:
            if not self.db:
                return []
            
            # 사용자의 분석 히스토리 조회
            contracts_ref = self.db.collection(self.contracts_collection)
            query = contracts_ref.where(filter=FieldFilter("user_id", "==", user_id)).order_by("created_at", direction=firestore.Query.DESCENDING)
            docs = query.get()
            
            history = []
            for doc in docs:
                data = doc.to_dict()
                history.append({
                    "analysis_id": data.get("analysis_id"),
                    "analysis_result": data.get("analysis_result"),
                    "processing_time": data.get("processing_time"),
                    "created_at": data.get("created_at")
                })
            
            return history
            
        except Exception as e:
            print(f"⚠️ 계약서 히스토리 조회 실패: {e}")
            return []
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """사용자 통계 조회"""
        try:
            if not self.db:
                return {"total_users": 0, "active_users": 0}
            
            # 전체 사용자 수
            users_ref = self.db.collection(self.users_collection)
            total_users = len(users_ref.get())
            
            # 활성 사용자 수 (최근 30일 내 로그인)
            cutoff_date = datetime.now() - timedelta(days=30)
            active_query = users_ref.where(filter=FieldFilter("last_login", ">=", cutoff_date))
            active_users = len(active_query.get())
            
            return {
                "total_users": total_users,
                "active_users": active_users
            }
            
        except Exception as e:
            print(f"⚠️ 사용자 통계 조회 실패: {e}")
            return {"total_users": 0, "active_users": 0} 