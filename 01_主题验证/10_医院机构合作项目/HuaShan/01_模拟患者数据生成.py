"""
胰腺癌患者血糖脆性虚拟数据生成脚本
作者: 医学AI团队
日期: 2025-10-07
用途: 生成术前/术中/术后不同阶段的模拟患者数据，用于测试血糖脆性分型与预测模型
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# 设置随机种子以便复现
np.random.seed(42)


class PancreaticCancerPatientSimulator:
    """胰腺癌患者数据模拟器"""

    def __init__(self, n_patients=50):
        self.n_patients = n_patients
        self.patient_ids = [f"PC{str(i+1).zfill(4)}" for i in range(n_patients)]

    def generate_basic_info(self):
        """生成基本信息"""
        data = {
            'patient_id': self.patient_ids,
            'assessment_date': [datetime.now() - timedelta(days=np.random.randint(0, 180))
                               for _ in range(self.n_patients)],
            'assessor_name': np.random.choice(['张医生', '李医生', '王医生', '刘医生'], self.n_patients),
            'age': np.random.randint(45, 80, self.n_patients),
            'gender': np.random.choice(['男', '女'], self.n_patients),
        }
        return data

    def generate_diabetes_baseline(self):
        """生成糖尿病基线特征"""
        # 定义三种脆性类型的患者比例
        brittleness_types = np.random.choice(['低脆性', '中脆性', '高脆性'],
                                             self.n_patients,
                                             p=[0.3, 0.4, 0.3])

        data = {
            'brittleness_type': brittleness_types,
            'diabetes_type_detailed': [],
            'diabetes_duration_years': [],
            'diabetes_treatment_preop': [],
            'insulin_dose_preop': [],
            'severe_hypo_history': [],
            'dka_hhs_history': []
        }

        for bt in brittleness_types:
            if bt == '低脆性':
                data['diabetes_type_detailed'].append(np.random.choice([1, 2], p=[0.1, 0.9]))
                data['diabetes_duration_years'].append(np.random.randint(0, 5))
                data['diabetes_treatment_preop'].append(json.dumps(['口服药']))
                data['insulin_dose_preop'].append(0 if np.random.random() > 0.3 else np.random.uniform(10, 20))
                data['severe_hypo_history'].append(0)
                data['dka_hhs_history'].append(0)
            elif bt == '中脆性':
                data['diabetes_type_detailed'].append(2)
                data['diabetes_duration_years'].append(np.random.randint(5, 12))
                treatment_choice = np.random.choice(['口服药+胰岛素', '胰岛素'], p=[0.6, 0.4])
                data['diabetes_treatment_preop'].append(
                    json.dumps(treatment_choice.split('+'))
                )
                data['insulin_dose_preop'].append(np.random.uniform(20, 40))
                data['severe_hypo_history'].append(np.random.choice([0, 1], p=[0.7, 0.3]))
                data['dka_hhs_history'].append(0)
            else:  # 高脆性
                data['diabetes_type_detailed'].append(np.random.choice([1, 2], p=[0.4, 0.6]))
                data['diabetes_duration_years'].append(np.random.randint(10, 25))
                treatment_choice = np.random.choice(['胰岛素', '胰岛素泵'], p=[0.7, 0.3])
                data['diabetes_treatment_preop'].append(
                    json.dumps([treatment_choice])
                )
                data['insulin_dose_preop'].append(np.random.uniform(40, 80))
                data['severe_hypo_history'].append(np.random.choice([0, 1], p=[0.4, 0.6]))
                data['dka_hhs_history'].append(np.random.choice([0, 1], p=[0.7, 0.3]))

        return data

    def generate_preop_glycemic_metrics(self, brittleness_types):
        """生成术前血糖指标（CGM数据）"""
        data = {
            'preop_hba1c': [],
            'preop_cgm_cv': [],
            'preop_cgm_tir': [],
            'preop_cgm_tar_level1': [],
            'preop_cgm_tar_level2': [],
            'preop_cgm_tbr_level1': [],
            'preop_cgm_tbr_level2': [],
            'preop_cgm_mage': [],
            'preop_cgm_gmi': []
        }

        for bt in brittleness_types:
            if bt == '低脆性':
                data['preop_hba1c'].append(round(np.random.uniform(5.5, 6.5), 2))
                data['preop_cgm_cv'].append(round(np.random.uniform(20, 30), 2))
                data['preop_cgm_tir'].append(round(np.random.uniform(85, 95), 2))
                data['preop_cgm_tar_level1'].append(round(np.random.uniform(3, 10), 2))
                data['preop_cgm_tar_level2'].append(round(np.random.uniform(0, 3), 2))
                data['preop_cgm_tbr_level1'].append(round(np.random.uniform(1, 4), 2))
                data['preop_cgm_tbr_level2'].append(round(np.random.uniform(0, 1), 2))
                data['preop_cgm_mage'].append(round(np.random.uniform(1.5, 2.5), 2))
                data['preop_cgm_gmi'].append(round(np.random.uniform(5.8, 6.5), 2))
            elif bt == '中脆性':
                data['preop_hba1c'].append(round(np.random.uniform(6.5, 8.0), 2))
                data['preop_cgm_cv'].append(round(np.random.uniform(30, 40), 2))
                data['preop_cgm_tir'].append(round(np.random.uniform(60, 75), 2))
                data['preop_cgm_tar_level1'].append(round(np.random.uniform(15, 25), 2))
                data['preop_cgm_tar_level2'].append(round(np.random.uniform(3, 8), 2))
                data['preop_cgm_tbr_level1'].append(round(np.random.uniform(3, 7), 2))
                data['preop_cgm_tbr_level2'].append(round(np.random.uniform(1, 3), 2))
                data['preop_cgm_mage'].append(round(np.random.uniform(3.0, 4.5), 2))
                data['preop_cgm_gmi'].append(round(np.random.uniform(6.8, 7.8), 2))
            else:  # 高脆性
                data['preop_hba1c'].append(round(np.random.uniform(8.0, 10.5), 2))
                data['preop_cgm_cv'].append(round(np.random.uniform(40, 55), 2))
                data['preop_cgm_tir'].append(round(np.random.uniform(30, 55), 2))
                data['preop_cgm_tar_level1'].append(round(np.random.uniform(20, 35), 2))
                data['preop_cgm_tar_level2'].append(round(np.random.uniform(10, 20), 2))
                data['preop_cgm_tbr_level1'].append(round(np.random.uniform(5, 12), 2))
                data['preop_cgm_tbr_level2'].append(round(np.random.uniform(2, 6), 2))
                data['preop_cgm_mage'].append(round(np.random.uniform(4.8, 7.0), 2))
                data['preop_cgm_gmi'].append(round(np.random.uniform(8.2, 10.0), 2))

        return data

    def generate_tumor_characteristics(self):
        """生成肿瘤特征"""
        data = {
            'tumor_type_detailed': np.random.choice(
                ['胰腺导管腺癌', '神经内分泌肿瘤', '囊性肿瘤'],
                self.n_patients,
                p=[0.75, 0.15, 0.1]
            ),
            'tumor_stage': np.random.choice(
                ['IIA', 'IIB', 'III', 'IV'],
                self.n_patients,
                p=[0.25, 0.30, 0.30, 0.15]
            ),
            'tumor_location_invasion': np.random.choice(
                ['胰头部', '胰体尾部', '胰头伴血管侵犯'],
                self.n_patients,
                p=[0.5, 0.3, 0.2]
            ),
            'ca199_level': np.random.lognormal(4, 1.5, self.n_patients),
            'cea_level': np.random.lognormal(1.5, 0.8, self.n_patients),
        }
        return data

    def generate_surgery_info(self, brittleness_types):
        """生成手术信息"""
        data = {
            'surgery_type': [],
            'operation_duration_min': [],
            'anesthesia_type': [],
            'intraop_fluid_volume': [],
            'intraop_blood_loss': [],
            'intraop_complications': [],
            'intraop_insulin_infusion_rate': [],
            'pancreatojejunostomy_type': []
        }

        for bt in brittleness_types:
            surgery = np.random.choice(
                ['胰十二指肠切除', '远端胰腺切除', '全胰切除', '姑息性手术'],
                p=[0.5, 0.3, 0.1, 0.1]
            )
            data['surgery_type'].append(surgery)
            data['operation_duration_min'].append(np.random.randint(240, 480))
            data['anesthesia_type'].append('全身麻醉')
            data['intraop_fluid_volume'].append(np.random.randint(2000, 5000))
            data['intraop_blood_loss'].append(np.random.randint(200, 1500))

            # 并发症根据脆性类型有不同概率
            if bt == '高脆性':
                complication = np.random.choice(
                    ['无', '术中出血', '血压不稳', '血糖波动'],
                    p=[0.4, 0.2, 0.2, 0.2]
                )
            else:
                complication = np.random.choice(['无', '术中出血'], p=[0.8, 0.2])
            data['intraop_complications'].append(complication)

            # 术中胰岛素用量
            if bt == '低脆性':
                data['intraop_insulin_infusion_rate'].append(round(np.random.uniform(0, 2), 2))
            elif bt == '中脆性':
                data['intraop_insulin_infusion_rate'].append(round(np.random.uniform(2, 5), 2))
            else:
                data['intraop_insulin_infusion_rate'].append(round(np.random.uniform(5, 10), 2))

            if surgery in ['胰十二指肠切除', '全胰切除']:
                data['pancreatojejunostomy_type'].append(
                    np.random.choice(['端侧吻合', '端端吻合'])
                )
            else:
                data['pancreatojejunostomy_type'].append('不适用')

        return data

    def generate_intraop_glycemic_metrics(self, brittleness_types):
        """生成术中血糖指标"""
        data = {
            'intraop_cgm_cv': [],
            'intraop_cgm_mean_glucose': [],
            'intraop_glucose_range': [],
            'intraop_hypo_episodes': [],
            'intraop_severe_hypo_episodes': []
        }

        for bt in brittleness_types:
            if bt == '低脆性':
                data['intraop_cgm_cv'].append(round(np.random.uniform(15, 25), 2))
                data['intraop_cgm_mean_glucose'].append(round(np.random.uniform(6.5, 8.5), 2))
                data['intraop_glucose_range'].append(round(np.random.uniform(2, 4), 2))
                data['intraop_hypo_episodes'].append(0)
                data['intraop_severe_hypo_episodes'].append(0)
            elif bt == '中脆性':
                data['intraop_cgm_cv'].append(round(np.random.uniform(25, 35), 2))
                data['intraop_cgm_mean_glucose'].append(round(np.random.uniform(7.5, 10.5), 2))
                data['intraop_glucose_range'].append(round(np.random.uniform(4, 7), 2))
                data['intraop_hypo_episodes'].append(np.random.randint(0, 2))
                data['intraop_severe_hypo_episodes'].append(0)
            else:
                data['intraop_cgm_cv'].append(round(np.random.uniform(35, 50), 2))
                data['intraop_cgm_mean_glucose'].append(round(np.random.uniform(8.5, 13.5), 2))
                data['intraop_glucose_range'].append(round(np.random.uniform(7, 12), 2))
                data['intraop_hypo_episodes'].append(np.random.randint(1, 4))
                data['intraop_severe_hypo_episodes'].append(np.random.randint(0, 2))

        return data

    def generate_postop_complications(self, brittleness_types):
        """生成术后并发症"""
        data = {
            'postop_pancreatic_fistula_grade': [],
            'dge_occurrence': [],
            'postop_bleeding_occurrence': [],
            'postop_infection_type': []
        }

        for bt in brittleness_types:
            # 高脆性患者更容易出现并发症
            if bt == '高脆性':
                fistula = np.random.choice(['无', 'A', 'B', 'C'], p=[0.3, 0.3, 0.3, 0.1])
                dge = np.random.choice([0, 1], p=[0.5, 0.5])
                bleeding = np.random.choice([0, 1], p=[0.7, 0.3])
                infection = np.random.choice(['无', '切口感染', '腹腔感染', '肺部感染'],
                                            p=[0.4, 0.2, 0.2, 0.2])
            elif bt == '中脆性':
                fistula = np.random.choice(['无', 'A', 'B'], p=[0.5, 0.3, 0.2])
                dge = np.random.choice([0, 1], p=[0.7, 0.3])
                bleeding = np.random.choice([0, 1], p=[0.85, 0.15])
                infection = np.random.choice(['无', '切口感染'], p=[0.7, 0.3])
            else:
                fistula = np.random.choice(['无', 'A'], p=[0.8, 0.2])
                dge = np.random.choice([0, 1], p=[0.9, 0.1])
                bleeding = 0
                infection = np.random.choice(['无', '切口感染'], p=[0.9, 0.1])

            data['postop_pancreatic_fistula_grade'].append(fistula)
            data['dge_occurrence'].append(dge)
            data['postop_bleeding_occurrence'].append(bleeding)
            data['postop_infection_type'].append(infection)

        return data

    def generate_postop_glycemic_metrics(self, brittleness_types):
        """生成术后不同时间点的血糖指标"""
        # 术后72小时
        data_72h = self._generate_postop_period_metrics(brittleness_types, '72h',
                                                         deterioration_factor=1.3)
        # 术后2周
        data_2w = self._generate_postop_period_metrics(brittleness_types, '2w',
                                                        deterioration_factor=1.1)
        # 术后3月
        data_3m = self._generate_postop_period_metrics(brittleness_types, '3m',
                                                        deterioration_factor=0.95)

        # 合并所有时间点数据
        all_data = {**data_72h, **data_2w, **data_3m}

        # 添加术后HbA1c
        all_data['postop_hba1c_3m'] = []
        for bt in brittleness_types:
            if bt == '低脆性':
                all_data['postop_hba1c_3m'].append(round(np.random.uniform(6.0, 7.0), 2))
            elif bt == '中脆性':
                all_data['postop_hba1c_3m'].append(round(np.random.uniform(7.0, 8.5), 2))
            else:
                all_data['postop_hba1c_3m'].append(round(np.random.uniform(8.5, 11.0), 2))

        return all_data

    def _generate_postop_period_metrics(self, brittleness_types, period, deterioration_factor):
        """生成特定术后时期的血糖指标"""
        data = {
            f'postop_cgm_cv_{period}': [],
            f'postop_cgm_tir_{period}': [],
            f'postop_cgm_tar_level1_{period}': [],
            f'postop_cgm_tar_level2_{period}': [],
            f'postop_cgm_tbr_level1_{period}': [],
            f'postop_cgm_tbr_level2_{period}': [],
        }

        if period in ['2w', '3m']:
            data[f'postop_cgm_mage_{period}'] = []
            data[f'postop_cgm_gmi_{period}'] = []

        for bt in brittleness_types:
            if bt == '低脆性':
                base_cv = np.random.uniform(25, 35)
                base_tir = np.random.uniform(75, 90)
            elif bt == '中脆性':
                base_cv = np.random.uniform(35, 45)
                base_tir = np.random.uniform(55, 70)
            else:
                base_cv = np.random.uniform(45, 60)
                base_tir = np.random.uniform(30, 50)

            # 应用恶化/恢复因子
            data[f'postop_cgm_cv_{period}'].append(
                round(base_cv * deterioration_factor, 2)
            )
            data[f'postop_cgm_tir_{period}'].append(
                round(base_tir / deterioration_factor, 2)
            )

            # 其他指标
            tar1 = round(np.random.uniform(10, 30), 2)
            tar2 = round(np.random.uniform(3, 15), 2)
            tbr1 = round(np.random.uniform(2, 10), 2)
            tbr2 = round(np.random.uniform(0, 5), 2)

            data[f'postop_cgm_tar_level1_{period}'].append(tar1)
            data[f'postop_cgm_tar_level2_{period}'].append(tar2)
            data[f'postop_cgm_tbr_level1_{period}'].append(tbr1)
            data[f'postop_cgm_tbr_level2_{period}'].append(tbr2)

            if period in ['2w', '3m']:
                if bt == '低脆性':
                    mage = round(np.random.uniform(2.0, 3.5), 2)
                    gmi = round(np.random.uniform(6.2, 7.2), 2)
                elif bt == '中脆性':
                    mage = round(np.random.uniform(3.5, 5.5), 2)
                    gmi = round(np.random.uniform(7.2, 8.5), 2)
                else:
                    mage = round(np.random.uniform(5.5, 8.0), 2)
                    gmi = round(np.random.uniform(8.5, 10.5), 2)

                data[f'postop_cgm_mage_{period}'].append(mage)
                data[f'postop_cgm_gmi_{period}'].append(gmi)

        return data

    def generate_future_brittleness_risk(self, brittleness_types, postop_complications):
        """生成未来脆性恶化风险预测"""
        data = {
            'future_brittleness_risk_3m': [],
            'future_brittleness_risk_score': []
        }

        for i, bt in enumerate(brittleness_types):
            # 基础风险
            if bt == '低脆性':
                base_risk = 0.15
            elif bt == '中脆性':
                base_risk = 0.45
            else:
                base_risk = 0.75

            # 并发症影响
            if postop_complications['postop_pancreatic_fistula_grade'][i] in ['B', 'C']:
                base_risk += 0.15
            if postop_complications['dge_occurrence'][i] == 1:
                base_risk += 0.10
            if postop_complications['postop_infection_type'][i] != '无':
                base_risk += 0.12

            # 限制在0-1之间
            base_risk = min(base_risk, 0.95)

            # 分类风险
            if base_risk < 0.3:
                risk_category = '低'
            elif base_risk < 0.6:
                risk_category = '中'
            else:
                risk_category = '高'

            data['future_brittleness_risk_3m'].append(risk_category)
            data['future_brittleness_risk_score'].append(round(base_risk, 3))

        return data

    def generate_complete_dataset(self):
        """生成完整的患者数据集"""
        print("开始生成虚拟患者数据...")

        # 基本信息
        print("  - 生成基本信息...")
        basic_info = self.generate_basic_info()
        df = pd.DataFrame(basic_info)

        # 糖尿病基线
        print("  - 生成糖尿病基线特征...")
        diabetes_baseline = self.generate_diabetes_baseline()
        for key, value in diabetes_baseline.items():
            df[key] = value

        # 术前血糖指标
        print("  - 生成术前血糖指标...")
        preop_glycemic = self.generate_preop_glycemic_metrics(df['brittleness_type'])
        for key, value in preop_glycemic.items():
            df[key] = value

        # 肿瘤特征
        print("  - 生成肿瘤特征...")
        tumor_chars = self.generate_tumor_characteristics()
        for key, value in tumor_chars.items():
            df[key] = value

        # 手术信息
        print("  - 生成手术信息...")
        surgery_info = self.generate_surgery_info(df['brittleness_type'])
        for key, value in surgery_info.items():
            df[key] = value

        # 术中血糖指标
        print("  - 生成术中血糖指标...")
        intraop_glycemic = self.generate_intraop_glycemic_metrics(df['brittleness_type'])
        for key, value in intraop_glycemic.items():
            df[key] = value

        # 术后并发症
        print("  - 生成术后并发症...")
        postop_complications = self.generate_postop_complications(df['brittleness_type'])
        for key, value in postop_complications.items():
            df[key] = value

        # 术后血糖指标
        print("  - 生成术后血糖指标...")
        postop_glycemic = self.generate_postop_glycemic_metrics(df['brittleness_type'])
        for key, value in postop_glycemic.items():
            df[key] = value

        # 未来风险预测
        print("  - 生成未来脆性风险预测...")
        future_risk = self.generate_future_brittleness_risk(
            df['brittleness_type'],
            postop_complications
        )
        for key, value in future_risk.items():
            df[key] = value

        print(f"✓ 成功生成 {self.n_patients} 例虚拟患者数据")
        return df


def main():
    """主函数"""
    print("=" * 60)
    print("胰腺癌患者血糖脆性虚拟数据生成工具")
    print("=" * 60)
    print()

    # 生成数据
    simulator = PancreaticCancerPatientSimulator(n_patients=50)
    df = simulator.generate_complete_dataset()

    # 保存数据
    output_file = '虚拟患者数据_术前术中术后.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ 数据已保存至: {output_file}")

    # 显示数据摘要
    print("\n" + "=" * 60)
    print("数据摘要")
    print("=" * 60)
    print(f"总患者数: {len(df)}")
    print(f"\n脆性类型分布:")
    print(df['brittleness_type'].value_counts())
    print(f"\n手术类型分布:")
    print(df['surgery_type'].value_counts())
    print(f"\n未来3个月脆性恶化风险分布:")
    print(df['future_brittleness_risk_3m'].value_counts())

    # 显示关键指标的统计
    print("\n术前/术后关键指标对比:")
    print(f"术前平均HbA1c: {df['preop_hba1c'].mean():.2f}%")
    print(f"术后3月平均HbA1c: {df['postop_hba1c_3m'].mean():.2f}%")
    print(f"术前平均TIR: {df['preop_cgm_tir'].mean():.1f}%")
    print(f"术后3月平均TIR: {df['postop_cgm_tir_3m'].mean():.1f}%")

    print("\n" + "=" * 60)
    print("数据生成完成！")
    print("=" * 60)

    return df


if __name__ == "__main__":
    df = main()
