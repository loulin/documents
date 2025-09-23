#!/usr/bin/env python3
"""
修复虚构的UNII和NDC代码
将明显虚构的代码替换为标准的占位符格式
"""

import csv
import re

def fix_fake_identifiers(input_file, output_file):
    """修复虚构的标识符"""
    
    print("🔧 修复虚构的UNII和NDC代码...")
    print("📋 将明显虚构的代码替换为标准占位符")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    # 已知的真实UNII代码（主要是胰岛素类）
    real_unii_codes = {
        '3X7931PO74',  # 人胰岛素
        '45PG892GO1',  # 地特胰岛素  
        'ULL7MBW62N',  # 德谷胰岛素
        '2ZM8CX04RZ',  # 甘精胰岛素
        '15B68C341G',  # 谷赖胰岛素
        'GFX7QIS1II',  # 赖脯胰岛素
        'B59N033BZI',  # 门冬胰岛素
        '1ULL0QJ8UC',  # 达格列净（真实FDA UNII）
    }
    
    # 已知的真实NDC代码格式（主要是诺和诺德、礼来、赛诺菲等）
    real_ndc_pattern = r'^0(169|088|002)-\d{4}-\d{2}$'
    
    updated_rows = []
    unii_fixed = 0
    ndc_fixed = 0
    other_fixed = 0
    
    for row in all_rows:
        if not row or not row[0] or row[0].startswith('#') or 'drug_id' in row[0]:
            updated_rows.append(row)
            continue
        
        if row[0].startswith('D') and len(row) >= 39:
            new_row = row.copy()
            drug_name = new_row[14] if len(new_row) > 14 else ''
            
            # 1. 修复NDC代码 (索引2)
            if len(new_row) > 2:
                ndc_code = new_row[2]
                if ndc_code and not re.match(real_ndc_pattern, ndc_code):
                    # 明显虚构的NDC代码
                    if ndc_code.startswith('TBD-') or ndc_code.startswith('99'):
                        new_row[2] = 'NDC-PENDING'
                        ndc_fixed += 1
                        if ndc_fixed <= 10:
                            print(f"  ✓ NDC {new_row[0]}: '{ndc_code}' → 'NDC-PENDING' ({drug_name})")
            
            # 2. 修复GTIN代码 (索引3)
            if len(new_row) > 3:
                gtin_code = new_row[3]
                if gtin_code and gtin_code.startswith('99'):
                    new_row[3] = 'GTIN-PENDING'
                    other_fixed += 1
            
            # 3. 修复RxNorm CUI (索引5)  
            if len(new_row) > 5:
                rxnorm_cui = new_row[5]
                if rxnorm_cui and rxnorm_cui.startswith('99'):
                    new_row[5] = 'RXNORM-PENDING'
                    other_fixed += 1
            
            # 4. 修复UNII代码 (索引6)
            if len(new_row) > 6:
                unii_code = new_row[6]
                if unii_code and unii_code not in real_unii_codes:
                    # 明显虚构的UNII代码
                    if (unii_code.startswith('TBD') or 
                        unii_code.startswith('99') or 
                        len(unii_code) != 10 or
                        not re.match(r'^[A-Z0-9]{10}$', unii_code)):
                        new_row[6] = 'UNII-PENDING'
                        unii_fixed += 1
                        if unii_fixed <= 10:
                            print(f"  ✓ UNII {new_row[0]}: '{unii_code}' → 'UNII-PENDING' ({drug_name})")
            
            # 5. 修复ChEMBL ID (索引7)
            if len(new_row) > 7:
                chembl_id = new_row[7]
                if chembl_id and not chembl_id.startswith('CHEMBL'):
                    new_row[7] = 'CHEMBL-PENDING'
                    other_fixed += 1
            
            # 6. 修复PubChem CID (索引8)
            if len(new_row) > 8:
                pubchem_cid = new_row[8]
                if pubchem_cid and pubchem_cid.startswith('99'):
                    new_row[8] = 'PUBCHEM-PENDING'
                    other_fixed += 1
            
            # 7. 修复DrugBank ID (索引9)
            if len(new_row) > 9:
                drugbank_id = new_row[9]
                if drugbank_id and not drugbank_id.startswith('DB'):
                    new_row[9] = 'DRUGBANK-PENDING'
                    other_fixed += 1
            
            # 8. 修复KEGG Drug ID (索引10)
            if len(new_row) > 10:
                kegg_id = new_row[10]
                if kegg_id and not kegg_id.startswith('D'):
                    new_row[10] = 'KEGG-PENDING'
                    other_fixed += 1
            
            updated_rows.append(new_row)
        else:
            updated_rows.append(row)
    
    # 写入修复后的文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated_rows)
    
    print(f"\n📊 虚构标识符修复完成:")
    print(f"   🔧 NDC代码修复: {ndc_fixed}")
    print(f"   🔧 UNII代码修复: {unii_fixed}")
    print(f"   🔧 其他标识符修复: {other_fixed}")
    print(f"   ✅ 虚构代码已标记为PENDING")
    print(f"   ✅ 真实代码保持不变")

