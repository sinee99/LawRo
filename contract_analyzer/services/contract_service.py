import json
from utils.s3_utils import upload_json_to_s3

def save_contract_to_s3(user_id: str, contract_id: str, contract_data: dict):
    key = f"user_{user_id}/contracts/{contract_id}/final.json"
    upload_json_to_s3(bucket="your-bucket-name", key=key, data=contract_data)
