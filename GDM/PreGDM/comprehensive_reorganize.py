#!/usr/bin/env python3
"""
全面重组药物数据库：修正CAS号、重新编号、优化分类
"""

import csv
import re
from collections import defaultdict

# 正确的CAS号映射表
CORRECT_CAS_MAPPING = {
    # 胰岛素类 - 每个变体应该有独特标识
    'Human Insulin': '11061-68-0',  # 人胰岛素基础CAS
    'Human Insulin 30/70': '11061-68-0',  # 复方制剂保持基础CAS但加备注
    'Insulin Aspart': '116094-23-6',
    'Insulin Aspart 30': '116094-23-6',  # 门冬胰岛素30
    'Insulin Aspart 50': '116094-23-6',  # 门冬胰岛素50
    'Insulin Lispro': '133107-64-9',
    'Insulin Lispro 25': '133107-64-9',
    'Insulin Lispro 50': '133107-64-9',
    
    # 二甲双胍类
    'Metformin': '657-24-9',
    'Metformin XR': '657-24-9',  # 缓释制剂同一CAS
    
    # GLP-1类
    'Semaglutide': '910463-68-2',
    'Oral Semaglutide': '910463-68-2',  # 口服制剂
    'Dulaglutide': '923950-08-7',
    'Polyethylene Glycol Loxenatide': '461432-26-8',  # 正确的洛塞那肽CAS
    
    # 紫杉醇类
    'Paclitaxel': '33069-62-4',
    'Albumin-bound Paclitaxel': '33069-62-4',  # 白蛋白结合型
}

# 药物分类重新定义
DRUG_CATEGORIES = {
    1: {'name': '糖尿病用药', 'range': (1, 100), 'subcategories': {
        '胰岛素及类似物': (1, 30),
        '口服降糖药': (31, 70),
        'GLP-1受体激动剂': (71, 85),
        '其他糖尿病药物': (86, 100)
    }},
    2: {'name': '心血管用药', 'range': (101, 150)},
    3: {'name': '内分泌用药', 'range': (151, 180)},
    4: {'name': '消化系统用药', 'range': (181, 200)},
    5: {'name': '神经系统用药', 'range': (201, 220)},
    6: {'name': '抗感染用药', 'range': (221, 250)},
    7: {'name': '肿瘤用药', 'range': (251, 350)},
    8: {'name': '维生素及营养药', 'range': (351, 380)},
    9: {'name': '其他用药', 'range': (381, 400)}
}

def analyze_current_data(input_file):
    """分析现有数据结构"""
    print("📊 分析现有数据结构...")
    
    drugs_by_category = defaultdict(list)
    cas_issues = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        for row_num, row in enumerate(reader, 1):
            if not row or not row[0].startswith('D') or not row[0][1:].isdigit():
                continue
                
            if len(row) < 23:
                continue
                
            drug_data = {
                'original_id': row[0],
                'cas_number': row[1],
                'english_name': row[2],
                'chinese_acronym': row[3],
                'chinese_name': row[4],
                'brand_name': row[5],
                'category': row[6],
                'therapeutic_class': row[7],
                'specifications': row[8],
                'full_row': row,
                'row_num': row_num
            }
            
            drugs_by_category[row[6]].append(drug_data)
            
            # 检查CAS号问题
            if row[2] in CORRECT_CAS_MAPPING:
                correct_cas = f"CA{CORRECT_CAS_MAPPING[row[2]]}"
                if row[1] != correct_cas:
                    cas_issues.append((row[0], row[2], row[1], correct_cas))
    
    print(f"发现 {len(cas_issues)} 个CAS号问题")
    return drugs_by_category, cas_issues

