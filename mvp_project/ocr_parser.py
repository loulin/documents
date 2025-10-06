import json

def parse_report(filename: str) -> dict:
    """
    Simulates the OCR and LLM parsing of a medical report file.
    In a real application, this function would contain calls to OCR services
    and a powerful LLM to extract structured data.
    For this MVP, it returns a hardcoded JSON based on the filename.
    """
    print(f"--- Simulating parsing for: {filename} ---")

    if "blood-routine" in filename.lower() or "血常规" in filename:
        print("--- Detected Blood Routine Report ---")
        return {
            "report_type": "blood-routine-schema.csv",
            "results": [
                {"id": "WBC", "name": "白细胞计数", "value": 12.5, "unit": "x10^9/L", "normal_range": "4.0-10.0"},
                {"id": "HGB", "name": "血红蛋白", "value": 110, "unit": "g/L", "normal_range": "120-160"},
                {"id": "PLT", "name": "血小板计数", "value": 350, "unit": "x10^9/L", "normal_range": "100-300"},
                {"id": "NEUT%", "name": "中性粒细胞百分比", "value": 75, "unit": "%", "normal_range": "50-70"}
            ]
        }
    
    elif "lipid" in filename.lower() or "血脂" in filename:
        print("--- Detected Lipid Panel Report ---")
        return {
            "report_type": "lipid-metabolism-schema.csv",
            "results": [
                {"id": "TC", "name": "总胆固醇", "value": 6.5, "unit": "mmol/L", "normal_range": "<5.2"},
                {"id": "TG", "name": "甘油三酯", "value": 2.5, "unit": "mmol/L", "normal_range": "<1.7"},
                {"id": "LDL-C", "name": "低密度脂蛋白胆固醇", "value": 4.5, "unit": "mmol/L", "normal_range": "<3.4"},
                {"id": "HDL-C", "name": "高密度脂蛋白胆固醇", "value": 0.9, "unit": "mmol/L", "normal_range": ">1.0"}
            ]
        }

    elif "thyroid-ultrasound" in filename.lower() or "甲状腺超声" in filename:
        print("--- Detected Thyroid Ultrasound Report ---")
        return {
            "report_type": "thyroid-ultrasound-schema.csv",
            "results": [
                {"id": "TI-RADS", "name": "甲状腺影像报告和数据系统分级", "value": "4A", "unit": "", "normal_range": "N/A"},
                {"id": "composition", "name": "成分", "value": "solid", "unit": "", "normal_range": "N/A"},
                {"id": "echogenicity", "name": "回声", "value": "hypoechoic", "unit": "", "normal_range": "N/A"}
            ]
        }

    else:
        print("--- No specific mock data found, returning default. ---")
        # Return a default or error structure if no match
        return {
            "report_type": "unknown",
            "results": []
        }