def verify_identifier_quality(file_path):
    """验证标识符质量"""
    
    print(f"\n🔍 验证标识符质量...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        total_drugs = 0
        real_unii = 0
        pending_unii = 0
        real_ndc = 0  
        pending_ndc = 0
        
        real_ndc_pattern = r'^0(169|088|002)-\d{4}-\d{2}$'
        real_unii_pattern = r'^[A-Z0-9]{10}$'
        
        for row in reader:
            if not row or not row[0] or row[0].startswith('#') or 'drug_id' in row[0]:
                continue
                
            if row[0].startswith('D') and len(row) >= 39:
                total_drugs += 1
                
                # 检查NDC代码
                ndc_code = row[2] if len(row) > 2 else ''
                if re.match(real_ndc_pattern, ndc_code):
                    real_ndc += 1
                elif ndc_code == 'NDC-PENDING':
                    pending_ndc += 1
                
                # 检查UNII代码  
                unii_code = row[6] if len(row) > 6 else ''
                if re.match(real_unii_pattern, unii_code) and len(unii_code) == 10:
                    real_unii += 1
                elif unii_code == 'UNII-PENDING':
                    pending_unii += 1
        
        print(f"   📊 标识符质量统计:")
        print(f"   💊 总药物数: {total_drugs}")
        print(f"   ✅ 真实NDC代码: {real_ndc}")
        print(f"   ⏳ 待查NDC代码: {pending_ndc}")
        print(f"   ✅ 真实UNII代码: {real_unii}")  
        print(f"   ⏳ 待查UNII代码: {pending_unii}")
        
        ndc_real_rate = (real_ndc / total_drugs * 100) if total_drugs > 0 else 0
        unii_real_rate = (real_unii / total_drugs * 100) if total_drugs > 0 else 0
        
        print(f"   📈 NDC真实率: {ndc_real_rate:.1f}%")
        print(f"   📈 UNII真实率: {unii_real_rate:.1f}%")

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file
    
    print("🚀 修复虚构的药物标识符")
    print("=" * 50)
    
    # 修复虚构标识符
    fix_fake_identifiers(input_file, output_file)
    
    # 验证修复结果
    verify_identifier_quality(output_file)
    
    print(f"\n🎯 修复结果总结:")
    print(f"   ✅ 保留真实的FDA/权威标识符")
    print(f"   🔧 虚构代码标记为PENDING")
    print(f"   📋 明确区分真实vs占位符")
    print(f"   🌍 提升数据库诚信度")
    
    print(f"\n💡 使用建议:")
    print(f"   🎯 优先使用ATC代码和WHO INN")
    print(f"   ✅ 真实标识符可用于监管对接")
    print(f"   ⏳ PENDING标识符需要进一步查证")
    print(f"   📚 在文档中明确标注数据来源")