#!/usr/bin/env python3
"""
清理药物数据库中的重复条目
"""

import csv
from collections import defaultdict

def remove_duplicates(input_file, output_file):
    """移除重复的药物条目，保留第一次出现的"""
    
    seen_drugs = set()
    unique_rows = []
    removed_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        for row_num, row in enumerate(reader, 1):
            # 跳过空行和注释行
            if not row or row[0].startswith('#') or not row[0].strip():
                unique_rows.append(row)
                continue
                
            # 检查是否为药物条目
            if row[0].startswith('D') and row[0][1:].isdigit():
                drug_id = row[0]
                
                if drug_id in seen_drugs:
                    print(f"移除重复药物: {drug_id} (行 {row_num})")
                    removed_count += 1
                    continue
                else:
                    seen_drugs.add(drug_id)
                    unique_rows.append(row)
            else:
                unique_rows.append(row)
    
    # 写入清理后的数据
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(unique_rows)
    
    print(f"清理完成:")
    print(f"- 移除重复条目: {removed_count} 个")
    print(f"- 保留唯一药物: {len(seen_drugs)} 个")
    print(f"- 输出文件: {output_file}")

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file  # 直接覆盖原文件
    
    print("开始清理重复药物条目...")
    remove_duplicates(input_file, output_file)
    print("重复条目清理完成！")