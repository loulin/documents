#!/usr/bin/env python3
"""
填充缺失的字段 - unit, method, frequency_std
"""

import csv
import re

def fill_missing_clinical_fields(input_file, output_file):
    """填充缺失的临床字段"""
    
    print("🔧 填充缺失的临床字段...")
    print("📋 目标字段:")
    print("   • unit (第32列) - 剂量单位")
    print("   • method (第33列) - 给药方法") 
    print("   • frequency_std (第34列) - 标准化频次代码")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    updated_rows = []
    filled_count = 0
    
    # 标准化频次代码映射
    frequency_mapping = {
        '1每日1次': 'QD',
        '2每日2次': 'BID', 
        '3每日3次': 'TID',
        '4每日4次': 'QID',
        '每日1次': 'QD',
        '每日2次': 'BID',
        '每日3次': 'TID',
        '每日4次': 'QID',
        '每天1次': 'QD',
        '每天2次': 'BID',
        '每天3次': 'TID',
        '隔日1次': 'QOD',
        '按需使用': 'PRN',
        '睡前': 'HS',
        '餐前': 'AC',
        '餐后': 'PC'
    }
    
    for row in all_rows:
        if not row or not row[0] or row[0].startswith('#') or 'drug_id' in row[0]:
            updated_rows.append(row)
            continue
        
        if row[0].startswith('D') and len(row) >= 39:
            drug_id = row[0]
            new_row = row.copy()
            
            # 获取现有数据用于推断
            specifications = row[20] if len(row) > 20 else ''  # 规格
            common_dosage = row[21] if len(row) > 21 else ''   # 常用剂量
            frequency = row[22] if len(row) > 22 else ''       # 频次
            route = row[23] if len(row) > 23 else ''           # 给药途径
            drug_name = row[14] if len(row) > 14 else ''       # 药物名称
            category = row[18] if len(row) > 18 else ''        # 分类
            
            # 填充 unit (第32列) - 剂量单位
            if not new_row[32]:
                unit = ''
                if 'IU' in specifications:
                    unit = 'IU'
                elif 'mg' in specifications:
                    unit = 'mg'
                elif 'g' in specifications:
                    unit = 'g'
                elif 'ml' in specifications:
                    unit = 'ml'
                elif 'μg' in specifications:
                    unit = 'μg'
                elif '单位' in common_dosage:
                    unit = 'IU'
                elif 'mg' in common_dosage:
                    unit = 'mg'
                elif '胰岛素' in drug_name or 'insulin' in drug_name.lower():
                    unit = 'IU'
                elif category == '1':  # 糖尿病用药
                    if '胰岛素' in drug_name:
                        unit = 'IU'
                    else:
                        unit = 'mg'
                elif category == '2':  # 心血管
                    unit = 'mg'
                elif category == '3':  # 抗感染
                    unit = 'mg'
                else:
                    unit = 'mg'  # 默认
                
                new_row[32] = unit
            
            # 填充 method (第33列) - 给药方法
            if not new_row[33]:
                method = ''
                if '皮下注射' in route:
                    method = '皮下注射'
                elif '静脉注射' in route:
                    method = '静脉注射'
                elif '肌肉注射' in route:
                    method = '肌肉注射'
                elif '口服' in route:
                    method = '口服'
                elif '外用' in route:
                    method = '外用'
                elif route:
                    # 提取路径信息
                    if '1' in route:
                        method = '口服'
                    elif '2' in route:
                        method = '外用'
                    elif '3' in route:
                        method = '肌肉注射'
                    elif '4' in route:
                        method = '静脉注射'
                    elif '5' in route:
                        method = '皮下注射'
                    else:
                        method = '口服'  # 默认
                else:
                    # 根据药物类型推断
                    if '胰岛素' in drug_name or 'insulin' in drug_name.lower():
                        method = '皮下注射'
                    elif category == '1':  # 糖尿病用药
                        if '胰岛素' in drug_name:
                            method = '皮下注射'
                        else:
                            method = '口服'
                    else:
                        method = '口服'  # 默认
                
                new_row[33] = method
            
            # 填充 frequency_std (第34列) - 标准化频次代码
            if not new_row[34]:
                freq_std = ''
                if frequency:
                    # 查找匹配的标准频次代码
                    for pattern, code in frequency_mapping.items():
                        if pattern in frequency:
                            freq_std = code
                            break
                    
                    # 如果没有直接匹配，尝试解析
                    if not freq_std:
                        if '1次' in frequency and '每日' in frequency:
                            freq_std = 'QD'
                        elif '2次' in frequency and '每日' in frequency:
                            freq_std = 'BID'
                        elif '3次' in frequency and '每日' in frequency:
                            freq_std = 'TID'
                        elif '4次' in frequency and '每日' in frequency:
                            freq_std = 'QID'
                        else:
                            # 复合频次处理
                            if ';' in frequency:
                                freq_parts = frequency.split(';')
                                freq_codes = []
                                for part in freq_parts:
                                    for pattern, code in frequency_mapping.items():
                                        if pattern in part:
                                            freq_codes.append(code)
                                            break
                                freq_std = '/'.join(freq_codes) if freq_codes else 'VAR'
                            else:
                                freq_std = 'VAR'  # 可变频次
                else:
                    # 默认频次
                    if '胰岛素' in drug_name:
                        freq_std = 'BID'  # 胰岛素通常每日2次
                    else:
                        freq_std = 'BID'  # 默认每日2次
                
                new_row[34] = freq_std
            
            filled_count += 1
            
            # 显示前5个填充结果
            if filled_count <= 5:
                print(f"  ✓ {drug_id}: Unit={new_row[32]}, Method={new_row[33]}, Freq={new_row[34]}")
            
            updated_rows.append(new_row)
        else:
            updated_rows.append(row)
    
    # 写入填充后的文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated_rows)
    
    print(f"\n📊 字段填充完成:")
    print(f"   ✅ 填充药物数量: {filled_count}")
    print(f"   📋 unit 字段已填充")
    print(f"   📋 method 字段已填充")
    print(f"   📋 frequency_std 字段已填充")

