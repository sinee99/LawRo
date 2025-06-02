import re
from rapidfuzz import fuzz
from typing import Dict, List
from models.response_models import RequiredFieldsResult, ViolationCheckResponse, ViolationItem

class AnalysisService:
    """계약서 분석 서비스"""
    
    def __init__(self):
        self.required_fields = {
            "사용자 정보": ["성명", "업체명", "소재지", "전화번호", "사업자등록번호", "주민등록번호"],
            "근로자 정보": ["근로자", "성명", "생년월일", "본국주소"],
            "근로계약기간": ["근로계약기간", "수습기간", "신규", "재입국"],
            "근로장소": ["근로장소", "장소"],
            "업무내용": ["업종", "사업내용", "직무내용"],
            "근로시간": ["근로시간", "시", "분", "교대제"],
            "휴게시간": ["휴게시간", "분"],
            "휴일": ["휴일", "일요일", "토요일", "공휴일", "유급", "무급"],
            "임금": ["통상임금", "기본급", "수당", "상여금", "수습", "가산수당"],
            "임금지급일": ["매월", "매주", "지급일", "요일", "공휴일", "전일"],
            "지급방법": ["계좌지급", "현금지급", "통장", "도장", "직접지급"],
            "숙식제공": ["숙소", "제공", "미제공", "자비", "식사", "숙소제공", "식사제공", "조식", "중식", "석식"],
            "규정준수": ["취업규칙", "단체협약", "성실", "이행"]
        }
        
        self.law_violation_rules = {
            "수습기간 6개월 이상": lambda t: re.search(r"수습.*(6개월|180일|이상)", t),
            "주 52시간 초과 근무": lambda t: re.search(r"(52시간|하루\s?10시간\s?초과|연장근로.*무제한)", t),
            "무급 휴일": lambda t: "무급" in t and "휴일" in t,
            "임금 미지급 가능성": lambda t: re.search(r"(임금.*지급하지.*않는다|무급근로|지연지급)", t)
        }
    
    def preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        lines = text.splitlines()
        cleaned = []
        for line in lines:
            line = re.sub(r"[■●☑️✔️]", "[X]", line)
            line = re.sub(r"[□⬜️☐]", "[ ]", line)
            line = line.strip()
            if line and not re.match(r"^[-=]{3,}$", line):
                cleaned.append(line)
        return "\n".join(cleaned)
    
    def is_similar(self, word: str, keyword: str, threshold: int = 85) -> bool:
        """단어 유사도 검사"""
        return fuzz.ratio(word.lower(), keyword.lower()) >= threshold or keyword.lower() in word.lower()
    
    def analyze_required_fields(self, text: str) -> RequiredFieldsResult:
        """필수 항목 분석"""
        words = text.split()
        found_fields = {}
        
        for category, keywords in self.required_fields.items():
            found = []
            for keyword in keywords:
                if any(self.is_similar(word, keyword) for word in words):
                    found.append(keyword)
            if found:
                found_fields[category] = found
        
        missing_fields = {}
        for category, keywords in self.required_fields.items():
            included = found_fields.get(category, [])
            remain = list(set(keywords) - set(included))
            if remain:
                missing_fields[category] = remain
        
        total_fields = sum(len(keywords) for keywords in self.required_fields.values())
        found_count = sum(len(found) for found in found_fields.values())
        completion_rate = (found_count / total_fields) * 100 if total_fields > 0 else 0
        
        return RequiredFieldsResult(
            found_fields=found_fields,
            missing_fields=missing_fields,
            completion_rate=completion_rate
        )
    
    def check_violations(self, text: str) -> ViolationCheckResponse:
        """법 위반 검사"""
        violations = []
        for rule_name, rule_func in self.law_violation_rules.items():
            if rule_func(text):
                severity = "high" if "52시간" in rule_name else "medium"
                violations.append(ViolationItem(
                    rule_name=rule_name,
                    description=f"{rule_name} 위반이 감지되었습니다.",
                    severity=severity
                ))
        
        risk_level = "safe"
        if len(violations) > 0:
            risk_level = "danger" if any(v.severity == "high" for v in violations) else "caution"
        
        return ViolationCheckResponse(
            success=True,
            violations=violations,
            violation_count=len(violations),
            risk_level=risk_level
        )
    
    def calculate_overall_score(self, required_fields: RequiredFieldsResult, violations: ViolationCheckResponse) -> float:
        """전체 점수 계산"""
        base_score = required_fields.completion_rate
        violation_penalty = len(violations.violations) * 10
        return max(0, base_score - violation_penalty)
    
    def generate_recommendations(self, required_fields: RequiredFieldsResult, violations: ViolationCheckResponse) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        if required_fields.missing_fields:
            recommendations.append("누락된 필수 항목을 추가해주세요.")
        
        if violations.violations:
            recommendations.append("근로기준법 위반 조항을 수정해주세요.")
        
        if required_fields.completion_rate < 80:
            recommendations.append("계약서 완성도를 높이기 위해 추가 정보를 기입해주세요.")
            
        return recommendations 