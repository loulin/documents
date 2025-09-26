#!/usr/bin/env python3
"""
将实验室检测JSON文件转换为CSV格式，展示所有字段结构
"""

import json
import pandas as pd
from typing import Dict, Any, List
import os

def load_json_file(filepath: str) -> Dict[str, Any]:
    """加载JSON文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON格式错误: {e}")
        return {}

def flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
    """扁平化嵌套字典"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # 对于列表，我们将其转换为字符串
            items.append((new_key, str(v) if v else ''))
        else:
            items.append((new_key, v))
    return dict(items)

def extract_all_tests_to_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """提取所有测试项目并转换为DataFrame"""
    all_tests = []
    
    # 检查是否有comprehensive_test_panels结构
    if 'comprehensive_test_panels' in data:
        data = data['comprehensive_test_panels']
    
    for panel_key, panel_data in data.items():
        if not isinstance(panel_data, dict) or 'tests' not in panel_data:
            continue
        
        panel_info = {
            'panel_id': panel_key,
            'panel_name': panel_data.get('panel_name', ''),
            'domain_code': panel_data.get('domain_code', ''),
            'icd10_codes': str(panel_data.get('icd10_codes', [])),
            'test_count': panel_data.get('test_count', 0)
        }
        
        for test in panel_data['tests']:
            # 创建测试项目的完整记录
            test_record = panel_info.copy()
            
            # 扁平化测试数据
            flattened_test = flatten_dict(test)
            test_record.update(flattened_test)
            
            all_tests.append(test_record)
    
    return pd.DataFrame(all_tests)

def analyze_json_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """分析JSON结构"""
    analysis = {
        'total_panels': 0,
        'total_tests': 0,
        'panels': [],
        'all_fields': set(),
        'field_frequency': {},
        'sample_test': None
    }
    
    # 检查是否有comprehensive_test_panels结构
    if 'comprehensive_test_panels' in data:
        data = data['comprehensive_test_panels']
    
    for panel_key, panel_data in data.items():
        if not isinstance(panel_data, dict) or 'tests' not in panel_data:
            continue
        
        analysis['total_panels'] += 1
        panel_tests = len(panel_data.get('tests', []))
        analysis['total_tests'] += panel_tests
        
        analysis['panels'].append({
            'panel_id': panel_key,
            'panel_name': panel_data.get('panel_name', ''),
            'test_count': panel_tests
        })
        
        # 分析字段
        for test in panel_data['tests']:
            if analysis['sample_test'] is None:
                analysis['sample_test'] = test
            
            flattened = flatten_dict(test)
            for field in flattened.keys():
                analysis['all_fields'].add(field)
                analysis['field_frequency'][field] = analysis['field_frequency'].get(field, 0) + 1
    
    return analysis

def main():
    json_file = '/Users/williamsun/Documents/gplus/docs/CRF_design/Comprehensive_Laboratory_Tests_with_LOINC.json'
    
    if not os.path.exists(json_file):
        print(f"文件不存在: {json_file}")
        return
    
    print("正在加载JSON文件...")
    data = load_json_file(json_file)
    
    if not data:
        print("无法加载JSON数据")
        return
    
    print("正在分析文件结构...")
    analysis = analyze_json_structure(data)
    
    print(f"\n📊 JSON文件结构分析:")
    print(f"总面板数: {analysis['total_panels']}")
    print(f"总测试项数: {analysis['total_tests']}")
    
    print(f"\n📋 检测面板列表:")
    for panel in analysis['panels']:
        print(f"  - {panel['panel_id']}: {panel['panel_name']} ({panel['test_count']}项)")
    
    print(f"\n🏷️  所有字段列表 (共{len(analysis['all_fields'])}个):")
    sorted_fields = sorted(analysis['field_frequency'].items(), key=lambda x: x[1], reverse=True)
    
    for field, count in sorted_fields[:30]:  # 显示前30个最常见字段
        print(f"  - {field}: {count}次")
    
    if len(sorted_fields) > 30:
        print(f"  ... 还有 {len(sorted_fields) - 30} 个字段")
    
    print(f"\n📝 示例测试项目结构:")
    if analysis['sample_test']:
        sample_flat = flatten_dict(analysis['sample_test'])
        for key, value in list(sample_flat.items())[:10]:
            print(f"  {key}: {value}")
        if len(sample_flat) > 10:
            print(f"  ... 还有 {len(sample_flat) - 10} 个字段")
    
    # 转换为CSV
    print(f"\n🔄 正在转换为CSV格式...")
    df = extract_all_tests_to_dataframe(data)
    
    # 保存CSV文件
    csv_file = json_file.replace('.json', '.csv')
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    
    print(f"✅ CSV文件已保存: {csv_file}")
    print(f"📊 CSV文件信息:")
    print(f"  - 行数: {len(df)}")
    print(f"  - 列数: {len(df.columns)}")
    print(f"  - 文件大小: {os.path.getsize(csv_file) / 1024 / 1024:.2f} MB")
    
    print(f"\n📋 CSV列名 (前20个):")
    for i, col in enumerate(df.columns[:20]):
        print(f"  {i+1:2d}. {col}")
    
    if len(df.columns) > 20:
        print(f"     ... 还有 {len(df.columns) - 20} 列")
    
    # 保存字段分析到单独文件
    field_analysis_file = json_file.replace('.json', '_field_analysis.txt')
    with open(field_analysis_file, 'w', encoding='utf-8') as f:
        f.write("实验室检测JSON字段分析报告\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"总面板数: {analysis['total_panels']}\n")
        f.write(f"总测试项数: {analysis['total_tests']}\n\n")
        
        f.write("所有字段及使用频率:\n")
        f.write("-" * 30 + "\n")
        for field, count in sorted_fields:
            f.write(f"{field}: {count}次\n")
    
    print(f"📄 字段分析报告已保存: {field_analysis_file}")

if __name__ == "__main__":
    main()