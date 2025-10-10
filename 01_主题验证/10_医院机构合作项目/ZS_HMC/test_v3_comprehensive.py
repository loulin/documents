#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：Agent_ZS v3.0 综合报告生成器

演示如何使用新的v3.0版本（整合GPlus可视化 + AGPAI深度分析）
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from Agent_ZS_HMC_Report_Generator_v3 import generate_comprehensive_report


def create_sample_cgm_data_v3(days=14, filename="sample_cgm_data_v3.csv"):
    """
    生成模拟CGM数据用于测试v3.0

    增加了更多真实模式：
    - 黎明现象
    - 夜间低血糖
    - 餐后高血糖
    - 工作日vs周末差异
    """
    print(f"📊 正在生成{days}天的模拟CGM数据（v3.0增强版）...")

    start_time = datetime.now() - timedelta(days=days)
    timestamps = []
    glucose_values = []

    for day in range(days):
        current_date = start_time + timedelta(days=day)
        is_weekend = current_date.weekday() >= 5  # 5=周六, 6=周日

        for hour in range(24):
            for minute in range(0, 60, 5):  # 每5分钟
                timestamp = current_date.replace(hour=hour, minute=minute, second=0)
                timestamps.append(timestamp)

                # 基础血糖
                base_glucose = 7.5

                # ==== 时段特征 ====

                # 1. 黎明现象 (4-6点血糖升高)
                if hour in [4, 5]:
                    base_glucose += 1.5  # 黎明现象

                # 2. 夜间低血糖风险 (2-4点)
                elif hour in [2, 3]:
                    base_glucose -= 1.2  # 夜间偏低

                # 3. 餐后血糖升高
                elif hour in [8, 9]:  # 早餐后
                    base_glucose += np.random.uniform(2.5, 4.0)
                elif hour in [13, 14]:  # 午餐后
                    base_glucose += np.random.uniform(2.0, 3.5)
                elif hour in [19, 20]:  # 晚餐后 (最高)
                    base_glucose += np.random.uniform(3.0, 5.0)

                # 4. 工作日 vs 周末差异
                if is_weekend:
                    # 周末：作息不规律，血糖更高
                    base_glucose += 0.8
                    # 周末早餐晚1-2小时，中午血糖更高
                    if hour in [10, 11]:
                        base_glucose += 2.0

                # 添加随机波动
                glucose = base_glucose + np.random.normal(0, 0.6)

                # 确保在合理范围
                glucose = max(2.8, min(16.0, glucose))

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
    print(f"   - 特殊模式: 黎明现象、夜间低血糖、餐后高血糖、工作日周末差异")

    return filename


def test_v3_comprehensive():
    """测试v3.0综合报告生成器"""
    print("\n" + "="*80)
    print("🧪 测试Agent_ZS v3.0 综合报告生成器")
    print("   (整合 GPlus可视化 + AGPAI深度分析)")
    print("="*80 + "\n")

    # Step 1: 生成测试数据
    data_file = create_sample_cgm_data_v3(days=14, filename="sample_cgm_data_v3.csv")

    # Step 2: 准备患者信息
    patient_info = {
        "name": "张三（v3.0测试）",
        "age": 45,
        "gender": "男",
        "diagnosis": "2型糖尿病"
    }

    # Step 3: 准备用药信息
    medication_data = {
        "medications": [
            {
                "name": "二甲双胍片",
                "dosage": "0.5g",
                "frequency": "每日3次",
                "start_date": "2025-07-15",
                "compliance": "良好"
            },
            {
                "name": "达格列净片",
                "dosage": "10mg",
                "frequency": "每日1次",
                "start_date": "2025-07-25",
                "compliance": "良好"
            }
        ]
    }

    # Step 4: 生成v3.0综合报告
    print("\n📄 开始生成v3.0综合报告...")
    try:
        html_path = generate_comprehensive_report(
            filepath=data_file,
            patient_id="TEST_V3_001",
            patient_info=patient_info,
            medication_data=medication_data,
            output_path="CGM_Comprehensive_Report_v3_Test.html"
        )

        print("\n" + "="*80)
        print("✅ v3.0综合报告生成成功!")
        print("="*80)
        print(f"\n📍 报告位置: {html_path}")
        print("\n💡 v3.0报告包含:")
        print("\n   【GPlus专业可视化模块】")
        print("   ✅ AGP动态血糖图谱（百分位数带状图）")
        print("   ✅ 14天每日血糖曲线小图")
        print("   ✅ TIR/TAR/TBR可视化分布条")
        print("   ✅ 详细指标表格（MAGE、AUC、IQR等）")
        print("\n   【AGPAI深度分析模块】")
        print("   ✅ 六时段综合深度分析")
        print("      - 夜间/晨起/上午/下午/晚间/睡前")
        print("      - 每个时段的问题识别和建议")
        print("   ✅ 工作日/周末对比分析")
        print("      - 血糖控制差异")
        print("      - 模式优化建议")
        print("   ✅ 异常模式检测")
        print("      - 黎明现象检测（检出率、严重程度）")
        print("      - 夜间低血糖风险评估")
        print("      - 餐后血糖峰值异常识别")
        print("   ✅ 高级血糖指标")
        print("      - MAGE（平均血糖波动幅度）")
        print("      - AUC（曲线下面积）")
        print("      - IQR（血糖四分差）")
        print("      - LBGI/HBGI（低/高血糖风险指数）")
        print("   ✅ 药物-血糖整合分析")
        print("      - 用药概览")
        print("      - 用药优化建议")
        print("   ✅ 综合风险评估")
        print("      - 低血糖/高血糖/波动风险")
        print("      - 并发症风险评估")
        print("   ✅ 自动文字评估生成")
        print("      - 总体血糖情况描述")
        print("      - 个性化改善建议")
        print("\n🌐 在浏览器中打开查看完整报告")
        print("📄 如需PDF，在浏览器中按 Cmd+P (Mac) 或 Ctrl+P (Windows)")
        print("   选择'另存为PDF'即可导出\n")

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


