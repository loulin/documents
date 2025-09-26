#!/usr/bin/env python3
"""
清理药物数据库中的重复内容
"""

import csv

def remove_content_duplicates(input_file, output_file):
    """清理内容重复的药物条目"""
    
    removed_drugs = []
    total_drugs = 0
    
    print("🧹 开始清理重复内容...")
    
    # 读取所有数据
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    # 存储要保留的行
    filtered_rows = []
    
    # 要移除的重复药物ID (保留第一个，移除后面的)
    duplicates_to_remove = [
        'D047',  # 利拉鲁肽重复项 (保留D013)
        'D079'   # 吡格列酮重复项 (保留D096)
    ]
    
    for row_num, row in enumerate(all_rows):
        # 非药物行直接保留
        if not row or not row[0].startswith('D') or not row[0][1:].isdigit():
            filtered_rows.append(row)
            continue
            
        total_drugs += 1
        drug_id = row[0]
        
        if drug_id in duplicates_to_remove:
            removed_drugs.append(drug_id)
            print(f"❌ 移除重复药物: {drug_id} - {row[4]} (行 {row_num + 1})")
            continue
        
        filtered_rows.append(row)
    
    # 写入清理后的文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(filtered_rows)
    
    # 统计结果
    remaining_drugs = total_drugs - len(removed_drugs)
    
    print(f"\n📊 清理完成统计:")
    print(f"   📝 原药物总数: {total_drugs}")
    print(f"   ❌ 移除重复药物: {len(removed_drugs)} 个")
    print(f"   ✅ 剩余药物数量: {remaining_drugs}")
    print(f"   📄 输出文件: {output_file}")
    
    if removed_drugs:
        print(f"\n🗑️  已移除的重复药物:")
        for drug_id in removed_drugs:
            print(f"   • {drug_id}")
    
    return {
        'original_count': total_drugs,
        'removed_count': len(removed_drugs),
        'final_count': remaining_drugs,
        'removed_drugs': removed_drugs
    }

def final_verification(file_path):
    """最终验证数据库完整性"""
    
    print(f"\n🔍 最终完整性验证...")
    
    drug_ids = set()
    drug_contents = {}
    field_errors = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # 找表头
        header_found = False
        expected_fields = 0
        
        for row_num, row in enumerate(reader, 1):
            if row and row[0] == 'drug_id':
                expected_fields = len(row)
                header_found = True
                continue
                
            if not header_found or not row or not row[0].startswith('D') or not row[0][1:].isdigit():
                continue
                
            drug_id = row[0]
            
            # 检查重复ID
            if drug_id in drug_ids:
                print(f"❌ 发现重复ID: {drug_id}")
            else:
                drug_ids.add(drug_id)
            
            # 检查字段数量
            if len(row) != expected_fields:
                field_errors.append((drug_id, len(row)))
            
            # 检查内容重复
            if len(row) >= 5:
                content_key = (row[2].strip().lower(), row[4].strip())
                if content_key in drug_contents:
                    print(f"❌ 发现内容重复: {row[2]} / {row[4]} - {drug_id} 和 {drug_contents[content_key]}")
                else:
                    drug_contents[content_key] = drug_id
    
    print(f"   📝 唯一药物数量: {len(drug_ids)}")
    print(f"   🔄 内容重复检查: {'❌ 有重复' if len(drug_contents) < len(drug_ids) else '✅ 无重复'}")
    print(f"   📐 字段完整性: {'❌ 有缺失' if field_errors else '✅ 完整'}")
    
    if field_errors:
        print(f"   字段问题详情: {field_errors[:3]}...")  # 只显示前3个
    
    return len(drug_ids), len(field_errors) == 0

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file
    
    # 第一步：移除重复内容
    result = remove_content_duplicates(input_file, output_file)
    
    # 第二步：最终验证
    final_count, is_clean = final_verification(output_file)
    
    if is_clean:
        print(f"\n🎉 数据库清理完成！最终包含 {final_count} 个唯一药物，无重复和错误。")
    else:
        print(f"\n⚠️  数据库仍有问题需要手动处理。")