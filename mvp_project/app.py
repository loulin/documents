import csv
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Import the new, real LLM parser ---
from llm_parser import parse_report_with_llm
# --- Import drug knowledge base ---
from drug_kb import get_drug_info, load_drug_data, DRUG_CSV_PATH

# --- Initialization ---
app = FastAPI(title="Medical Report Interpreter MVP")
templates = Jinja2Templates(directory="templates")

# --- Load drug data on app startup ---
# This ensures drug data is loaded once when the app starts
@app.on_event("startup")
async def startup_event():
    load_drug_data(DRUG_CSV_PATH)

# --- Schema Engine (Updated to handle medications) ---
def schema_engine(data: dict) -> dict:
    report_type = data.get("report_type")
    parsed_results = data.get("results", [])
    interpretations = []
    medication_details = []
    drug_lab_interactions = []

    if report_type == "error":
        return {"interpretations": [{"item_name": "服务器错误", "interpretation_text": parsed_results[0].get('error', '未知错误')}], "medications": [], "interactions": []}

    # Process lab tests
    lab_test_results = [r for r in parsed_results if r.get("type") == "lab_test"]
    if report_type != "unknown" and lab_test_results:
        schema_path = os.path.join("schemas", report_type)
        print(f"--- Loading schema: {schema_path} ---")

        if not os.path.exists(schema_path):
            interpretations.append({"item_name": "错误", "interpretation_text": f"未找到对应的Schema文件: {report_type}"})
        else:
            with open(schema_path, mode='r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                schema_rules = list(reader)

            for result in lab_test_results:
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
    
    print(f"--- Found {len(interpretations)} lab interpretations ---")

    # Process medications
    medications_from_llm = [r for r in parsed_results if r.get("type") == "medication"]
    for med_llm in medications_from_llm:
        drug_info = get_drug_info(med_llm.get("name")) or get_drug_info(med_llm.get("generic_name"))
        if drug_info:
            medication_details.append({
                "name": drug_info.get('药品名称'),
                "generic_name": drug_info.get('通用名'),
                "dosage": med_llm.get('dosage', drug_info.get('用法用量', 'N/A')),
                "indications": drug_info.get('适应症', 'N/A'),
                "side_effects": drug_info.get('不良反应', 'N/A'),
                "contraindications": drug_info.get('禁忌症', 'N/A'),
                "interactions": drug_info.get('药物相互作用', 'N/A'),
            })
            # Basic drug-lab interaction check (MVP simplified)
            # Example: If Metformin is present and HGB is low (anemia), flag it as a potential interaction
            if drug_info.get('通用名') == '二甲双胍' and any(i.get('id') == 'HGB' and '低' in i.get('severity_level','') for i in interpretations):
                drug_lab_interactions.append({
                    "drug": drug_info.get('药品名称'),
                    "lab_test": "血红蛋白 (HGB)",
                    "interaction_type": "潜在不良反应",
                    "details": "二甲双胍长期使用可能影响维生素B12吸收，间接导致贫血。建议监测维生素B12水平。"
                })
            # Add more interaction rules here based on drug_info.get('不良反应') and lab results
            # This part would be greatly enhanced by a structured drug-lab interaction KB
        else:
            medication_details.append({
                "name": med_llm.get("name"),
                "generic_name": med_llm.get("generic_name", "N/A"),
                "dosage": med_llm.get("dosage", "N/A"),
                "indications": "未找到详细信息",
                "side_effects": "未找到详细信息",
                "contraindications": "未找到详细信息",
                "interactions": "未找到详细信息",
            })

    return {"interpretations": interpretations, "medications": medication_details, "interactions": drug_lab_interactions}

# --- API Endpoints (Updated) ---

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/interpret", response_class=HTMLResponse)
async def interpret_text(request: Request, report_text: str = Form(...)):
    # 1. Call the REAL LLM parser
    parsed_data = parse_report_with_llm(report_text)

    # 2. Run the schema engine
    processed_results = schema_engine(parsed_data)
    interpretations = processed_results["interpretations"]
    medication_details = processed_results["medications"]
    drug_lab_interactions = processed_results["interactions"]

    # 3. Generate summary
    summary = ""
    if interpretations and not interpretations[0].get('interpretation_text','').startswith('无法'):
        abnormal_count = sum(1 for r in interpretations if r.get('severity_level') and '正常' not in r.get('severity_level') and '正常范围' not in r.get('severity_level'))
        if abnormal_count > 0:
            summary = f"报告中发现 {abnormal_count} 项主要异常指标，请重点关注。"
        else:
            summary = "报告中的各项指标均在正常范围内，未发现主要异常。"
    elif not interpretations and not medication_details:
        summary = "无法从您粘贴的文本中生成解读概要。请检查服务器日志以获取详细错误信息。"
    else:
        summary = "已识别出部分信息，但无法生成完整解读概要。"

    # 4. Render results
    return templates.TemplateResponse("results.html", {
        "request": request,
        "results": interpretations,
        "medications": medication_details,
        "interactions": drug_lab_interactions,
        "summary": summary
    })

# --- Main execution ---

if __name__ == "__main__":
    import uvicorn
    print("Starting Medical Report Interpreter MVP (REAL AI-Powered Mode with Drug KB)..." )
    print("Access the application at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)