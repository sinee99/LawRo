from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from services.contract_service import save_contract_to_s3

router = APIRouter()

class SaveContractRequest(BaseModel):
    user_id: str
    contract_id: str
    structured_result: Dict  # 사용자가 수정한 전체 계약 항목 JSON

@router.post("/contracts/save")
def save_contract(req: SaveContractRequest):
    try:
        save_contract_to_s3(
            user_id=req.user_id,
            contract_id=req.contract_id,
            contract_data=req.structured_result
        )
        return {"message": "계약서 저장 완료"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
