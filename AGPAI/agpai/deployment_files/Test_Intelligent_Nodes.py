#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能节点检测测试脚本
用于测试不同患者数据的智能转折点检测功能
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 导入智能分段分析器
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Intelligent_Segmentation import IntelligentSegmentationAnalyzer

def test_intelligent_nodes(filepath: str, patient_name: str = None, output_dir: str = None):
    """
    测试智能节点检测
    
    Parameters:
    - filepath: Excel文件路径
    - patient_name: 患者名称（用于输出文件命名）
    - output_dir: 输出目录（默认当前目录）
    """
    
    print(f"🔍 开始智能节点检测测试...")
    print(f"📁 数据文件: {filepath}")
    
    # 检查文件是否存在
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return None
    
    try:
        # 加载数据
        print("📊 正在加载数据...")
        df = pd.read_excel(filepath)
        
        # 标准化列名
        if 'glucose' in df.columns:
            glucose_col = 'glucose'
            time_col = 'timestamp' if 'timestamp' in df.columns else df.columns[0]
        elif '值' in df.columns:
            df = df.rename(columns={'值': 'glucose', '时间': 'timestamp'})
            glucose_col = 'glucose'
            time_col = 'timestamp'
        else:
            # 自动检测数值列
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                print("❌ 未找到血糖数值列")
                return None
            glucose_col = numeric_cols[0]
            time_col = df.columns[0]
            df = df.rename(columns={glucose_col: 'glucose', time_col: 'timestamp'})
            print(f"🔄 自动识别血糖列: {glucose_col}")
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        glucose_values = df['glucose'].dropna().values
        total_days = (df['timestamp'].max() - df['timestamp'].min()).days + 1
        
        print(f"✅ 数据加载完成:")
        print(f"   📈 数据点数: {len(glucose_values)}")
        print(f"   📅 监测天数: {total_days}")
        print(f"   📊 血糖范围: {glucose_values.min():.1f} - {glucose_values.max():.1f} mg/dL")
        print(f"   🕐 时间范围: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
        
        # 创建智能分段分析器
        print("\n🤖 启动智能分段分析器...")
        analyzer = IntelligentSegmentationAnalyzer(min_segment_days=1, max_segments=8)
        
        # 进行智能分段分析
        print("🔬 执行多算法融合变化点检测...")
        result = analyzer.analyze_intelligent_segments(df, glucose_values, total_days)
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if patient_name:
            safe_name = patient_name.replace('/', '_').replace('\\', '_')
            base_filename = f"Intelligent_Nodes_{safe_name}_{timestamp}"
        else:
            base_filename = f"Intelligent_Nodes_Analysis_{timestamp}"
        
        # 设置输出目录
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            json_filename = os.path.join(output_dir, f"{base_filename}.json")
            txt_filename = os.path.join(output_dir, f"{base_filename}.txt")
        else:
            json_filename = f"{base_filename}.json"
            txt_filename = f"{base_filename}.txt"
        
        # 保存完整结果
        print(f"\n💾 保存分析结果...")
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ JSON结果已保存: {json_filename}")
        
        # 生成可读性报告
        generate_readable_report(result, txt_filename, filepath, patient_name)
        print(f"✅ 文本报告已保存: {txt_filename}")
        
        # 打印核心结果
        print_core_results(result)
        
        return result
        
    except Exception as e:
        print(f"❌ 分析过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_readable_report(result: dict, filename: str, filepath: str, patient_name: str):
    """生成可读性报告"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("🔬 智能转折点检测分析报告\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"📁 数据文件: {filepath}\n")
        if patient_name:
            f.write(f"👤 患者姓名: {patient_name}\n")
        f.write(f"📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"🔬 分析方法: {result.get('分段方法', 'N/A')}\n\n")
        
        # 检测参数
        params = result.get('检测参数', {})
        if params:
            f.write("⚙️ 检测参数配置\n")
            f.write("-" * 30 + "\n")
            for key, value in params.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
        
        # 分段结果
        segments = result.get('最终分段', [])
        f.write(f"🎯 智能分段结果 (共检测到 {len(segments)} 个分段)\n")
        f.write("-" * 30 + "\n")
        
        for i, segment in enumerate(segments, 1):
            f.write(f"第{i}段:\n")
            f.write(f"  ⏰ 时间范围: {segment['start_time']} ~ {segment['end_time']}\n")
            f.write(f"  📊 持续天数: {segment['duration_days']:.1f}天\n")
            f.write(f"  📈 持续小时: {segment.get('duration_hours', 'N/A')}小时\n")
            
            # 血糖统计
            stats = segment.get('glucose_stats', {})
            if stats:
                f.write(f"  🩸 血糖统计:\n")
                f.write(f"    平均值: {stats.get('mean', 0):.1f} mg/dL\n")
                f.write(f"    标准差: {stats.get('std', 0):.1f} mg/dL\n")
                f.write(f"    变异系数: {stats.get('cv', 0):.1f}%\n")
                if 'tir' in stats:
                    f.write(f"    目标范围内时间: {stats['tir']:.1f}%\n")
            
            f.write("\n")
        
        # 变化点分析
        change_points = result.get('检测到的变化点', {})
        if change_points:
            f.write("🔍 变化点检测详情\n")
            f.write("-" * 30 + "\n")
            
            for method, points in change_points.items():
                if points and len(points) > 0:
                    f.write(f"{method}: 检测到 {len(points)} 个变化点\n")
            f.write("\n")
        
        # 分段质量评估
        quality = result.get('分段评估', {})
        if quality:
            f.write("📋 分段质量评估\n")
            f.write("-" * 30 + "\n")
            f.write(f"质量等级: {quality.get('质量等级', 'N/A')}\n")
            f.write(f"质量评分: {quality.get('分段质量评分', 'N/A')}\n")
            f.write(f"质量描述: {quality.get('质量描述', 'N/A')}\n\n")
        
        # 临床意义
        if '临床意义' in result:
            f.write("🏥 临床意义分析\n")
            f.write("-" * 30 + "\n")
            f.write(f"{result['临床意义']}\n\n")

def print_core_results(result: dict):
    """打印核心结果"""
    
    print("\n" + "="*60)
    print("🎯 智能转折点检测核心结果")
    print("="*60)
    
    segments = result.get('最终分段', [])
    print(f"📊 检测到 {len(segments)} 个智能分段:")
    
    for i, segment in enumerate(segments, 1):
        duration = segment['duration_days']
        start = segment['start_time']
        end = segment['end_time']
        points = segment.get('duration_hours', 0)
        
        if isinstance(start, str):
            start_str = start[:16]  # 截取到分钟
            end_str = end[:16]
        else:
            start_str = start.strftime('%m-%d %H:%M')
            end_str = end.strftime('%m-%d %H:%M')
        
        print(f"  第{i}段: {duration:4.1f}天 | {start_str} ~ {end_str} | {points:5.1f}小时")
        
        # 显示血糖统计
        stats = segment.get('glucose_stats', {})
        if stats:
            mean = stats.get('mean', 0)
            cv = stats.get('cv', 0)
            tir = stats.get('tir', 0)
            print(f"        血糖: {mean:5.1f}±{cv:4.1f}% | TIR: {tir:5.1f}%")
    
    # 显示质量评估
    quality = result.get('分段评估', {})
    if quality:
        print(f"\n📋 分段质量: {quality.get('质量等级', 'N/A')} | 评分: {quality.get('分段质量评分', 'N/A')}")
    
    # 显示变化点统计
    change_points = result.get('检测到的变化点', {})
    if change_points:
        print("\n🔍 变化点检测统计:")
        for method, points in change_points.items():
            if points and len(points) > 0:
                print(f"  {method}: {len(points)}个")
    
    print("="*60)

def batch_test_directory(directory_path: str, output_dir: str = "batch_results"):
    """批量测试目录下的所有Excel文件"""
    
    print(f"🗂️  开始批量测试目录: {directory_path}")
    
    directory = Path(directory_path)
    if not directory.exists():
        print(f"❌ 目录不存在: {directory_path}")
        return
    
    # 查找所有Excel文件
    excel_files = list(directory.glob("*.xlsx")) + list(directory.glob("*.xls"))
    
    if not excel_files:
        print("❌ 目录中未找到Excel文件")
        return
    
    print(f"📁 找到 {len(excel_files)} 个Excel文件")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 批量处理
    results = {}
    for i, filepath in enumerate(excel_files, 1):
        print(f"\n{'='*20} 文件 {i}/{len(excel_files)} {'='*20}")
        
        # 提取患者名称
        patient_name = filepath.stem
        
        result = test_intelligent_nodes(str(filepath), patient_name, output_dir)
        if result:
            results[patient_name] = result
    
    print(f"\n🎉 批量测试完成！共处理 {len(results)} 个有效文件")
    print(f"📁 结果保存在: {output_dir}")

if __name__ == "__main__":
    print("🤖 智能转折点检测测试工具")
    print("="*50)
    
    if len(sys.argv) > 1:
        # 从命令行参数获取文件路径
        filepath = sys.argv[1]
        patient_name = sys.argv[2] if len(sys.argv) > 2 else None
        test_intelligent_nodes(filepath, patient_name)
    else:
        # 交互式选择
        print("\n选择测试模式:")
        print("1. 单个文件测试")
        print("2. 批量目录测试") 
        print("3. 使用示例数据测试")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            filepath = input("请输入Excel文件路径: ").strip()
            patient_name = input("请输入患者名称 (可选): ").strip() or None
            test_intelligent_nodes(filepath, patient_name)
            
        elif choice == "2":
            directory = input("请输入目录路径: ").strip()
            batch_test_directory(directory)
            
        elif choice == "3":
            # 使用示例数据
            sample_path = "/Users/williamsun/Documents/gplus/docs/AGPAI/demodata/胰腺外科/上官李军-253124-1MH011R56MM.xlsx"
            if os.path.exists(sample_path):
                test_intelligent_nodes(sample_path, "上官李军-253124")
            else:
                print("❌ 示例数据文件不存在")
        else:
            print("❌ 无效选择")