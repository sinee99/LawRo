from lawro_client import LawRoClient, quick_chat, analyze_contract_with_custom_prompt, multi_language_chat

def example_1_basic_chat():
    """예제 1: 기본적인 채팅"""
    print("📋 예제 1: 기본적인 채팅")
    print("-" * 30)
    
    # 클라이언트 생성
    client = LawRoClient()
    
    # 간단한 질문들
    questions = [
        "근로계약서란 무엇인가요?",
        "최저임금은 얼마인가요?",
        "연차휴가는 몇 일인가요?"
    ]
    
    for question in questions:
        print(f"👤 질문: {question}")
        response = client.send_message(question)
        
        if response.success:
            print(f"🤖 답변: {response.response[:200]}...")
            print(f"⏱️ 처리시간: {response.processing_time:.2f}초")
        else:
            print(f"❌ 오류: {response.error}")
        print()

def example_2_custom_prompt():
    """예제 2: 커스텀 프롬프트 사용"""
    print("📋 예제 2: 커스텀 프롬프트 사용")
    print("-" * 30)
    
    client = LawRoClient()
    
    # JSON 형태 분석 프롬프트
    json_prompt = """
    당신은 계약서 분석 전문가입니다. 
    다음 형태의 JSON으로 답변해주세요:
    {
        "analysis": "분석 내용",
        "risk_score": 1-10,
        "recommendations": ["권장사항1", "권장사항2"],
        "key_points": ["핵심포인트1", "핵심포인트2"]
    }
    """
    
    question = "외국인 근로자 계약서에서 주의해야 할 점이 무엇인가요?"
    
    print(f"👤 질문: {question}")
    print(f"🎯 커스텀 프롬프트: JSON 형태 분석")
    
    response = client.send_message(question, custom_prompt=json_prompt)
    
    if response.success:
        print(f"🤖 JSON 답변:")
        print(response.response)
    else:
        print(f"❌ 오류: {response.error}")
    
    print()
    
    # 다음 질문 (자동으로 기본 프롬프트로 복귀)
    next_question = "퇴직금은 어떻게 계산하나요?"
    print(f"👤 다음 질문 (기본 프롬프트): {next_question}")
    
    response = client.send_message(next_question)
    if response.success:
        print(f"🤖 일반 답변: {response.response[:200]}...")
    else:
        print(f"❌ 오류: {response.error}")

def example_3_multi_language():
    """예제 3: 다국어 지원"""
    print("📋 예제 3: 다국어 지원")
    print("-" * 30)
    
    client = LawRoClient()
    
    languages = [
        ("korean", "한국의 근로기준법에 대해 알려주세요."),
        ("english", "Tell me about labor laws in Korea."),
        ("chinese", "请告诉我韩国的劳动法。"),
        ("vietnamese", "Hãy cho tôi biết về luật lao động ở Hàn Quốc."),
        ("japanese", "韓国の労働法について教えてください。")
    ]
    
    for lang_code, question in languages:
        print(f"👤 [{lang_code.upper()}] {question}")
        
        response = client.send_message(question, user_language=lang_code)
        
        if response.success:
            print(f"🤖 답변: {response.response[:150]}...")
        else:
            print(f"❌ 오류: {response.error}")
        print()

def example_4_conversation_flow():
    """예제 4: 대화 흐름 관리"""
    print("📋 예제 4: 대화 흐름 관리")
    print("-" * 30)
    
    client = LawRoClient()
    
    # 연속적인 대화
    conversation = [
        "안녕하세요. 근로계약서 관련 상담을 받고 싶습니다.",
        "제가 외국인 근로자인데, 특별히 주의해야 할 점이 있나요?",
        "임금 체불이 발생했을 때는 어떻게 해야 하나요?",
        "노동청에 신고하는 절차를 자세히 알려주세요.",
        "감사합니다. 도움이 많이 되었습니다."
    ]
    
    responses = client.chat_conversation(
        messages=conversation,
        delay_between_messages=1.0
    )
    
    print(f"\n📊 대화 요약:")
    print(f"총 {len(responses)}개의 메시지")
    successful = sum(1 for r in responses if r.success)
    print(f"성공한 응답: {successful}개")
    
    if responses:
        avg_time = sum(r.processing_time for r in responses if r.success) / successful
        print(f"평균 응답 시간: {avg_time:.2f}초")