def create_new_numbering_scheme(drugs_by_category):
    """创建新的编号方案"""
    print("🔢 创建新的编号方案...")
    
    new_assignments = []
    
    # 重新分类和编号
    category_mapping = {
        '1': 1,   # 糖尿病用药
        '2': 2,   # 心血管用药 (原心律失常)
        '3': 2,   # 合并到心血管用药
        '4': 2,   # 合并到心血管用药
        '5': 2,   # 合并到心血管用药 (降压药)
        '6': 2,   # 合并到心血管用药 (调脂药)
        '7': 2,   # 合并到心血管用药
        '8': 2,   # 合并到心血管用药
        '9': 4,   # 消化系统用药
        '10': 4,  # 消化系统用药
        '11': 4,  # 消化系统用药
        '12': 8,  # 维生素及营养药
        '13': 8,  # 维生素及营养药
        '14': 3,  # 内分泌用药
        '15': 3,  # 内分泌用药
        '16': 8,  # 维生素及营养药
        '17': 6,  # 抗感染用药
        '18': 4,  # 消化系统用药 (肝病)
        '19': 7,  # 肿瘤用药
    }
    
    # 按新分类重新编号
    new_drugs_by_category = defaultdict(list)
    
    for old_category, drugs in drugs_by_category.items():
        new_category = category_mapping.get(old_category, 9)  # 默认分到其他用药
        
        for drug in drugs:
            drug['new_category'] = new_category
            new_drugs_by_category[new_category].append(drug)
    
    # 分配新编号
    for new_category in sorted(new_drugs_by_category.keys()):
        category_info = DRUG_CATEGORIES[new_category]
        start_num, end_num = category_info['range']
        
        drugs = new_drugs_by_category[new_category]
        print(f"类别 {new_category} ({category_info['name']}): {len(drugs)} 个药物, 编号范围 D{start_num:03d}-D{end_num:03d}")
        
        # 糖尿病用药按子类别分配
        if new_category == 1:
            # 按治疗类别细分
            insulin_drugs = [d for d in drugs if '胰岛素' in d['therapeutic_class']]
            oral_drugs = [d for d in drugs if any(x in d['therapeutic_class'] for x in ['双胍', '磺脲', 'DPP-4', '格列', '噻唑'])]
            glp1_drugs = [d for d in drugs if 'GLP-1' in d['therapeutic_class']]
            other_drugs = [d for d in drugs if d not in insulin_drugs + oral_drugs + glp1_drugs]
            
            current_num = start_num
            
            # 胰岛素类：D001-D030
            for i, drug in enumerate(sorted(insulin_drugs, key=lambda x: x['chinese_name'])):
                drug['new_id'] = f"D{current_num:03d}"
                new_assignments.append(drug)
                current_num += 1
            
            # 口服降糖药：D031-D070
            current_num = 31
            for i, drug in enumerate(sorted(oral_drugs, key=lambda x: x['chinese_name'])):
                drug['new_id'] = f"D{current_num:03d}"
                new_assignments.append(drug)
                current_num += 1
            
            # GLP-1类：D071-D085
            current_num = 71
            for i, drug in enumerate(sorted(glp1_drugs, key=lambda x: x['chinese_name'])):
                drug['new_id'] = f"D{current_num:03d}"
                new_assignments.append(drug)
                current_num += 1
            
            # 其他糖尿病药物：D086-D100
            current_num = 86
            for i, drug in enumerate(sorted(other_drugs, key=lambda x: x['chinese_name'])):
                drug['new_id'] = f"D{current_num:03d}"
                new_assignments.append(drug)
                current_num += 1
                
        else:
            # 其他类别按字母顺序分配
            current_num = start_num
            for drug in sorted(drugs, key=lambda x: x['chinese_name']):
                drug['new_id'] = f"D{current_num:03d}"
                new_assignments.append(drug)
                current_num += 1
    
    return new_assignments

def fix_cas_numbers(new_assignments):
    """修正CAS号"""
    print("🔧 修正CAS号...")
    
    fixed_count = 0
    for drug in new_assignments:
        english_name = drug['english_name']
        if english_name in CORRECT_CAS_MAPPING:
            correct_cas = f"CA{CORRECT_CAS_MAPPING[english_name]}"
            if drug['cas_number'] != correct_cas:
                print(f"修正 {drug['original_id']}->{drug['new_id']} {drug['chinese_name']}: {drug['cas_number']} -> {correct_cas}")
                drug['cas_number'] = correct_cas
                fixed_count += 1
    
    print(f"修正了 {fixed_count} 个CAS号")
    return fixed_count

