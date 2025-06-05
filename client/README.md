# LawRo 클라이언트 라이브러리

다른 서버에서 LawRo 도커 서버로 요청을 보내기 위한 Python 클라이언트 라이브러리입니다.

## 📋 **주요 기능**

- ✅ **기본 채팅**: 일반적인 법률 상담
- ✅ **커스텀 프롬프트**: JSON 분석, 특화된 응답 형식
- ✅ **다국어 지원**: 한국어, 영어, 중국어, 베트남어, 일본어 등 10개 언어
- ✅ **세션 관리**: 대화 히스토리 유지 및 관리
- ✅ **에러 처리**: 안정적인 오류 처리 및 재시도
- ✅ **배치 처리**: 여러 질문 일괄 처리
- ✅ **통계 조회**: 서버 상태 및 통계 정보

## 🚀 **빠른 시작**

### 1. 기본 설치

```python
# 필요한 라이브러리 설치
pip install requests
```

### 2. 간단한 사용법

```python
from lawro_client import LawRoClient

# 클라이언트 생성
client = LawRoClient()

# 간단한 질문
response = client.send_message("근로계약서란 무엇인가요?")

if response.success:
    print(f"답변: {response.response}")
else:
    print(f"오류: {response.error}")
```

### 3. 편의 함수 사용

```python
from lawro_client import quick_chat, multi_language_chat

# 빠른 일회성 채팅
answer = quick_chat("최저임금은 얼마인가요?")
print(answer)

# 다국어 채팅
english_answer = multi_language_chat("What is minimum wage?", "english")
print(english_answer)
```

## 📖 **상세 사용법**

### **LawRoClient 클래스**

#### 초기화

```python
client = LawRoClient(
    base_url="http://16.176.26.197:8000",  # LawRo 서버 주소
    timeout=30  # 요청 타임아웃 (초)
)
```

#### 주요 메서드

##### 1. `send_message()` - 메시지 전송

```python
response = client.send_message(
    message="사용자 메시지",
    session_id=None,  # 세션 ID (자동 생성)
    custom_prompt=None,  # 커스텀 프롬프트
    user_language="korean",  # 응답 언어
    context=None  # 문맥 정보
)
```

##### 2. `create_session()` - 세션 생성

```python
session_id = client.create_session()
print(f"새 세션: {session_id}")
```

##### 3. `get_chat_history()` - 히스토리 조회

```python
history = client.get_chat_history(session_id)
for msg in history:
    print(f"{msg.role}: {msg.content}")
```

##### 4. `health_check()` - 서버 상태 확인

```python
health = client.health_check()
if health["success"]:
    print("서버 정상")
else:
    print(f"서버 오류: {health['error']}")
```

## 🎯 **사용 예제**

### **예제 1: 기본 법률 상담**

```python
from lawro_client import LawRoClient

client = LawRoClient()

# 연속 질문
questions = [
    "근로계약서 작성 시 필수 요소는 무엇인가요?",
    "최저임금 위반 시 처벌은 어떻게 되나요?",
    "외국인 근로자 권리에 대해 알려주세요."
]

for question in questions:
    response = client.send_message(question)
    if response.success:
        print(f"Q: {question}")
        print(f"A: {response.response[:200]}...")
        print(f"처리시간: {response.processing_time:.2f}초\n")
```

### **예제 2: 커스텀 프롬프트로 JSON 분석**

```python
# JSON 형태 분석 프롬프트
json_prompt = """
계약서를 분석하여 다음 JSON 형태로 답변해주세요:
{
    "analysis": "분석 내용",
    "risk_score": 1-10,
    "recommendations": ["권장사항1", "권장사항2"],
    "violations": ["위법사항1", "위법사항2"]
}
"""

contract_text = """
근무시간: 주 6일, 하루 12시간
임금: 월 150만원 (최저임금 미달)
휴가: 연차휴가 없음
"""

response = client.send_message(
    message=contract_text,
    custom_prompt=json_prompt
)

print("JSON 분석 결과:")
print(response.response)
```

### **예제 3: 다국어 상담**

```python
# 다양한 언어로 같은 질문
question = "근로계약서에 대해 알려주세요."

languages = {
    "korean": "근로계약서에 대해 알려주세요.",
    "english": "Tell me about employment contracts.",
    "chinese": "请告诉我关于劳动合同。",
    "vietnamese": "Hãy cho tôi biết về hợp đồng lao động."
}

for lang, msg in languages.items():
    response = client.send_message(msg, user_language=lang)
    print(f"[{lang.upper()}] {response.response[:100]}...")
```

