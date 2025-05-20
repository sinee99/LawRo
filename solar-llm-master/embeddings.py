# save_embeddings.py
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_upstage import UpstageEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ▶️ 디렉토리 준비
os.makedirs("chroma_db", exist_ok=True)

law_files = [
    "law_data/law_foreign.pdf",
    "law_data/law_mwage.pdf",
    "law_data/law_worker.pdf"
]

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " "]
)

all_chunks = []
for path in law_files:
    loader = PyPDFLoader(path)
    pages = loader.load()
    chunks = splitter.split_documents(pages)
    
    for chunk in chunks:
        chunk.metadata["source"] = os.path.basename(path)
    all_chunks.extend(chunks)

embedding = UpstageEmbeddings(
    model="solar-embedding-1-large",
    upstage_api_key=os.getenv("UPSTAGE_API_KEY")
)

vectorstore = Chroma.from_documents(
    documents=all_chunks,
    embedding=embedding,
    persist_directory="chroma_db"
)

# ✅ persist() 사용 가능
vectorstore.persist()
print("✅ 벡터 저장 완료: chroma_db/")
