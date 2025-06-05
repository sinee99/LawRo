def format_contract_json_as_text(contract: dict) -> str:
    parts = []

    # 1. 사용자(사업주) 정보
    employer = contract.get("사업주", {})
    parts.append("【사업주 정보】")
    parts.append(f"- 업체명: {employer.get('업체명', '')}")
    parts.append(f"- 전화번호: {employer.get('전화번호', '')}")
    parts.append(f"- 소재지: {employer.get('소재지', '')}")
    parts.append(f"- 대표자명: {employer.get('대표자명', '')}")
    parts.append(f"- 사업자등록번호: {employer.get('사업자등록번호', '')}")

    # 2. 근로자 정보
    employee = contract.get("근로자", {})
    parts.append("\n【근로자 정보】")
    parts.append(f"- 이름: {employee.get('이름', '')}")
    parts.append(f"- 생년월일: {employee.get('생년월일', '')}")
    parts.append(f"- 본국 주소: {employee.get('본국주소', '')}")

    # 3. 근로계약기간
    period = contract.get("근로계약기간", {})
    parts.append("\n【계약 기간】")
    parts.append(f"- 신규계약 개월수: {period.get('신규계약_개월수', '')}")
    if "사업장변경기간" in period:
        change = period["사업장변경기간"]
        parts.append(f"- 사업장 변경 기간: {change.get('시작일', '')} ~ {change.get('종료일', '')}")
    if "수습기간" in period:
        probation = period["수습기간"]
        parts.append(f"- 수습 기간 사용 여부: {probation.get('사용여부', False)}, 기간: {probation.get('기간_개월수', '')}개월")

    # … 생략 가능: 근무장소, 업무내용, 근로시간 등도 같은 방식으로 추가

    return "\n".join(parts)