def example_5_contract_analysis():
    """예제 5: 계약서 분석"""
    print("📋 예제 5: 계약서 분석")
    print("-" * 30)
    
    # 샘플 계약서 텍스트
    contract_text = """
    근로계약서
    
    1. 근로자: 김○○
    2. 근무지: 서울시 강남구 ○○동
    3. 근무시간: 주 6일, 하루 10시간
    4. 임금: 월 200만원 (최저임금 미달)
    5. 휴가: 연차휴가 없음
    6. 퇴직금: 지급하지 않음
    """
    
    analysis_prompt = """
    이 계약서를 분석하여 다음 형태로 답변해주세요:
    1. 위법 사항 목록
    2. 위험도 점수 (1-10)
    3. 개선 권고사항
    4. 근로자가 취해야 할 조치
    """
    
    print("📄 계약서 분석 중...")
    
    result = analyze_contract_with_custom_prompt(contract_text, analysis_prompt)
    
    print("🔍 분석 결과:")
    print(result)

def example_6_batch_processing():
    """예제 6: 배치 처리"""
    print("📋 예제 6: 배치 처리")
    print("-" * 30)
    
    client = LawRoClient()
    
    # 여러 질문을 한 번에 처리
    questions = [
        "최저임금 위반 시 처벌은?",
        "야간근로 수당은 얼마인가?",
        "임신 중 해고는 가능한가?",
        "외국인 등록증 없이 취업 가능한가?",
        "산업재해 발생 시 처리절차는?"
    ]
    
    print(f"📤 {len(questions)}개 질문 배치 처리 시작...")
    
    results = []
    for i, question in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {question}")
        
        response = client.send_message(question)
        results.append({
            "question": question,
            "success": response.success,
            "response_length": len(response.response) if response.success else 0,
            "processing_time": response.processing_time
        })
        
        if response.success:
            print(f"✅ 완료 ({response.processing_time:.2f}초)")
        else:
            print(f"❌ 실패: {response.error}")
    
    # 통계 출력
    print(f"\n📊 배치 처리 결과:")
    successful = [r for r in results if r["success"]]
    print(f"성공률: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
    
    if successful:
        avg_time = sum(r["processing_time"] for r in successful) / len(successful)
        avg_length = sum(r["response_length"] for r in successful) / len(successful)
        print(f"평균 응답 시간: {avg_time:.2f}초")
        print(f"평균 응답 길이: {avg_length:.0f}자")

def example_7_error_handling():
    """예제 7: 에러 처리"""
    print("📋 예제 7: 에러 처리")
    print("-" * 30)
    
    # 잘못된 서버 주소로 테스트
    client = LawRoClient(base_url="http://invalid-server:8000", timeout=5)
    
    print("❌ 의도적인 오류 테스트...")
    
    # 서버 상태 확인
    health = client.health_check()
    if not health["success"]:
        print(f"서버 연결 실패: {health['error']}")
    
    # 메시지 전송 시도
    response = client.send_message("테스트 메시지")
    if not response.success:
        print(f"메시지 전송 실패: {response.error}")
    
    print("✅ 에러 처리 확인 완료")

# 편의 함수 예제
def example_8_convenience_functions():
    """예제 8: 편의 함수들"""
    print("📋 예제 8: 편의 함수들")
    print("-" * 30)
    
    # 1. 빠른 채팅
    print("🚀 빠른 채팅:")
    result = quick_chat("근로계약서 필수 요소는?")
    print(f"결과: {result[:100]}...")
    print()
    
    # 2. 다국어 채팅
    print("🌍 영어 채팅:")
    result = multi_language_chat("What is minimum wage in Korea?", "english")
    print(f"결과: {result[:100]}...")
    print()
    
    # 3. 계약서 분석
    print("📄 계약서 분석:")
    sample_contract = "근무시간: 주 7일, 하루 12시간. 임금: 월 150만원"
    analysis = analyze_contract_with_custom_prompt(
        sample_contract,
        "이 계약서의 문제점을 찾아주세요."
    )
    print(f"분석: {analysis[:100]}...")

if __name__ == "__main__":
    print("🤖 LawRo 클라이언트 사용 예제")
    print("=" * 50)
    
    try:
        example_1_basic_chat()
        print("\n" + "="*50 + "\n")
        
        example_2_custom_prompt()
        print("\n" + "="*50 + "\n")
        
        example_3_multi_language()
        print("\n" + "="*50 + "\n")
        
        example_4_conversation_flow()
        print("\n" + "="*50 + "\n")
        
        example_5_contract_analysis()
        print("\n" + "="*50 + "\n")
        
        example_6_batch_processing()
        print("\n" + "="*50 + "\n")
        
        example_7_error_handling()
        print("\n" + "="*50 + "\n")
        
        example_8_convenience_functions()
        
    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 예기치 못한 오류: {str(e)}")
    
    print("\n🎉 모든 예제 완료!") 