import openai
import json
from pathlib import Path
from config.settings import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def load_prompt_template(name: str) -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / name
    return prompt_path.read_text(encoding="utf-8")

'''def call_gpt_api(prompt: str, model="gpt-4", temperature=0.0) -> str:
    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content.strip()

def extract_page_summary_from_text(page_text: str) -> str:
    """
    페이지 단위 텍스트를 받아 요약문 반환.
    요약 프롬프트 템플릿 파일명: "page_summary_template.txt"
    """
    prompt_template = load_prompt_template("page_summary_template.txt")
    prompt = prompt_template.replace("{{page_text}}", page_text)
    summary = call_gpt_api(prompt)
    return summary

def extract_contract_items_from_file(json_path: str) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        ocr_data = json.load(f)
    html_content = ocr_data["full_html"][:5000]  # GPT token limit 대응

    prompt_template = load_prompt_template()
    prompt = prompt_template.replace("{{html_content}}", html_content)

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )

    content = response.choices[0].message.content.strip()
    try:
        return json.loads(content)  # 안전하게 JSON으로 파싱
    except json.JSONDecodeError:
        return {"raw_text": content}
def extract_contract_items_from_summary(combined_summary_text: str) -> dict:
    """
    여러 페이지 요약을 합친 텍스트를 받아 표준근로계약서 항목별 JSON 반환.
    프롬프트 템플릿 파일명: "gpt_template.txt"
    """
    prompt_template = load_prompt_template("gpt_template.txt")
    prompt = prompt_template.replace("{{html_content}}", combined_summary_text)  # 이름은 그대로 사용해도 됨
    content = call_gpt_api(prompt)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 raw_text 필드에 내용 전달
        return {"raw_text": content}
    '''
def extract_contract_items_from_summaries(summaries: list[str]) -> dict:
    prompt = load_prompt_template("gpt_template.txt")
    for i, summary in enumerate(summaries, 1):
        prompt += f"페이지 {i} 요약:\n{summary}\n\n"

    prompt += "JSON 출력:"
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    import json
    return json.loads(response.choices[0].message.content)
