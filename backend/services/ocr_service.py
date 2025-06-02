import os
import requests
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class OCRService:
    """Upstage OCR API를 사용한 텍스트 추출 서비스"""
    
    def __init__(self):
        self.api_key = os.getenv("UPSTAGE_API_KEY")
        self.ocr_url = "https://ap-northeast-2.apistage.ai/v1/document-ai/ocr"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY 환경변수가 설정되지 않았습니다.")
    
    async def extract_text(self, file_content: bytes, filename: str) -> str:
        """
        이미지에서 텍스트를 추출합니다.
        
        Args:
            file_content: 이미지 파일 바이트 데이터
            filename: 파일명
        
        Returns:
            str: 추출된 텍스트
        """
        try:
            files = {"image": (filename, file_content)}
            
            # 비동기 요청을 위해 requests를 별도 스레드에서 실행
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.post(self.ocr_url, headers=self.headers, files=files)
            )
            
            if response.status_code == 200:
                result = response.json()
                # 페이지별 텍스트를 하나로 합침
                text = " ".join([
                    page.get("text", "") 
                    for page in result.get("pages", [])
                ])
                return text
            else:
                raise Exception(f"OCR API 오류: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"OCR 처리 중 오류 발생: {str(e)}")
    
    async def health_check(self) -> bool:
        """
        OCR API 연결 상태를 확인합니다.
        
        Returns:
            bool: 연결 상태
        """
        try:
            # 더미 요청을 보내서 API 상태 확인
            test_data = b"test"
            files = {"image": ("test.jpg", test_data)}
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    self.ocr_url, 
                    headers=self.headers, 
                    files=files,
                    timeout=10
                )
            )
            
            # 400번대 에러도 API가 살아있다는 의미
            return response.status_code < 500
            
        except Exception:
            return False 