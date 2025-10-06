import csv
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Import the new, real LLM parser ---
from llm_parser import parse_report_with_llm

# --- Initialization ---
app = FastAPI(title="Medical Report Interpreter MVP")
templates = Jinja2Templates(directory="templates")

# --- Schema Engine (remains the same) ---
def schema_engine(data: dict) -> list:
    report_type = data.get("report_type")
    patient_results = data.get("results", [])
    interpretations = []

    if report_type == "unknown" or not patient_results:
        return [{"item_name": "错误", "interpretation_text": "无法从您的文本中识别出可解读的报告类型。"}]
    if report_type == "error":
        return [{"item_name": "服务器错误", "interpretation_text": patient_results[0].get('error', '未知错误')}]

    schema_path = os.path.join("schemas", report_type)
    print(f"--- Loading schema: {schema_path} ---")

    if not os.path.exists(schema_path):
        return [{"item_name": "错误", "interpretation_text": f"未找到对应的Schema文件: {report_type}"}]

    with open(schema_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        schema_rules = list(reader)

    for result in patient_results:
        patient_value = result.get("value")
        
        for rule in schema_rules:
            if rule.get('id') == result.get('id') or rule.get('item_name') == result.get('name'):
                rule_value = rule.get('score_value') or rule.get('value_range')
                is_match = False

                if isinstance(patient_value, (int, float)) and rule_value:
                    try:
                        if '-' in rule_value:
                            low, high = map(float, rule_value.split('-'))
                            if low <= patient_value <= high: is_match = True
                        elif '>' in rule_value:
                            limit = float(rule_value.replace('>', '').replace('=', ''))
                            if patient_value > limit or ('>=' in rule_value and patient_value == limit): is_match = True
                        elif '<' in rule_value:
                            limit = float(rule_value.replace('<', '').replace('=', ''))
                            if patient_value < limit or ('<=' in rule_value and patient_value == limit): is_match = True
                    except (ValueError, TypeError):
                        pass
                
                elif isinstance(patient_value, str) and rule_value and patient_value.lower() == rule_value.lower():
                    is_match = True

                if is_match:
                    interpretation = rule.copy()
                    interpretation['value'] = patient_value
                    interpretation['normal_range'] = result.get('normal_range', 'N/A')
                    interpretations.append(interpretation)
                    break
    
    print(f"--- Found {len(interpretations)} interpretations ---")
    return interpretations

# --- API Endpoints (Updated) ---

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/interpret", response_class=HTMLResponse)
async def interpret_text(request: Request, report_text: str = Form(...)):
    # 1. Call the REAL LLM parser
    parsed_data = parse_report_with_llm(report_text)

    # 2. Run the schema engine
    results = schema_engine(parsed_data)

    # 3. Generate summary
    summary = ""
    if results and not results[0].get('interpretation_text','').startswith('无法'):
        abnormal_count = sum(1 for r in results if r.get('severity_level') and '正常' not in r.get('severity_level'))
        if abnormal_count > 0:
            summary = f"报告中发现 {abnormal_count} 项主要异常指标，请重点关注。"
        else:
            summary = "报告中的各项指标均在正常范围内，未发现主要异常。"
    else:
        summary = "无法从您粘贴的文本中生成解读概要。请检查服务器日志以获取详细错误信息。"

    # 4. Render results
    return templates.TemplateResponse("results.html", {
        "request": request,
        "results": results,
        "summary": summary
    })

# --- Main execution ---

if __name__ == "__main__":
    import uvicorn
    print("Starting Medical Report Interpreter MVP (REAL AI-Powered Mode)..." )
    print("Access the application at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
