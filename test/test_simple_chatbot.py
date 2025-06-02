import os
from dotenv import load_dotenv

load_dotenv()

def test_basic_chat():
    """기본 챗봇 기능을 테스트합니다"""
    try:
        from langchain_upstage import ChatUpstage
        
        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            print("❌ UPSTAGE_API_KEY가 설정되지 않았습니다.")
            return False
            
        # 기본 LLM만 테스트
        chat = ChatUpstage(
            model="solar-pro",
            upstage_api_key=api_key
        )
        
        print("🤖 LawRo 법률 상담 테스트")
        print("="*40)
        
        # 테스트 질문들
        test_questions = [
            "근로기준법에서 연장근로에 대해 설명해주세요.",
            "최저임금 위반 시 어떤 처벌을 받나요?",
            "부당해고를 당했을 때 어떻게 대응해야 하나요?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n📋 질문 {i}: {question}")
            try:
                response = chat.invoke(f"법률 전문가로서 다음 질문에 답변해주세요: {question}")
                print(f"💡 답변: {response.content[:200]}...")
                print("✅ 성공")
            except Exception as e:
                print(f"❌ 오류: {e}")
                
        return True
        
    except ImportError as e:
        print(f"❌ 패키지 임포트 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def test_rag_system():
    """RAG 시스템을 테스트합니다"""
    try:
        from langchain_chroma import Chroma
        from langchain_upstage import UpstageEmbeddings
        
        api_key = os.getenv("UPSTAGE_API_KEY")
        
        # 벡터스토어 로딩 테스트
        embedding = UpstageEmbeddings(
            model="solar-embedding-1-large",
            upstage_api_key=api_key
        )
        
        vectorstore = Chroma(
            persist_directory="chroma_db",
            embedding_function=embedding
        )
        
        # 검색 테스트
        docs = vectorstore.similarity_search("해고", k=2)
        print(f"\n🔍 벡터 검색 테스트:")
        print(f"✅ {len(docs)}개 문서 검색됨")
        
        for i, doc in enumerate(docs, 1):
            content = doc.page_content[:100] if hasattr(doc, 'page_content') else str(doc)[:100]
            print(f"📄 문서 {i}: {content}...")
            
        return True
        
    except Exception as e:
        print(f"❌ RAG 시스템 오류: {e}")
        return False

if __name__ == "__main__":
    print("🧪 LawRo 시스템 테스트 시작")
    print("="*50)
    
    # 1. 기본 챗봇 테스트
    basic_success = test_basic_chat()
    
    # 2. RAG 시스템 테스트  
    if basic_success:
        print("\n" + "="*50)
        rag_success = test_rag_system()
        
        if rag_success:
            print("\n🎉 모든 테스트 성공! 시스템이 정상 작동합니다.")
        else:
            print("\n⚠️ RAG 시스템에 문제가 있지만, 기본 챗봇은 작동합니다.")
    else:
        print("\n❌ 기본 시스템에 문제가 있습니다. 환경설정을 확인하세요.") 