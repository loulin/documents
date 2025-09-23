#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent5 报告结构演示脚本
展示新的报告组织结构：
1. 专业术语与缩写说明
2. 患者用药信息分析  
3. Agent1模块1-6按顺序
4. Agent2智能分段分析
5. 药物-血糖整合分析
"""

import sys
import os
import json
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from Agent5_Comprehensive_Analyzer import ComprehensiveAGPAIAnalyzer
    print("✅ Agent5模块导入成功")
except ImportError as e:
    print(f"❌ Agent5模块导入失败: {e}")
    sys.exit(1)

def create_demo_glucose_data():
    """创建演示用的血糖数据"""
    import pandas as pd
    import numpy as np
    
    # 生成13天的血糖数据
    dates = pd.date_range('2025-07-28', periods=13*96, freq='15T')  # 15分钟间隔
    
    # 模拟血糖数据（包含一些变化）
    np.random.seed(42)
    base_glucose = 9.0  # 基础血糖偏高
    
    glucose_values = []
    for i, timestamp in enumerate(dates):
        # 添加昼夜节律
        hour = timestamp.hour
        if 6 <= hour <= 8:  # 早晨
            daily_factor = 1.2
        elif 12 <= hour <= 14:  # 午间
            daily_factor = 1.4
        elif 18 <= hour <= 20:  # 晚间
            daily_factor = 1.1
        else:
            daily_factor = 0.9
        
        # 添加时间趋势（模拟治疗效果）
        day_num = i // 96
        if day_num <= 4:  # 前4天相对较好
            time_factor = 0.9
        elif day_num <= 8:  # 中期恶化
            time_factor = 1.3
        else:  # 后期轻微改善
            time_factor = 1.1
        
        # 生成血糖值
        glucose = base_glucose * daily_factor * time_factor + np.random.normal(0, 1.5)
        glucose = max(3.0, min(25.0, glucose))  # 限制在合理范围内
        glucose_values.append(round(glucose, 1))
    
    # 创建DataFrame
    df = pd.DataFrame({
        'timestamp': dates,
        'glucose_value': glucose_values
    })
    
    # 保存为CSV文件
    filename = "Demo_Glucose_Data.csv"
    df.to_csv(filename, index=False)
    print(f"✅ 演示血糖数据已生成: {filename}")
    return filename

def create_demo_medication_data():
    """创建演示用的药物数据"""
    medication_data = {
        "patient_id": "演示患者-001",
        "medication_input_date": "2025-08-27",
        "medications": [
            {
                "name": "二甲双胍片",
                "specification": "0.5g",
                "dosage": "1片",
                "frequency": "每日3次",
                "timing": "三餐前30分钟",
                "purpose": "基础降糖，改善胰岛素抵抗",
                "start_date": "2025-07-20",
                "compliance": "良好",
                "notes": "监测期间一直在使用，患者依从性好"
            },
            {
                "name": "达格列净片",
                "specification": "10mg",
                "dosage": "1片", 
                "frequency": "每日1次",
                "timing": "早餐前",
                "purpose": "SGLT-2抑制，促进葡萄糖排泄",
                "start_date": "2025-08-02",
                "compliance": "良好",
                "notes": "监测期中期加入，期望改善空腹血糖"
            },
            {
                "name": "西格列汀片",
                "specification": "100mg",
                "dosage": "1片",
                "frequency": "每日1次", 
                "timing": "早餐后",
                "purpose": "DPP-4抑制，改善餐后血糖",
                "start_date": "2025-08-06",
                "compliance": "良好",
                "notes": "监测后期加入，针对餐后高血糖"
            }
        ],
        "medication_history": {
            "treatment_timeline": [
                "2025-07-20: 开始二甲双胍单药治疗",
                "2025-08-02: 因空腹血糖控制不理想，加用达格列净",
                "2025-08-06: 因餐后血糖仍高，加用西格列汀",
                "2025-08-10: 三药联合治疗，通过Agent5分析效果"
            ],
            "treatment_rationale": "渐进式加药策略，期望通过多靶点治疗改善血糖控制"
        }
    }
    
    filename = "Demo_Medication_Data.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(medication_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 演示药物数据已生成: {filename}")
    return medication_data

def demonstrate_report_structure():
    """演示新的报告结构"""
    print("\n" + "="*80)
    print("Agent5 新报告结构演示")
    print("="*80)
    
    # 创建演示数据
    print("\n📊 创建演示数据...")
    glucose_file = create_demo_glucose_data()
    medication_data = create_demo_medication_data()
    
    # 创建分析器
    print("\n🔧 初始化Agent5分析器...")
    analyzer = ComprehensiveAGPAIAnalyzer()
    
    # 生成完整报告
    print("\n📋 生成完整分析报告...")
    try:
        report = analyzer.generate_complete_report(
            filepath=glucose_file,
            patient_id="演示患者-001",
            medication_data=medication_data
        )
        
        print("✅ 报告生成成功!")
        
        # 显示报告结构
        print("\n" + "="*80)
        print("📋 报告结构展示 (按新顺序)")
        print("="*80)
        
        structure_order = [
            ("报告头信息", "基本信息和版本"),
            ("专业术语与缩写说明", "🆕 第1位：英文缩写+中文+介绍"),
            ("患者用药信息分析", "🆕 第2位：药物信息及相关"),
            ("模块1_总体血糖控制状况和建议", "🆕 第3位：Agent1第一模块"),
            ("模块2_核心血糖控制指标分析", "第4位：Agent1第二模块"),
            ("模块3_六时段综合深度分析", "第5位：Agent1第三模块"),
            ("模块4_工作日周末对比分析", "第6位：Agent1第四模块"),
            ("模块5_异常模式检测与风险预警", "第7位：Agent1第五模块"),
            ("模块6_时间分段纵向分析", "第8位：Agent1第六模块"),
            ("模块7_智能时间分段分析", "第9位：Agent2智能分段"),
            ("模块8_药物-血糖整合分析", "第10位：药物-血糖整合"),
            ("专业94指标详细分析", "专业指标"),
            ("数据质量评估", "数据质量"),
            ("患者基本信息", "基本信息"),
            ("报告总结", "总结信息")
        ]
        
        for i, (key, description) in enumerate(structure_order, 1):
            if key in report:
                status = "✅ 存在"
                # 显示关键内容
                if key == "专业术语与缩写说明":
                    abbreviations = report[key]
                    print(f"{i:2d}. {key}: {status} - {description}")
                    print(f"    📖 包含 {len(abbreviations.get('核心血糖指标', {}))} 个核心血糖指标")
                    print(f"    💊 包含 {len(abbreviations.get('药物分类术语', {}))} 个药物分类")
                    print(f"    🔬 包含 {len(abbreviations.get('技术分析指标', {}))} 个技术指标")
                elif key == "患者用药信息分析":
                    med_analysis = report[key]
                    print(f"{i:2d}. {key}: {status} - {description}")
                    print(f"    💊 药物数量: {med_analysis.get('药物数量', 0)}")
                    print(f"    📋 分析状态: {med_analysis.get('分析状态', 'N/A')}")
                elif key == "模块1_总体血糖控制状况和建议":
                    module1 = report[key]
                    print(f"{i:2d}. {key}: {status} - {description}")
                    if module1 and "核心控制指标" in module1:
                        indicators = module1["核心控制指标"]
                        print(f"    📊 GMI: {indicators.get('GMI', 'N/A')}")
                        print(f"    🎯 TIR: {indicators.get('TIR标准范围', 'N/A')}")
                else:
                    print(f"{i:2d}. {key}: {status} - {description}")
            else:
                status = "❌ 缺失"
                print(f"{i:2d}. {key}: {status} - {description}")
        
        # 显示专业术语说明示例
        if "专业术语与缩写说明" in report:
            print("\n" + "="*50)
            print("🔍 专业术语说明示例")
            print("="*50)
            
            abbreviations = report["专业术语与缩写说明"]
            
            # 显示GMI说明
            if "核心血糖指标" in abbreviations and "GMI" in abbreviations["核心血糖指标"]:
                gmi_info = abbreviations["核心血糖指标"]["GMI"]
                print("📊 GMI (血糖管理指标):")
                print(f"   英文全称: {gmi_info['全称']}")
                print(f"   中文名称: {gmi_info['中文']}")
                print(f"   简要介绍: {gmi_info['简要介绍']}")
                print(f"   正常范围: {gmi_info['正常范围']}")
                print(f"   临床意义: {gmi_info['临床意义']}")
            
            # 显示药物分类示例
            if "药物分类术语" in abbreviations and "SGLT-2抑制剂" in abbreviations["药物分类术语"]:
                sglt2_info = abbreviations["药物分类术语"]["SGLT-2抑制剂"]
                print("\n💊 SGLT-2抑制剂:")
                print(f"   英文全称: {sglt2_info['全称']}")
                print(f"   中文名称: {sglt2_info['中文']}")
                print(f"   作用机制: {sglt2_info['简要介绍']}")
                print(f"   代表药物: {sglt2_info['代表药物']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
        return False

def main():
    """主函数"""
    print("Agent5 报告结构重新组织演示")
    print("="*80)
    print("新的报告结构:")
    print("1. 🆕 专业术语与缩写说明 (第一位)")
    print("2. 🆕 患者用药信息分析 (第二位)")  
    print("3. 🆕 Agent1第一模块 (第三位)")
    print("4-8. Agent1其他模块 (依次排列)")
    print("9. Agent2智能分段分析")
    print("10. 药物-血糖整合分析")
    print()
    
    success = demonstrate_report_structure()
    
    if success:
        print("\n🎉 Agent5 新报告结构演示成功!")
        print("\n📋 主要改进:")
        print("✅ 英文缩写+中文+介绍放在第一位，便于理解专业术语")
        print("✅ 用药信息放在第二位，突出药物治疗重要性")
        print("✅ Agent1第一模块放在第三位，展示总体控制状况")
        print("✅ 其他模块按逻辑顺序依次排列")
        print("\n💡 临床价值:")
        print("• 医生首先了解专业术语，便于解读报告")
        print("• 快速掌握患者用药情况")
        print("• 按重要性顺序展示分析结果")
        print("• 提升报告的可读性和实用性")
    else:
        print("\n❌ 演示失败，请检查错误信息")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)