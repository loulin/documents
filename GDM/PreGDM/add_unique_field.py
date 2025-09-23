#!/usr/bin/env python3
"""
为药物数据库添加唯一产品ID字段
"""

import csv
import hashlib
import re

def generate_unique_product_id(row):
    """基于药物信息生成唯一产品ID"""
    
    if len(row) < 10:
        return "UNKNOWN"
    
    # 提取关键信息
    english_name = row[2].strip() if len(row) > 2 else ""
    chinese_name = row[4].strip() if len(row) > 4 else ""
    brand_name = row[5].strip() if len(row) > 5 else ""
    specifications = row[8].strip() if len(row) > 8 else ""
    
    # 1. 英文名缩写
    english_clean = re.sub(r'[^A-Za-z]', '', english_name)
    if len(english_clean) >= 4:
        name_part = english_clean[:4].upper()
    else:
        name_part = (english_clean + chinese_name.replace('胰岛素', 'INS').replace('二甲双胍', 'MET'))[:4].upper()
    
    # 2. 规格特征码
    spec_features = ""
    if 'mg' in specifications:
        # 提取mg数值
        mg_match = re.search(r'(\\d+)mg', specifications)
        if mg_match:
            mg_val = int(mg_match.group(1))
            spec_features += f"M{mg_val%100:02d}"
    elif 'IU' in specifications:
        spec_features += "IU"
    elif 'ml' in specifications:
        spec_features += "ML"
    else:
        spec_features += "XX"
    
    # 3. 剂型代码
    if '注射' in chinese_name or 'Injection' in english_name:
        form_code = "I"
    elif '片' in chinese_name or 'Tablet' in english_name:
        form_code = "T"
    elif '胶囊' in chinese_name or 'Capsule' in english_name:
        form_code = "C"
    elif '缓释' in chinese_name or 'XR' in english_name:
        form_code = "X"
    else:
        form_code = "S"
    
    # 4. 品牌哈希
    brand_hash = hashlib.md5((brand_name + specifications).encode('utf-8')).hexdigest()[:2].upper()
    
    # 组合唯一ID
    unique_id = f"{name_part}{spec_features}{form_code}{brand_hash}"
    
    return unique_id

def add_unique_product_id_field(input_file, output_file):
    """为数据库添加唯一产品ID字段"""
    
    print("🆔 添加唯一产品ID字段...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    # 找到表头行
    header_found = False
    updated_rows = []
    unique_ids = set()
    
    for i, row in enumerate(all_rows):
        if not header_found and row and len(row) > 0 and 'drug_id' in row[0]:
            # 这是表头行，添加unique_product_id字段
            new_header = row.copy()
            new_header.insert(2, 'unique_product_id')
            updated_rows.append(new_header)
            header_found = True
            print(f"✅ 找到表头在第 {i+1} 行，已添加unique_product_id字段")
            continue
        
        if not row or not row[0].startswith('D') or not row[0][1:].isdigit():
            # 非药物行，添加空字段保持结构一致
            if header_found and len(row) > 0:
                new_row = row.copy()
                new_row.insert(2, '')
                updated_rows.append(new_row)
            else:
                updated_rows.append(row)
            continue
        
        # 药物行，生成唯一产品ID
        unique_id = generate_unique_product_id(row)
        
        # 处理重复ID
        original_id = unique_id
        counter = 1
        while unique_id in unique_ids:
            unique_id = f"{original_id}{counter:02d}"
            counter += 1
        
        unique_ids.add(unique_id)
        
        # 插入唯一ID到第3列
        new_row = row.copy()
        new_row.insert(2, unique_id)
        updated_rows.append(new_row)
        
        print(f"  {row[0]}: {row[4] if len(row) > 4 else 'Unknown'} -> {unique_id}")
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated_rows)
    
    print(f"\\n📊 完成统计:")
    print(f"   🆔 生成唯一产品ID: {len(unique_ids)} 个")
    print(f"   📄 输出文件: {output_file}")
    
    return len(unique_ids)

def verify_new_structure(file_path):
    """验证新的文件结构"""
    
    print(f"\\n🔍 验证文件结构...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        drug_count = 0
        unique_ids = set()
        field_counts = {}
        
        for row_num, row in enumerate(reader, 1):
            if not row:
                continue
                
            field_count = len(row)
            field_counts[field_count] = field_counts.get(field_count, 0) + 1
            
            if row[0].startswith('D') and row[0][1:].isdigit():
                drug_count += 1
                if len(row) > 2:
                    unique_id = row[2]
                    if unique_id in unique_ids:
                        print(f"❌ 重复唯一ID: {unique_id} 在行 {row_num}")
                    unique_ids.add(unique_id)
    
    print(f"   💊 药物数量: {drug_count}")
    print(f"   🆔 唯一ID数量: {len(unique_ids)}")
    print(f"   📐 字段数量分布: {field_counts}")
    
    # 检查表头
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if 'drug_id' in line:
                fields = line.strip().split(',')
                print(f"   📋 表头 (行{line_num}): {len(fields)}个字段")
                if len(fields) > 2:
                    print(f"      字段1: {fields[0]}")
                    print(f"      字段2: {fields[1]}")
                    print(f"      字段3: {fields[2]}")
                break
    
    return drug_count == len(unique_ids)

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file
    
    # 添加唯一产品ID字段
    count = add_unique_product_id_field(input_file, output_file)
    
    # 验证结果
    success = verify_new_structure(output_file)
    
    if success:
        print(f"\\n🎉 成功！现在每个药物都有唯一的产品标识符")
        print("\\n标识符说明:")
        print("• drug_id: 分类编号 (D001-D142)")
        print("• unique_product_id: 唯一产品编号")
        print("• ca_number: CAS化学编号 (可重复)")
    else:
        print(f"\\n⚠️  需要进一步检查")