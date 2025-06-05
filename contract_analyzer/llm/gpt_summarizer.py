from llm.gpt_parser import openai  # openai 초기화 포함
from llm.gpt_parser import load_prompt_template

def summarize_page(html_content: str) -> str:
    if not html_content:
        raise ValueError("HTML 내용이 비어 있습니다.")

    prompt = load_prompt_template("page_summary_template.txt")
    # 프롬프트와 html_content를 합쳐서 전달
    full_prompt = f"{prompt}\n\n[HTML]\n{html_content}"
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def summarize_pages(page_html_list: list[str]) -> list[str]:
    return [summarize_page(html) for html in page_html_list]
