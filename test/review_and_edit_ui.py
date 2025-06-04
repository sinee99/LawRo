import streamlit as st

def review_and_edit_ui(fields: dict, form_index: int = 0) -> dict:
    """근로계약서 항목 검토 및 수정 UI"""
    st.write("✏️ 추출된 정보를 확인하고 필요한 경우 수정하세요.")

    # 세션 상태 초기화
    if f'final_fields_{form_index}' not in st.session_state:
        st.session_state[f'final_fields_{form_index}'] = fields.copy()

    # 주요 필드 순서 정의
    field_order = [
        "성명", "사용자", "생년월일", "근로계약기간",
        "근로시간", "근무일", "휴일", "휴게시간",
        "임금", "임금지급일", "숙소제공"
    ]

    with st.form(f"edit_form_{form_index}"):
        updated_fields = {}
        
        # 2열 레이아웃으로 필드 배치
        col1, col2 = st.columns(2)
        
        # 왼쪽 컬럼 (기본 정보)
        with col1:
            st.markdown("#### 👤 기본 정보")
            for field in ["성명", "사용자", "생년월일", "근로계약기간"]:
                if field in fields:
                    value = st.session_state[f'final_fields_{form_index}'].get(field, fields[field])
                    updated_fields[field] = st.text_input(
                        label=field,
                        value=str(value),
                        key=f"{field}_{form_index}"
                    )
        
        # 오른쪽 컬럼 (근로 조건)
        with col2:
            st.markdown("#### ⏰ 근로 조건")
            for field in ["근로시간", "근무일", "휴일", "휴게시간"]:
                if field in fields:
                    value = st.session_state[f'final_fields_{form_index}'].get(field, fields[field])
                    updated_fields[field] = st.text_input(
                        label=field,
                        value=str(value),
                        key=f"{field}_{form_index}"
                    )

        # 임금 관련 정보 (전체 너비)
        st.markdown("#### 💰 임금 정보")
        col3, col4 = st.columns(2)
        with col3:
            for field in ["임금", "임금지급일"]:
                if field in fields:
                    value = st.session_state[f'final_fields_{form_index}'].get(field, fields[field])
                    updated_fields[field] = st.text_input(
                        label=field,
                        value=str(value),
                        key=f"{field}_{form_index}"
                    )
        with col4:
            if "숙소제공" in fields:
                value = st.session_state[f'final_fields_{form_index}'].get("숙소제공", fields["숙소제공"])
                updated_fields["숙소제공"] = st.text_input(
                    label="숙소제공",
                    value=str(value),
                    key=f"숙소제공_{form_index}"
                )

        # 기타 필드 처리 (정의된 순서에 없는 필드가 있는 경우)
        extra_fields = [f for f in fields if f not in field_order]
        if extra_fields:
            st.markdown("#### 📝 기타 정보")
            for field in extra_fields:
                value = st.session_state[f'final_fields_{form_index}'].get(field, fields[field])
                updated_fields[field] = st.text_input(
                    label=field,
                    value=str(value),
                    key=f"{field}_{form_index}"
                )

        submitted = st.form_submit_button("✅ 수정 완료", use_container_width=True)
        if submitted:
            st.session_state[f'final_fields_{form_index}'] = updated_fields
            st.success("✅ 수정된 항목이 반영되었습니다.")

    return st.session_state[f'final_fields_{form_index}']
