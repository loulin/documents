#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract diabetes-focused knowledge from comprehensive endocrine knowledge graph."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

DIABETES_KEYWORDS = ["糖尿病", "diabetes"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate diabetes-specific knowledge CSV from JSON knowledge graph")
    parser.add_argument("input_json", type=Path, help="Path to comprehensive knowledge graph JSON file")
    parser.add_argument("output_csv", type=Path, help="Path to output CSV file")
    return parser.parse_args()


def collect_entities(obj: Any, entity_map: Dict[str, str]) -> None:
    if isinstance(obj, dict):
        if "id" in obj and "name" in obj:
            entity_map[obj["id"]] = obj.get("name", "")
        for value in obj.values():
            collect_entities(value, entity_map)
    elif isinstance(obj, list):
        for item in obj:
            collect_entities(item, entity_map)


def flatten(obj: Any, prefix: str = "") -> Iterable[Tuple[str, Any]]:
    if isinstance(obj, dict):
        for key, value in obj.items():
            next_prefix = f"{prefix}.{key}" if prefix else key
            yield from flatten(value, next_prefix)
    elif isinstance(obj, list):
        if not obj:
            yield prefix, ""
        elif all(not isinstance(item, (dict, list)) for item in obj):
            joined = "; ".join(str(item) for item in obj)
            yield prefix, joined
        else:
            for index, item in enumerate(obj):
                next_prefix = f"{prefix}[{index}]" if prefix else f"[{index}]"
                yield from flatten(item, next_prefix)
    else:
        yield prefix, obj


def string_contains_diabetes(text: str) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in (kw.lower() for kw in DIABETES_KEYWORDS))


def normalize_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    return re.sub(r"\s+", " ", text).strip()


def should_include_text(value: Any) -> bool:
    if isinstance(value, str):
        return string_contains_diabetes(value)
    if isinstance(value, list):
        return any(should_include_text(item) for item in value)
    if isinstance(value, dict):
        return any(should_include_text(item) for item in value.values())
    return False


def add_entity_rows(rows: List[List[str]], section: str, entities: List[Dict[str, Any]]) -> None:
    for entity in entities:
        entity_id = entity.get("id", "")
        entity_name = entity.get("name", "")
        entity_name_en = entity.get("name_en", "")
        entity_type = entity.get("type", "")
        category = entity.get("category", "")
        core_fields = {k: v for k, v in entity.items() if k not in {"id", "name", "name_en", "type", "category"}}
        for attr_path, value in flatten(core_fields):
            rows.append([
                section,
                entity_id,
                entity_name,
                entity_name_en,
                entity_type,
                category,
                attr_path,
                normalize_value(value),
            ])


def main() -> None:
    args = parse_args()
    with args.input_json.open(encoding="utf-8") as fh:
        data = json.load(fh)

    graph = data.get("comprehensive_endocrine_knowledge_graph", {})
    entities_section = graph.get("entities", {})

    # Build entity map for ID -> name resolution
    entity_map: Dict[str, str] = {}
    collect_entities(data, entity_map)
    entity_map.setdefault("DIS_001", "糖尿病")

    diabetes_ids = {eid for eid, name in entity_map.items() if name and string_contains_diabetes(name)}
    diabetes_ids.update({eid for eid in entity_map if eid.startswith("DM_") or eid.startswith("GDM_")})
    diabetes_ids.add("DIS_001")

    rows: List[List[str]] = []

    # Extract diabetes-specific entity groups
    for section_key in [
        "diabetes_entities",
        "diabetes_complications",
        "diabetes_medications",
        "diabetes_technology_devices",
    ]:
        entities = entities_section.get(section_key)
        if isinstance(entities, list):
            add_entity_rows(rows, section_key, entities)

    # Clinical decision pathways filtered for diabetes context
    clinical_pathways = graph.get("clinical_decision_pathways", {})
    for attr_path, value in flatten(clinical_pathways):
        if string_contains_diabetes(attr_path) or should_include_text(value):
            rows.append([
                "clinical_decision_pathways",
                "CLINICAL_PATHWAY",
                "临床决策路径",
                "Clinical Decision Pathways",
                "pathway",
                "clinical",
                attr_path,
                normalize_value(value),
            ])

    # Comorbidity patterns involving diabetes
    for pattern in graph.get("comorbidity_patterns", []) or []:
        name = pattern.get("name", "")
        description = pattern.get("description", "")
        components = pattern.get("components", [])
        has_diabetes_component = any(comp in diabetes_ids for comp in components)
        if has_diabetes_component or string_contains_diabetes(name) or string_contains_diabetes(description):
            section = "comorbidity_patterns"
            entity_id = pattern.get("pattern_id", "")
            entity_name = name
            entity_name_en = pattern.get("name_en", "")
            entity_type = "comorbidity_pattern"
            category = "pattern"
            core_fields = {k: v for k, v in pattern.items() if k not in {"pattern_id", "name", "name_en"}}
            for attr_path, value in flatten(core_fields):
                rows.append([
                    section,
                    entity_id,
                    entity_name,
                    entity_name_en,
                    entity_type,
                    category,
                    attr_path,
                    normalize_value(value),
                ])

    # Relationships where source or target linked to diabetes
    for rel in graph.get("relationships", []) or []:
        source = rel.get("source")
        target = rel.get("target")
        if source not in diabetes_ids and target not in diabetes_ids:
            continue
        enriched_rel = {k: v for k, v in rel.items()}
        enriched_rel["source_name"] = entity_map.get(source) or source or ""
        enriched_rel["target_name"] = entity_map.get(target) or target or ""
        section = "relationships"
        entity_id = rel.get("id", "")
        entity_name = f"{entity_map.get(source, source)} -> {entity_map.get(target, target)}"
        entity_name_en = ""
        entity_type = rel.get("type", "relationship")
        category = "relationship"
        core_fields = {k: v for k, v in enriched_rel.items() if k not in {"id"}}
        for attr_path, value in flatten(core_fields):
            rows.append([
                section,
                entity_id,
                entity_name,
                entity_name_en,
                entity_type,
                category,
                attr_path,
                normalize_value(value),
            ])

    # Sort rows for readability
    rows.sort(key=lambda r: (r[0], r[1], r[6]))

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as out_f:
        writer = csv.writer(out_f)
        writer.writerow([
            "source_section",
            "entity_id",
            "entity_name",
            "entity_name_en",
            "entity_type",
            "category",
            "attribute_path",
            "value",
        ])
        writer.writerows(rows)


if __name__ == "__main__":
    main()
