#!/usr/bin/env python3
"""
调试脚本：查找所有panic值，显示与参考范围的关系
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple

def load_json_file(filepath: str) -> Dict[str, Any]:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_all_panic_values(data: Dict[str, Any]) -> List[str]:
    """查找所有panic值并分析"""
    results = []
    panic_count = 0
    
    for panel_key, panel_data in data.items():
        if not isinstance(panel_data, dict) or 'tests' not in panel_data:
            continue
            
        for test in panel_data['tests']:
            test_id = test.get('test_id', 'Unknown')
            test_name = test.get('test_name', 'Unknown')
            
            if 'biological_limits' not in test:
                continue
            
            biological_limits = test['biological_limits']
            
            # 检查是否有panic值
            has_panic_low = 'panic_low' in biological_limits
            has_panic_high = 'panic_high' in biological_limits
            
            if has_panic_low or has_panic_high:
                panic_count += 1
                
                # 获取参考范围信息
                ref_info = ""
                if 'reference_range' in test:
                    ref_info = f"ref_range: {test['reference_range']}"
                elif 'reference_ranges' in test:
                    ref_info = f"ref_ranges: {list(test['reference_ranges'].keys())}"
                
                results.append(f"\n📊 {test_id} ({test_name})")
                results.append(f"   {ref_info}")
                
                if has_panic_low:
                    panic_low = biological_limits['panic_low']
                    results.append(f"   panic_low: {panic_low}")
                
                if has_panic_high:
                    panic_high = biological_limits['panic_high']
                    results.append(f"   panic_high: {panic_high}")
                
                # 检查是否有明显不合理的数值
                if has_panic_high:
                    for unit, val in biological_limits['panic_high'].items():
                        if val > 10000:  # 明显过大的值
                            results.append(f"   ⚠️ 可能过大: panic_high[{unit}] = {val}")
                        if val > 1000 and ('mg' in unit or 'μmol' in unit or 'mmol' in unit):
                            results.append(f"   ❓ 检查: panic_high[{unit}] = {val}")
                
                if has_panic_low:
                    for unit, val in biological_limits['panic_low'].items():
                        if val < 0:  # 负值
                            results.append(f"   ❌ 负值: panic_low[{unit}] = {val}")
                        if val == 0 and 'mmol/mol' in unit:  # HbA1c的mmol/mol不能为0
                            results.append(f"   ❌ 零值: panic_low[{unit}] = {val}")
    
    results.insert(0, f"总共找到 {panic_count} 个包含panic值的测试项目:")
    return results

def main():
    json_file = '/Users/williamsun/Documents/gplus/docs/CRF_design/Complete_Laboratory_Tests_with_LOINC_Units_Limits.json'
    
    try:
        print("正在分析JSON文件中的panic值...")
        data = load_json_file(json_file)
        results = find_all_panic_values(data)
        
        for result in results:
            print(result)
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()