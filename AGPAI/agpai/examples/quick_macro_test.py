#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import json
from datetime import datetime
import sys
import os

# 添加路径
sys.path.append('/Users/williamsun/Documents/gplus/docs/AGPAI/agpai/examples')

# 导入主分析函数
from Agent2_Intelligent_Analysis import (
    load_and_validate_data,
    analyze_longitudinal_segments_macro_trend
)

def quick_macro_analysis():
    filepath = "/Users/williamsun/Documents/gplus/docs/AGPAI/demodata/某科室/吴四毛-103782-1MH00V9XRF4.xlsx"
    patient_id = "吴四毛-103782"
    
    print(f"开始快速宏观分段分析: {patient_id}")
    
    # 加载数据
    print("加载数据...")
    df = load_and_validate_data(filepath)
    
    # 检查列名并统一命名
    if '值' in df.columns:
        df['血糖'] = df['值']
    elif 'glucose' in df.columns:
        df['血糖'] = df['glucose'] 
    elif '血糖值' in df.columns:
        df['血糖'] = df['血糖值']
        
    glucose_values = df['血糖'].values
    total_days = (df['时间'].max() - df['时间'].min()).days + 1
    
    print(f"数据点数: {len(glucose_values)}, 监测天数: {total_days}")
    
    # 宏观分段分析
    print("执行宏观趋势分段...")
    macro_result = analyze_longitudinal_segments_macro_trend(df, glucose_values, total_days)
    
    # 输出结果
    print("\n" + "="*60)
    print("🏢 吴四毛-103782 宏观趋势分段结果")
    print("="*60)
    
    segment_info = macro_result.get('分段结果', {})
    print(f"分段数量: {segment_info.get('分段数量', 'N/A')}")
    
    if '段落详情' in segment_info:
        for segment in segment_info['段落详情']:
            print(f"\n【第{segment['段落编号']}段】")
            print(f"  时间范围: {segment['开始时间']} - {segment['结束时间']}")
            print(f"  持续时间: {segment['持续时间']}")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Wu_Simao_Macro_Analysis_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(macro_result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n宏观分析结果已保存: {filename}")
    return macro_result

if __name__ == "__main__":
    try:
        result = quick_macro_analysis()
    except Exception as e:
        print(f"分析过程出错: {e}")
        import traceback
        traceback.print_exc()