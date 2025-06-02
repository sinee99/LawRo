import re

def preprocess_ocr_text(raw_text):
    """OCR로 추출한 원본 텍스트를 전처리합니다."""
    lines = raw_text.splitlines()
    cleaned = []

    for line in lines:
        line = re.sub(r"[■●☑️✔️]", "[X]", line)
        line = re.sub(r"[□⬜️☐]", "[ ]", line)
        line = line.strip()

        if not line or re.match(r"^[-=]{3,}$", line):
            continue
        cleaned.append(line)

    return "\n".join(cleaned) 