#!/usr/bin/env python3
"""
为每个药物创建唯一标识符
基于药物特征生成唯一的产品编号
"""

import csv
import hashlib
import re

def generate_unique_identifier(drug_data):
    """为每个药物生成唯一标识符"""
    
    # 方案1: 基于关键特征的结构化编号
    english_name = drug_data['english_name'].strip()
    specifications = drug_data['specifications'].strip()
    route = drug_data['route'].strip()
    brand_name = drug_data['brand_name'].strip()
    
    # 提取关键信息
    # 1. 英文名缩写 (取前3-4个字符)
    english_abbr = re.sub(r'[^A-Z]', '', english_name.upper())[:4]
    if len(english_abbr) < 3:
        english_abbr = english_name.upper().replace(' ', '')[:4]
    
    # 2. 剂型代码
    form_code = ''
    if 'tablet' in english_name.lower() or '片' in drug_data['chinese_name']:
        form_code = 'TAB'
    elif 'injection' in english_name.lower() or '注射' in route:
        form_code = 'INJ'
    elif 'capsule' in english_name.lower() or '胶囊' in drug_data['chinese_name']:
        form_code = 'CAP'
    elif 'solution' in english_name.lower() or '口服液' in drug_data['chinese_name']:
        form_code = 'SOL'
    elif 'XR' in english_name or 'SR' in english_name or '缓释' in drug_data['chinese_name']:
        form_code = 'XR'
    else:
        form_code = 'STD'
    
    # 3. 规格哈希 (前4位)
    spec_hash = hashlib.md5(specifications.encode('utf-8')).hexdigest()[:4].upper()
    
    # 4. 品牌哈希 (前2位)
    brand_hash = hashlib.md5(brand_name.encode('utf-8')).hexdigest()[:2].upper()
    
    # 组合唯一标识符
    unique_id = f"{english_abbr}{form_code}{spec_hash}{brand_hash}"
    
    return unique_id

def create_unique_ids_database(input_file, output_file):
    """为数据库中每个药物创建唯一标识符"""
    
    print("🆔 为每个药物创建唯一标识符...")
    
    drugs_data = []
    unique_ids = set()
    duplicates = []
    
    # 读取现有数据
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    # 找到表头并添加新字段
    header_row_index = None
    for i, row in enumerate(all_rows):
        if row and len(row) > 0 and row[0] == 'drug_id':
            header_row_index = i
            # 在CAS号后添加唯一产品编号字段
            row.insert(2, 'unique_product_id')
            break
    
    if header_row_index is None:
        print("❌ 未找到表头")
        return
    
    # 处理每个药物条目
    for i, row in enumerate(all_rows):
        if i <= header_row_index or not row or not row[0].startswith('D'):
            continue
            
        # 调整后的字段索引 (因为插入了unique_product_id)
        drug_data = {
            'drug_id': row[0],
            'cas_number': row[1],
            'english_name': row[3],  # 原来是2，现在是3
            'chinese_acronym': row[4],  # 原来是3，现在是4
            'chinese_name': row[5],  # 原来是4，现在是5
            'brand_name': row[6],  # 原来是5，现在是6
            'category': row[7],  # 原来是6，现在是7
            'therapeutic_class': row[8],  # 原来是7，现在是8
            'specifications': row[9],  # 原来是8，现在是9
            'route': row[13],  # 原来是12，现在是13
            'full_row': row
        }
        
        # 生成唯一标识符
        base_unique_id = generate_unique_identifier(drug_data)
        unique_id = base_unique_id
        
        # 处理冲突 - 如果已存在则添加数字后缀
        counter = 1
        while unique_id in unique_ids:
            unique_id = f"{base_unique_id}{counter:02d}"
            counter += 1
            if counter > 1:
                duplicates.append((drug_data['drug_id'], drug_data['chinese_name'], base_unique_id))
        
        unique_ids.add(unique_id)
        
        # 插入唯一标识符到第3列 (索引2)
        row.insert(2, unique_id)
        
        drugs_data.append({
            **drug_data,
            'unique_id': unique_id
        })
        
        print(f"  {drug_data['drug_id']}: {drug_data['chinese_name']} -> {unique_id}")
    
    # 写入更新后的文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(all_rows)
    
    # 报告结果
    print(f"\\n📊 唯一标识符生成完成:")
    print(f"   🆔 生成唯一ID: {len(unique_ids)} 个")
    print(f"   🔄 处理冲突: {len(duplicates)} 个")
    print(f"   📄 输出文件: {output_file}")
    
    if duplicates:
        print(f"\\n⚠️  冲突处理 (已自动解决):")
        for drug_id, chinese_name, base_id in duplicates[:5]:
            print(f"   {drug_id} ({chinese_name}): 基础ID {base_id} 有冲突")
    
    # 显示一些示例
    print(f"\\n📝 唯一标识符示例:")
    for drug in drugs_data[:8]:
        print(f"   {drug['drug_id']}: {drug['chinese_name']} = {drug['unique_id']}")
        
    return len(unique_ids)

def verify_uniqueness(file_path):
    """验证唯一标识符的唯一性"""
    
    print(f"\\n🔍 验证唯一标识符...")
    
    unique_ids = set()
    drug_ids = set()
    duplicates = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        for row in reader:
            if row and row[0].startswith('D') and row[0][1:].isdigit():
                drug_id = row[0]
                unique_id = row[2] if len(row) > 2 else ''
                
                if drug_id in drug_ids:
                    print(f"❌ 重复药物ID: {drug_id}")
                drug_ids.add(drug_id)
                
                if unique_id:
                    if unique_id in unique_ids:
                        duplicates.append(unique_id)
                    unique_ids.add(unique_id)
    
    print(f"   🆔 唯一产品ID数量: {len(unique_ids)}")
    print(f"   💊 药物条目数量: {len(drug_ids)}")
    
    if len(unique_ids) == len(drug_ids) and not duplicates:
        print("   ✅ 所有标识符都是唯一的")
        return True
    else:
        print(f"   ❌ 发现问题: 重复标识符 {len(duplicates)} 个")
        return False

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file  # 覆盖原文件
    
    # 创建唯一标识符
    count = create_unique_ids_database(input_file, output_file)
    
    # 验证结果
    is_unique = verify_uniqueness(output_file)
    
    if is_unique:
        print(f"\\n🎉 成功为 {count} 个药物创建了唯一标识符！")
        print("现在每个药物都有三种标识符：")
        print("1. drug_id (D001-D142) - 按类别排序的编号") 
        print("2. unique_product_id - 基于产品特征的唯一编号")
        print("3. ca_number - 化学物质CAS号 (可重复)")
    else:
        print(f"\\n⚠️  还有问题需要解决")