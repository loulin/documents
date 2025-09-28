#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create keyword-filtered subset CSVs from modular endocrine knowledge."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable, List

BASE_DIR = Path(__file__).resolve().parent
MODULAR_DIR = BASE_DIR / "modular_endocrine_knowledge"
SUBSET_DIR = MODULAR_DIR / "subsets"
SUBSET_DIR.mkdir(parents=True, exist_ok=True)

FIELDS = [
    "section",
    "entity_id",
    "entity_name",
    "entity_name_en",
    "entity_type",
    "category",
    "attribute_path",
    "value",
    "source_file",
]


def keyword_match(text: str, keywords: List[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def filter_rows(keywords: List[str]) -> Iterable[List[str]]:
    for csv_path in sorted(MODULAR_DIR.glob("*.csv")):
        if csv_path.name == "index.csv" or csv_path.is_dir():
            continue
        with csv_path.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                text_parts = [row.get(field, "") for field in reader.fieldnames or []]
                combined = " ".join(part for part in text_parts if part)
                if keyword_match(combined, keywords):
                    yield [
                        row.get("section", ""),
                        row.get("entity_id", ""),
                        row.get("entity_name", ""),
                        row.get("entity_name_en", ""),
                        row.get("entity_type", ""),
                        row.get("category", ""),
                        row.get("attribute_path", ""),
                        row.get("value", ""),
                        csv_path.name,
                    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create keyword-based subset CSV from modular knowledge base")
    parser.add_argument("output", help="Output CSV file name (will be stored under subsets directory)")
    parser.add_argument("keywords", nargs="+", help="Keywords to filter rows (case-insensitive)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = SUBSET_DIR / args.output
    rows = list(filter_rows(args.keywords))
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(FIELDS)
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
