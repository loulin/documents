#!/usr/bin/env python3
"""
修复极端不合理的panic值
"""

import json
import re
from typing import Dict, Any, List, Optional

def load_json_file(filepath: str) -> Dict[str, Any]:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(filepath: str, data: Dict[str, Any]) -> None:
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_value_extreme(value: float, unit: str) -> bool:
    """判断数值是否极端不合理"""
    
    # 这些模式通常表示复制粘贴错误导致的极端值
    extreme_patterns = [
        (lambda v: v > 100000, ['μmol/L', 'pmol/L', 'nmol/L']),  # 微摩尔单位超过10万
        (lambda v: v > 10000000, ['ng/L']),  # 纳克/升超过1千万  
        (lambda v: v > 1000000, ['mg/24h']),  # 24小时尿蛋白超过100万mg
        (lambda v: v > 1000000000, ['cells/μL']),  # 细胞计数超过10亿
        (lambda v: v > 500000, ['pg/mL', 'ng/mL']),  # pg/mL或ng/mL超过50万
        (lambda v: v > 100000 and 'fmol' in unit, [unit]),  # fmol单位超过10万
    ]
    
    for condition, units in extreme_patterns:
        if unit in units and condition(value):
            return True
    
    return False

def has_repeated_decimals(value: float) -> bool:
    """检查是否有重复的小数模式，如10000.9, 90000.1等"""
    str_val = str(value)
    # 检查类似10000.9, 90000.1, 8000.72这样的模式
    patterns = [
        r'10000\.9$',
        r'90000\.1$', 
        r'8000\.72$',
        r'135000\.15$',
        r'180000\.2$',
        r'6000\.54$'
    ]
    
    for pattern in patterns:
        if re.search(pattern, str_val):
            return True
    return False

def fix_extreme_values(data: Dict[str, Any]) -> List[str]:
    """修复极端值"""
    fixes = []
    
    for panel_key, panel_data in data.items():
        if not isinstance(panel_data, dict) or 'tests' not in panel_data:
            continue
            
        for test in panel_data['tests']:
            test_id = test.get('test_id', 'Unknown')
            test_name = test.get('test_name', 'Unknown')
            
            if 'biological_limits' not in test:
                continue
            
            biological_limits = test['biological_limits']
            
            # 检查所有类型的生物学极限值
            for limit_type in ['panic_low', 'panic_high', 'physiological_minimum', 'physiological_maximum', 
                             'critical_low', 'critical_high', 'absolute_minimum', 'absolute_maximum']:
                
                if limit_type in biological_limits:
                    limit_data = biological_limits[limit_type]
                    units_to_remove = []
                    
                    for unit, value in limit_data.items():
                        if isinstance(value, (int, float)):
                            # 检查极端值
                            if is_value_extreme(value, unit):
                                units_to_remove.append(unit)
                                fixes.append(f"❌ {test_id} ({test_name}): 移除极端{limit_type}[{unit}] = {value}")
                            
                            # 检查重复小数模式
                            elif has_repeated_decimals(value):
                                units_to_remove.append(unit)
                                fixes.append(f"🔧 {test_id} ({test_name}): 移除可疑{limit_type}[{unit}] = {value}")
                    
                    # 移除极端值
                    for unit in units_to_remove:
                        limit_data.pop(unit, None)
                    
                    # 如果该类型的所有单位都被移除，删除整个字段
                    if not limit_data:
                        biological_limits.pop(limit_type, None)
                        fixes.append(f"🗑️  {test_id} ({test_name}): 删除空的{limit_type}")
    
    return fixes

def main():
    json_file = '/Users/williamsun/Documents/gplus/docs/CRF_design/Complete_Laboratory_Tests_with_LOINC_Units_Limits.json'
    
    try:
        print("正在加载JSON文件...")
        data = load_json_file(json_file)
        
        print("正在修复极端panic值...")
        fixes = fix_extreme_values(data)
        
        if fixes:
            print("正在保存修复后的文件...")
            save_json_file(json_file, data)
            
            print(f"\n修复完成! 共处理了 {len(fixes)} 个问题:")
            for fix in fixes:
                print(f"  {fix}")
        else:
            print("未发现需要修复的极端值。")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()