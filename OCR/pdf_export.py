from fpdf import FPDF
import io

def export_pdf(text, found, missing, violations, rag_result, llm_result):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def add_line(line):
        pdf.multi_cell(0, 10, line)

    pdf.set_font("Arial", "B", size=14)
    add_line("근로계약서 분석 결과 리포트")
    pdf.set_font("Arial", size=12)

    add_line("\n▶ 전처리된 계약서 내용 (요약):\n")
    add_line(text[:1000] + ("..." if len(text) > 1000 else ""))

    add_line("\n▶ 포함된 필수 항목:\n")
    for cat, items in found.items():
        add_line(f"- {cat}: {', '.join(items)}")

    if missing:
        add_line("\n▶ 누락된 항목:\n")
        for cat, items in missing.items():
            add_line(f"- {cat}: {', '.join(items)}")
    else:
        add_line("\n✅ 모든 필수 항목 포함됨")

    if violations:
        add_line("\n▶ 정규식 기반 위반 조항:\n")
        for v in violations:
            add_line(f"- {v}")
    else:
        add_line("\n✅ 명시적 위반 없음")

    add_line("\n▶ Embedding 기반 위반 판단 (RAG):\n")
    add_line(rag_result["result"])

    add_line("\n▶ 근거 법률 조항:\n")
    for doc in rag_result["source_documents"]:
        add_line("- " + doc.page_content.strip()[:300] + ("..." if len(doc.page_content) > 300 else ""))

    add_line("\n▶ LLM 판단 결과:\n")
    add_line(llm_result)

    # 메모리 버퍼에 PDF 저장
    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