def generate_new_database(new_assignments, output_file):
    """生成新的数据库文件"""
    print("📝 生成重组后的数据库...")
    
    # 准备输出数据
    output_rows = []
    
    # 添加文件头注释
    output_rows.extend([
        ['# 药物基础数据库 - 重组优化版'],
        ['# 重组日期: 2025-01-09'],
        ['# 版本: v3.0 - 修正CAS号错误，重新整理编号体系，优化分类结构'],
        [''],
        ['# 数据库说明：'],
        ['# 1. 修正了CAS号分配错误'],
        ['# 2. 重新整理编号让同类药物编号连续'],
        ['# 3. 优化了药物分类体系'],
        ['# 4. 保持了所有原有字段完整性'],
        [''],
        ['drug_id,ca_number,english_name,chinese_acronym,drug_name,brand_name,category,therapeutic_class,specifications,common_dosage,frequency,route,indications,contraindications,side_effects,drug_interactions,special_instructions,pregnancy_category,renal_adjustment,hepatic_adjustment,unit,method,frequency_std'],
        ['']
    ])
    
    # 按新编号排序
    sorted_drugs = sorted(new_assignments, key=lambda x: int(x['new_id'][1:]))
    
    # 添加分类注释
    current_category = None
    for drug in sorted_drugs:
        if drug['new_category'] != current_category:
            current_category = drug['new_category']
            category_name = DRUG_CATEGORIES[current_category]['name']
            output_rows.append([f'# ==================== {category_name} ({current_category}类) ===================='])
            output_rows.append([''])
        
        # 更新行数据
        new_row = drug['full_row'].copy()
        new_row[0] = drug['new_id']  # 新ID
        new_row[1] = drug['cas_number']  # 修正后的CAS号
        new_row[6] = str(drug['new_category'])  # 新分类
        
        output_rows.append(new_row)
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(output_rows)
    
    print(f"✅ 重组后的数据库已保存到: {output_file}")
    return len(sorted_drugs)

def comprehensive_reorganize(input_file, output_file):
    """全面重组数据库"""
    
    print("🚀 开始全面重组药物数据库...")
    print("=" * 60)
    
    # 第1步：分析现有数据
    drugs_by_category, cas_issues = analyze_current_data(input_file)
    print(f"✅ 分析完成：发现 {sum(len(drugs) for drugs in drugs_by_category.values())} 个药物")
    
    # 第2步：创建新编号方案
    new_assignments = create_new_numbering_scheme(drugs_by_category)
    print(f"✅ 编号方案创建完成：重新分配 {len(new_assignments)} 个药物")
    
    # 第3步：修正CAS号
    fixed_cas_count = fix_cas_numbers(new_assignments)
    
    # 第4步：生成新数据库
    final_count = generate_new_database(new_assignments, output_file)
    
    # 第5步：生成变更报告
    print("\n📋 重组完成报告:")
    print(f"   📝 重组药物总数: {final_count}")
    print(f"   🔧 修正CAS号: {fixed_cas_count} 个")
    print(f"   📂 新分类数量: {len(DRUG_CATEGORIES)} 大类")
    print(f"   🔢 编号重新分配: {len(new_assignments)} 个")
    print(f"   📄 输出文件: {output_file}")
    
    # 生成编号对照表
    print(f"\n📊 编号变更对照 (前10个):")
    for drug in sorted(new_assignments, key=lambda x: int(x['new_id'][1:]))[:10]:
        print(f"   {drug['original_id']} -> {drug['new_id']}: {drug['chinese_name']}")
    
    return {
        'total_drugs': final_count,
        'fixed_cas': fixed_cas_count,
        'new_categories': len(DRUG_CATEGORIES),
        'assignments': new_assignments
    }

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file  # 覆盖原文件
    
    result = comprehensive_reorganize(input_file, output_file)
    
    print(f"\n🎉 数据库重组完成！")
    print(f"新的药物数据库具有清晰的分类体系和连续的编号。")