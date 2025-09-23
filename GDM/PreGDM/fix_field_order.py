#!/usr/bin/env python3
"""
修正字段顺序，确保unique_product_id在正确位置
"""

import csv

def fix_field_order(input_file, output_file):
    """修正字段顺序"""
    
    print("🔧 修正字段顺序...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    fixed_rows = []
    header_fixed = False
    
    for i, row in enumerate(all_rows):
        if not row:
            fixed_rows.append(row)
            continue
            
        # 处理表头
        if not header_fixed and 'drug_id' in row[0]:
            # 正确的字段顺序
            correct_header = [
                'drug_id', 'ca_number', 'unique_product_id', 'english_name', 
                'chinese_acronym', 'drug_name', 'brand_name', 'category', 
                'therapeutic_class', 'specifications', 'common_dosage', 'frequency',
                'route', 'indications', 'contraindications', 'side_effects',
                'drug_interactions', 'special_instructions', 'pregnancy_category',
                'renal_adjustment', 'hepatic_adjustment', 'unit', 'method', 'frequency_std'
            ]
            fixed_rows.append(correct_header)
            header_fixed = True
            print(f"✅ 修正表头，共 {len(correct_header)} 个字段")
            continue
        
        # 处理药物行
        if row[0].startswith('D') and row[0][1:].isdigit():
            if len(row) >= 24:  # 确保有足够字段
                # 重新排列字段顺序
                fixed_row = [
                    row[0],   # drug_id
                    row[1],   # ca_number  
                    row[2],   # unique_product_id (已经在正确位置)
                    row[3],   # english_name
                    row[4],   # chinese_acronym
                    row[5],   # drug_name
                    row[6],   # brand_name
                    row[7],   # category
                    row[8],   # therapeutic_class
                    row[9],   # specifications
                    row[10],  # common_dosage
                    row[11],  # frequency
                    row[12],  # route
                    row[13],  # indications
                    row[14],  # contraindications
                    row[15],  # side_effects
                    row[16],  # drug_interactions
                    row[17],  # special_instructions
                    row[18],  # pregnancy_category
                    row[19],  # renal_adjustment
                    row[20],  # hepatic_adjustment
                    row[21],  # unit
                    row[22],  # method
                    row[23],  # frequency_std
                ]
                fixed_rows.append(fixed_row)
            else:
                print(f"⚠️  {row[0]} 字段不足: {len(row)}")
                fixed_rows.append(row)
        else:
            # 非药物行
            fixed_rows.append(row)
    
    # 写入修正后的文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(fixed_rows)
    
    print(f"✅ 字段顺序已修正")
    
def verify_final_structure(file_path):
    """最终验证"""
    
    print(f"\\n🔍 最终验证...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        header_row = None
        drug_count = 0
        unique_ids = []
        
        for row_num, row in enumerate(reader, 1):
            if not row:
                continue
                
            if 'drug_id' in row[0]:
                header_row = row
                print(f"   📋 表头字段数: {len(row)}")
                print(f"   🔤 前5个字段: {row[:5]}")
                continue
                
            if row[0].startswith('D') and row[0][1:].isdigit():
                drug_count += 1
                if len(row) >= 3:
                    unique_ids.append(row[2])  # unique_product_id应该在第3列
                
                # 检查前几个药物的结构
                if drug_count <= 3:
                    print(f"   💊 {row[0]}: unique_id={row[2]}, name={row[5] if len(row)>5 else 'N/A'}")
    
    print(f"   📊 药物总数: {drug_count}")
    print(f"   🆔 唯一ID数: {len(set(unique_ids))}")
    print(f"   ✅ 唯一性: {'是' if len(set(unique_ids)) == drug_count else '否'}")
    
    return len(set(unique_ids)) == drug_count

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file
    
    fix_field_order(input_file, output_file)
    success = verify_final_structure(output_file)
    
    if success:
        print(f"\\n🎉 完成！数据库现在有三种标识符：")
        print(f"1. drug_id (分类编号): D001, D002, D003...")
        print(f"2. unique_product_id (唯一产品编号): HUMAIUS5E, METFSE1...")  
        print(f"3. ca_number (化学CAS号): 可重复，标识化学物质")
    else:
        print(f"\\n⚠️  仍需调整")