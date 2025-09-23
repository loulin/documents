#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRF数据挖掘Agent完整测试脚本
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_data():
    """创建测试数据"""
    print("📊 正在创建测试数据...")
    
    # 创建测试数据目录
    test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
    os.makedirs(test_data_dir, exist_ok=True)
    
    np.random.seed(42)
    n_patients = 300  # 增加样本量到300
    
    # 患者基本信息 - 引入更多临床相关的关联性
    demographics_data = {
        'patient_id': [f'P{i:03d}' for i in range(1, n_patients + 1)],
        'age': np.random.normal(58, 15, n_patients).astype(int),  # 年龄范围更广
        'gender': np.random.choice(['male', 'female'], n_patients, p=[0.55, 0.45]),
        'diabetes_type': np.random.choice(['type1', 'type2'], n_patients, p=[0.12, 0.88]),  # 更现实的比例
        'duration': np.random.exponential(10, n_patients).astype(int),  # 病程更长
        'bmi': np.random.normal(28, 5, n_patients),  # BMI更高，更符合糖尿病患者特征
        'education_level': np.random.choice(['primary', 'middle', 'high_school', 'college', 'graduate'], 
                                          n_patients, p=[0.1, 0.2, 0.35, 0.3, 0.05])
    }
    
    demographics_df = pd.DataFrame(demographics_data)
    demographics_df['age'] = np.clip(demographics_df['age'], 18, 85)
    demographics_path = os.path.join(test_data_dir, 'patient_demographics.csv')
    demographics_df.to_csv(demographics_path, index=False)
    
    # 临床数据 - 引入更强的相关性和临床意义
    clinical_data = {
        'patient_id': demographics_df['patient_id'],
        'hba1c': np.random.normal(8.5, 2.0, n_patients),  # 更大的变异性
        'fbg': np.random.normal(10.2, 3.2, n_patients),
        'creatinine': np.random.normal(90, 25, n_patients),
        'total_cholesterol': np.random.normal(5.2, 1.1, n_patients),
        'triglycerides': np.random.normal(2.8, 1.8, n_patients),  # 更高的基线值
        'systolic_bp': np.random.normal(142, 22, n_patients),  # 更高的血压
        'diastolic_bp': np.random.normal(88, 15, n_patients)
    }
    
    clinical_df = pd.DataFrame(clinical_data)
    
    # 加入强烈的临床关联性
    # 年龄与HbA1c的关联 - 老年患者血糖控制更差
    age_effect_hba1c = np.where(demographics_df['age'] > 65, 
                                np.random.normal(1.2, 0.5, n_patients), 0)
    clinical_df['hba1c'] += age_effect_hba1c
    
    # 病程与并发症风险的关联
    duration_effect = np.where(demographics_df['duration'] > 10,
                              np.random.normal(0.8, 0.3, n_patients), 0)
    clinical_df['hba1c'] += duration_effect
    clinical_df['creatinine'] += duration_effect * 15  # 肾功能恶化
    
    # BMI与代谢指标的强关联
    bmi_effect = (demographics_df['bmi'] - 25) * 0.15
    clinical_df['hba1c'] += np.maximum(bmi_effect, 0)  # 只有正向效应
    clinical_df['systolic_bp'] += bmi_effect * 2
    clinical_df['triglycerides'] += bmi_effect * 0.3
    
    clinical_df['hba1c'] = np.clip(clinical_df['hba1c'], 5.5, 15.0)
    clinical_path = os.path.join(test_data_dir, 'clinical_data.csv')
    clinical_df.to_csv(clinical_path, index=False)
    
    # PHQ-9数据 (加入与HbA1c的关联性和一些数据质量问题)
    base_depression = np.random.poisson(4, n_patients)  # 基础抑郁评分
    
    # 强化HbA1c与抑郁的关联
    hba1c_effect = np.where(clinical_df['hba1c'] > 9.0, 
                           np.random.poisson(6, n_patients), 
                           np.random.poisson(1, n_patients))
    
    # 性别效应 - 女性抑郁症状更严重
    gender_effect = np.where(demographics_df['gender'] == 'female',
                            np.random.poisson(2, n_patients), 0)
    
    phq9_data = {
        'patient_id': demographics_df['patient_id'],
        'total_score': base_depression + hba1c_effect + gender_effect
    }
    phq9_df = pd.DataFrame(phq9_data)
    phq9_df['total_score'] = np.clip(phq9_df['total_score'], 0, 27)
    
    # 故意添加一些缺失值来测试数据质量检验
    missing_indices = np.random.choice(n_patients, size=int(n_patients * 0.05), replace=False)
    phq9_df.loc[missing_indices, 'total_score'] = np.nan
    
    # 添加一些异常高值作为异常值测试
    extreme_indices = np.random.choice(n_patients, size=int(n_patients * 0.02), replace=False)
    phq9_df.loc[extreme_indices, 'total_score'] = 25  # 异常高的抑郁评分
    
    phq9_path = os.path.join(test_data_dir, 'phq9.csv')
    phq9_df.to_csv(phq9_path, index=False)
    
    # GAD-7数据 (与PHQ-9有强烈共病关系)
    base_anxiety = np.random.poisson(3, n_patients)
    
    # 抑郁-焦虑共病效应 - 基于真实PHQ-9评分
    phq9_scores = phq9_df['total_score'].fillna(0)  # 处理缺失值
    depression_effect = np.where(phq9_scores > 10, 
                                np.random.poisson(5, n_patients), 
                                np.random.poisson(1, n_patients))
    
    # 年龄效应 - 年轻人焦虑更严重
    age_effect = np.where(demographics_df['age'] < 40,
                         np.random.poisson(2, n_patients), 0)
    
    gad7_data = {
        'patient_id': demographics_df['patient_id'],
        'total_score': base_anxiety + depression_effect + age_effect
    }
    gad7_df = pd.DataFrame(gad7_data)
    gad7_df['total_score'] = np.clip(gad7_df['total_score'], 0, 21)
    
    # 添加一些重复记录来测试重复检测
    duplicate_indices = np.random.choice(n_patients, size=int(n_patients * 0.03), replace=False)
    duplicate_rows = gad7_df.iloc[duplicate_indices].copy()
    gad7_df = pd.concat([gad7_df, duplicate_rows], ignore_index=True)
    
    gad7_path = os.path.join(test_data_dir, 'gad7.csv')
    gad7_df.to_csv(gad7_path, index=False)
    
    # MMAS-8数据 (药物依从性与多因素关联)
    base_adherence = np.random.binomial(8, 0.6, n_patients)  # 基础依从性较低
    
    # 教育水平对依从性的影响
    education_effect = np.where(demographics_df['education_level'].isin(['college', 'graduate']),
                               np.random.binomial(2, 0.8, n_patients), 0)
    
    # 年龄对依从性的影响 - 老年人依从性可能更好或更差
    age_effect = np.where(demographics_df['age'] > 70,
                         np.random.choice([-1, 1], n_patients) * np.random.binomial(1, 0.3, n_patients), 0)
    
    # 抑郁对依从性的负面影响
    depression_effect = np.where(phq9_scores > 15,
                                -np.random.binomial(2, 0.7, n_patients), 0)
    
    mmas8_data = {
        'patient_id': demographics_df['patient_id'],
        'total_score': base_adherence + education_effect + age_effect + depression_effect
    }
    mmas8_df = pd.DataFrame(mmas8_data)
    mmas8_df['total_score'] = np.clip(mmas8_df['total_score'], 0, 8)
    
    # 添加一些临床不合理值进行测试
    invalid_indices = np.random.choice(n_patients, size=int(n_patients * 0.01), replace=False)
    mmas8_df.loc[invalid_indices, 'total_score'] = -1  # 不合理的负值
    
    mmas8_path = os.path.join(test_data_dir, 'mmas8.csv')
    mmas8_df.to_csv(mmas8_path, index=False)
    
    print(f"✅ 测试数据已创建在 {test_data_dir}")
    
    return {
        'patient_demographics': demographics_path,
        'clinical_data': clinical_path,
        'phq9': phq9_path,
        'gad7': gad7_path,
        'mmas8': mmas8_path
    }

