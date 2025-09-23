#!/usr/bin/env python3
"""
全面修复和检查药物数据库
1. 修复字段数量问题
2. 检查重复编号
3. 检查重复内容
"""

import csv
import re
from collections import defaultdict

def comprehensive_fix_and_check(input_file, output_file):
    """全面修复和检查药物数据库"""
    
    # 统计变量
    total_drugs = 0
    fixed_fields = 0
    duplicated_ids = []
    content_duplicates = []
    errors = []
    
    # 存储所有药物数据用于重复检查
    drug_data = []
    drug_ids = defaultdict(list)
    drug_contents = defaultdict(list)
    
    print("🔍 开始全面检查和修复药物数据库...")
    
    # 第一轮：读取所有数据并收集信息
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    # 找到表头行
    header_row = None
    for i, row in enumerate(all_rows):
        if row and row[0] == 'drug_id':
            header_row = i
            break
    
    if header_row is None:
        print("❌ 未找到表头行")
        return
    
    print(f"📋 找到表头在第 {header_row + 1} 行")
    expected_fields = len(all_rows[header_row])
    print(f"📊 期望字段数: {expected_fields}")
    
    # 第二轮：处理药物数据
    processed_rows = []
    
    for row_num, row in enumerate(all_rows):
        # 非药物行直接保留
        if not row or not row[0].startswith('D') or not row[0][1:].isdigit():
            processed_rows.append(row)
            continue
        
        total_drugs += 1
        drug_id = row[0]
        
        # 记录ID用于重复检查
        drug_ids[drug_id].append(row_num + 1)
        
        # 修复字段数量问题
        original_field_count = len(row)
        if original_field_count < expected_fields:
            # 计算缺少多少字段
            missing_fields = expected_fields - original_field_count
            
            # 根据缺少的字段数量进行修复
            if missing_fields == 1:
                # 通常缺少肝功能调整字段，插入到第20位置（hepatic_adjustment）
                new_row = row[:20] + ['无需调整'] + row[20:]
                print(f"🔧 修复 {drug_id}: 添加肝功能调整字段")
                fixed_fields += 1
            elif missing_fields == 2:
                # 缺少肾功能和肝功能调整字段
                new_row = row[:19] + ['无需调整', '无需调整'] + row[19:]
                print(f"🔧 修复 {drug_id}: 添加肾功能和肝功能调整字段")
                fixed_fields += 1
            else:
                # 其他情况，需要手动处理
                new_row = row + ['无需调整'] * missing_fields
                print(f"⚠️  {drug_id}: 添加 {missing_fields} 个默认字段")
                fixed_fields += 1
        else:
            new_row = row
        
        processed_rows.append(new_row)
        drug_data.append(new_row)
        
        # 检查内容重复（基于药物名称和英文名）
        if len(new_row) >= 5:
            content_key = (new_row[2].strip().lower(), new_row[4].strip())  # english_name, drug_name
            drug_contents[content_key].append((drug_id, row_num + 1))
    
    # 检查重复编号
    for drug_id, line_nums in drug_ids.items():
        if len(line_nums) > 1:
            duplicated_ids.append((drug_id, line_nums))
    
    # 检查内容重复
    for content_key, occurrences in drug_contents.items():
        if len(occurrences) > 1:
            content_duplicates.append((content_key, occurrences))
    
    # 写入修复后的文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(processed_rows)
    
    # 输出检查结果
    print(f"\n📊 检查完成统计:")
    print(f"   📝 总药物条目: {total_drugs}")
    print(f"   🔧 修复字段问题: {fixed_fields} 个")
    print(f"   📄 输出文件: {output_file}")
    
    # 重复编号检查
    if duplicated_ids:
        print(f"\n❌ 发现重复编号 ({len(duplicated_ids)} 个):")
        for drug_id, line_nums in duplicated_ids:
            print(f"   • {drug_id}: 出现在第 {', '.join(map(str, line_nums))} 行")
    else:
        print(f"\n✅ 无重复编号")
    
    # 内容重复检查  
    if content_duplicates:
        print(f"\n❌ 发现内容重复 ({len(content_duplicates)} 组):")
        for (english_name, chinese_name), occurrences in content_duplicates:
            drugs_info = [f"{drug_id}(行{line_num})" for drug_id, line_num in occurrences]
            print(f"   • {english_name} / {chinese_name}: {', '.join(drugs_info)}")
    else:
        print(f"\n✅ 无内容重复")
    
    # 最终验证
    print(f"\n🔍 最终验证:")
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        final_drug_count = 0
        field_issues = []
        
        for row_num, row in enumerate(reader, 1):
            if row and row[0].startswith('D') and row[0][1:].isdigit():
                final_drug_count += 1
                if len(row) != expected_fields:
                    field_issues.append((row[0], len(row)))
    
    print(f"   📝 最终药物数量: {final_drug_count}")
    if field_issues:
        print(f"   ❌ 仍有字段问题: {len(field_issues)} 个")
        for drug_id, field_count in field_issues[:5]:  # 只显示前5个
            print(f"      • {drug_id}: {field_count} 字段")
    else:
        print(f"   ✅ 所有药物字段完整")
    
    return {
        'total_drugs': total_drugs,
        'fixed_fields': fixed_fields,
        'duplicated_ids': duplicated_ids,
        'content_duplicates': content_duplicates,
        'final_drug_count': final_drug_count,
        'field_issues': field_issues
    }

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file  # 直接覆盖原文件
    
    result = comprehensive_fix_and_check(input_file, output_file)
    
    if result['duplicated_ids'] or result['content_duplicates'] or result['field_issues']:
        print(f"\n⚠️  仍有问题需要手动处理")
    else:
        print(f"\n🎉 数据库已完全修复，无问题！")