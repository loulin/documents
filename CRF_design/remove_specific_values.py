#!/usr/bin/env python3
"""
移除特定的极端panic值
"""

import json
from typing import Dict, Any, List

def load_json_file(filepath: str) -> Dict[str, Any]:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(filepath: str, data: Dict[str, Any]) -> None:
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def remove_extreme_values(data: Dict[str, Any]) -> List[str]:
    """移除明显错误的极端值"""
    fixes = []
    
    # 这些值明显是错误的模板数据
    extreme_values_to_remove = [
        180000.2, 135000.15, 90000.1, 10000.9, 8000.72, 6000.54
    ]
    
    for panel_key, panel_data in data.items():
        if not isinstance(panel_data, dict) or 'tests' not in panel_data:
            continue
            
        for test in panel_data['tests']:
            test_id = test.get('test_id', 'Unknown')
            test_name = test.get('test_name', 'Unknown')
            
            if 'biological_limits' not in test:
                continue
            
            biological_limits = test['biological_limits']
            
            for limit_type in list(biological_limits.keys()):
                if limit_type in biological_limits:
                    limit_data = biological_limits[limit_type]
                    
                    # 移除极端值
                    units_to_remove = []
                    for unit, value in limit_data.items():
                        if isinstance(value, (int, float)) and value in extreme_values_to_remove:
                            units_to_remove.append(unit)
                            fixes.append(f"移除 {test_id} ({test_name}): {limit_type}[{unit}] = {value}")
                    
                    for unit in units_to_remove:
                        del limit_data[unit]
                    
                    # 如果该限制类型变为空，删除整个字段
                    if not limit_data:
                        del biological_limits[limit_type]
                        fixes.append(f"删除空字段 {test_id} ({test_name}): {limit_type}")
    
    return fixes

def main():
    json_file = '/Users/williamsun/Documents/gplus/docs/CRF_design/Complete_Laboratory_Tests_with_LOINC_Units_Limits.json'
    
    try:
        print("正在加载JSON文件...")
        data = load_json_file(json_file)
        
        print("正在移除极端值...")
        fixes = remove_extreme_values(data)
        
        if fixes:
            print("正在保存修复后的文件...")
            save_json_file(json_file, data)
            
            print(f"\n修复完成! 共处理了 {len(fixes)} 个问题:")
            for fix in fixes[:20]:  # 只显示前20个
                print(f"  {fix}")
            if len(fixes) > 20:
                print(f"  ... 还有 {len(fixes) - 20} 个修复")
        else:
            print("未发现需要修复的值。")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()