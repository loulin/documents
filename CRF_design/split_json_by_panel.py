#!/usr/bin/env python3
"""
将大型实验室检测JSON文件按panel_name拆分为多个小文件
"""

import json
import os
from typing import Dict, Any

def load_json_file(filepath: str) -> Dict[str, Any]:
    """加载JSON文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON格式错误: {e}")
        return {}
    except FileNotFoundError:
        print(f"文件不存在: {filepath}")
        return {}

def split_json_by_panel(json_file: str, output_dir: str = None):
    """按panel_name拆分JSON文件"""
    
    # 设置输出目录
    if output_dir is None:
        output_dir = os.path.dirname(json_file)
    
    split_dir = os.path.join(output_dir, "panels")
    os.makedirs(split_dir, exist_ok=True)
    
    print(f"正在加载JSON文件: {json_file}")
    data = load_json_file(json_file)
    
    if not data:
        print("无法加载JSON数据")
        return
    
    # 检查是否有comprehensive_test_panels结构
    if 'comprehensive_test_panels' in data:
        panels_data = data['comprehensive_test_panels']
        print("检测到comprehensive_test_panels结构")
    else:
        panels_data = data
        print("使用根级别数据结构")
    
    panel_count = 0
    
    for panel_key, panel_data in panels_data.items():
        if not isinstance(panel_data, dict):
            print(f"跳过非字典类型的面板: {panel_key}")
            continue
        
        panel_name = panel_data.get('panel_name', panel_key)
        safe_panel_name = panel_name.replace(' ', '_').replace('/', '_')
        
        # 创建单独的面板文件
        panel_file_data = {
            panel_key: panel_data
        }
        
        # 生成文件名
        output_filename = f"{panel_key}_{safe_panel_name}.json"
        output_path = os.path.join(split_dir, output_filename)
        
        # 保存文件
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(panel_file_data, f, ensure_ascii=False, indent=2)
            
            test_count = panel_data.get('test_count', len(panel_data.get('tests', [])))
            print(f"✅ 已保存面板: {panel_name} ({test_count}项测试)")
            print(f"   文件路径: {output_path}")
            panel_count += 1
            
        except Exception as e:
            print(f"❌ 保存面板失败 {panel_name}: {e}")
    
    print(f"\n📊 拆分完成统计:")
    print(f"  - 总面板数: {panel_count}")
    print(f"  - 输出目录: {split_dir}")
    print(f"  - 文件大小减少比例: ~{100/panel_count:.1f}% per file")

def main():
    json_file = '/Users/williamsun/Documents/gplus/docs/CRF_design/Comprehensive_Laboratory_Tests_with_LOINC.json'
    
    if not os.path.exists(json_file):
        print(f"文件不存在: {json_file}")
        return
    
    print("🔄 开始拆分JSON文件...")
    split_json_by_panel(json_file)
    print("✨ 拆分任务完成!")

if __name__ == "__main__":
    main()