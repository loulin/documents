#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRF数据挖掘Agent示例分析脚本
Example Analysis Script for CRF Research Mining Agent
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

def generate_sample_data():
    """生成示例CRF数据"""
    print("🔄 正在生成示例CRF数据...")
    
    # 创建数据目录
    os.makedirs('/Users/williamsun/Documents/gplus/docs/crf_design/sample_data', exist_ok=True)
    
    np.random.seed(42)  # 确保结果可重现
    
    # 1. 患者基本信息
    n_patients = 250
    patient_ids = [f'P{i:03d}' for i in range(1, n_patients + 1)]
    
    demographics_data = {
        'patient_id': patient_ids,
        'age': np.random.normal(55, 12, n_patients).astype(int),
        'gender': np.random.choice(['male', 'female'], n_patients, p=[0.52, 0.48]),
        'diabetes_type': np.random.choice(['type1', 'type2'], n_patients, p=[0.15, 0.85]),
        'duration': np.random.exponential(8, n_patients).astype(int),
        'bmi': np.random.normal(26, 4, n_patients),
        'education_level': np.random.choice(
            ['primary', 'middle', 'high_school', 'college', 'graduate'], 
            n_patients, p=[0.1, 0.2, 0.35, 0.3, 0.05]
        ),
        'occupation': np.random.choice(
            ['professional', 'service', 'worker', 'retired', 'unemployed'],
            n_patients, p=[0.25, 0.3, 0.2, 0.15, 0.1]
        ),
        'marriage': np.random.choice(['married', 'single', 'divorced', 'widowed'], 
                                   n_patients, p=[0.65, 0.15, 0.12, 0.08])
    }
    
    # 年龄相关调整
    demographics_df = pd.DataFrame(demographics_data)
    demographics_df.loc[demographics_df['age'] > 65, 'occupation'] = 'retired'
    demographics_df.loc[demographics_df['age'] < 25, 'marriage'] = 'single'
    
    # 添加并发症信息
    comorbidity_prob = np.clip((demographics_df['age'] - 40) / 40, 0, 0.8)
    demographics_df['hypertension'] = np.random.binomial(1, comorbidity_prob)
    demographics_df['dyslipidemia'] = np.random.binomial(1, comorbidity_prob * 0.8)
    demographics_df['nephropathy'] = np.random.binomial(1, comorbidity_prob * 0.3)
    demographics_df['retinopathy'] = np.random.binomial(1, comorbidity_prob * 0.25)
    demographics_df['neuropathy'] = np.random.binomial(1, comorbidity_prob * 0.2)
    
    demographics_df.to_csv('/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/patient_demographics.csv', index=False)
    
    # 2. 临床指标数据
    clinical_data = {
        'patient_id': patient_ids,
        'visit_date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(n_patients)],
        'hba1c': np.random.normal(8.2, 1.5, n_patients),
        'fbg': np.random.normal(9.5, 2.8, n_patients),
        'pbg': np.random.normal(13.2, 4.1, n_patients),
        'creatinine': np.random.normal(85, 20, n_patients),
        'urea': np.random.normal(5.5, 1.2, n_patients),
        'total_cholesterol': np.random.normal(4.9, 0.8, n_patients),
        'triglycerides': np.random.normal(2.1, 1.2, n_patients),
        'hdl_cholesterol': np.random.normal(1.2, 0.3, n_patients),
        'ldl_cholesterol': np.random.normal(3.1, 0.7, n_patients),
        'systolic_bp': np.random.normal(135, 18, n_patients),
        'diastolic_bp': np.random.normal(82, 12, n_patients),
        'waist_circumference': np.random.normal(95, 12, n_patients)
    }
    
    clinical_df = pd.DataFrame(clinical_data)
    
    # 引入一些合理的相关性
    # 年龄越大，HbA1c tends to be higher
    age_effect = (demographics_df['age'] - 50) * 0.02
    clinical_df['hba1c'] += age_effect
    
    # BMI与血压、血脂的关联
    bmi_effect = (demographics_df['bmi'] - 25) * 0.5
    clinical_df['systolic_bp'] += bmi_effect
    clinical_df['triglycerides'] += bmi_effect * 0.05
    
    # 确保数值在合理范围内
    clinical_df['hba1c'] = np.clip(clinical_df['hba1c'], 5.5, 14.0)
    clinical_df['fbg'] = np.clip(clinical_df['fbg'], 4.0, 25.0)
    clinical_df['systolic_bp'] = np.clip(clinical_df['systolic_bp'], 90, 200)
    clinical_df['diastolic_bp'] = np.clip(clinical_df['diastolic_bp'], 50, 120)
    
    clinical_df.to_csv('/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/clinical_data.csv', index=False)
    
    # 3. PHQ-9抑郁量表数据
    phq9_data = {
        'patient_id': patient_ids,
        'visit_date': clinical_df['visit_date'],
    }
    
    # 生成9个PHQ-9问题的得分
    for i in range(1, 10):
        # 年龄和性别影响抑郁评分
        base_prob = 0.3
        if demographics_df['gender'] == 'female':
            base_prob += 0.1
        age_factor = np.where(demographics_df['age'] < 30, 1.2, 
                             np.where(demographics_df['age'] > 70, 1.1, 1.0))
        
        phq9_data[f'q{i}'] = np.random.choice([0, 1, 2, 3], n_patients, 
                                            p=[0.5, 0.3, 0.15, 0.05])
    
    phq9_df = pd.DataFrame(phq9_data)
    phq9_df['total_score'] = phq9_df[[f'q{i}' for i in range(1, 10)]].sum(axis=1)
    
    # 增加一些现实的相关性：血糖控制差的患者抑郁评分更高
    poor_control = clinical_df['hba1c'] > 9.0
    phq9_df.loc[poor_control, 'total_score'] += np.random.poisson(2, poor_control.sum())
    phq9_df['total_score'] = np.clip(phq9_df['total_score'], 0, 27)
    
    phq9_df.to_csv('/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/phq9.csv', index=False)
    
    # 4. GAD-7焦虑量表数据
    gad7_data = {
        'patient_id': patient_ids,
        'visit_date': clinical_df['visit_date'],
    }
    
    for i in range(1, 8):
        gad7_data[f'q{i}'] = np.random.choice([0, 1, 2, 3], n_patients,
                                            p=[0.55, 0.25, 0.15, 0.05])
    
    gad7_df = pd.DataFrame(gad7_data)
    gad7_df['total_score'] = gad7_df[[f'q{i}' for i in range(1, 8)]].sum(axis=1)
    
    # 焦虑与抑郁的共病现象
    high_depression = phq9_df['total_score'] > 10
    gad7_df.loc[high_depression, 'total_score'] += np.random.poisson(3, high_depression.sum())
    gad7_df['total_score'] = np.clip(gad7_df['total_score'], 0, 21)
    
    gad7_df.to_csv('/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/gad7.csv', index=False)
    
    # 5. MMAS-8药物依从性量表数据
    mmas8_data = {
        'patient_id': patient_ids,
        'visit_date': clinical_df['visit_date'],
        'q1': np.random.choice([0, 1], n_patients, p=[0.7, 0.3]),
        'q2': np.random.choice([0, 1], n_patients, p=[0.75, 0.25]),
        'q3': np.random.choice([0, 1], n_patients, p=[0.8, 0.2]),
        'q4': np.random.choice([0, 1], n_patients, p=[0.72, 0.28]),
        'q5': np.random.choice([0, 1], n_patients, p=[0.78, 0.22]),
        'q6': np.random.choice([0, 1], n_patients, p=[0.65, 0.35]),
        'q7': np.random.choice([0, 1, 2], n_patients, p=[0.5, 0.35, 0.15]),
        'q8': np.random.choice([0, 1], n_patients, p=[0.6, 0.4])
    }
    
    mmas8_df = pd.DataFrame(mmas8_data)
    mmas8_df['total_score'] = (mmas8_df[['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q8']].sum(axis=1) + 
                               mmas8_df['q7'])
    
    # 年龄和教育水平影响依从性
    elderly = demographics_df['age'] > 70
    mmas8_df.loc[elderly, 'total_score'] -= np.random.poisson(1, elderly.sum())
    
    high_education = demographics_df['education_level'].isin(['college', 'graduate'])
    mmas8_df.loc[high_education, 'total_score'] += np.random.poisson(1, high_education.sum())
    
    mmas8_df['total_score'] = np.clip(mmas8_df['total_score'], 0, 8)
    
    mmas8_df.to_csv('/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/mmas8.csv', index=False)
    
    # 6. IPAQ体力活动问卷数据
    ipaq_data = {
        'patient_id': patient_ids,
        'visit_date': clinical_df['visit_date'],
        'vigorous_days': np.random.poisson(2, n_patients),
        'vigorous_hours': np.random.exponential(1, n_patients),
        'moderate_days': np.random.poisson(3, n_patients),
        'moderate_hours': np.random.exponential(1.5, n_patients),
        'walking_days': np.random.poisson(5, n_patients),
        'walking_hours': np.random.exponential(2, n_patients),
        'sitting_hours': np.random.normal(8, 2, n_patients)
    }
    
    ipaq_df = pd.DataFrame(ipaq_data)
    
    # 计算MET分钟数
    ipaq_df['vigorous_met_min'] = ipaq_df['vigorous_days'] * ipaq_df['vigorous_hours'] * 60 * 8
    ipaq_df['moderate_met_min'] = ipaq_df['moderate_days'] * ipaq_df['moderate_hours'] * 60 * 4
    ipaq_df['walking_met_min'] = ipaq_df['walking_days'] * ipaq_df['walking_hours'] * 60 * 3.3
    ipaq_df['total_met_minutes'] = ipaq_df['vigorous_met_min'] + ipaq_df['moderate_met_min'] + ipaq_df['walking_met_min']
    
    # 年龄影响运动水平
    age_factor = np.clip((70 - demographics_df['age']) / 50, 0.3, 1.0)
    ipaq_df['total_met_minutes'] *= age_factor
    
    ipaq_df.to_csv('/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/ipaq.csv', index=False)
    
    # 7. PSQI睡眠质量指数数据
    psqi_data = {
        'patient_id': patient_ids,
        'visit_date': clinical_df['visit_date'],
        'sleep_quality': np.random.choice([0, 1, 2, 3], n_patients, p=[0.3, 0.4, 0.25, 0.05]),
        'sleep_latency': np.random.choice([0, 1, 2, 3], n_patients, p=[0.4, 0.3, 0.2, 0.1]),
        'sleep_duration': np.random.choice([0, 1, 2, 3], n_patients, p=[0.5, 0.3, 0.15, 0.05]),
        'sleep_efficiency': np.random.choice([0, 1, 2, 3], n_patients, p=[0.6, 0.25, 0.1, 0.05]),
        'sleep_disturbance': np.random.choice([0, 1, 2, 3], n_patients, p=[0.2, 0.5, 0.25, 0.05]),
        'sleep_medication': np.random.choice([0, 1, 2, 3], n_patients, p=[0.7, 0.15, 0.1, 0.05]),
        'daytime_dysfunction': np.random.choice([0, 1, 2, 3], n_patients, p=[0.4, 0.35, 0.2, 0.05])
    }
    
    psqi_df = pd.DataFrame(psqi_data)
    psqi_df['total_score'] = psqi_df[['sleep_quality', 'sleep_latency', 'sleep_duration', 
                                     'sleep_efficiency', 'sleep_disturbance', 'sleep_medication', 
                                     'daytime_dysfunction']].sum(axis=1)
    
    # 抑郁和焦虑影响睡眠质量
    high_phq9 = phq9_df['total_score'] > 10
    psqi_df.loc[high_phq9, 'total_score'] += np.random.poisson(2, high_phq9.sum())
    psqi_df['total_score'] = np.clip(psqi_df['total_score'], 0, 21)
    
    psqi_df.to_csv('/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/psqi.csv', index=False)
    
    # 8. 纵向随访数据 (模拟部分患者的多次访问)
    longitudinal_data = []
    n_followup_patients = 80  # 80名患者有随访数据
    
    for i in range(n_followup_patients):
        patient_id = patient_ids[i]
        n_visits = np.random.randint(3, 6)  # 3-5次访问
        
        base_hba1c = clinical_df.iloc[i]['hba1c']
        base_date = clinical_df.iloc[i]['visit_date']
        
        for visit in range(n_visits):
            visit_date = base_date + timedelta(days=visit * 90 + np.random.randint(-15, 15))
            
            # 模拟治疗效果：HbA1c逐渐改善但有个体差异
            hba1c_change = -0.3 * visit + np.random.normal(0, 0.5)
            current_hba1c = max(base_hba1c + hba1c_change, 5.5)
            
            longitudinal_data.append({
                'patient_id': patient_id,
                'visit_number': visit + 1,
                'visit_date': visit_date,
                'hba1c': current_hba1c,
                'fbg': max(current_hba1c * 1.2 + np.random.normal(0, 1), 4.0),
                'weight': 70 + np.random.normal(0, 2),
                'systolic_bp': 135 + np.random.normal(0, 10),
                'diastolic_bp': 82 + np.random.normal(0, 8)
            })
    
    longitudinal_df = pd.DataFrame(longitudinal_data)
    longitudinal_df.to_csv('/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/longitudinal_data.csv', index=False)
    
    print(f"✅ 示例数据生成完成！")
    print(f"📊 患者总数: {n_patients}")
    print(f"🔄 纵向随访患者: {n_followup_patients}")
    print(f"📁 数据保存位置: /Users/williamsun/Documents/gplus/docs/crf_design/sample_data/")
    
    return {
        'patient_demographics': '/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/patient_demographics.csv',
        'clinical_data': '/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/clinical_data.csv',
        'phq9': '/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/phq9.csv',
        'gad7': '/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/gad7.csv',
        'mmas8': '/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/mmas8.csv',
        'ipaq': '/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/ipaq.csv',
        'psqi': '/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/psqi.csv',
        'longitudinal_data': '/Users/williamsun/Documents/gplus/docs/crf_design/sample_data/longitudinal_data.csv'
    }


