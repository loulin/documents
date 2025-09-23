#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGPAI批量分析脚本
支持批量处理多个患者的CGM数据
"""

import os
import json
from datetime import datetime
from AGPAI_Agent_V2 import AGPAI_Agent_V2

def batch_analyze_patients(data_directory, output_directory="./reports"):
    """
    批量分析患者数据
    
    Args:
        data_directory: CGM数据文件目录
        output_directory: 输出报告目录
    """
    
    # 创建输出目录
    os.makedirs(output_directory, exist_ok=True)
    
    # 初始化Agent
    agent = AGPAI_Agent_V2()
    
    # 支持的文件格式
    supported_extensions = ['.txt', '.csv']
    
    # 扫描数据文件
    data_files = []
    for file in os.listdir(data_directory):
        if any(file.lower().endswith(ext) for ext in supported_extensions):
            data_files.append(file)
    
    print(f"🔍 发现 {len(data_files)} 个数据文件")
    
    results_summary = []
    
    for i, filename in enumerate(data_files, 1):
        try:
            print(f"\n📊 正在分析 {i}/{len(data_files)}: {filename}")
            
            # 提取患者ID（从文件名）
            patient_id = os.path.splitext(filename)[0]
            file_path = os.path.join(data_directory, filename)
            
            # 执行分析
            report = agent.generate_comprehensive_report(
                patient_id=patient_id,
                cgm_file_path=file_path,
                include_historical=True
            )
            
            # 保存文本报告
            report_file = os.path.join(output_directory, f"{patient_id}_report.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            # 获取分析数据
            analysis_data = agent._get_last_analysis_data()  # 需要添加这个方法
            
            # 保存JSON数据
            json_file = os.path.join(output_directory, f"{patient_id}_data.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            # 记录成功
            results_summary.append({
                'patient_id': patient_id,
                'status': 'success',
                'report_file': report_file,
                'json_file': json_file,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"✅ 完成: {patient_id}")
            
        except Exception as e:
            print(f"❌ 错误: {filename} - {str(e)}")
            results_summary.append({
                'patient_id': patient_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    # 保存汇总结果
    summary_file = os.path.join(output_directory, "batch_analysis_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results_summary, f, ensure_ascii=False, indent=2)
    
    # 打印汇总
    success_count = sum(1 for r in results_summary if r['status'] == 'success')
    error_count = len(results_summary) - success_count
    
    print(f"\n📋 批量分析完成:")
    print(f"   ✅ 成功: {success_count} 个")
    print(f"   ❌ 失败: {error_count} 个")
    print(f"   📂 输出目录: {output_directory}")
    print(f"   📄 汇总文件: {summary_file}")

def analyze_single_patient(file_path, patient_id=None, output_dir="./reports"):
    """
    分析单个患者
    
    Args:
        file_path: CGM数据文件路径
        patient_id: 患者ID（可选，默认从文件名提取）
        output_dir: 输出目录
    """
    
    if patient_id is None:
        patient_id = os.path.splitext(os.path.basename(file_path))[0]
    
    print(f"🩺 分析患者: {patient_id}")
    print(f"📁 数据文件: {file_path}")
    
    try:
        # 初始化Agent
        agent = AGPAI_Agent_V2()
        
        # 执行分析
        report = agent.generate_comprehensive_report(
            patient_id=patient_id,
            cgm_file_path=file_path,
            include_historical=True
        )
        
        # 输出到控制台
        print("\n" + "="*60)
        print(report)
        print("="*60)
        
        # 保存报告文件
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            report_file = os.path.join(output_dir, f"{patient_id}_report.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n💾 报告已保存: {report_file}")
        
        return report
        
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  单个文件分析: python3 batch_analysis.py single /path/to/file.txt")
        print("  批量分析:     python3 batch_analysis.py batch /path/to/directory")
        print("  示例:")
        print("    python3 batch_analysis.py single './R002 v11.txt'")
        print("    python3 batch_analysis.py batch '/path/to/cgm/data/folder'")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "single":
        if len(sys.argv) < 3:
            print("❌ 请提供文件路径")
            sys.exit(1)
        
        file_path = sys.argv[2]
        patient_id = sys.argv[3] if len(sys.argv) > 3 else None
        
        analyze_single_patient(file_path, patient_id)
        
    elif mode == "batch":
        if len(sys.argv) < 3:
            print("❌ 请提供数据目录路径")
            sys.exit(1)
        
        data_dir = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else "./reports"
        
        batch_analyze_patients(data_dir, output_dir)
        
    else:
        print(f"❌ 未知模式: {mode}")
        print("支持的模式: single, batch")
        sys.exit(1)