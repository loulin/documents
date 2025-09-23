#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGPAI 简易运行脚本
快速运行AGPAI Agent V2.0分析
"""

from AGPAI_Agent_V2 import AGPAI_Agent_V2
import sys
import os

def main():
    print("🩺 AGPAI Agent V2.0 - 智能血糖分析系统")
    print("=" * 50)
    
    # 检查参数
    if len(sys.argv) < 2:
        print("使用方法:")
        print(f"  python3 {sys.argv[0]} <CGM数据文件路径> [患者ID]")
        print("\n示例:")
        print(f"  python3 {sys.argv[0]} 'R002 v11.txt'")
        print(f"  python3 {sys.argv[0]} '/path/to/R016_v11.txt' 'R016_v11'")
        return
    
    # 获取参数
    cgm_file = sys.argv[1]
    patient_id = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(os.path.basename(cgm_file))[0]
    
    # 检查文件是否存在
    if not os.path.exists(cgm_file):
        print(f"❌ 文件不存在: {cgm_file}")
        return
    
    print(f"📁 分析文件: {cgm_file}")
    print(f"👤 患者ID: {patient_id}")
    print("⏳ 正在分析...")
    print("-" * 50)
    
    try:
        # 初始化Agent
        agent = AGPAI_Agent_V2()
        
        # 执行分析
        report = agent.generate_comprehensive_report(
            patient_id=patient_id,
            cgm_file_path=cgm_file,
            include_historical=True
        )
        
        # 输出结果
        print(report)
        
        # 保存报告
        output_file = f"{patient_id}_AGPAI_Report.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n💾 报告已保存至: {output_file}")
        
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")
        print("请检查:")
        print("  1. 文件格式是否正确")
        print("  2. 文件路径是否正确")
        print("  3. 数据格式是否符合要求")

if __name__ == "__main__":
    main()