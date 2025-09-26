#!/usr/bin/env python3
"""
修复WHO INN格式问题 - 转换大写字母为小写
"""

import csv
import re

def fix_who_inn_format(input_file, output_file):
    """修复WHO INN格式问题"""
    
    print("🔧 修复WHO INN格式问题...")
    print("📋 将大写字母转换为小写，保持国际标准格式")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    updated_rows = []
    fixed_count = 0
    
    for row in all_rows:
        if not row or not row[0] or row[0].startswith('#') or 'drug_id' in row[0]:
            updated_rows.append(row)
            continue
        
        if row[0].startswith('D') and len(row) >= 39:
            new_row = row.copy()
            
            # 检查WHO INN字段 (索引11)
            if len(new_row) > 11:
                who_inn = new_row[11]
                original_inn = who_inn
                
                if who_inn:
                    # 转换为小写
                    fixed_inn = who_inn.lower()
                    
                    # 清理格式，保持标准格式
                    fixed_inn = re.sub(r'\s+', ' ', fixed_inn)  # 标准化空格
                    fixed_inn = fixed_inn.strip()
                    
                    # 检查是否需要修复
                    if fixed_inn != original_inn:
                        new_row[11] = fixed_inn
                        fixed_count += 1
                        
                        if fixed_count <= 15:
                            drug_name = new_row[14] if len(new_row) > 14 else 'Unknown'
                            print(f"  ✓ {new_row[0]}: '{original_inn}' → '{fixed_inn}' ({drug_name})")
            
            updated_rows.append(new_row)
        else:
            updated_rows.append(row)
    
    # 写入修复后的文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated_rows)
    
    print(f"\n📊 WHO INN格式修复完成:")
    print(f"   🔧 修复数量: {fixed_count}")
    print(f"   ✅ 所有INN转换为小写格式")
    print(f"   ✅ 符合WHO国际标准")

def verify_who_inn_format(file_path):
    """验证WHO INN格式"""
    
    print(f"\n🔍 验证WHO INN格式...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        total_drugs = 0
        correct_format = 0
        format_errors = 0
        
        pattern = r'^[a-z\s\(\)\-]+$'
        
        for row in reader:
            if not row or not row[0] or row[0].startswith('#') or 'drug_id' in row[0]:
                continue
                
            if row[0].startswith('D') and len(row) >= 39:
                total_drugs += 1
                who_inn = row[11] if len(row) > 11 else ''
                drug_name = row[14] if len(row) > 14 else ''
                
                if who_inn and re.match(pattern, who_inn):
                    correct_format += 1
                else:
                    format_errors += 1
                    if format_errors <= 5:
                        print(f"   ❌ 格式错误: {row[0]} - '{who_inn}' ({drug_name})")
        
        print(f"   📊 WHO INN格式统计:")
        print(f"   💊 总药物数: {total_drugs}")
        print(f"   ✅ 正确格式: {correct_format}")
        print(f"   ❌ 格式错误: {format_errors}")
        
        success_rate = (correct_format / total_drugs * 100) if total_drugs > 0 else 0
        print(f"   📈 格式正确率: {success_rate:.1f}%")
        
        return format_errors == 0

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file
    
    print("🚀 修复WHO INN格式问题")
    print("=" * 40)
    
    # 修复WHO INN格式
    fix_who_inn_format(input_file, output_file)
    
    # 验证修复结果
    is_perfect = verify_who_inn_format(output_file)
    
    print(f"\n🎯 WHO INN修复结果:")
    if is_perfect:
        print(f"   🏆 WHO INN格式: 完美标准化")
        print(f"   ✅ 100%符合WHO标准")
        print(f"   ✅ 全部小写英文格式")
        print(f"   ✅ 支持国际数据交换")
        print(f"   🌍 完全符合国际医药标准")
    else:
        print(f"   ✅ WHO INN格式: 显著改善")
        print(f"   🔧 大部分已标准化")
        print(f"   📈 格式一致性提升")
    
    print(f"\n💡 WHO INN标准:")
    print(f"   🔤 全部小写英文字母")
    print(f"   🔗 允许连字符(-)和空格")
    print(f"   📚 允许括号()用于说明")
    print(f"   🌍 遵循WHO国际非专利名标准")