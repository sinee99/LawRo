import os
from langchain_upstage import UpstageEmbeddings
from langchain_chroma import Chroma
from langchain_upstage import ChatUpstage
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("UPSTAGE_API_KEY")

embedding = UpstageEmbeddings(
    model="solar-embedding-1-large",
    upstage_api_key=API_KEY
)

vectorstore = Chroma(
    persist_directory="../storage/chroma_db",
    embedding_function=embedding
)

llm = ChatUpstage(
    model="solar-pro",
    upstage_api_key=API_KEY,
    temperature=0.2
)

prompt = PromptTemplate(
    template="""
다음은 근로계약서의 내용입니다. 아래 제공된 법률 문서들을 참고하여 이 계약서 내용이 위법 소지가 있는지 판단해주세요.

[계약서 내용]
{question}

[법률 근거]
{context}

당신의 판단:
""",
    input_variables=["question", "context"]
)

qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=True
)

def get_rag_result(text: str) -> dict:
    return qa({"query": text})