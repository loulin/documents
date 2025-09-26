#!/usr/bin/env python3
"""
修复胰岛素ATC代码 - 区分纯制剂和混合制剂
"""

import csv

def fix_insulin_atc_codes(input_file, output_file):
    """修复胰岛素ATC代码，正确区分混合制剂"""
    
    print("🔧 修复胰岛素ATC代码...")
    print("📋 区分纯制剂(A10AB)和混合制剂(A10AD)")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    # 胰岛素混合制剂ATC代码映射
    insulin_atc_mapping = {
        # 纯制剂 A10AB系列
        '人胰岛素': 'A10AB01',
        '赖脯胰岛素': 'A10AB04',  # 纯制剂
        '门冬胰岛素': 'A10AB05',  # 纯制剂
        '谷赖胰岛素': 'A10AB06',
        
        # 混合制剂 A10AD系列
        '人胰岛素30/70': 'A10AD01',     # 人胰岛素混合制剂
        '赖脯胰岛素25': 'A10AD04',      # 赖脯胰岛素25/75混合
        '赖脯胰岛素50': 'A10AD05',      # 赖脯胰岛素50/50混合
        '门冬胰岛素30': 'A10AD05',      # 门冬胰岛素30/70混合
        '门冬胰岛素50': 'A10AD06',      # 门冬胰岛素50/50混合
        '门冬胰岛素70': 'A10AD06',      # 门冬胰岛素70/30混合
        
        # 长效胰岛素 A10AE系列 (保持不变)
        '甘精胰岛素': 'A10AE04',
        '地特胰岛素': 'A10AE05', 
        '德谷胰岛素': 'A10AE06',
    }
    
    updated_rows = []
    fixed_count = 0
    
    for row in all_rows:
        if not row or not row[0] or row[0].startswith('#') or 'drug_id' in row[0]:
            updated_rows.append(row)
            continue
        
        if row[0].startswith('D') and len(row) >= 39:
            new_row = row.copy()
            drug_name = new_row[14] if len(new_row) > 14 else ''
            current_atc = new_row[4] if len(new_row) > 4 else ''
            
            # 检查是否是胰岛素
            if '胰岛素' in drug_name:
                correct_atc = None
                
                # 精确匹配药物名称
                for name_pattern, atc_code in insulin_atc_mapping.items():
                    if drug_name == name_pattern:  # 完全匹配
                        correct_atc = atc_code
                        break
                
                # 如果找到正确的ATC且与当前不同，则修复
                if correct_atc and correct_atc != current_atc:
                    new_row[4] = correct_atc
                    fixed_count += 1
                    print(f"  ✓ {new_row[0]}: {current_atc} → {correct_atc} ({drug_name})")
            
            updated_rows.append(new_row)
        else:
            updated_rows.append(row)
    
    # 写入修复后的文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated_rows)
    
    print(f"\n📊 胰岛素ATC代码修复完成:")
    print(f"   🔧 修复数量: {fixed_count}")
    print(f"   ✅ A10AB: 速效纯制剂")
    print(f"   ✅ A10AD: 混合制剂")  
    print(f"   ✅ A10AE: 长效制剂")

def show_identification_strategy():
    """展示剂型识别策略"""
    
    print(f"\n💡 推荐的剂型识别策略:")
    print(f"=" * 50)
    
    print(f"🎯 主标识符 (用于数据交换):")
    print(f"   📋 ATC代码 - 精确到剂型级别")
    print(f"   📝 示例:")
    print(f"      • A10AB04: 赖脯胰岛素(纯)")  
    print(f"      • A10AD04: 赖脯胰岛素25/75")
    print(f"      • A10AD05: 赖脯胰岛素50/50")
    
    print(f"\n🔍 辅助标识符 (用于详细区分):")
    print(f"   📊 specifications字段 - 规格浓度")
    print(f"   📋 english_name字段 - 包含剂型信息") 
    print(f"   🏷️ brand_name字段 - 商品名区分")
    print(f"   💊 drug_name字段 - 中文名称区分")
    
    print(f"\n🎯 完整识别方案:")
    print(f"   1. ATC代码 (剂型分类)")
    print(f"   2. WHO INN + 规格 (化学成分+浓度)")
    print(f"   3. NDC代码 (包装规格)")
    print(f"   4. 品牌名 (商业区分)")
    
    print(f"\n📝 实际使用示例:")
    print(f"   主键: ATC代码 (A10AD04)")
    print(f"   描述: 赖脯胰岛素25/75, 100IU/ml(3ml)")
    print(f"   品牌: 优泌乐25")
    print(f"   这样可以精确识别到具体剂型和规格")

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file
    
    print("🚀 修复胰岛素ATC代码剂型问题")
    print("=" * 50)
    
    # 修复胰岛素ATC代码
    fix_insulin_atc_codes(input_file, output_file) 
    
    # 展示识别策略
    show_identification_strategy()
    
    print(f"\n🎯 总结:")
    print(f"   ✅ 混合制剂使用A10AD系列")
    print(f"   ✅ 纯制剂使用A10AB系列") 
    print(f"   ✅ 长效制剂使用A10AE系列")
    print(f"   🔍 结合多个字段精确识别剂型")
    print(f"   🌍 符合WHO ATC分类标准")