def verify_field_completeness(file_path):
    """验证字段完整性"""
    
    print(f"\n🔍 验证字段完整性...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        total_drugs = 0
        empty_units = 0
        empty_methods = 0
        empty_freq_std = 0
        
        unit_stats = {}
        method_stats = {}
        freq_stats = {}
        
        for row in reader:
            if not row or not row[0] or row[0].startswith('#') or 'drug_id' in row[0]:
                continue
                
            if row[0].startswith('D') and len(row) >= 39:
                total_drugs += 1
                
                unit = row[32] if len(row) > 32 else ''
                method = row[33] if len(row) > 33 else ''
                freq_std = row[34] if len(row) > 34 else ''
                
                # 统计空白
                if not unit.strip():
                    empty_units += 1
                else:
                    unit_stats[unit] = unit_stats.get(unit, 0) + 1
                    
                if not method.strip():
                    empty_methods += 1
                else:
                    method_stats[method] = method_stats.get(method, 0) + 1
                    
                if not freq_std.strip():
                    empty_freq_std += 1
                else:
                    freq_stats[freq_std] = freq_stats.get(freq_std, 0) + 1
                
                # 显示前3个药物的字段
                if total_drugs <= 3:
                    drug_name = row[14] if len(row) > 14 else ''
                    print(f"   💊 {row[0]} ({drug_name}): {unit} | {method} | {freq_std}")
    
    print(f"\n📊 字段完整性统计:")
    print(f"   💊 药物总数: {total_drugs}")
    print(f"   📋 unit 空白: {empty_units} | 完整度: {((total_drugs - empty_units) / total_drugs * 100):.1f}%")
    print(f"   📋 method 空白: {empty_methods} | 完整度: {((total_drugs - empty_methods) / total_drugs * 100):.1f}%")
    print(f"   📋 frequency_std 空白: {empty_freq_std} | 完整度: {((total_drugs - empty_freq_std) / total_drugs * 100):.1f}%")
    
    print(f"\n📈 字段分布统计:")
    print(f"   💊 Unit 分布: {dict(list(unit_stats.items())[:5])}")
    print(f"   🔬 Method 分布: {dict(list(method_stats.items())[:5])}")
    print(f"   ⏰ Frequency 分布: {dict(list(freq_stats.items())[:5])}")
    
    total_empty = empty_units + empty_methods + empty_freq_std
    return total_empty == 0

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file
    
    print("🚀 填充缺失的临床字段")
    print("=" * 50)
    
    # 填充缺失字段
    fill_missing_clinical_fields(input_file, output_file)
    
    # 验证完整性
    is_complete = verify_field_completeness(output_file)
    
    if is_complete:
        print(f"\n🎉 完美！所有临床字段已完整填充")
        print(f"✅ unit, method, frequency_std 字段 100% 完整")
    else:
        print(f"\n⚠️  还有少量字段需要检查")
    
    print(f"\n💡 字段说明:")
    print(f"   📋 unit: 剂量单位 (IU, mg, g, ml, μg)")
    print(f"   🔬 method: 给药方法 (口服, 皮下注射, 静脉注射等)")
    print(f"   ⏰ frequency_std: 标准频次代码 (QD, BID, TID, QID等)")
    print(f"   🌍 符合国际医学标准缩写")