#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split the comprehensive endocrine knowledge graph JSON into modular CSV files with an index."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "comprehensive_endocrine_knowledge_graph.json"
OUTPUT_DIR = BASE_DIR / "modular_endocrine_knowledge"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VALUE_JOINER = "; "
ID_CANDIDATE_KEYS = [
    "id",
    "pattern_id",
    "rule_id",
    "case_id",
    "code",
    "entity_id",
]
NAME_CANDIDATE_KEYS = [
    "name",
    "title",
    "rule_name",
    "case_name",
]
TYPE_CANDIDATE_KEYS = [
    "type",
    "entity_type",
    "category",
]
CATEGORY_CANDIDATE_KEYS = ["category", "domain", "group"]
BASE_FIELDS = set(ID_CANDIDATE_KEYS + NAME_CANDIDATE_KEYS + TYPE_CANDIDATE_KEYS + CATEGORY_CANDIDATE_KEYS)

SECTION_DESCRIPTIONS: Dict[str, str] = {
    "metadata": "图谱元数据与版本信息",
    "system_architecture": "系统架构与模块组件",
    "entities.endocrine_system_entities": "内分泌系统核心实体信息",
    "entities.thyroid_entities": "甲状腺相关实体定义",
    "entities.diabetes_entities": "糖尿病实体定义",
    "entities.diabetes_complications": "糖尿病并发症实体详表",
    "entities.diabetes_medications": "糖尿病药物信息",
    "entities.diabetes_technology_devices": "糖尿病监测与设备",
    "entities.adrenal_entities": "肾上腺相关实体",
    "entities.pituitary_entities": "垂体相关实体",
    "entities.hypertension_entities": "高血压相关实体",
    "entities.gonadal_entities": "性腺相关实体",
    "entities.dyslipidemia_entities": "血脂异常相关实体",
    "parathyroid_calcium_entities": "甲状旁腺与钙代谢实体",
    "bone_metabolism_entities": "骨代谢相关实体",
    "endocrine_tumor_entities": "内分泌肿瘤实体",
    "obesity_metabolic_entities": "肥胖与代谢综合征实体",
    "nutrition_endocrine_entities": "营养与内分泌相关实体",
    "pediatric_endocrine_entities": "儿童内分泌实体",
    "female_endocrine_entities": "女性内分泌实体",
    "male_endocrine_entities": "男性内分泌实体",
    "glucose_management_entities": "血糖管理实体",
    "rheumatic_endocrine_relationships": "风湿与内分泌关系",
    "cardiovascular_diseases": "心血管疾病实体",
    "cerebrovascular_diseases": "脑血管疾病实体",
    "relationships": "跨系统关系定义",
    "comorbidity_patterns": "共病模式与组成",
    "inference_rules": "推理规则库",
    "clinical_validation_cases": "临床验证病例",
    "llm_integration_architecture": "LLM集成架构说明",
    "research_support_features": "科研支持特性",
}


def normalize_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        if not value:
            return ""
        if all(not isinstance(item, (dict, list)) for item in value):
            return VALUE_JOINER.join(str(item) for item in value)
    text = str(value)
    return re.sub(r"\s+", " ", text).strip()


def flatten(obj: Any, prefix: str = "") -> Iterable[Tuple[str, Any]]:
    if isinstance(obj, dict):
        for key, value in obj.items():
            next_prefix = f"{prefix}.{key}" if prefix else key
            yield from flatten(value, next_prefix)
    elif isinstance(obj, list):
        if not obj:
            yield prefix, ""
        elif all(not isinstance(item, (dict, list)) for item in obj):
            yield prefix, VALUE_JOINER.join(str(item) for item in obj)
        else:
            for index, item in enumerate(obj):
                next_prefix = f"{prefix}[{index}]" if prefix else f"[{index}]"
                yield from flatten(item, next_prefix)
    else:
        yield prefix, obj


def pick_first(item: Dict[str, Any], keys: List[str]) -> str:
    for key in keys:
        if key in item and item[key]:
            return str(item[key])
    return ""


def ensure_list_of_entities(section: str, data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [item if isinstance(item, dict) else {"value": item} for item in data]
    if isinstance(data, dict):
        if any(key in data for key in ID_CANDIDATE_KEYS):
            return [data]
        items: List[Dict[str, Any]] = []
        for key, value in data.items():
            if isinstance(value, dict):
                candidate = dict(value)
                if not any(k in candidate for k in ID_CANDIDATE_KEYS):
                    candidate.setdefault("id", key)
                if not any(k in candidate for k in NAME_CANDIDATE_KEYS):
                    candidate.setdefault("name", key.replace("_", " "))
                items.append(candidate)
            else:
                items.append({"id": key, "value": value})
        return items
    # fallback for primitive
    return [{"id": section, "value": data}]


def generate_rows(section: str, data: Any) -> List[List[str]]:
    rows: List[List[str]] = []
    for entity in ensure_list_of_entities(section, data):
        entity_id = pick_first(entity, ID_CANDIDATE_KEYS) or section
        entity_name = pick_first(entity, NAME_CANDIDATE_KEYS)
        entity_type = pick_first(entity, TYPE_CANDIDATE_KEYS)
        category = pick_first(entity, CATEGORY_CANDIDATE_KEYS)
        core = {k: v for k, v in entity.items() if k not in BASE_FIELDS}
        if not core:
            rows.append([section, entity_id, entity_name, "", entity_type, category, "", ""])
            continue
        for attr_path, value in flatten(core):
            rows.append([
                section,
                entity_id,
                entity_name,
                "",
                entity_type,
                category,
                attr_path,
                normalize_value(value),
            ])
    return rows


def write_csv(file_path: Path, rows: List[List[str]]) -> None:
    with file_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "section",
            "entity_id",
            "entity_name",
            "entity_name_en",
            "entity_type",
            "category",
            "attribute_path",
            "value",
        ])
        writer.writerows(rows)


def main() -> None:
    with INPUT_PATH.open(encoding="utf-8") as fh:
        data = json.load(fh)["comprehensive_endocrine_knowledge_graph"]

    index_rows: List[List[str]] = []

    for section, value in data.items():
        if section == "entities" and isinstance(value, dict):
            for sub_section, sub_value in value.items():
                section_name = f"entities.{sub_section}"
                rows = generate_rows(section_name, sub_value)
                file_name = f"{section_name.replace('.', '_')}.csv"
                write_csv(OUTPUT_DIR / file_name, rows)
                index_rows.append([
                    section_name,
                    file_name,
                    str(len(rows)),
                    SECTION_DESCRIPTIONS.get(section_name, ""),
                ])
            continue

        section_name = section
        rows = generate_rows(section_name, value)
        file_name = f"{section_name.replace('.', '_')}.csv"
        write_csv(OUTPUT_DIR / file_name, rows)
        index_rows.append([
            section_name,
            file_name,
            str(len(rows)),
            SECTION_DESCRIPTIONS.get(section_name, ""),
        ])

    # Write index file
    index_path = OUTPUT_DIR / "index.csv"
    with index_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["section", "file", "rows", "description"])
        writer.writerows(index_rows)

    print(f"Generated {len(index_rows)} CSV files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
