#!/usr/bin/env python3
"""
重复检查器 - 全面检查药物数据库中的重复问题
检查：
1. 相同编号但内容不同
2. 不同编号但内容相同
3. 各种标识符的重复情况
"""

import csv
from collections import defaultdict
import hashlib

def comprehensive_duplicate_check(file_path):
    """全面重复检查"""
    
    print("🔍 开始全面重复检查...")
    print("📋 检查项目:")
    print("   1. Drug ID 重复")
    print("   2. 相同内容不同ID")
    print("   3. 各种标识符重复")
    print("   4. 中英文名称重复")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    # 数据收集
    drugs = []
    drug_ids = []
    
    for row in all_rows:
        if not row or not row[0] or row[0].startswith('#') or 'drug_id' in row[0]:
            continue
            
        if row[0].startswith('D') and len(row) >= 39:
            drugs.append(row)
            drug_ids.append(row[0])
    
    print(f"📊 总计药物数量: {len(drugs)}")
    
    # 1. 检查Drug ID重复
    print(f"\n1️⃣ 检查Drug ID重复...")
    drug_id_count = defaultdict(int)
    for drug_id in drug_ids:
        drug_id_count[drug_id] += 1
    
    duplicate_drug_ids = {k: v for k, v in drug_id_count.items() if v > 1}
    if duplicate_drug_ids:
        print(f"   ❌ 发现重复Drug ID: {len(duplicate_drug_ids)} 个")
        for drug_id, count in duplicate_drug_ids.items():
            print(f"      • {drug_id}: 出现 {count} 次")
    else:
        print(f"   ✅ Drug ID 无重复")
    
    # 2. 检查相同内容不同ID
    print(f"\n2️⃣ 检查相同内容不同ID...")
    content_hashes = defaultdict(list)
    
    for drug in drugs:
        # 创建内容指纹 - 使用关键字段
        key_content = {
            'english_name': drug[12] if len(drug) > 12 else '',
            'drug_name': drug[14] if len(drug) > 14 else '',
            'brand_name': drug[15] if len(drug) > 15 else '',
            'manufacturer': drug[16] if len(drug) > 16 else '',
            'specifications': drug[20] if len(drug) > 20 else '',
            'therapeutic_class': drug[19] if len(drug) > 19 else ''
        }
        
        content_str = '|'.join([f"{k}:{v.lower().strip()}" for k, v in key_content.items()])
        content_hash = hashlib.md5(content_str.encode()).hexdigest()
        content_hashes[content_hash].append({
            'drug_id': drug[0],
            'english_name': key_content['english_name'],
            'drug_name': key_content['drug_name'],
            'brand_name': key_content['brand_name']
        })
    
    duplicate_contents = {k: v for k, v in content_hashes.items() if len(v) > 1}
    if duplicate_contents:
        print(f"   ❌ 发现相同内容不同ID: {len(duplicate_contents)} 组")
        for hash_key, drug_list in duplicate_contents.items():
            print(f"      📋 重复组:")
            for drug_info in drug_list:
                print(f"         • {drug_info['drug_id']}: {drug_info['english_name']} | {drug_info['drug_name']}")
    else:
        print(f"   ✅ 无相同内容不同ID的情况")
    
    # 3. 检查各种标识符重复
    print(f"\n3️⃣ 检查标识符重复...")
    
    identifier_fields = {
        'CAS Number': 1,
        'NDC Code': 2,
        'GTIN Code': 3,
        'ATC Code': 4,
        'RxNorm CUI': 5,
        'UNII Code': 6,
        'ChEMBL ID': 7,
        'PubChem CID': 8,
        'DrugBank ID': 9,
        'KEGG Drug ID': 10
    }
    
    identifier_duplicates = {}
    
    for name, col_idx in identifier_fields.items():
        identifier_count = defaultdict(list)
        
        for drug in drugs:
            if len(drug) > col_idx and drug[col_idx].strip():
                identifier_value = drug[col_idx].strip()
                # 跳过明显的占位符
                if not any(placeholder in identifier_value.upper() for placeholder in ['TBD', 'XXX', '999']):
                    identifier_count[identifier_value].append(drug[0])
        
        # 找到重复的标识符
        duplicates = {k: v for k, v in identifier_count.items() if len(v) > 1}
        if duplicates:
            identifier_duplicates[name] = duplicates
            print(f"   ❌ {name} 重复: {len(duplicates)} 个")
            for identifier, drug_list in duplicates.items():
                print(f"      • {identifier}: 药物 {', '.join(drug_list)}")
        else:
            print(f"   ✅ {name} 无重复")
    
    # 4. 检查中英文名称重复
    print(f"\n4️⃣ 检查中英文名称重复...")
    
    name_fields = {
        'English Name': 12,
        'Chinese Name': 14,
        'Brand Name': 15
    }
    
    name_duplicates = {}
    
    for name_type, col_idx in name_fields.items():
        name_count = defaultdict(list)
        
        for drug in drugs:
            if len(drug) > col_idx and drug[col_idx].strip():
                name_value = drug[col_idx].strip().lower()
                name_count[name_value].append({
                    'drug_id': drug[0],
                    'original_name': drug[col_idx].strip()
                })
        
        # 找到重复的名称
        duplicates = {k: v for k, v in name_count.items() if len(v) > 1}
        if duplicates:
            name_duplicates[name_type] = duplicates
            print(f"   ⚠️  {name_type} 重复: {len(duplicates)} 个")
            for name, drug_list in duplicates.items():
                drug_ids = [d['drug_id'] for d in drug_list]
                original_name = drug_list[0]['original_name']
                print(f"      • '{original_name}': 药物 {', '.join(drug_ids)}")
        else:
            print(f"   ✅ {name_type} 无重复")
    
    # 5. 生成重复报告
    print(f"\n📊 重复检查总结:")
    
    total_issues = (
        len(duplicate_drug_ids) + 
        len(duplicate_contents) + 
        len(identifier_duplicates) + 
        len(name_duplicates)
    )
    
    if total_issues == 0:
        print(f"   🎉 完美！未发现任何重复问题")
        print(f"   ✅ Drug ID 唯一性: 100%")
        print(f"   ✅ 内容唯一性: 100%")
        print(f"   ✅ 标识符唯一性: 100%")
        print(f"   ✅ 名称唯一性: 基本唯一(合理重复)")
        return True
    else:
        print(f"   ⚠️  发现 {total_issues} 类重复问题需要处理")
        
        if duplicate_drug_ids:
            print(f"   🔴 Drug ID重复: {len(duplicate_drug_ids)} 个")
        if duplicate_contents:
            print(f"   🔴 内容重复: {len(duplicate_contents)} 组")
        if identifier_duplicates:
            print(f"   🔴 标识符重复: {len(identifier_duplicates)} 类")
        if name_duplicates:
            print(f"   🟡 名称重复: {len(name_duplicates)} 类 (可能合理)")
        
        return False

