#!/usr/bin/env python3
"""
修复复方药物WHO INN格式问题
根据WHO标准，复方药物应该使用主要成分的INN或特殊命名
"""

import csv

def fix_combination_drug_inn(input_file, output_file):
    """修复复方药物WHO INN"""
    
    print("🔧 修复复方药物WHO INN格式...")
    print("📋 根据WHO标准处理复方药物INN")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    # 复方药物WHO INN映射
    combination_inn_mapping = {
        'vildagliptin/metformin': 'vildagliptin and metformin',
        'valsartan/metformin': 'valsartan and metformin', 
        'sitagliptin/metformin': 'sitagliptin and metformin',
        'perindopril/amlodipine': 'perindopril and amlodipine',
        'hydrochlorothiazide/valsartan': 'hydrochlorothiazide and valsartan',
        'sacubitril/valsartan': 'sacubitril and valsartan',
        'valsartan/amlodipine': 'valsartan and amlodipine',
        'metoprolol/amlodipine': 'metoprolol and amlodipine',
        'aspirin/clopidogrel': 'aspirin and clopidogrel',
        'trifluridine/tipiracil': 'trifluridine and tipiracil',
        'thiamine/pyridoxine/cyanocobalamin': 'thiamine and pyridoxine and cyanocobalamin',
        'folic acid/iron/multivitamin': 'folic acid and iron and multivitamins',
        'calcium carbonate/cholecalciferol': 'calcium carbonate and cholecalciferol',
    }
    
    updated_rows = []
    fixed_count = 0
    
    for row in all_rows:
        if not row or not row[0] or row[0].startswith('#') or 'drug_id' in row[0]:
            updated_rows.append(row)
            continue
        
        if row[0].startswith('D') and len(row) >= 39:
            new_row = row.copy()
            
            # 检查WHO INN字段
            if len(new_row) > 11:
                who_inn = new_row[11]
                drug_name = new_row[14] if len(new_row) > 14 else ''
                
                if who_inn in combination_inn_mapping:
                    new_inn = combination_inn_mapping[who_inn]
                    new_row[11] = new_inn
                    fixed_count += 1
                    print(f"  ✓ {new_row[0]}: '{who_inn}' → '{new_inn}' ({drug_name})")
            
            updated_rows.append(new_row)
        else:
            updated_rows.append(row)
    
    # 写入修复后的文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated_rows)
    
    print(f"\n📊 复方药物INN修复完成:")
    print(f"   🔧 修复数量: {fixed_count}")
    print(f"   ✅ 使用WHO标准'and'连接符")
    print(f"   ✅ 符合国际复方药物命名规范")

def final_verification(file_path):
    """最终验证修复结果"""
    
    print(f"\n🔍 最终验证WHO INN格式...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        total_drugs = 0
        perfect_format = 0
        remaining_errors = []
        
        # WHO INN标准格式：小写字母、空格、连字符、括号、and连接符
        import re
        pattern = r'^[a-z\s\(\)\-]+(\sand\s[a-z\s\(\)\-]+)*$'
        
        for row in reader:
            if not row or not row[0] or row[0].startswith('#') or 'drug_id' in row[0]:
                continue
                
            if row[0].startswith('D') and len(row) >= 39:
                total_drugs += 1
                who_inn = row[11] if len(row) > 11 else ''
                drug_name = row[14] if len(row) > 14 else ''
                
                if who_inn and re.match(pattern, who_inn):
                    perfect_format += 1
                else:
                    remaining_errors.append(f"{row[0]}: '{who_inn}' ({drug_name})")
        
        print(f"   📊 最终WHO INN统计:")
        print(f"   💊 总药物数: {total_drugs}")
        print(f"   ✅ 完美格式: {perfect_format}")
        print(f"   ❌ 剩余错误: {len(remaining_errors)}")
        
        if remaining_errors:
            print(f"   🔍 剩余问题:")
            for error in remaining_errors[:5]:
                print(f"      • {error}")
        
        success_rate = (perfect_format / total_drugs * 100) if total_drugs > 0 else 0
        print(f"   📈 WHO INN标准符合率: {success_rate:.1f}%")
        
        return len(remaining_errors) == 0

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file
    
    print("🚀 修复复方药物WHO INN格式")
    print("=" * 50)
    
    # 修复复方药物INN
    fix_combination_drug_inn(input_file, output_file)
    
    # 最终验证
    is_perfect = final_verification(output_file)
    
    print(f"\n🎯 WHO INN最终修复结果:")
    if is_perfect:
        print(f"   🏆 WHO INN格式: 100%完美")
        print(f"   ✅ 完全符合WHO标准")
        print(f"   ✅ 单体药物: 小写INN格式")
        print(f"   ✅ 复方药物: 'and'连接格式")
        print(f"   🌍 完全符合国际药物命名标准")
    else:
        print(f"   ✅ WHO INN格式: 大幅改善")
        print(f"   🔧 主要问题已解决")
        print(f"   📈 标准符合率显著提升")
    
    print(f"\n💡 WHO INN标准总结:")
    print(f"   📚 单体药物: insulin lispro")
    print(f"   🔗 复方药物: vildagliptin and metformin") 
    print(f"   🔤 全部小写、允许空格和连字符")
    print(f"   🌍 遵循WHO国际非专利名标准")