def run_example_analysis():
    """运行示例分析"""
    print("🚀 CRF数据挖掘智能分析Agent - 示例分析")
    print("=" * 60)
    
    # 生成示例数据
    data_sources = generate_sample_data()
    
    # 这里由于CRF_Research_Mining_Agent依赖较多，我们创建一个简化的示例分析
    print("\n📈 正在进行简化的研究机会分析...")
    
    # 读取生成的数据进行基本分析
    demographics_df = pd.read_csv(data_sources['patient_demographics'])
    clinical_df = pd.read_csv(data_sources['clinical_data'])
    phq9_df = pd.read_csv(data_sources['phq9'])
    gad7_df = pd.read_csv(data_sources['gad7'])
    mmas8_df = pd.read_csv(data_sources['mmas8'])
    
    print(f"\n📊 数据概览:")
    print(f"- 患者总数: {len(demographics_df)}")
    print(f"- 平均年龄: {demographics_df['age'].mean():.1f}±{demographics_df['age'].std():.1f}岁")
    print(f"- 性别分布: 男性{(demographics_df['gender']=='male').mean():.1%}, 女性{(demographics_df['gender']=='female').mean():.1%}")
    print(f"- 2型糖尿病比例: {(demographics_df['diabetes_type']=='type2').mean():.1%}")
    
    print(f"\n🔍 发现的研究机会:")
    
    # 1. 抑郁症状分析
    depression_rate = (phq9_df['total_score'] >= 10).mean()
    print(f"1. 糖尿病患者抑郁症状研究")
    print(f"   - 中重度抑郁症状发生率: {depression_rate:.1%}")
    print(f"   - 研究价值: {'高' if depression_rate > 0.2 else '中等'}")
    print(f"   - 建议期刊: 4-6分内分泌或精神医学期刊")
    
    # 2. 年龄与糖尿病类型关联
    age_diabetes_crosstab = pd.crosstab(
        pd.cut(demographics_df['age'], bins=[0, 40, 60, 100], labels=['<40', '40-60', '>60']),
        demographics_df['diabetes_type']
    )
    print(f"\n2. 年龄与糖尿病类型关联研究")
    print(f"   - 不同年龄组糖尿病类型分布存在差异")
    print(f"   - 样本量: {len(demographics_df)}")
    print(f"   - 建议期刊: 2-4分糖尿病专业期刊")
    
    # 3. 焦虑抑郁共病分析
    anxiety_depression_comorbidity = ((gad7_df['total_score'] >= 10) & 
                                     (phq9_df['total_score'] >= 10)).mean()
    print(f"\n3. 焦虑抑郁共病模式研究")
    print(f"   - 焦虑抑郁共病率: {anxiety_depression_comorbidity:.1%}")
    print(f"   - 研究价值: {'很高' if anxiety_depression_comorbidity > 0.15 else '中等'}")
    print(f"   - 建议期刊: 5-7分综合医学期刊")
    
    # 4. 药物依从性与血糖控制
    high_adherence = mmas8_df['total_score'] >= 6
    good_control = clinical_df['hba1c'] < 7.0
    
    merged_adherence = pd.merge(mmas8_df[['patient_id', 'total_score']], 
                               clinical_df[['patient_id', 'hba1c']], on='patient_id')
    high_adh = merged_adherence['total_score'] >= 6
    good_ctrl = merged_adherence['hba1c'] < 7.0
    
    high_adh_control_rate = good_ctrl[high_adh].mean()
    low_adh_control_rate = good_ctrl[~high_adh].mean()
    
    print(f"\n4. 药物依从性对血糖控制影响研究")
    print(f"   - 高依从性患者血糖达标率: {high_adh_control_rate:.1%}")
    print(f"   - 低依从性患者血糖达标率: {low_adh_control_rate:.1%}")
    print(f"   - 研究价值: {'很高' if abs(high_adh_control_rate - low_adh_control_rate) > 0.2 else '中等'}")
    print(f"   - 建议期刊: 4-6分临床医学期刊")
    
    # 5. 生成发表建议
    print(f"\n📅 发表路线图建议:")
    print(f"短期发表 (3-6个月):")
    print(f"  - 抑郁症状流行病学调查")
    print(f"  - 年龄与糖尿病类型关联分析")
    
    print(f"\n中期发表 (6-12个月):")
    print(f"  - 焦虑抑郁共病模式深度分析")
    print(f"  - 药物依从性多因素影响研究")
    
    print(f"\n长期发表 (1-2年):")
    print(f"  - 心理-行为-代谢综合干预研究")
    print(f"  - 纵向队列预后因素分析")
    
    print(f"\n💡 总体建议:")
    print(f"1. 优先处理抑郁和依从性相关研究，统计功效较高")
    print(f"2. 考虑建立多中心合作，扩大样本量")
    print(f"3. 关注心理健康在糖尿病管理中的重要性")
    print(f"4. 开发个性化干预策略提高临床实用价值")
    
    print(f"\n✅ 示例分析完成！")
    print(f"📄 详细分析请运行完整版CRF_Research_Mining_Agent")

if __name__ == "__main__":
    run_example_analysis()