def compare_versions():
    """对比v2.0和v3.0的功能差异"""
    print("\n" + "="*80)
    print("📊 Agent_ZS 版本功能对比")
    print("="*80 + "\n")

    comparison = [
        ("", "v2.0 Enhanced", "v3.0 Ultimate"),
        ("=" * 25, "=" * 25, "=" * 25),
        ("基础功能", "", ""),
        ("AGP可视化", "✅", "✅"),
        ("每日曲线小图", "✅", "✅"),
        ("TIR可视化条", "✅", "✅"),
        ("核心指标计算", "✅", "✅"),
        ("", "", ""),
        ("高级指标", "", ""),
        ("MAGE计算", "❌", "✅ 峰谷检测算法"),
        ("AUC计算", "❌", "✅ 白天/夜晚/全天"),
        ("血糖四分差", "❌", "✅ IQR"),
        ("LBGI/HBGI", "❌", "✅ Kovatchev算法"),
        ("", "", ""),
        ("深度分析", "", ""),
        ("六时段分析", "❌", "✅ 含问题识别+建议"),
        ("工作日周末对比", "❌", "✅ 含差异分析"),
        ("黎明现象检测", "❌", "✅ 检出率+严重程度"),
        ("夜间低血糖检测", "❌", "✅ 风险评估"),
        ("餐后高血糖检测", "❌", "✅ 峰值分析"),
        ("综合风险评估", "❌", "✅ 多维度评级"),
        ("", "", ""),
        ("临床应用", "", ""),
        ("药物效果分析", "简单", "✅ 整合分析"),
        ("自动文字评估", "❌", "✅ 智能生成"),
        ("个性化建议", "通用", "✅ 基于模式"),
        ("", "", ""),
        ("报告质量", "专业", "专业+深度+智能"),
        ("临床实用性", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"),
    ]

    for row in comparison:
        print(f"{row[0]:<25} {row[1]:<25} {row[2]:<30}")

    print("\n" + "="*80)
    print("\n💡 升级亮点:")
    print("   1. 新增5个高级血糖指标（MAGE/AUC/IQR/LBGI/HBGI）")
    print("   2. 新增3大异常模式检测（黎明现象/夜间低血糖/餐后高血糖）")
    print("   3. 新增多维度深度分析（六时段/工作日周末/综合风险）")
    print("   4. 智能化文字评估生成，无需手动撰写")
    print("   5. 完全整合GPlus可视化 + AGPAI分析框架")
    print("\n🎯 适用场景:")
    print("   ✅ 内分泌科门诊随访")
    print("   ✅ 健康管理中心CGM报告")
    print("   ✅ 临床科研数据分析")
    print("   ✅ 药物效果评估研究")
    print("   ✅ 糖尿病管理APP后台")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    # 显示版本对比
    compare_versions()

    # 执行v3.0测试
    test_v3_comprehensive()

    print("\n" + "="*80)
    print("🎉 v3.0测试完成!")
    print("="*80 + "\n")
    print("💡 后续步骤:")
    print("   1. 在浏览器中查看生成的HTML报告")
    print("   2. 验证所有深度分析模块是否正常工作")
    print("   3. 测试真实患者CGM数据")
    print("   4. 根据反馈优化算法参数")
    print("   5. 考虑添加更多可视化图表（如TIR趋势面积图）\n")