### **예제 4: 연속 대화 처리**

```python
# 자동으로 세션을 관리하며 연속 대화
conversation = [
    "안녕하세요. 계약서 상담 받고 싶습니다.",
    "외국인 근로자 특별 주의사항이 있나요?",
    "임금 체불 시 대처 방법을 알려주세요.",
    "노동청 신고 절차를 설명해주세요."
]

responses = client.chat_conversation(
    messages=conversation,
    delay_between_messages=1.0  # 1초 간격
)

# 결과 요약
successful = sum(1 for r in responses if r.success)
print(f"성공률: {successful}/{len(responses)}")
```

### **예제 5: 배치 처리**

```python
# 여러 질문을 한 번에 처리
questions = [
    "최저임금은 얼마인가요?",
    "야간수당 계산법은?",
    "퇴직금 지급 기준은?",
    "산재보험 적용 범위는?",
    "외국인 취업 제한은?"
]

results = []
for question in questions:
    response = client.send_message(question)
    results.append({
        "question": question,
        "success": response.success,
        "processing_time": response.processing_time
    })

# 통계
successful = [r for r in results if r["success"]]
avg_time = sum(r["processing_time"] for r in successful) / len(successful)
print(f"평균 처리 시간: {avg_time:.2f}초")
```

## 🔧 **고급 기능**

### **커스텀 프롬프트 자동 복귀**

```python
# 첫 번째 메시지에 커스텀 프롬프트 적용
response1 = client.send_message(
    "계약서를 분석해주세요.",
    custom_prompt="JSON 형태로 답변해주세요."
)

# 두 번째 메시지는 자동으로 기본 프롬프트로 복귀
response2 = client.send_message("퇴직금은 어떻게 계산하나요?")

print("첫 번째 응답 (JSON):", response1.response[:50])
print("두 번째 응답 (일반):", response2.response[:50])
```

### **에러 처리**

```python
try:
    response = client.send_message("질문 내용")
    
    if response.success:
        print(f"성공: {response.response}")
    else:
        print(f"실패: {response.error}")
        
except Exception as e:
    print(f"예외 발생: {str(e)}")
```

### **서버 통계 조회**

```python
stats = client.get_server_stats()

if "stats" in stats:
    print(f"활성 세션: {stats['stats']['total_sessions']}")
    print(f"총 메시지: {stats['stats']['total_messages']}")
    print(f"세션 만료시간: {stats['stats']['session_timeout_hours']}시간")
```

## 🌐 **지원 언어**

| 언어 코드 | 언어명 | 예제 |
|----------|--------|------|
| `korean` | 한국어 | "한국어로 답변하세요." |
| `english` | 영어 | "Please respond in English." |
| `chinese` | 중국어 | "请用中文回答。" |
| `vietnamese` | 베트남어 | "Vui lòng trả lời bằng tiếng Việt." |
| `japanese` | 일본어 | "日本語で答えてください。" |
| `thai` | 태국어 | "กรุณาตอบเป็นภาษาไทย" |
| `indonesian` | 인도네시아어 | "Silakan jawab dalam bahasa Indonesia." |
| `tagalog` | 필리핀어 | "Mangyaring sumagot sa wikang Filipino." |
| `spanish` | 스페인어 | "Por favor responde en español." |
| `french` | 프랑스어 | "Veuillez répondre en français." |

## ⚠️ **주의사항**

1. **서버 연결**: 서버 주소 `http://16.176.26.197:8000`가 접근 가능한지 확인
2. **타임아웃**: 긴 분석 작업의 경우 타임아웃 값 조정 필요
3. **세션 관리**: 세션은 5분 후 자동 만료됨
4. **동시 요청**: 서버 부하를 고려하여 적절한 간격으로 요청
5. **에러 처리**: 네트워크 오류 등을 위한 재시도 로직 구현 권장

## 📞 **API 엔드포인트**

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/health` | GET | 서버 상태 확인 |
| `/create_session` | POST | 새 세션 생성 |
| `/chat` | POST | 메시지 전송 |
| `/chat/history/{session_id}` | GET | 히스토리 조회 |
| `/stats` | GET | 서버 통계 |

## 🎯 **완전한 예제 실행**

```bash
# 기본 테스트
python lawro_client.py

# 다양한 예제 실행
python examples.py
```

## 🔄 **버전 정보**

- **현재 버전**: 1.0.0
- **Python 요구사항**: Python 3.7+
- **필수 라이브러리**: requests

---

더 자세한 사용법은 `examples.py` 파일을 참고하세요! 🚀 