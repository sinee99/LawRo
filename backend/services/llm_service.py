import os
import time
from typing import List, Optional
from models.response_models import LLMJudgmentResponse

class LLMService:
    """LLM 기반 판단 서비스"""
    
    def __init__(self):
        self.api_key = os.getenv("UPSTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY 환경변수가 설정되지 않았습니다.")
    
    async def get_judgment(self, text: str, focus_areas: Optional[List[str]] = None) -> LLMJudgmentResponse:
        """LLM을 사용하여 계약서 내용을 판단합니다."""
        start_time = time.time()
        
        try:
            # 실제 구현에서는 langchain_upstage.ChatUpstage 사용
            # 현재는 임시 응답 반환
            judgment = "계약서 분석 결과, 전반적으로 근로기준법에 준수하는 내용으로 보입니다."
            confidence_score = 0.85
            
            processing_time = time.time() - start_time
            
            return LLMJudgmentResponse(
                success=True,
                judgment=judgment,
                confidence_score=confidence_score,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return LLMJudgmentResponse(
                success=False,
                judgment=f"판단 중 오류가 발생했습니다: {str(e)}",
                confidence_score=0.0,
                processing_time=processing_time
            ) 