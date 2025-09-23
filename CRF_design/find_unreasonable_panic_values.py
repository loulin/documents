#!/usr/bin/env python3
"""
查找明显不合理的panic_low和panic_high值
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple

def load_json_file(filepath: str) -> Dict[str, Any]:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_reference_range_values(reference_ranges: Dict[str, Any]) -> Dict[str, Tuple[Optional[float], Optional[float]]]:
    """从reference_ranges提取最小和最大值"""
    ranges = {}
    
    if not reference_ranges:
        return ranges
    
    for condition, condition_data in reference_ranges.items():
        if isinstance(condition_data, dict):
            for unit, unit_data in condition_data.items():
                if isinstance(unit_data, dict):
                    min_val = unit_data.get('min') or unit_data.get('low')
                    max_val = unit_data.get('max') or unit_data.get('high')
                    target = unit_data.get('target')
                    
                    if unit not in ranges:
                        ranges[unit] = [[], []]  # [mins, maxs]
                    
                    if min_val is not None:
                        ranges[unit][0].append(float(min_val))
                    if max_val is not None:
                        ranges[unit][1].append(float(max_val))
                    if target is not None:
                        ranges[unit][1].append(float(target))  # target当作上限
    
    # 计算每个单位的最小和最大值
    result = {}
    for unit, (mins, maxs) in ranges.items():
        min_val = min(mins) if mins else None
        max_val = max(maxs) if maxs else None
        result[unit] = (min_val, max_val)
    
    return result

def parse_reference_range_string(ref_range: str) -> Dict[str, Tuple[Optional[float], Optional[float]]]:
    """解析reference_range字符串"""
    ranges = {}
    
    # 匹配模式如 "2.9-8.2 mmol/L" 或 "男 208-428 μmol/L; 女 155-357 μmol/L"
    patterns = [
        r'(\d+\.?\d*)-(\d+\.?\d*)\s*([^\s;]+)',  # 基本范围模式
        r'[男女]\s*(\d+\.?\d*)-(\d+\.?\d*)\s*([^\s;]+)',  # 性别特定模式
        r'<(\d+\.?\d*)\s*([^\s;]+)',  # 小于模式
        r'>(\d+\.?\d*)\s*([^\s;]+)'   # 大于模式
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, ref_range)
        for match in matches:
            if len(match) == 3:  # 范围模式
                min_val, max_val, unit = match
                if unit not in ranges:
                    ranges[unit] = ([], [])
                ranges[unit][0].append(float(min_val))
                ranges[unit][1].append(float(max_val))
            elif len(match) == 2:  # 单边模式
                val, unit = match
                if unit not in ranges:
                    ranges[unit] = ([], [])
                ranges[unit][1].append(float(val))  # 当作上限
    
    # 计算每个单位的最小和最大值
    result = {}
    for unit, (mins, maxs) in ranges.items():
        min_val = min(mins) if mins else None
        max_val = max(maxs) if maxs else None
        result[unit] = (min_val, max_val)
    
    return result

def find_unreasonable_panic_values(data: Dict[str, Any]) -> List[str]:
    """查找不合理的panic值"""
    issues = []
    
    for panel_key, panel_data in data.items():
        if not isinstance(panel_data, dict) or 'tests' not in panel_data:
            continue
            
        for test in panel_data['tests']:
            test_id = test.get('test_id', 'Unknown')
            test_name = test.get('test_name', 'Unknown')
            
            if 'biological_limits' not in test:
                continue
            
            biological_limits = test['biological_limits']
            
            # 获取参考范围
            ref_ranges = {}
            
            # 首先尝试从reference_ranges获取
            if 'reference_ranges' in test:
                ref_ranges = extract_reference_range_values(test['reference_ranges'])
            
            # 如果没有，尝试从reference_range字符串获取
            if not ref_ranges and 'reference_range' in test:
                ref_ranges = parse_reference_range_string(test['reference_range'])
            
            # 如果有enhanced_reference_ranges，也检查它
            if 'enhanced_reference_ranges' in test:
                enhanced_ranges = extract_reference_range_values(test['enhanced_reference_ranges'])
                # 合并范围
                for unit, (min_val, max_val) in enhanced_ranges.items():
                    if unit not in ref_ranges:
                        ref_ranges[unit] = (min_val, max_val)
            
            # 检查panic_low
            if 'panic_low' in biological_limits:
                panic_low = biological_limits['panic_low']
                for unit, panic_val in panic_low.items():
                    if unit in ref_ranges:
                        ref_min, ref_max = ref_ranges[unit]
                        # panic_low应该比参考范围的最小值更低
                        if ref_min is not None and panic_val >= ref_min:
                            issues.append(f"❌ {test_id} ({test_name}): panic_low[{unit}]={panic_val} >= ref_min={ref_min}")
                        # 检查是否过于离谱（比参考最小值小10倍以上）
                        if ref_min is not None and ref_min > 0 and panic_val < ref_min * 0.1:
                            issues.append(f"⚠️  {test_id} ({test_name}): panic_low[{unit}]={panic_val} 过低 (ref_min={ref_min})")
                    else:
                        issues.append(f"📍 {test_id} ({test_name}): panic_low[{unit}]={panic_val} 无对应参考范围")
            
            # 检查panic_high
            if 'panic_high' in biological_limits:
                panic_high = biological_limits['panic_high']
                for unit, panic_val in panic_high.items():
                    if unit in ref_ranges:
                        ref_min, ref_max = ref_ranges[unit]
                        # panic_high应该比参考范围的最大值更高
                        if ref_max is not None and panic_val <= ref_max:
                            issues.append(f"❌ {test_id} ({test_name}): panic_high[{unit}]={panic_val} <= ref_max={ref_max}")
                        # 检查是否过于离谱（比参考最大值大10倍以上）
                        if ref_max is not None and panic_val > ref_max * 10:
                            issues.append(f"⚠️  {test_id} ({test_name}): panic_high[{unit}]={panic_val} 过高 (ref_max={ref_max})")
                    else:
                        issues.append(f"📍 {test_id} ({test_name}): panic_high[{unit}]={panic_val} 无对应参考范围")
            
            # 检查其他明显不合理的生物学极限值
            for limit_type in ['physiological_minimum', 'physiological_maximum', 'critical_low', 'critical_high']:
                if limit_type in biological_limits:
                    limit_values = biological_limits[limit_type]
                    for unit, limit_val in limit_values.items():
                        if unit in ref_ranges:
                            ref_min, ref_max = ref_ranges[unit]
                            # 生理学最小值不应该比参考范围更高
                            if limit_type == 'physiological_minimum' and ref_max is not None and limit_val > ref_max:
                                issues.append(f"❌ {test_id} ({test_name}): {limit_type}[{unit}]={limit_val} > ref_max={ref_max}")
                            # 生理学最大值不应该比参考范围最小值更低
                            elif limit_type == 'physiological_maximum' and ref_min is not None and limit_val < ref_min:
                                issues.append(f"❌ {test_id} ({test_name}): {limit_type}[{unit}]={limit_val} < ref_min={ref_min}")
    
    return issues

def main():
    json_file = '/Users/williamsun/Documents/gplus/docs/CRF_design/Complete_Laboratory_Tests_with_LOINC_Units_Limits.json'
    
    try:
        print("正在分析JSON文件中的panic值...")
        data = load_json_file(json_file)
        issues = find_unreasonable_panic_values(data)
        
        print(f"\n发现 {len(issues)} 个可能的问题:")
        for issue in issues:
            print(f"  {issue}")
        
        if not issues:
            print("未发现明显不合理的panic值。")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()