from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import upload, analyze_copy

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(analyze_copy.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Contract Analyzer API is running"}
