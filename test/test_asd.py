import requests
from typing import Optional
from xml.etree import ElementTree as ET

def search_nlrc_decisions(
    user_id: str,
    query: str,
    search: int = 1,
    display: int = 10,
    page: int = 1,
    output_type: str = "XML"
) -> Optional[list[dict]]:
    """
    노동위원회 결정문 목록을 검색합니다.

    Args:
        user_id (str): API 요청자 이메일 ID
        query (str): 검색어
        search (int): 검색 범위 (1: 제목, 2: 본문)
        display (int): 결과 개수
        page (int): 페이지 번호
        output_type (str): 결과 형식 (HTML/XML/JSON)

    Returns:
        list[dict]: 결정문 결과 목록 (제목, 날짜, ID 등)
    """
    # 목록 조회 API 엔드포인트
    url = "https://www.law.go.kr/DRF/lawSearch.do"
    params = {
        "OC": user_id,
        "target": "nlrc",
        "type": output_type,
        "search": search,
        "query": query,
        "display": display,
        "page": page,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"📋 목록 조회 URL: {response.url}")
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            # HTML 응답인지 확인
            if response.text.strip().startswith('<!DOCTYPE html') or response.text.strip().startswith('<html'):
                print("❌ HTML 응답이 반환되었습니다. API 키나 파라미터를 확인하세요.")
                return None
            
            if output_type.upper() == "XML":
                return parse_nlrc_search_xml(response.text)
            else:
                print(response.text)
                return None
        else:
            print(f"❌ 요청 실패: {response.status_code}")
            print(f"응답 내용: {response.text[:200]}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 네트워크 오류: {e}")
        return None
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return None


def get_nlrc_decision_content(
    user_id: str,
    decision_id: str,
    output_type: str = "XML"
) -> Optional[dict]:
    """
    노동위원회 결정문 본문을 조회합니다.

    Args:
        user_id (str): API 요청자 이메일 ID  
        decision_id (str): 결정문 일련번호
        output_type (str): 결과 형식 (HTML/XML/JSON)

    Returns:
        dict: 결정문 상세 내용 (제목, 내용, 사건번호 등)
    """
    # 본문 조회 API 엔드포인트 (이미지에서 확인한 URL)
    url = "https://www.law.go.kr/DRF/lawService.do"
    params = {
        "OC": user_id,
        "target": "nlrc", 
        "type": output_type,
        "ID": decision_id,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"📄 본문 조회 URL: {response.url}")
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            # HTML 응답인지 확인
            if response.text.strip().startswith('<!DOCTYPE html') or response.text.strip().startswith('<html'):
                print("❌ HTML 응답이 반환되었습니다. API 키나 파라미터를 확인하세요.")
                return None
            
            if output_type.upper() == "XML":
                return parse_nlrc_content_xml(response.text)
            else:
                print(response.text)
                return None
        else:
            print(f"❌ 요청 실패: {response.status_code}")
            print(f"응답 내용: {response.text[:200]}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 네트워크 오류: {e}")
        return None
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return None


def parse_nlrc_search_xml(xml_text: str) -> list[dict]:
    """
    노동위원회 검색 결과 XML을 파싱합니다.
    """
    try:
        root = ET.fromstring(xml_text)
        items = []

        for child in root.findall("item"):
            title = child.findtext("title")
            date = child.findtext("date") 
            court = child.findtext("court")
            decision_id = child.findtext("ID")  # 결정문 ID 추가
            
            items.append({
                "title": title,
                "date": date, 
                "court": court,
                "id": decision_id
            })

        return items
    except Exception as e:
        print(f"❌ XML 파싱 오류: {e}")
        print(f"XML 내용: {xml_text[:300]}")
        return []


def parse_nlrc_content_xml(xml_text: str) -> dict:
    """
    노동위원회 결정문 본문 XML을 파싱합니다.
    """
    try:
        root = ET.fromstring(xml_text)
        
        # 이미지에서 확인한 응답 필드들
        content_data = {
            "결정문일련번호": root.findtext("결정문일련번호"),
            "기관명": root.findtext("기관명"),
            "사건번호": root.findtext("사건번호"), 
            "사건구분": root.findtext("사건구분"),
            "당사자명": root.findtext("당사자명"),
            "등록일": root.findtext("등록일"),
            "제목": root.findtext("제목"),
            "내용": root.findtext("내용"),  # 실제 결정문 본문
            "판정사유": root.findtext("판정사유"),
            "관련법령": root.findtext("관련법령"),
            "판정결과": root.findtext("판정결과"),
            "작성법원": root.findtext("작성법원"),
            "작성사법": root.findtext("작성사법")
        }
        
        return content_data
    except Exception as e:
        print(f"❌ XML 파싱 오류: {e}")
        print(f"XML 내용: {xml_text[:300]}")
        return {}


# ✅ 테스트 실행
if __name__ == "__main__":
    print("🔍 노동위원회 결정문 API 테스트")
    print("="*60)
    
    user_email = "frog9032@naver.com"
    search_query = "해고"
    
    # 1단계: 결정문 목록 검색
    print("1️⃣ 결정문 목록 검색 중...")
    search_results = search_nlrc_decisions(
        user_id=user_email,
        query=search_query,
        search=1,
        display=3,  # 처음 3개만 테스트
        page=1
    )

    if search_results:
        print(f"✅ 검색 결과 {len(search_results)}건 발견")
        
        # 2단계: 각 결정문의 본문 내용 조회
        for i, item in enumerate(search_results, 1):
            print(f"\n2️⃣ [{i}] 결정문 본문 조회 중...")
            print(f"제목: {item['title']}")
            print(f"날짜: {item['date']}")
            print(f"ID: {item['id']}")
            
            if item['id']:
                content = get_nlrc_decision_content(
                    user_id=user_email,
                    decision_id=item['id']
                )
                
                if content and content.get('내용'):
                    print(f"✅ 본문 조회 성공")
                    print(f"사건번호: {content.get('사건번호', 'N/A')}")
                    print(f"당사자명: {content.get('당사자명', 'N/A')}")
                    print(f"내용 미리보기: {content.get('내용', '')[:200]}...")
                else:
                    print(f"❌ 본문 조회 실패")
            else:
                print(f"❌ 결정문 ID가 없습니다")
                
            print("-" * 50)
            
    else:
        print("❌ 검색 결과가 없습니다. API 인증을 확인하세요.")
        print("\n💡 해결 방법:")
        print("1. https://www.law.go.kr/DRF/ 에서 API 키 확인")
        print("2. 올바른 사용자 이메일 ID 사용")
