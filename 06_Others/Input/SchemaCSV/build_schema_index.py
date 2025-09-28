#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional

UNIT_IN_DESC_RE = re.compile(r"单位[:：]\s*([^\n<*]+)")
PAREN_CONTENT_RE = re.compile(r"[（(]([^()（）]+)[)）]")
HTML_BREAK_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)

UNIT_MARKERS = {
    "g", "kg", "mg", "μg", "ng", "pg", "fg", "mol", "mmol",
    "nmol", "pmol", "fL", "pL", "L", "mL", "μL",
    "IU", "IU/L", "U", "U/L", "mmHg", "kPa", "Pa",
    "cm", "mm", "m", "cm²", "cm³", "m²", "m³",
    "%", "℃", "°C", "次/分", "次/min", "秒", "分钟", "小时", "天",
    "日", "周", "月", "年", "BPM", "AU", "HU", "dB", "kg/m²",
    "mg/24h", "μmol/24h", "nmol/24h", "个/HP", "个/LP",
    "×10⁹/L", "×10¹²/L", "×10⁶/mL", "×10⁶"
}


@dataclass
class FieldSchema:
    english_name: str
    chinese_name: str
    data_type: str
    description_html: str
    description_text: str
    example: str
    unit: Optional[str]


def clean_html(text: str) -> str:
    text = HTML_BREAK_RE.sub(" ", text)
    return text.replace("\u3000", " ").strip()


def is_unit_candidate(candidate: str) -> bool:
    cand = candidate.strip()
    if not cand:
        return False
    if any(marker in cand for marker in UNIT_MARKERS):
        return True
    return bool(re.search(r"[A-Za-zμnmMkKgG/%°]+", cand))


def extract_unit(description: str, chinese_name: str, english_name: str) -> Optional[str]:
    match = UNIT_IN_DESC_RE.search(description)
    if match:
        return match.group(1).strip()
    for text in (chinese_name, english_name):
        for candidate in PAREN_CONTENT_RE.findall(text):
            if is_unit_candidate(candidate):
                return candidate.strip()
    return None


def normalize_row(row: List[str]) -> List[str]:
    if len(row) < 5:
        return row + ["" for _ in range(5 - len(row))]
    if len(row) == 5:
        return row
    merged_desc = ",".join(row[3:-1])
    return row[:3] + [merged_desc, row[-1]]


def parse_schema_csv(path: Path) -> List[FieldSchema]:
    fields: List[FieldSchema] = []
    with path.open(encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header_seen = False
        for raw_row in reader:
            if not raw_row:
                continue
            row = [cell.strip() for cell in normalize_row(raw_row)]
            if not header_seen:
                header_seen = True
                continue
            english_name, chinese_name, data_type, desc_html, example = row[:5]
            if not english_name:
                continue
            desc_html = desc_html or ""
            desc_text = clean_html(desc_html)
            unit = extract_unit(desc_text, chinese_name, english_name)
            fields.append(
                FieldSchema(
                    english_name=english_name,
                    chinese_name=chinese_name,
                    data_type=data_type,
                    description_html=desc_html,
                    description_text=desc_text,
                    example=example,
                    unit=unit,
                )
            )
    return fields


def build_index(directory: Path) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    index: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
    for csv_path in sorted(directory.glob("*.csv")):
        schema_name = csv_path.stem
        fields = parse_schema_csv(csv_path)
        index[schema_name] = {
            "schema_name": schema_name,
            "source": csv_path.name,
            "fields": [asdict(field) for field in fields]
        }
    return index


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build JSON index from schema CSV files")
    parser.add_argument("--input-dir", type=Path, default=Path.cwd(), help="Folder containing schema CSV files")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON path")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    index = build_index(args.input_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
