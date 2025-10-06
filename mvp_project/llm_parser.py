import os
import json
from volcengine.maas import MaasService, MaasException

# --- LLM Parser using Volcano Engine ---

def parse_report_with_llm(text: str) -> dict:
    """
    Parses unstructured medical text into a structured JSON using Volcano Engine's LLM.
    """
    # 1. Get credentials from environment variables
    ak = os.getenv("VOLC_ACCESSKEY")
    sk = os.getenv("VOLC_SECRETKEY")
    endpoint_id = os.getenv("VOLC_ENDPOINT_ID")

    if not all([ak, sk, endpoint_id]):
        print("--- ERROR: Volcano Engine credentials not found in environment variables. ---")
        return {"report_type": "error", "results": [{"error": "Server credentials not configured."}]}

    # 2. Initialize the service
    maas = MaasService('maas-api.ml-platform-cn-beijing.volces.com', 'cn-beijing')
    maas.set_ak(ak)
    maas.set_sk(sk)

    # 3. Construct the powerful prompt
    prompt = f"""你是一个专业的医疗报告解析机器人。你的任务是将用户提供的非结构化文本，严格地转换为指定的JSON格式。请自行判断报告类型。

可能的报告类型包括：
- 血常规: 'blood-routine-schema.csv'
- 血脂: 'lipid-metabolism-schema.csv'
- 甲状腺超声: 'thyroid-ultrasound-schema.csv'

JSON格式必须如下:
```json
{{
  "report_type": "你的判断结果，例如 blood-routine-schema.csv",
  "results": [
    {{"id": "项目ID", "name": "项目名称", "value": 数值, "unit": "单位", "normal_range": "正常范围"}},
    ...
  ]
}}
```

请直接返回纯JSON文本，不要包含任何额外的解释或标记。

用户报告文本如下：
---
{text}
---
"""

    # 4. Prepare the request payload
    req = {
        "model": {
            "endpoint_id": endpoint_id,
        },
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "parameters": {
            "max_new_tokens": 2048,
            "temperature": 0.1, # Use low temperature for predictable, structured output
        },
    }

    # 5. Make the API call and handle response/errors
    try:
        print("--- Calling Volcano Engine LLM API... ---")
        res = maas.chat(req)
        llm_output = res.choice.message.content
        print(f"--- LLM Raw Output: {llm_output} ---")
        
        # Clean up the output to be valid JSON
        # LLMs sometimes wrap the JSON in ```json ... ```
        if llm_output.strip().startswith('```json'):
            llm_output = llm_output.strip()[7:-3].strip()

        # Parse the JSON string into a Python dictionary
        parsed_json = json.loads(llm_output)
        return parsed_json

    except MaasException as e:
        print(f"--- Volcano Engine API Error: {e} ---")
        return {"report_type": "error", "results": [{"error": f"API Error: {e.message}"}]}
    except json.JSONDecodeError as e:
        print(f"--- JSON Parsing Error: {e} ---")
        return {"report_type": "error", "results": [{"error": "LLM returned invalid JSON."}]}
    except Exception as e:
        print(f"--- An unexpected error occurred: {e} ---")
        return {"report_type": "error", "results": [{"error": "An unexpected server error occurred."}]}
