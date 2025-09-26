#!/usr/bin/env python3
"""
修复缺失的中英文名称字段
填充 english_name 和 chinese_acronym 字段
"""

import csv
import re

def fix_missing_name_fields(input_file, output_file):
    """修复缺失的名称字段"""
    
    print("🔧 修复缺失的药物名称字段...")
    print("📋 目标字段:")
    print("   - english_name (第12列)")
    print("   - chinese_acronym (第13列)")
    
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
            drug_id = row[0]
            new_row = row.copy()
            
            # 从现有数据字段获取信息
            who_inn = row[11] if len(row) > 11 else ''  # WHO国际通用名
            existing_english = row[19] if len(row) > 19 else ''  # 原english_name位置
            chinese_acronym_old = row[20] if len(row) > 20 else ''  # 原chinese_acronym位置
            drug_name = row[21] if len(row) > 21 else ''  # 中文通用名
            brand_name = row[22] if len(row) > 22 else ''  # 商品名
            
            # 修复 english_name (第12列)
            if not new_row[12]:  # 如果英文名为空
                if who_inn and who_inn != 'generic_name':
                    # 使用WHO国际通用名
                    new_row[12] = who_inn.title()
                elif existing_english:
                    # 使用原有英文名
                    new_row[12] = existing_english
                else:
                    # 生成英文名
                    if '胰岛素' in drug_name:
                        if '人胰岛素' in drug_name:
                            if '30' in drug_name:
                                new_row[12] = 'Human Insulin 30/70'
                            else:
                                new_row[12] = 'Human Insulin'
                        elif '地特' in drug_name:
                            new_row[12] = 'Insulin Detemir'
                        elif '德谷' in drug_name:
                            new_row[12] = 'Insulin Degludec'
                        elif '甘精' in drug_name:
                            new_row[12] = 'Insulin Glargine'
                        elif '谷赖' in drug_name:
                            new_row[12] = 'Insulin Glulisine'
                        elif '赖脯' in drug_name:
                            if '25' in drug_name:
                                new_row[12] = 'Insulin Lispro 25'
                            elif '50' in drug_name:
                                new_row[12] = 'Insulin Lispro 50'
                            else:
                                new_row[12] = 'Insulin Lispro'
                        elif '门冬' in drug_name:
                            if '30' in drug_name:
                                new_row[12] = 'Insulin Aspart 30'
                            elif '50' in drug_name:
                                new_row[12] = 'Insulin Aspart 50'
                            elif '70' in drug_name:
                                new_row[12] = 'Insulin Aspart 70'
                            else:
                                new_row[12] = 'Insulin Aspart'
                    elif '二甲双胍' in drug_name or 'metformin' in who_inn.lower():
                        if '缓释' in drug_name:
                            new_row[12] = 'Metformin Extended Release'
                        else:
                            new_row[12] = 'Metformin'
                    elif '利拉鲁肽' in drug_name:
                        new_row[12] = 'Liraglutide'
                    elif '司美格鲁肽' in drug_name:
                        new_row[12] = 'Semaglutide'
                    elif '格列' in drug_name:
                        if '格列齐特' in drug_name:
                            new_row[12] = 'Gliclazide'
                        elif '格列美脲' in drug_name:
                            new_row[12] = 'Glimepiride'
                        elif '格列本脲' in drug_name:
                            new_row[12] = 'Glyburide'
                        else:
                            new_row[12] = 'Sulfonylurea'
                    elif '西格列汀' in drug_name:
                        new_row[12] = 'Sitagliptin'
                    elif '维格列汀' in drug_name:
                        new_row[12] = 'Vildagliptin'
                    elif '沙格列汀' in drug_name:
                        new_row[12] = 'Saxagliptin'
                    elif '卡格列净' in drug_name:
                        new_row[12] = 'Canagliflozin'
                    elif '达格列净' in drug_name:
                        new_row[12] = 'Dapagliflozin'
                    elif '恩格列净' in drug_name:
                        new_row[12] = 'Empagliflozin'
                    elif '吡格列酮' in drug_name:
                        new_row[12] = 'Pioglitazone'
                    elif '罗格列酮' in drug_name:
                        new_row[12] = 'Rosiglitazone'
                    else:
                        # 默认处理
                        clean_name = re.sub(r'[^\u4e00-\u9fa5a-zA-Z\s]', '', drug_name)
                        new_row[12] = f"Generic_{drug_id}"
            
            # 修复 chinese_acronym (第13列)
            if not new_row[13]:  # 如果中文缩写为空
                if chinese_acronym_old:
                    # 使用原有缩写
                    new_row[13] = chinese_acronym_old
                else:
                    # 生成中文缩写
                    if '胰岛素' in drug_name:
                        if '人胰岛素' in drug_name:
                            if '30' in drug_name:
                                new_row[13] = 'RYDS30'
                            else:
                                new_row[13] = 'RYDS'
                        elif '地特' in drug_name:
                            new_row[13] = 'DTYDS'
                        elif '德谷' in drug_name:
                            new_row[13] = 'DGYDS'
                        elif '甘精' in drug_name:
                            new_row[13] = 'GJYDS'
                        elif '谷赖' in drug_name:
                            new_row[13] = 'GLYDS'
                        elif '赖脯' in drug_name:
                            if '25' in drug_name:
                                new_row[13] = 'LPYDS25'
                            elif '50' in drug_name:
                                new_row[13] = 'LPYDS50'
                            else:
                                new_row[13] = 'LPYDS'
                        elif '门冬' in drug_name:
                            if '30' in drug_name:
                                new_row[13] = 'MCYDS30'
                            elif '50' in drug_name:
                                new_row[13] = 'MCYDS50'
                            elif '70' in drug_name:
                                new_row[13] = 'MCYDS70'
                            else:
                                new_row[13] = 'MCYDS'
                    elif '二甲双胍' in drug_name:
                        new_row[13] = 'EMSSG'
                    elif '利拉鲁肽' in drug_name:
                        new_row[13] = 'LLLT'
                    elif '司美格鲁肽' in drug_name:
                        new_row[13] = 'SMGLT'
                    elif '格列齐特' in drug_name:
                        new_row[13] = 'GLQT'
                    elif '格列美脲' in drug_name:
                        new_row[13] = 'GLMN'
                    elif '格列本脲' in drug_name:
                        new_row[13] = 'GLBN'
                    elif '西格列汀' in drug_name:
                        new_row[13] = 'XGLT'
                    elif '维格列汀' in drug_name:
                        new_row[13] = 'WGLT'
                    elif '沙格列汀' in drug_name:
                        new_row[13] = 'SGLT'
                    elif '卡格列净' in drug_name:
                        new_row[13] = 'KGLJ'
                    elif '达格列净' in drug_name:
                        new_row[13] = 'DGLJ'
                    elif '恩格列净' in drug_name:
                        new_row[13] = 'ENGLJ'
                    elif '吡格列酮' in drug_name:
                        new_row[13] = 'PGLT'
                    elif '罗格列酮' in drug_name:
                        new_row[13] = 'RGLT'
                    else:
                        # 生成通用缩写
                        new_row[13] = f'YW{drug_id[1:].zfill(3)}'
            
            # 清理原位置的重复数据 (19-22列)
            # 这些列现在应该是 therapeutic_class, specifications, common_dosage, frequency
            # 不需要修改，保持原有数据
            
            fixed_count += 1
            
            # 显示前5个修复结果
            if fixed_count <= 5:
                print(f"  ✓ {drug_id}: {new_row[12]} ({new_row[13]}) - {drug_name}")
            
            updated_rows.append(new_row)
        else:
            updated_rows.append(row)
    
    # 写入修复后的文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated_rows)
    
    print(f"\n📊 修复完成:")
    print(f"   ✅ 修复药物数量: {fixed_count}")
    print(f"   📋 english_name 字段已填充")
    print(f"   📋 chinese_acronym 字段已填充")

