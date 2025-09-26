#!/usr/bin/env python3
"""
修复药物数据库字段数量问题
"""

import csv
import sys

def fix_medication_fields(input_file, output_file):
    """修复缺失字段的问题"""
    
    fixed_count = 0
    total_drugs = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        with open(output_file, 'w', encoding='utf-8', newline='') as out_f:
            reader = csv.reader(f)
            writer = csv.writer(out_f)
            
            for row_num, row in enumerate(reader, 1):
                # 非药物行直接写入
                if not row or not row[0].startswith('D') or not row[0][1:].isdigit():
                    writer.writerow(row)
                    continue
                
                total_drugs += 1
                
                # 检查字段数量
                if len(row) == 23:
                    # 字段完整，直接写入
                    writer.writerow(row)
                elif len(row) == 22:
                    # 缺少肝功能调整字段，在第20个位置插入
                    new_row = row[:20] + ['无需调整'] + row[20:]
                    writer.writerow(new_row)
                    print(f"修复 {row[0]}: 添加肝功能调整字段")
                    fixed_count += 1
                elif len(row) == 21:
                    # 缺少肝功能和肾功能调整字段
                    new_row = row[:19] + ['无需调整', '无需调整'] + row[19:]
                    writer.writerow(new_row)
                    print(f"修复 {row[0]}: 添加肾功能和肝功能调整字段")
                    fixed_count += 1
                else:
                    # 其他情况，需要手动检查
                    print(f"警告: {row[0]} 有 {len(row)} 个字段，需要手动检查")
                    writer.writerow(row)
    
    print(f"\n修复完成:")
    print(f"- 总药物数: {total_drugs}")
    print(f"- 修复数量: {fixed_count}")
    print(f"- 输出文件: {output_file}")

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file  # 直接覆盖原文件
    
    print("开始修复药物数据库字段问题...")
    fix_medication_fields(input_file, output_file)
    print("字段修复完成！")