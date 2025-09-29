#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert free-text exam descriptions into structured data using schema definitions.

Usage examples:

    python3 structure_exam.py --schema blood-biochemistry-schema --text "患者空腹血糖 6.8 mmol/L，...")
    python3 structure_exam.py --schema blood-biochemistry-schema --input-file note.txt

If the OpenAI SDK is available and OPENAI_API_KEY is set, the script will call the
model and attempt to parse its JSON output. Otherwise it will print a prompt for
manual use with your preferred LLM interface.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_INDEX_PATH = BASE_DIR / "combined_schema_index.json"

try:
    from openai import OpenAI  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None


def load_schema(schema_name: str) -> Dict[str, Any]:
    if not SCHEMA_INDEX_PATH.exists():
        raise FileNotFoundError(f"未找到 {SCHEMA_INDEX_PATH}")

    with SCHEMA_INDEX_PATH.open(encoding="utf-8") as fh:
        data = json.load(fh)

    entry = data.get(schema_name)
    if not entry:
        raise KeyError(f"schema '{schema_name}' 不存在，请确认名称是否与 CSV 文件一致")
    return entry


def build_prompt(schema_entry: Dict[str, Any], free_text: str) -> str:
    header = (
        "你是一名临床数据结构化助手。根据以下自由文本记录，从提供的字段中选择"\
        "能够确认的项目填写数值或描述。只使用给定字段，不要编造不存在的信息。"\
        "输出必须是 JSON 格式，结构如下：\n"\
        '{"schema": "<schema_name>", "data": {<字段英文名>: <值或子对象>}}\n'\
        "对于未知字段，请省略而不是填写 null。"
    )

    rows = []
    for field in schema_entry.get("fields", []):
        rows.append(
            f"- {field['english_name']}: {field.get('chinese_name', '')}"
            f" | 类型: {field.get('data_type', 'String')}"
            f" | 描述: {field.get('description_text', '')}"
        )

    schema_overview = "\n".join(rows)

    prompt = (
        f"{header}\n\n"
        f"Schema 名称: {schema_entry.get('schema_name')}\n"
        f"字段列表:\n{schema_overview}\n\n"
        f"待结构化文本:\n{free_text.strip()}\n\n"
        f"请直接返回 JSON，不要添加额外说明。"
    )
    return prompt


def call_llm(prompt: str, model: str = "gpt-4o-mini") -> str:
    if OpenAI is None:
        raise RuntimeError("未安装 openai SDK，请先运行 `pip install openai` 或使用 --show-prompt 模式")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("未设置 OPENAI_API_KEY 环境变量")

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=prompt,
        temperature=0.0,
        max_output_tokens=1500,
    )

    text = "".join([segment.text for segment in response.output if hasattr(segment, "text")])
    return text.strip()


def parse_json_output(raw: str) -> Dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        # 清理 Markdown 代码块
        raw = raw.strip("`")
        if raw.lstrip().startswith("json"):
            raw = raw.split('\n', 1)[1]
    return json.loads(raw)


def main() -> None:
    parser = argparse.ArgumentParser(description="将检查描述结构化")
    parser.add_argument("--schema", required=True, help="schema 名称（例如 blood-biochemistry-schema）")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="直接输入的自由文本")
    group.add_argument("--input-file", type=Path, help="包含原始文本的文件路径")
    parser.add_argument("--model", default="gpt-4o-mini", help="LLM 模型名称")
    parser.add_argument("--show-prompt", action="store_true", help="仅生成提示词，不调用模型")
    args = parser.parse_args()

    if args.input_file:
        if not args.input_file.exists():
            print(f"无法找到输入文件：{args.input_file}", file=sys.stderr)
            sys.exit(1)
        free_text = args.input_file.read_text(encoding="utf-8")
    else:
        free_text = args.text or ""

    schema_entry = load_schema(args.schema)
    prompt = build_prompt(schema_entry, free_text)

    if args.show_prompt:
        print(prompt)
        return

    try:
        raw_output = call_llm(prompt, model=args.model)
    except RuntimeError as exc:
        print(f"[提示] {exc}")
        print("以下是可在其他 LLM 工具中使用的提示词：\n")
        print(prompt)
        sys.exit(0)

    try:
        structured = parse_json_output(raw_output)
    except json.JSONDecodeError:
        print("模型输出无法解析为 JSON，原始输出如下：")
        print(raw_output)
        sys.exit(1)

    print(json.dumps(structured, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
