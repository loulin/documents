# 非结构化检查记录批量结构化方案

> 目标：利用 Schema CSV + 大语言模型，将批量检查报告转成结构化 JSON/CSV。

## 1. 准备工作

- 确保目录 `06_Others/Input/SchemaCSV/combined_schema_index.json` 为最新，可运行 `python3 build_schema_index.py` 生成。
- 安装依赖（示例）：`pip install openai pandas tqdm`
- 对于使用 OpenAI 模型：设置 `OPENAI_API_KEY` 环境变量。

## 2. 单条抽取脚本（structure_exam.py）

结构在 `structure_exam.py` 中：
- 加载指定 schema 的字段列表
- 构造 LLM 提示词，要求输出 `{"schema": ..., "data": {...}}`
- 调用模型并尝试解析 JSON
- 支持 `--show-prompt` 模式，用于手工粘贴到其他 LLM 界面

示例：
```
python3 structure_exam.py --schema thyroid-ultrasound-schema --input-file report.txt
```
或生成提示词：
```
python3 structure_exam.py --schema thyroid-ultrasound-schema --text "报告内容..." --show-prompt
```

## 3. 批量处理流程

### 3.1 数据准备
- 将待处理的非结构化文本保存为一个 CSV/Excel/纯文本列表。例如 CSV 中包含列 `id`, `schema_name`, `raw_text`。

### 3.2 示例批处理脚本
创建 `batch_structure.py`（伪代码）：
```python
import csv
import json
from pathlib import Path
from structure_exam import load_schema, build_prompt, call_llm, parse_json_output

input_path = Path('raw_reports.csv')
output_path = Path('structured_results.jsonl')

with input_path.open(encoding='utf-8') as fh, output_path.open('w', encoding='utf-8') as out:
    reader = csv.DictReader(fh)
    for row in reader:
        schema_name = row['schema_name']
        free_text = row['raw_text']

        schema_entry = load_schema(schema_name)
        prompt = build_prompt(schema_entry, free_text)
        raw_output = call_llm(prompt)  # 可加重试、异常处理
        structured = parse_json_output(raw_output)

        out.write(json.dumps({
            'id': row['id'],
            'schema': schema_name,
            'structured_data': structured,
        }, ensure_ascii=False) + '\n')
```

在实际环境中需考虑：
- **批处理速率**：模型调用通常需要限速，可加入 `time.sleep` 或异步队列。
- **异常重试**：针对 JSON 解析失败或网络错误，建议捕获后重试/标记。
- **日志和审计**：记录每条输出的提示词、原始结果，以便追溯。

### 3.3 后处理
- 解析完的 JSON 可进一步加载为 Pandas DataFrame，导出 Excel 或入库。
- 根据 schema 中的描述、单位信息做二次校验，如数值范围、枚举值等。

## 4. 扩展建议

- **分层处理**：先用规则或传统 NLP 抓取明显字段，再让 LLM 补全/校验。
- **Prompt 参数化**：可在 `structure_exam.py` 中扩展提示词模板，例如固定输出顺序、要求引用原文片段等。
- **模型抽象层**：若需要切换到其他 LLM 服务（如本地模型），替换 `call_llm` 函数即可。
- **批量接口**：结合 FastAPI/Flask 包装为服务，提供 HTTP 接口批量提交任务。

## 5. 常见问题

- **输出非 JSON**：提示词中强调“只能返回 JSON”；解析失败时打印原始输出以便人工修正。
- **字段缺失**：说明原文未提供信息或模型理解不到位，可考虑补充示例、压缩 schema 字段数量。
- **跨 schema 文本**：如果一段文本涉及多个检查类型，可在前置阶段做分类或在提示词中描述多 schema 结构。

---
以上流程可直接放入 README 或团队 Wiki，按需调整成你的技术栈。需要协助搭建批处理脚本或服务端实现时，可以继续扩展。 
