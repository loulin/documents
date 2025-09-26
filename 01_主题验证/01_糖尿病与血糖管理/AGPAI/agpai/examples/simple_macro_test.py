#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import json
from datetime import datetime

def simple_macro_analysis():
    filepath = "/Users/williamsun/Documents/gplus/docs/AGPAI/demodata/某科室/吴四毛-103782-1MH00V9XRF4.xlsx"
    
    print("开始简单宏观分段分析: 吴四毛-103782")
    
    # 直接加载数据
    print("加载原始数据...")
    df = pd.read_excel(filepath)
    print(f"列名: {df.columns.tolist()}")
    
    # 数据预处理
    df['时间'] = pd.to_datetime(df['时间'])
    df = df.sort_values('时间').reset_index(drop=True)
    
    glucose_values = df['值'].values  # 使用'值'列
    total_days = (df['时间'].max() - df['时间'].min()).days + 1
    
    print(f"数据点数: {len(glucose_values)}, 监测天数: {total_days}")
    print(f"数据范围: {df['时间'].min()} 至 {df['时间'].max()}")
    print(f"血糖范围: {glucose_values.min():.1f} - {glucose_values.max():.1f} mmol/L")
    
    # 简单分段分析 - 基于统计变化点
    def simple_macro_segmentation(values, n_segments=4):
        """简单的宏观分段算法"""
        n = len(values)
        segment_size = n // n_segments
        
        segments = []
        for i in range(n_segments):
            start_idx = i * segment_size
            if i == n_segments - 1:  # 最后一段包含所有剩余数据
                end_idx = n
            else:
                end_idx = (i + 1) * segment_size
            
            segment_data = values[start_idx:end_idx]
            segment_times = df.iloc[start_idx:end_idx]['时间']
            
            segments.append({
                '段落编号': i + 1,
                '开始时间': segment_times.iloc[0].strftime('%Y-%m-%d %H:%M'),
                '结束时间': segment_times.iloc[-1].strftime('%Y-%m-%d %H:%M'),
                '数据点数': len(segment_data),
                '平均血糖': f"{segment_data.mean():.2f} mmol/L",
                '血糖标准差': f"{segment_data.std():.2f} mmol/L",
                '变异系数': f"{(segment_data.std() / segment_data.mean() * 100):.1f}%",
                '最低血糖': f"{segment_data.min():.1f} mmol/L",
                '最高血糖': f"{segment_data.max():.1f} mmol/L",
                '目标范围时间': f"{((segment_data >= 3.9) & (segment_data <= 10.0)).sum() / len(segment_data) * 100:.1f}%"
            })
        
        return segments
    
    # 执行分段
    print("\n执行宏观趋势分段...")
    segments = simple_macro_segmentation(glucose_values, 4)
    
    # 输出结果
    print("\n" + "="*80)
    print("🏢 吴四毛-103782 宏观趋势分段结果")
    print("="*80)
    print(f"分段数量: {len(segments)}")
    
    for segment in segments:
        print(f"\n【第{segment['段落编号']}段】")
        print(f"  时间范围: {segment['开始时间']} - {segment['结束时间']}")
        print(f"  数据点数: {segment['数据点数']}")
        print(f"  平均血糖: {segment['平均血糖']}")
        print(f"  变异系数: {segment['变异系数']}")
        print(f"  目标范围时间(TIR): {segment['目标范围时间']}")
        print(f"  血糖范围: {segment['最低血糖']} - {segment['最高血糖']}")
    
    # 保存结果
    result = {
        "患者ID": "吴四毛-103782",
        "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "分段模式": "宏观趋势分段",
        "分段数量": len(segments),
        "监测天数": total_days,
        "数据点数": len(glucose_values),
        "宏观分段结果": segments
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Wu_Simao_Simple_Macro_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n宏观分析结果已保存: {filename}")
    return result

if __name__ == "__main__":
    try:
        result = simple_macro_analysis()
    except Exception as e:
        print(f"分析过程出错: {e}")
        import traceback
        traceback.print_exc()