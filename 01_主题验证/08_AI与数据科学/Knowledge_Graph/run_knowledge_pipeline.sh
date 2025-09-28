#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 split_endocrine_knowledge.py

python3 create_subset.py pregnancy_endocrine.csv 妊娠 孕 pregnancy 胎儿

python3 create_subset.py endocrine_bone.csv 骨 骨质疏松 骨密度 osteoporosis

python3 create_subset.py pediatric_endocrine.csv 儿童 青少年 adolescent pediatric 儿科

if [[ "$#" -gt 0 ]]; then
  python3 rag_demo.py "$@"
fi