def test_agent():
    """测试Agent功能"""
    print("🚀 CRF数据挖掘智能分析Agent - 完整测试")
    print("=" * 60)
    
    try:
        # 1. 导入Agent
        from CRF_Research_Mining_Agent import CRFResearchMiningAgent
        print("✅ Agent导入成功")
        
        # 2. 初始化Agent
        agent = CRFResearchMiningAgent()
        print("✅ Agent初始化成功")
        
        # 3. 创建测试数据
        data_sources = create_test_data()
        
        # 4. 加载数据
        print("\n📊 正在加载数据...")
        datasets = agent.load_crf_data(data_sources)
        print(f"✅ 成功加载 {len(datasets)} 个数据集")
        
        # 5. 数据质量评估
        print("\n🔍 正在评估数据质量...")
        quality_report = agent.assess_data_quality()
        
        print("数据质量报告:")
        for dataset_name, metrics in quality_report.items():
            print(f"\n📊 {dataset_name}:")
            print(f"  - 记录数: {metrics['total_records']}")
            print(f"  - 特征数: {metrics['total_features']}")
            print(f"  - 缺失率: {metrics['missing_rate']:.1%}")
            print(f"  - 重复率: {metrics['duplicate_rate']:.1%}")
            print(f"  - 质量等级: {metrics['overall_grade']}")
            
            # 显示异常值信息
            if 'outlier_rates' in metrics:
                high_outlier_cols = [col for col, rate in metrics['outlier_rates'].items() if rate > 0.05]
                if high_outlier_cols:
                    print(f"  - 异常值较多字段: {', '.join(high_outlier_cols)}")
            
            # 显示质量问题
            if 'quality_issues' in metrics and metrics['quality_issues']:
                print(f"  - 主要问题: {'; '.join(metrics['quality_issues'][:2])}")
            
            # 显示清理建议
            if 'cleaning_recommendations' in metrics and metrics['cleaning_recommendations']:
                print(f"  - 清理建议: {metrics['cleaning_recommendations'][0]}")
        
        # 6. 发现研究机会
        print("\n💡 正在发现研究机会...")
        insights = agent.discover_research_opportunities()
        print(f"✅ 发现 {len(insights)} 个研究机会")
        
        # 显示前3个研究机会
        if insights:
            print("\n🎯 TOP 3 研究机会:")
            for i, insight in enumerate(insights[:3], 1):
                print(f"{i}. {insight.title}")
                print(f"   - 研究价值: {insight.value_level.value}")
                print(f"   - 统计功效: {insight.statistical_power:.2f}")
                print(f"   - 样本量: {insight.sample_size}")
                print(f"   - 期刊档次: {insight.expected_impact_factor}")
        
        # 7. 生成优先级矩阵
        print("\n📈 正在生成优先级矩阵...")
        priority_matrix = agent.generate_research_priority_matrix()
        if not priority_matrix.empty:
            print("优先级最高的3个研究:")
            for i, row in priority_matrix.head(3).iterrows():
                print(f"- {row['research_topic']} (优先级: {row['priority_score']:.2f})")
        
        # 8. 生成发表路线图
        print("\n📅 正在生成发表路线图...")
        roadmap = agent.generate_publication_roadmap()
        
        print("发表路线图:")
        for timeframe, projects in roadmap.items():
            print(f"- {timeframe}: {len(projects)}个项目")
        
        # 9. 生成综合报告
        print("\n📝 正在生成综合报告...")
        output_path = os.path.join(os.path.dirname(__file__), 'CRF_Test_Analysis_Report.md')
        report = agent.generate_comprehensive_report(output_path)
        
        print(f"✅ 报告已生成: {output_path}")
        
        # 10. 显示总结
        print("\n" + "=" * 60)
        print("✅ 测试完成！Agent功能正常")
        print(f"📊 处理数据: {sum(len(df) for df in datasets.values())}条记录")
        print(f"🔍 发现研究机会: {len(insights)}个")
        print(f"📄 生成报告: {len(report)}字符")
        print("🎯 所有核心功能工作正常")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    test_agent()

if __name__ == "__main__":
    main()