def verify_name_fields(file_path):
    """验证名称字段"""
    
    print(f"\n🔍 验证名称字段完整性...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        total_drugs = 0
        empty_english = 0
        empty_chinese_acronym = 0
        
        for row in reader:
            if not row or not row[0] or row[0].startswith('#') or 'drug_id' in row[0]:
                continue
                
            if row[0].startswith('D') and len(row) >= 39:
                total_drugs += 1
                
                english_name = row[12] if len(row) > 12 else ''
                chinese_acronym = row[13] if len(row) > 13 else ''
                drug_name = row[14] if len(row) > 14 else ''
                brand_name = row[15] if len(row) > 15 else ''
                
                if not english_name.strip():
                    empty_english += 1
                if not chinese_acronym.strip():
                    empty_chinese_acronym += 1
                
                # 显示前3个药物的名称字段
                if total_drugs <= 3:
                    print(f"   💊 {row[0]}: EN='{english_name}', CN_SHORT='{chinese_acronym}', CN='{drug_name}', BRAND='{brand_name}'")
    
    print(f"\n📊 名称字段统计:")
    print(f"   💊 药物总数: {total_drugs}")
    print(f"   📋 english_name 缺失: {empty_english}")
    print(f"   📋 chinese_acronym 缺失: {empty_chinese_acronym}")
    print(f"   ✅ english_name 完整度: {((total_drugs - empty_english) / total_drugs * 100):.1f}%")
    print(f"   ✅ chinese_acronym 完整度: {((total_drugs - empty_chinese_acronym) / total_drugs * 100):.1f}%")
    
    return empty_english == 0 and empty_chinese_acronym == 0

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file
    
    print("🚀 修复药物名称字段")
    print("=" * 50)
    
    # 修复缺失的名称字段
    fix_missing_name_fields(input_file, output_file)
    
    # 验证修复结果
    is_complete = verify_name_fields(output_file)
    
    if is_complete:
        print(f"\n🎉 完美！所有名称字段已完整填充")
    else:
        print(f"\n⚠️  还有少量字段需要检查")
    
    print(f"\n💡 字段说明:")
    print(f"   📋 english_name (第12列): 英文通用名")
    print(f"   📋 chinese_acronym (第13列): 中文缩写")
    print(f"   📋 drug_name (第14列): 中文通用名")
    print(f"   📋 brand_name (第15列): 商品名/品牌名")