def analyze_cas_number_duplicates(file_path):
    """专门分析CAS号重复情况"""
    
    print(f"\n🔬 CAS号重复详细分析...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        cas_mapping = defaultdict(list)
        
        for row in reader:
            if not row or not row[0] or row[0].startswith('#') or 'drug_id' in row[0]:
                continue
                
            if row[0].startswith('D') and len(row) >= 39:
                cas_number = row[1] if len(row) > 1 else ''
                if cas_number and cas_number.strip():
                    cas_mapping[cas_number].append({
                        'drug_id': row[0],
                        'english_name': row[12] if len(row) > 12 else '',
                        'drug_name': row[14] if len(row) > 14 else ''
                    })
    
    cas_duplicates = {k: v for k, v in cas_mapping.items() if len(v) > 1}
    
    if cas_duplicates:
        print(f"   📋 CAS号重复详情:")
        for cas_num, drugs in cas_duplicates.items():
            print(f"   🧪 {cas_num}:")
            for drug in drugs:
                print(f"      • {drug['drug_id']}: {drug['english_name']} ({drug['drug_name']})")
        
        print(f"\n   💡 CAS号重复说明:")
        print(f"      • 同一化学成分的不同制剂共享CAS号是正常的")
        print(f"      • 如: 胰岛素的不同规格、不同浓度制剂")
        print(f"      • 如: 同一药物的不同品牌名称")
    else:
        print(f"   ✅ CAS号无重复")

if __name__ == "__main__":
    file_path = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    
    print("🚀 药物数据库重复检查系统")
    print("=" * 60)
    
    # 全面重复检查
    is_clean = comprehensive_duplicate_check(file_path)
    
    # CAS号专项分析
    analyze_cas_number_duplicates(file_path)
    
    print(f"\n🎯 最终评估:")
    if is_clean:
        print(f"   🏆 数据库质量: 优秀 - 无重复问题")
        print(f"   ✅ 可以安全使用于生产环境")
    else:
        print(f"   🔧 数据库质量: 良好 - 有少量需要处理的重复")
        print(f"   📝 建议: 根据业务需求决定是否需要去重")
    
    print(f"\n💡 重复检查说明:")
    print(f"   • Drug ID 必须唯一")
    print(f"   • 相同药物不同规格可以有不同ID")
    print(f"   • CAS号可以重复(同成分不同制剂)")
    print(f"   • 品牌名可以重复(不同厂家同名产品)")
    print(f"   • 标识符重复需要仔细验证")