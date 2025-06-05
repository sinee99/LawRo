import os
from dotenv import load_dotenv

load_dotenv()

UPSTAGE_OCR_API_KEY = os.getenv("UPSTAGE_OCR_API_KEY")
UPSTAGE_OCR_ENDPOINT = "https://api.upstage.ai/v1/document-digitization"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TMP_DIR = os.getenv("TMP_DIR")