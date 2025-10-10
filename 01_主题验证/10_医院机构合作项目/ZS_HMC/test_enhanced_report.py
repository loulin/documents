#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：Agent_ZS增强版CGM报告生成器

演示如何使用新的可视化报告功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from Agent_ZS_HMC_Report_Generator_Enhanced import generate_enhanced_report


def create_sample_cgm_data(days=14, filename="sample_cgm_data.csv"):
    """
    生成模拟CGM数据用于测试

    Args:
        days: 监测天数
        filename: 输出文件名
    """
    print(f"📊 正在生成{days}天的模拟CGM数据...")

    # 起始时间
    start_time = datetime.now() - timedelta(days=days)

    # 生成时间序列（每5分钟一个数据点）
    timestamps = []
    glucose_values = []

    for day in range(days):
        current_date = start_time + timedelta(days=day)

        for hour in range(24):
            for minute in range(0, 60, 5):  # 每5分钟
                timestamp = current_date.replace(hour=hour, minute=minute, second=0)
                timestamps.append(timestamp)

                # 模拟血糖波动模式
                # 基础血糖: 6-8 mmol/L
                base_glucose = 7.0

                # 餐后血糖升高模式
                if hour in [7, 8]:  # 早餐后
                    glucose = base_glucose + np.random.uniform(2, 4)
                elif hour in [12, 13]:  # 午餐后
                    glucose = base_glucose + np.random.uniform(2, 4)
                elif hour in [18, 19]:  # 晚餐后
                    glucose = base_glucose + np.random.uniform(2, 4)
                # 夜间血糖偏低
                elif hour in [0, 1, 2, 3, 4, 5]:
                    glucose = base_glucose - np.random.uniform(1, 2)
                else:
                    glucose = base_glucose + np.random.uniform(-1, 1)

                # 添加随机波动
                glucose += np.random.normal(0, 0.5)

                # 确保血糖值在合理范围
                glucose = max(3.0, min(15.0, glucose))

                glucose_values.append(round(glucose, 1))

    # 创建DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'glucose_value': glucose_values
    })

    # 保存为CSV
    df.to_csv(filename, index=False)
    print(f"✅ 模拟数据已生成: {filename}")
    print(f"   - 时间范围: {df['timestamp'].min()} 至 {df['timestamp'].max()}")
    print(f"   - 数据点数: {len(df)}")
    print(f"   - 平均血糖: {df['glucose_value'].mean():.1f} mmol/L")

    return filename


def test_enhanced_report():
    """测试增强版报告生成器"""
    print("\n" + "="*60)
    print("🧪 测试Agent_ZS增强版CGM报告生成器")
    print("="*60 + "\n")

    # Step 1: 生成测试数据
    data_file = create_sample_cgm_data(days=14, filename="sample_cgm_data.csv")

    # Step 2: 准备患者信息
    patient_info = {
        "name": "张三（测试）",
        "age": 45,
        "gender": "男"
    }

    # Step 3: 准备用药信息（可选）
    medication_data = {
        "medications": [
            {
                "name": "二甲双胍",
                "dosage": "500mg",
                "frequency": "bid",
                "start_date": "2025-09-01",
                "purpose": "控制血糖",
                "compliance": "良好"
            }
        ]
    }

    # Step 4: 生成报告
    print("\n📄 开始生成增强版HTML报告...")
    try:
        html_path = generate_enhanced_report(
            filepath=data_file,
            patient_id="TEST_P001",
            patient_info=patient_info,
            medication_data=medication_data,
            output_path="CGM_Report_Enhanced_Test.html"
        )

        print("\n" + "="*60)
        print("✅ 报告生成成功!")
        print("="*60)
        print(f"\n📍 报告位置: {html_path}")
        print("\n💡 下一步操作:")
        print("   1. 在浏览器中打开生成的HTML文件")
        print("   2. 查看以下可视化内容:")
        print("      - AGP动态血糖图谱（百分位数带状图）")
        print("      - 14天每日血糖曲线小图")
        print("      - TIR/TAR/TBR可视化分布条")
        print("      - 核心指标摘要卡片")
        print("   3. 如需PDF，在浏览器中按 Cmd+P (Mac) 或 Ctrl+P (Windows)")
        print("      选择'另存为PDF'即可导出\n")

        # 尝试在浏览器中打开（仅macOS）
        import subprocess
        import platform

        if platform.system() == 'Darwin':  # macOS
            try:
                subprocess.run(['open', html_path], check=True)
                print("🌐 已自动在默认浏览器中打开报告")
            except:
                pass

    except Exception as e:
        print(f"\n❌ 报告生成失败: {e}")
        import traceback
        traceback.print_exc()


def compare_with_original():
    """对比原版和增强版的差异"""
    print("\n" + "="*60)
    print("📊 原版 vs 增强版功能对比")
    print("="*60 + "\n")

    comparison = [
        ("输出格式", "JSON", "HTML (可打印PDF)"),
        ("AGP可视化", "❌", "✅ 百分位数带状图"),
        ("每日曲线", "❌", "✅ 14天小图网格"),
        ("TIR可视化", "仅数值", "✅ 堆叠柱状图"),
        ("交互图表", "无", "✅ Chart.js"),
        ("样式设计", "基础", "✅ GPlus专业样式"),
        ("可打印性", "需要额外处理", "✅ 浏览器直接打印"),
    ]

    print(f"{'功能':<15} {'原版 (v1.0)':<20} {'增强版 (v2.0)':<30}")
    print("-" * 60)
    for feature, v1, v2 in comparison:
        print(f"{feature:<15} {v1:<20} {v2:<30}")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # 显示功能对比
    compare_with_original()

    # 执行测试
    test_enhanced_report()

    print("\n" + "="*60)
    print("🎉 测试完成!")
    print("="*60 + "\n")
