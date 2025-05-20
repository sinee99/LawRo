import re
import json
from pdfminer.high_level import extract_text

def extract_pdf_text(pdf_path):
    """PDF에서 텍스트 추출"""
    text = extract_text(pdf_path)
    return text

def clean_text(text):
    """불필요한 정보(머리글, 바닥글, 광고 등) 제거"""
    # 페이지 번호 제거 (단독 숫자)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    # 예시: 저작권, 목차, 광고 등 키워드 포함 줄 제거
    patterns = [r'저작권', r'목차', r'광고']
    for p in patterns:
        text = re.sub(p + r'.*?\n', '', text)
    return text

def split_articles_full(text):
    """
    '제1조(목적) ... [전문개정 ...]' 전체를 한 덩어리로 추출
    """
    # '제n조'로 시작해서, 다음 '제n조' 전까지를 한 조문으로 추출
    pattern = r'(^제\d+조(?:\([^)]+\))?[\s\S]*?)(?=^제\d+조|\Z)'
    articles = re.findall(pattern, text, flags=re.MULTILINE)
    results = []
    for article in articles:
        # 조문 번호와 제목 추출 (예: 제1조(목적))
        m = re.match(r'(제\d+조(?:\([^)]+\))?)', article)
        if m:
            article_num = m.group(1)
            content = article[m.end():].strip()
        else:
            article_num = ""
            content = article.strip()
        results.append({
            "article": article_num,
            "content": content
        })
    return results

def standardize_text(text):
    """공백, 특수문자 정리"""
    text = text.replace('\r', '')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def add_metadata_and_save(articles, source, doc_type, date, output_path):
    """메타데이터 추가 및 JSON 저장"""
    data = []
    for article in articles:
        item = {
            'source': source,
            'type': doc_type,
            'date': date,
            'article': article['article'],
            'content': standardize_text(article['content'])
        }
        data.append(item)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def preprocess_pdf(pdf_path, source, doc_type, date, output_path):
    raw_text = extract_pdf_text(pdf_path)
    cleaned_text = clean_text(raw_text)
    articles = split_articles_full(cleaned_text)
    add_metadata_and_save(articles, source, doc_type, date, output_path)

# ====== 수정하여 사용 ======
if __name__ == "__main__":
    pdf_path = r"C:\Users\sinee\Documents\VSCODE\LawRo\law_data\law_mwage.pdf"
    source = "최저임금법"
    doc_type = "법령"
    date = "2020-05-26"
    output_path = r"C:\Users\sinee\Documents\VSCODE\LawRo\law_data\law_mwage_processed.json"
    preprocess_pdf(pdf_path, source, doc_type, date, output_path)
    print("완료! 결과 파일:", output_path)
