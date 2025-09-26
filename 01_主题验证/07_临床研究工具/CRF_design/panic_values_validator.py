#!/usr/bin/env python3
"""
Panic Values Validator for Laboratory Tests JSON
校验和修复panic_low和panic_high值与reference_range的一致性
"""

import json
import sys
from typing import Dict, Any, List, Optional

def load_json_file(filepath: str) -> Dict[str, Any]:
    """加载JSON文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(filepath: str, data: Dict[str, Any]) -> None:
    """保存JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_numeric_ranges(reference_ranges: Dict[str, Any]) -> Dict[str, tuple]:
    """从reference_ranges中提取数值范围"""
    ranges = {}
    
    if not reference_ranges:
        return ranges
    
    # 遍历reference_ranges中的每个条件
    for condition, condition_data in reference_ranges.items():
        if isinstance(condition_data, dict):
            for unit, unit_data in condition_data.items():
                if isinstance(unit_data, dict):
                    min_val = unit_data.get('min')
                    max_val = unit_data.get('max')
                    target_val = unit_data.get('target')
                    
                    if unit not in ranges:
                        ranges[unit] = {'min_vals': [], 'max_vals': [], 'targets': []}
                    
                    if min_val is not None:
                        ranges[unit]['min_vals'].append(float(min_val))
                    if max_val is not None:
                        ranges[unit]['max_vals'].append(float(max_val))
                    if target_val is not None:
                        ranges[unit]['targets'].append(float(target_val))
    
    # 计算整体范围
    final_ranges = {}
    for unit, vals in ranges.items():
        if vals['min_vals'] or vals['max_vals'] or vals['targets']:
            all_vals = vals['min_vals'] + vals['max_vals'] + vals['targets']
            final_ranges[unit] = (min(all_vals) if all_vals else None, 
                                max(all_vals) if all_vals else None)
    
    return final_ranges

def is_panic_value_reasonable(panic_val: float, ref_min: Optional[float], ref_max: Optional[float], 
                            is_low: bool = True) -> bool:
    """检查panic值是否合理"""
    if ref_min is None and ref_max is None:
        return False  # 没有参考范围就不应该有panic值
    
    if is_low:
        # panic_low应该比参考范围的最小值更低，但不能太离谱（不超过10倍差异）
        if ref_min is not None:
            if panic_val >= ref_min:  # panic_low不应该比正常范围还高
                return False
            if ref_min > 0 and panic_val < ref_min * 0.1:  # 相差超过10倍可能不合理
                return False
        return True
    else:
        # panic_high应该比参考范围的最大值更高，但不能太离谱
        if ref_max is not None:
            if panic_val <= ref_max:  # panic_high不应该比正常范围还低
                return False
            if panic_val > ref_max * 10:  # 相差超过10倍可能不合理
                return False
        return True

def validate_and_fix_panic_values(data: Dict[str, Any]) -> List[str]:
    """验证并修复panic值"""
    issues_found = []
    
    for panel_key, panel_data in data.items():
        if not isinstance(panel_data, dict) or 'tests' not in panel_data:
            continue
            
        for test in panel_data['tests']:
            test_id = test.get('test_id', 'Unknown')
            test_name = test.get('test_name', 'Unknown')
            
            if 'biological_limits' not in test:
                continue
                
            biological_limits = test['biological_limits']
            reference_ranges = test.get('reference_ranges', {})
            
            # 如果没有reference_ranges，清除所有panic值
            if not reference_ranges:
                if 'panic_low' in biological_limits or 'panic_high' in biological_limits:
                    issues_found.append(f"{test_id} ({test_name}): 移除panic值 - 无参考范围")
                    biological_limits.pop('panic_low', None)
                    biological_limits.pop('panic_high', None)
                continue
            
            # 提取参考范围
            ref_ranges = extract_numeric_ranges(reference_ranges)
            
            # 检查panic_low
            if 'panic_low' in biological_limits:
                panic_low = biological_limits['panic_low']
                to_remove_units = []
                
                for unit, panic_val in panic_low.items():
                    if unit in ref_ranges:
                        ref_min, ref_max = ref_ranges[unit]
                        if not is_panic_value_reasonable(panic_val, ref_min, ref_max, is_low=True):
                            to_remove_units.append(unit)
                            issues_found.append(f"{test_id} ({test_name}): 移除不合理的panic_low[{unit}] = {panic_val}")
                    else:
                        # 没有对应单位的参考范围
                        to_remove_units.append(unit)
                        issues_found.append(f"{test_id} ({test_name}): 移除panic_low[{unit}] - 无对应参考范围")
                
                # 移除不合理的单位
                for unit in to_remove_units:
                    panic_low.pop(unit, None)
                
                # 如果panic_low为空，移除整个字段
                if not panic_low:
                    biological_limits.pop('panic_low', None)
            
            # 检查panic_high
            if 'panic_high' in biological_limits:
                panic_high = biological_limits['panic_high']
                to_remove_units = []
                
                for unit, panic_val in panic_high.items():
                    if unit in ref_ranges:
                        ref_min, ref_max = ref_ranges[unit]
                        if not is_panic_value_reasonable(panic_val, ref_min, ref_max, is_low=False):
                            to_remove_units.append(unit)
                            issues_found.append(f"{test_id} ({test_name}): 移除不合理的panic_high[{unit}] = {panic_val}")
                    else:
                        # 没有对应单位的参考范围
                        to_remove_units.append(unit)
                        issues_found.append(f"{test_id} ({test_name}): 移除panic_high[{unit}] - 无对应参考范围")
                
                # 移除不合理的单位
                for unit in to_remove_units:
                    panic_high.pop(unit, None)
                
                # 如果panic_high为空，移除整个字段
                if not panic_high:
                    biological_limits.pop('panic_high', None)
    
    return issues_found

def main():
    if len(sys.argv) != 2:
        print("Usage: python panic_values_validator.py <json_file_path>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    try:
        # 加载数据
        print("正在加载JSON文件...")
        data = load_json_file(json_file)
        
        # 验证和修复
        print("正在验证和修复panic值...")
        issues = validate_and_fix_panic_values(data)
        
        # 保存修复后的数据
        print("正在保存修复后的文件...")
        save_json_file(json_file, data)
        
        # 输出结果
        print(f"\n修复完成! 共发现并处理了 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  - {issue}")
        
        if not issues:
            print("未发现需要修复的panic值问题。")
            
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()