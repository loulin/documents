"""
胰腺癌患者血糖脆性虚拟数据生成脚本 - 完整版
作者: 医学AI团队
日期: 2025-10-07
版本: v2.0 (完整版 - 覆盖数据字典所有字段)
用途: 生成术前/术中/术后完整的模拟患者数据，包含所有临床特征
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# 设置随机种子以便复现
np.random.seed(42)


class CompletePancreaticCancerSimulator:
    """胰腺癌患者完整数据模拟器 - 覆盖数据字典全部字段"""

    def __init__(self, n_patients=100):
        self.n_patients = n_patients
        self.patient_ids = [f"PC{str(i+1).zfill(4)}" for i in range(n_patients)]

    def generate_basic_info(self):
        """生成基本信息"""
        data = {
            'patient_id': self.patient_ids,
            'assessment_date': [datetime.now() - timedelta(days=np.random.randint(0, 180))
                               for _ in range(self.n_patients)],
            'assessor_name': np.random.choice(['张医生', '李医生', '王医生', '刘医生', '陈医生'],
                                             self.n_patients),
        }
        return data

    def generate_diabetes_detailed(self):
        """生成详细的糖尿病相关特征"""
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
            'dka_hhs_history': [],
            'other_endocrine_diseases': [],
            'autoimmune_diseases': [],
            'chronic_infection_history': [],
            'concomitant_medications': [],
        }

        for bt in brittleness_types:
            if bt == '低脆性':
                data['diabetes_type_detailed'].append(np.random.choice([0, 2], p=[0.3, 0.7]))  # 30%无糖尿病
                data['diabetes_duration_years'].append(np.random.randint(0, 5))
                # 使用索引选择
                treatment_choice = np.random.choice([0, 1], p=[0.3, 0.7])
                treatment_opts = [[], ['口服药']]
                data['diabetes_treatment_preop'].append(
                    json.dumps(treatment_opts[treatment_choice])
                )
                data['insulin_dose_preop'].append(
                    0 if np.random.random() > 0.2 else round(np.random.uniform(8, 20), 2)
                )
                data['severe_hypo_history'].append(0)
                data['dka_hhs_history'].append(0)
                data['other_endocrine_diseases'].append(
                    np.random.choice(['无', '甲状腺功能减退'], p=[0.9, 0.1])
                )
                data['autoimmune_diseases'].append('无')
                data['chronic_infection_history'].append('无')
                data['concomitant_medications'].append(
                    np.random.choice(['无', '他汀类', 'ACEI/ARB'], p=[0.7, 0.2, 0.1])
                )

            elif bt == '中脆性':
                data['diabetes_type_detailed'].append(2)
                data['diabetes_duration_years'].append(np.random.randint(5, 12))
                treatment_choice = np.random.choice(['口服药+胰岛素', '胰岛素'], p=[0.6, 0.4])
                data['diabetes_treatment_preop'].append(json.dumps(treatment_choice.split('+')))
                data['insulin_dose_preop'].append(round(np.random.uniform(20, 45), 2))
                data['severe_hypo_history'].append(np.random.choice([0, 1], p=[0.7, 0.3]))
                data['dka_hhs_history'].append(np.random.choice([0, 1], p=[0.95, 0.05]))
                data['other_endocrine_diseases'].append(
                    np.random.choice(['无', '甲状腺功能减退', '甲状腺功能亢进'], p=[0.8, 0.15, 0.05])
                )
                data['autoimmune_diseases'].append(
                    np.random.choice(['无', '桥本甲状腺炎'], p=[0.9, 0.1])
                )
                data['chronic_infection_history'].append(
                    np.random.choice(['无', '慢性牙周炎'], p=[0.85, 0.15])
                )
                data['concomitant_medications'].append(
                    np.random.choice(['他汀类', '他汀类+ACEI', '多种'], p=[0.4, 0.4, 0.2])
                )

            else:  # 高脆性
                data['diabetes_type_detailed'].append(np.random.choice([1, 2], p=[0.3, 0.7]))
                data['diabetes_duration_years'].append(np.random.randint(10, 30))
                treatment_choice = np.random.choice(['胰岛素', '胰岛素泵'], p=[0.7, 0.3])
                data['diabetes_treatment_preop'].append(json.dumps([treatment_choice]))
                data['insulin_dose_preop'].append(round(np.random.uniform(45, 90), 2))
                data['severe_hypo_history'].append(np.random.choice([0, 1], p=[0.3, 0.7]))
                data['dka_hhs_history'].append(np.random.choice([0, 1], p=[0.7, 0.3]))
                data['other_endocrine_diseases'].append(
                    np.random.choice(['无', '甲状腺疾病', '肾上腺功能不全'], p=[0.6, 0.3, 0.1])
                )
                data['autoimmune_diseases'].append(
                    np.random.choice(['无', '桥本甲状腺炎', '类风湿关节炎'], p=[0.7, 0.2, 0.1])
                )
                data['chronic_infection_history'].append(
                    np.random.choice(['无', '慢性牙周炎', '泌尿系感染'], p=[0.7, 0.2, 0.1])
                )
                data['concomitant_medications'].append('多种(他汀+降压+抗血小板)')

        return data

    def generate_psychosocial_factors(self, brittleness_types):
        """生成心理社会因素"""
        data = {
            'phq9_score': [],
            'gad7_score': [],
            'family_support': [],
            'smoking_status_detailed': [],
            'drinking_status_detailed': [],
            'ipaq_score': []
        }

        for bt in brittleness_types:
            if bt == '低脆性':
                data['phq9_score'].append(np.random.randint(0, 8))  # 无-轻度抑郁
                data['gad7_score'].append(np.random.randint(0, 7))  # 无-轻度焦虑
                data['family_support'].append(np.random.choice([1, 2], p=[0.7, 0.3]))  # 好/中
                data['smoking_status_detailed'].append(
                    np.random.choice([1, 2], p=[0.6, 0.4])  # 从不/已戒
                )
                data['drinking_status_detailed'].append(
                    np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2])  # 从不/已戒/偶尔
                )
                data['ipaq_score'].append(round(np.random.uniform(1200, 3000), 2))

            elif bt == '中脆性':
                data['phq9_score'].append(np.random.randint(5, 15))  # 轻-中度抑郁
                data['gad7_score'].append(np.random.randint(5, 12))  # 轻-中度焦虑
                data['family_support'].append(np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2]))
                data['smoking_status_detailed'].append(
                    np.random.choice([1, 2, 3, 4], p=[0.3, 0.4, 0.2, 0.1])
                )
                data['drinking_status_detailed'].append(
                    np.random.choice([1, 2, 3, 4], p=[0.3, 0.3, 0.3, 0.1])
                )
                data['ipaq_score'].append(round(np.random.uniform(600, 2000), 2))

            else:  # 高脆性
                data['phq9_score'].append(np.random.randint(10, 24))  # 中-重度抑郁
                data['gad7_score'].append(np.random.randint(10, 20))  # 中-重度焦虑
                data['family_support'].append(np.random.choice([2, 3], p=[0.4, 0.6]))  # 中/差
                data['smoking_status_detailed'].append(
                    np.random.choice([1, 2, 3, 4], p=[0.2, 0.3, 0.3, 0.2])
                )
                data['drinking_status_detailed'].append(
                    np.random.choice([1, 2, 3, 4], p=[0.2, 0.2, 0.3, 0.3])
                )
                data['ipaq_score'].append(round(np.random.uniform(200, 1200), 2))

        return data

    def generate_preop_glycemic_comprehensive(self, brittleness_types):
        """生成术前完整血糖指标"""
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
                hba1c = round(np.random.uniform(5.2, 6.5), 2)
                cv = round(np.random.uniform(18, 30), 2)
                tir = round(np.random.uniform(85, 98), 2)
                tar1 = round(np.random.uniform(1, 10), 2)
                tar2 = round(np.random.uniform(0, 2), 2)
                tbr1 = round(np.random.uniform(0.5, 4), 2)
                tbr2 = round(np.random.uniform(0, 0.5), 2)
                mage = round(np.random.uniform(1.2, 2.8), 2)
                gmi = round(np.random.uniform(5.5, 6.5), 2)

            elif bt == '中脆性':
                hba1c = round(np.random.uniform(6.5, 8.2), 2)
                cv = round(np.random.uniform(30, 42), 2)
                tir = round(np.random.uniform(58, 78), 2)
                tar1 = round(np.random.uniform(12, 28), 2)
                tar2 = round(np.random.uniform(3, 10), 2)
                tbr1 = round(np.random.uniform(3, 8), 2)
                tbr2 = round(np.random.uniform(0.5, 3), 2)
                mage = round(np.random.uniform(2.8, 5.0), 2)
                gmi = round(np.random.uniform(6.5, 8.0), 2)

            else:  # 高脆性
                hba1c = round(np.random.uniform(8.0, 11.5), 2)
                cv = round(np.random.uniform(40, 60), 2)
                tir = round(np.random.uniform(25, 58), 2)
                tar1 = round(np.random.uniform(20, 38), 2)
                tar2 = round(np.random.uniform(8, 25), 2)
                tbr1 = round(np.random.uniform(5, 15), 2)
                tbr2 = round(np.random.uniform(2, 8), 2)
                mage = round(np.random.uniform(4.8, 8.5), 2)
                gmi = round(np.random.uniform(8.0, 11.0), 2)

            data['preop_hba1c'].append(hba1c)
            data['preop_cgm_cv'].append(cv)
            data['preop_cgm_tir'].append(tir)
            data['preop_cgm_tar_level1'].append(tar1)
            data['preop_cgm_tar_level2'].append(tar2)
            data['preop_cgm_tbr_level1'].append(tbr1)
            data['preop_cgm_tbr_level2'].append(tbr2)
            data['preop_cgm_mage'].append(mage)
            data['preop_cgm_gmi'].append(gmi)

        return data

    def generate_tumor_comprehensive(self):
        """生成完整肿瘤特征"""
        data = {
            'tumor_type_detailed': [],
            'tumor_stage': [],
            'tumor_location_invasion': [],
            'ctdna_level': [],
            'ca199_level': [],
            'cea_level': []
        }

        for _ in range(self.n_patients):
            tumor_type = np.random.choice(
                ['胰腺导管腺癌', '神经内分泌肿瘤', '囊性肿瘤', '其他'],
                p=[0.75, 0.12, 0.08, 0.05]
            )
            data['tumor_type_detailed'].append(tumor_type)

            stage = np.random.choice(
                ['IA', 'IB', 'IIA', 'IIB', 'III', 'IV'],
                p=[0.05, 0.10, 0.20, 0.30, 0.25, 0.10]
            )
            data['tumor_stage'].append(stage)

            location = np.random.choice(
                ['胰头部', '胰体部', '胰尾部', '胰头伴血管侵犯', '全胰'],
                p=[0.5, 0.2, 0.15, 0.12, 0.03]
            )
            data['tumor_location_invasion'].append(location)

            # ctDNA水平
            data['ctdna_level'].append(round(np.random.lognormal(1.5, 1.2), 2))

            # CA19-9水平 (正常<37 U/mL)
            if tumor_type == '胰腺导管腺癌':
                ca199 = round(np.random.lognormal(5, 1.8), 2)  # 大多数升高
            else:
                ca199 = round(np.random.lognormal(3, 1.2), 2)
            data['ca199_level'].append(ca199)

            # CEA水平 (正常<5 ng/mL)
            data['cea_level'].append(round(np.random.lognormal(1.5, 0.9), 2))

        return data

    def generate_nutrition_comprehensive(self, brittleness_types):
        """生成完整营养评估指标"""
        data = {
            'prealbumin': [],
            'transferrin': [],
            'total_lymphocyte_count': [],
            'sga_score': [],
            'nrs2002_score': [],
            'handgrip_strength': [],
            'bmi': [],
            'weight_loss_6m': []
        }

        for bt in brittleness_types:
            # 营养状态与脆性相关
            if bt == '低脆性':
                # 营养状态较好
                data['prealbumin'].append(round(np.random.uniform(0.25, 0.35), 3))  # g/L
                data['transferrin'].append(round(np.random.uniform(2.2, 3.2), 2))
                data['total_lymphocyte_count'].append(round(np.random.uniform(1.5, 3.0), 2))
                data['sga_score'].append(np.random.choice([0, 1], p=[0.7, 0.3]))  # A-B
                data['nrs2002_score'].append(np.random.randint(0, 3))
                data['handgrip_strength'].append(round(np.random.uniform(28, 42), 1))
                data['bmi'].append(round(np.random.uniform(20, 27), 1))
                data['weight_loss_6m'].append(round(np.random.uniform(0, 5), 1))

            elif bt == '中脆性':
                data['prealbumin'].append(round(np.random.uniform(0.18, 0.28), 3))
                data['transferrin'].append(round(np.random.uniform(1.8, 2.5), 2))
                data['total_lymphocyte_count'].append(round(np.random.uniform(1.0, 2.0), 2))
                data['sga_score'].append(np.random.choice([1, 2], p=[0.6, 0.4]))  # B-C
                data['nrs2002_score'].append(np.random.randint(2, 5))
                data['handgrip_strength'].append(round(np.random.uniform(20, 32), 1))
                data['bmi'].append(round(np.random.uniform(18, 24), 1))
                data['weight_loss_6m'].append(round(np.random.uniform(3, 10), 1))

            else:  # 高脆性
                data['prealbumin'].append(round(np.random.uniform(0.12, 0.22), 3))
                data['transferrin'].append(round(np.random.uniform(1.2, 2.0), 2))
                data['total_lymphocyte_count'].append(round(np.random.uniform(0.6, 1.5), 2))
                data['sga_score'].append(np.random.choice([2, 3], p=[0.5, 0.5]))  # C
                data['nrs2002_score'].append(np.random.randint(4, 7))
                data['handgrip_strength'].append(round(np.random.uniform(12, 24), 1))
                data['bmi'].append(round(np.random.uniform(16, 21), 1))
                data['weight_loss_6m'].append(round(np.random.uniform(8, 20), 1))

        return data

    def generate_pancreatic_function(self, brittleness_types):
        """生成胰腺功能指标"""
        data = {
            'fecal_elastase1': [],
            'fat_excretion_72h': [],
            'amylase_level': [],
            'lipase_level': [],
            'pancreas_volume_ct_mri': [],
            'pancreas_parenchyma_hu': [],
            'pancreatic_duct_diameter': [],
            'tumor_pancreas_ratio': []
        }

        for bt in brittleness_types:
            # 胰腺外分泌功能
            if bt == '低脆性':
                elastase = np.random.randint(350, 550)
                fat_exc = round(np.random.uniform(2, 5), 1)
            elif bt == '中脆性':
                elastase = np.random.randint(180, 380)
                fat_exc = round(np.random.uniform(4, 9), 1)
            else:
                elastase = np.random.randint(50, 200)
                fat_exc = round(np.random.uniform(8, 18), 1)

            data['fecal_elastase1'].append(elastase)
            data['fat_excretion_72h'].append(fat_exc)

            # 血清酶
            data['amylase_level'].append(round(np.random.uniform(30, 150), 1))
            data['lipase_level'].append(round(np.random.uniform(20, 180), 1))

            # 影像学
            data['pancreas_volume_ct_mri'].append(round(np.random.uniform(40, 85), 1))
            data['pancreas_parenchyma_hu'].append(np.random.randint(30, 55))
            data['pancreatic_duct_diameter'].append(round(np.random.uniform(1.5, 6.0), 1))
            data['tumor_pancreas_ratio'].append(round(np.random.uniform(0.05, 0.45), 2))

        return data

    def generate_islet_function(self, brittleness_types):
        """生成胰岛功能评估"""
        data = {
            'ogtt_ivggt_results': [],
            'proinsulin_level': [],
            'insulin_secretion_index': [],
            'glucagon_level': []
        }

        for bt in brittleness_types:
            # OGTT/IVGTT结果(JSON格式)
            if bt == '低脆性':
                ogtt = {
                    '0min': round(np.random.uniform(5.0, 6.5), 1),
                    '30min': round(np.random.uniform(8.0, 10.5), 1),
                    '60min': round(np.random.uniform(7.5, 9.5), 1),
                    '120min': round(np.random.uniform(6.0, 8.5), 1)
                }
                proinsulin = round(np.random.uniform(5, 15), 1)
                secretion_idx = round(np.random.uniform(0.8, 1.5), 2)
                glucagon = round(np.random.uniform(50, 100), 1)
            elif bt == '中脆性':
                ogtt = {
                    '0min': round(np.random.uniform(6.5, 8.5), 1),
                    '30min': round(np.random.uniform(10.5, 13.5), 1),
                    '60min': round(np.random.uniform(9.5, 12.5), 1),
                    '120min': round(np.random.uniform(8.5, 11.5), 1)
                }
                proinsulin = round(np.random.uniform(15, 35), 1)
                secretion_idx = round(np.random.uniform(0.4, 0.9), 2)
                glucagon = round(np.random.uniform(90, 150), 1)
            else:
                ogtt = {
                    '0min': round(np.random.uniform(8.0, 12.0), 1),
                    '30min': round(np.random.uniform(13.0, 18.0), 1),
                    '60min': round(np.random.uniform(12.0, 17.0), 1),
                    '120min': round(np.random.uniform(11.0, 16.0), 1)
                }
                proinsulin = round(np.random.uniform(30, 60), 1)
                secretion_idx = round(np.random.uniform(0.1, 0.5), 2)
                glucagon = round(np.random.uniform(130, 200), 1)

            data['ogtt_ivggt_results'].append(json.dumps(ogtt))
            data['proinsulin_level'].append(proinsulin)
            data['insulin_secretion_index'].append(secretion_idx)
            data['glucagon_level'].append(glucagon)

        return data

    def generate_inflammation_markers(self, brittleness_types):
        """生成炎症标志物"""
        data = {
            'hs_crp': [],
            'il6': [],
            'tnfa': []
        }

        for bt in brittleness_types:
            if bt == '低脆性':
                data['hs_crp'].append(round(np.random.uniform(0.5, 3.0), 2))
                data['il6'].append(round(np.random.uniform(2, 8), 1))
                data['tnfa'].append(round(np.random.uniform(5, 15), 1))
            elif bt == '中脆性':
                data['hs_crp'].append(round(np.random.uniform(2.5, 8.0), 2))
                data['il6'].append(round(np.random.uniform(7, 20), 1))
                data['tnfa'].append(round(np.random.uniform(12, 30), 1))
            else:
                data['hs_crp'].append(round(np.random.uniform(6.0, 20.0), 2))
                data['il6'].append(round(np.random.uniform(18, 50), 1))
                data['tnfa'].append(round(np.random.uniform(25, 60), 1))

        return data

    def generate_surgery_comprehensive(self, brittleness_types):
        """生成完整手术信息"""
        data = {
            'surgery_type': [],
            'operation_duration_min': [],
            'anesthesia_type': [],
            'anesthesia_drugs': [],
            'intraop_fluid_type': [],
            'intraop_fluid_volume': [],
            'intraop_blood_loss': [],
            'intraop_blood_transfusion': [],
            'vasoactive_drugs': [],
            'intraop_complications': [],
            'pancreatojejunostomy_type': [],
            'pancreatojejunostomy_diameter': [],
            'intraop_cortisol': [],
            'intraop_catecholamines': [],
            'intraop_insulin_infusion_rate': [],
            'intraop_glucose_infusion_volume': []
        }

        for bt in brittleness_types:
            # 手术类型
            surgery = np.random.choice(
                ['胰十二指肠切除', '远端胰腺切除', '全胰切除', '姑息性手术'],
                p=[0.50, 0.30, 0.10, 0.10]
            )
            data['surgery_type'].append(surgery)

            # 手术时长与类型相关
            if surgery == '胰十二指肠切除':
                duration = np.random.randint(300, 480)
            elif surgery == '远端胰腺切除':
                duration = np.random.randint(180, 320)
            elif surgery == '全胰切除':
                duration = np.random.randint(360, 540)
            else:
                duration = np.random.randint(120, 250)
            data['operation_duration_min'].append(duration)

            # 麻醉
            data['anesthesia_type'].append('全身麻醉')
            data['anesthesia_drugs'].append(
                np.random.choice([
                    '丙泊酚+瑞芬太尼+罗库溴铵',
                    '七氟醚+瑞芬太尼+顺式阿曲库铵',
                    '丙泊酚+舒芬太尼+罗库溴铵'
                ])
            )

            # 液体管理
            data['intraop_fluid_type'].append(
                np.random.choice(['晶体+胶体', '晶体为主', '晶体+血制品'])
            )
            data['intraop_fluid_volume'].append(np.random.randint(1500, 5000))
            data['intraop_blood_loss'].append(np.random.randint(200, 1800))
            data['intraop_blood_transfusion'].append(
                0 if np.random.random() > 0.3 else np.random.randint(200, 1200)
            )

            # 血管活性药物
            if bt == '高脆性' or duration > 400:
                vasoactive = np.random.choice([
                    '去甲肾上腺素', '多巴胺+去甲肾上腺素', '无'
                ], p=[0.4, 0.3, 0.3])
            else:
                vasoactive = np.random.choice(['无', '去甲肾上腺素'], p=[0.7, 0.3])
            data['vasoactive_drugs'].append(vasoactive)

            # 术中并发症
            if bt == '高脆性':
                complication = np.random.choice(
                    ['无', '术中出血', '血压不稳', '血糖波动', '心律失常'],
                    p=[0.35, 0.25, 0.20, 0.15, 0.05]
                )
            else:
                complication = np.random.choice(
                    ['无', '术中出血', '血压不稳'],
                    p=[0.75, 0.15, 0.10]
                )
            data['intraop_complications'].append(complication)

            # 胰肠吻合
            if surgery in ['胰十二指肠切除', '全胰切除']:
                data['pancreatojejunostomy_type'].append(
                    np.random.choice(['端侧吻合', '端端吻合', '胰胃吻合'],
                                   p=[0.6, 0.3, 0.1])
                )
                data['pancreatojejunostomy_diameter'].append(
                    round(np.random.uniform(8, 18), 1)
                )
            else:
                data['pancreatojejunostomy_type'].append('不适用')
                data['pancreatojejunostomy_diameter'].append(0)

            # 应激激素
            data['intraop_cortisol'].append(round(np.random.uniform(15, 45), 1))
            data['intraop_catecholamines'].append(round(np.random.uniform(200, 800), 0))

            # 术中血糖管理
            if bt == '低脆性':
                insulin_rate = round(np.random.uniform(0, 2.5), 2)
            elif bt == '中脆性':
                insulin_rate = round(np.random.uniform(2, 5.5), 2)
            else:
                insulin_rate = round(np.random.uniform(4.5, 12), 2)
            data['intraop_insulin_infusion_rate'].append(insulin_rate)
            data['intraop_glucose_infusion_volume'].append(np.random.randint(0, 500))

        return data

    def generate_intraop_glycemic(self, brittleness_types):
        """生成术中血糖监测数据"""
        data = {
            'intraop_cgm_cv': [],
            'intraop_cgm_mean_glucose': [],
            'intraop_glucose_range': [],
            'intraop_hypo_episodes': [],
            'intraop_severe_hypo_episodes': []
        }

        for bt in brittleness_types:
            if bt == '低脆性':
                data['intraop_cgm_cv'].append(round(np.random.uniform(12, 25), 2))
                data['intraop_cgm_mean_glucose'].append(round(np.random.uniform(6.2, 8.8), 2))
                data['intraop_glucose_range'].append(round(np.random.uniform(1.5, 4.2), 2))
                data['intraop_hypo_episodes'].append(0)
                data['intraop_severe_hypo_episodes'].append(0)
            elif bt == '中脆性':
                data['intraop_cgm_cv'].append(round(np.random.uniform(23, 38), 2))
                data['intraop_cgm_mean_glucose'].append(round(np.random.uniform(7.0, 11.0), 2))
                data['intraop_glucose_range'].append(round(np.random.uniform(3.5, 7.5), 2))
                data['intraop_hypo_episodes'].append(np.random.randint(0, 2))
                data['intraop_severe_hypo_episodes'].append(0)
            else:
                data['intraop_cgm_cv'].append(round(np.random.uniform(35, 55), 2))
                data['intraop_cgm_mean_glucose'].append(round(np.random.uniform(8.0, 14.5), 2))
                data['intraop_glucose_range'].append(round(np.random.uniform(6.5, 13), 2))
                data['intraop_hypo_episodes'].append(np.random.randint(1, 5))
                data['intraop_severe_hypo_episodes'].append(np.random.randint(0, 3))

        return data

    def generate_postop_complications_comprehensive(self, brittleness_types):
        """生成完整术后并发症"""
        data = {
            'postop_pancreatic_fistula_grade': [],
            'postop_pancreatic_fistula_drainage': [],
            'postop_pancreatic_fistula_duration': [],
            'postop_pancreatic_fistula_mgmt': [],
            'dge_occurrence': [],
            'postop_bleeding_occurrence': [],
            'postop_infection_type': [],
            'postop_infection_type_severity': [],
            'enteral_nutrition_start_day': [],
            'parenteral_nutrition_start_day': [],
            'pert_dose': [],
            'pain_score': [],
            'analgesic_medications': [],
            'postop_pain_mgmt_plan': []
        }

        for bt in brittleness_types:
            # 胰瘘
            if bt == '高脆性':
                fistula = np.random.choice(['无', 'A', 'B', 'C'], p=[0.25, 0.30, 0.30, 0.15])
            elif bt == '中脆性':
                fistula = np.random.choice(['无', 'A', 'B', 'C'], p=[0.45, 0.30, 0.20, 0.05])
            else:
                fistula = np.random.choice(['无', 'A', 'B'], p=[0.75, 0.20, 0.05])

            data['postop_pancreatic_fistula_grade'].append(fistula)

            if fistula != '无':
                data['postop_pancreatic_fistula_drainage'].append(np.random.randint(50, 500))
                data['postop_pancreatic_fistula_duration'].append(np.random.randint(3, 21))
                if fistula in ['B', 'C']:
                    mgmt = np.random.choice([
                        '保守治疗+生长抑素',
                        '保守+生长抑素+引流',
                        '介入治疗',
                        '再次手术'
                    ], p=[0.4, 0.4, 0.15, 0.05])
                else:
                    mgmt = '保守观察'
                data['postop_pancreatic_fistula_mgmt'].append(mgmt)
            else:
                data['postop_pancreatic_fistula_drainage'].append(0)
                data['postop_pancreatic_fistula_duration'].append(0)
                data['postop_pancreatic_fistula_mgmt'].append('不适用')

            # 其他并发症
            data['dge_occurrence'].append(
                np.random.choice([0, 1], p=[0.75, 0.25] if bt != '高脆性' else [0.55, 0.45])
            )
            data['postop_bleeding_occurrence'].append(
                np.random.choice([0, 1], p=[0.85, 0.15] if bt != '高脆性' else [0.70, 0.30])
            )

            # 感染
            if bt == '高脆性':
                infection = np.random.choice(
                    ['无', '切口感染', '腹腔感染', '肺部感染', '泌尿系感染'],
                    p=[0.35, 0.25, 0.20, 0.15, 0.05]
                )
            else:
                infection = np.random.choice(
                    ['无', '切口感染', '腹腔感染', '肺部感染'],
                    p=[0.70, 0.15, 0.10, 0.05]
                )
            data['postop_infection_type'].append(infection)

            if infection != '无':
                severity = np.random.choice(['轻度', '中度', '重度'], p=[0.5, 0.35, 0.15])
                data['postop_infection_type_severity'].append(f'{infection}-{severity}')
            else:
                data['postop_infection_type_severity'].append('无')

            # 营养支持
            data['enteral_nutrition_start_day'].append(np.random.randint(1, 5))
            data['parenteral_nutrition_start_day'].append(
                0 if np.random.random() > 0.4 else np.random.randint(0, 3)
            )
            data['pert_dose'].append(round(np.random.uniform(25000, 75000), 0))

            # 疼痛管理
            data['pain_score'].append(np.random.randint(2, 8))
            data['analgesic_medications'].append(
                np.random.choice([
                    'PCIA',
                    'PCIA+非甾体',
                    '阿片类+非甾体',
                    '非甾体抗炎药'
                ], p=[0.4, 0.3, 0.2, 0.1])
            )
            data['postop_pain_mgmt_plan'].append(
                np.random.choice([
                    '阶梯镇痛',
                    '多模式镇痛',
                    '个体化镇痛'
                ])
            )

        return data

    def generate_postop_glycemic_comprehensive(self, brittleness_types, complications):
        """生成完整术后血糖轨迹"""
        # 基础函数：根据脆性和并发症生成某个时期的血糖指标
        def generate_period_metrics(bt, has_complications, period_factor):
            if bt == '低脆性':
                base_tir = np.random.uniform(75, 92)
                base_cv = np.random.uniform(22, 35)
                base_mage = np.random.uniform(1.8, 3.2)
            elif bt == '中脆性':
                base_tir = np.random.uniform(52, 72)
                base_cv = np.random.uniform(32, 48)
                base_mage = np.random.uniform(3.0, 5.2)
            else:
                base_tir = np.random.uniform(28, 52)
                base_cv = np.random.uniform(45, 65)
                base_mage = np.random.uniform(5.0, 8.5)

            # 并发症影响
            if has_complications:
                base_tir *= 0.85
                base_cv *= 1.25
                base_mage *= 1.30

            # 时间因素
            base_tir *= period_factor['tir']
            base_cv *= period_factor['cv']
            base_mage *= period_factor['mage']

            return {
                'tir': round(max(10, min(98, base_tir)), 2),
                'cv': round(max(15, min(70, base_cv)), 2),
                'mage': round(max(1.0, min(12.0, base_mage)), 2)
            }

        data = {}

        # 术后72小时 (最差时期)
        period_72h = {'tir': 0.75, 'cv': 1.40, 'mage': 1.35}
        for suffix in ['_72h']:
            data[f'postop_cgm_cv{suffix}'] = []
            data[f'postop_cgm_tir{suffix}'] = []
            data[f'postop_cgm_tar_level1{suffix}'] = []
            data[f'postop_cgm_tar_level2{suffix}'] = []
            data[f'postop_cgm_tbr_level1{suffix}'] = []
            data[f'postop_cgm_tbr_level2{suffix}'] = []

        # 术后2周 (恢复期)
        period_2w = {'tir': 0.90, 'cv': 1.15, 'mage': 1.12}
        for suffix in ['_2w']:
            data[f'postop_cgm_cv{suffix}'] = []
            data[f'postop_cgm_tir{suffix}'] = []
            data[f'postop_cgm_tar_level1{suffix}'] = []
            data[f'postop_cgm_tar_level2{suffix}'] = []
            data[f'postop_cgm_tbr_level1{suffix}'] = []
            data[f'postop_cgm_tbr_level2{suffix}'] = []
            data[f'postop_cgm_mage{suffix}'] = []
            data[f'postop_cgm_gmi{suffix}'] = []

        # 术后3月 (稳定期)
        period_3m = {'tir': 0.97, 'cv': 1.05, 'mage': 1.08}
        for suffix in ['_3m']:
            data[f'postop_cgm_cv{suffix}'] = []
            data[f'postop_cgm_tir{suffix}'] = []
            data[f'postop_cgm_tar_level1{suffix}'] = []
            data[f'postop_cgm_tar_level2{suffix}'] = []
            data[f'postop_cgm_tbr_level1{suffix}'] = []
            data[f'postop_cgm_tbr_level2{suffix}'] = []
            data[f'postop_cgm_mage{suffix}'] = []
            data[f'postop_cgm_gmi{suffix}'] = []

        data['postop_hba1c_3m'] = []
        data['postop_hba1c_6m'] = []
        data['postop_hba1c_1y'] = []
        data['postop_fecal_elastase1_3m'] = []

        for i, bt in enumerate(brittleness_types):
            # 判断是否有重要并发症
            has_complications = (
                complications['postop_pancreatic_fistula_grade'][i] in ['B', 'C'] or
                complications['postop_infection_type'][i] != '无' or
                complications['dge_occurrence'][i] == 1
            )

            # 生成各时期数据
            for period, period_factor in [
                ('_72h', period_72h),
                ('_2w', period_2w),
                ('_3m', period_3m)
            ]:
                metrics = generate_period_metrics(bt, has_complications, period_factor)

                data[f'postop_cgm_tir{period}'].append(metrics['tir'])
                data[f'postop_cgm_cv{period}'].append(metrics['cv'])

                # TAR和TBR基于TIR计算
                tar_total = 100 - metrics['tir']
                tar1 = round(tar_total * np.random.uniform(0.55, 0.75), 2)
                tar2 = round(tar_total - tar1 - np.random.uniform(3, 8), 2)
                tbr1 = round(np.random.uniform(2, 6), 2)
                tbr2 = round(np.random.uniform(0.5, 2.5), 2)

                data[f'postop_cgm_tar_level1{period}'].append(tar1)
                data[f'postop_cgm_tar_level2{period}'].append(max(0, tar2))
                data[f'postop_cgm_tbr_level1{period}'].append(tbr1)
                data[f'postop_cgm_tbr_level2{period}'].append(tbr2)

                if period in ['_2w', '_3m']:
                    data[f'postop_cgm_mage{period}'].append(metrics['mage'])
                    # GMI基于TIR估算
                    gmi = round(3.31 + (0.02392 * (100 - metrics['tir'])), 2)
                    data[f'postop_cgm_gmi{period}'].append(gmi)

            # HbA1c
            if bt == '低脆性':
                hba1c_3m = round(np.random.uniform(5.8, 7.2), 2)
                hba1c_6m = round(np.random.uniform(5.6, 7.0), 2)
                hba1c_1y = round(np.random.uniform(5.5, 6.8), 2)
            elif bt == '中脆性':
                hba1c_3m = round(np.random.uniform(6.8, 8.8), 2)
                hba1c_6m = round(np.random.uniform(6.5, 8.5), 2)
                hba1c_1y = round(np.random.uniform(6.3, 8.2), 2)
            else:
                hba1c_3m = round(np.random.uniform(8.2, 11.5), 2)
                hba1c_6m = round(np.random.uniform(7.8, 11.0), 2)
                hba1c_1y = round(np.random.uniform(7.5, 10.5), 2)

            if has_complications:
                hba1c_3m += np.random.uniform(0.3, 0.8)
                hba1c_6m += np.random.uniform(0.2, 0.6)
                hba1c_1y += np.random.uniform(0.1, 0.4)

            data['postop_hba1c_3m'].append(round(hba1c_3m, 2))
            data['postop_hba1c_6m'].append(round(hba1c_6m, 2))
            data['postop_hba1c_1y'].append(round(hba1c_1y, 2))

            # 术后胰腺外分泌功能
            data['postop_fecal_elastase1_3m'].append(np.random.randint(80, 300))

        return data

    def generate_genetic_markers(self):
        """生成基因标志物"""
        data = {
            'tcf7l2_genotype': [],
            'kcnj11_genotype': [],
            'brca1_2_mutation': [],
            'palb2_mutation': [],
            'atm_mutation': [],
            'dme_polymorphism': []
        }

        for _ in range(self.n_patients):
            # TCF7L2基因型
            data['tcf7l2_genotype'].append(
                np.random.choice(['CC', 'CT', 'TT'], p=[0.45, 0.42, 0.13])
            )
            # KCNJ11基因型
            data['kcnj11_genotype'].append(
                np.random.choice(['EE', 'EK', 'KK'], p=[0.50, 0.40, 0.10])
            )
            # BRCA突变
            data['brca1_2_mutation'].append(np.random.choice([0, 1], p=[0.92, 0.08]))
            # PALB2突变
            data['palb2_mutation'].append(np.random.choice([0, 1], p=[0.96, 0.04]))
            # ATM突变
            data['atm_mutation'].append(np.random.choice([0, 1], p=[0.94, 0.06]))
            # 药物代谢酶多态性
            dme = np.random.choice([
                '无异常',
                'CYP2C19慢代谢',
                'CYP2D6慢代谢',
                'CYP3A4快代谢'
            ], p=[0.70, 0.12, 0.10, 0.08])
            data['dme_polymorphism'].append(dme)

        return data

    def generate_qol_and_outcomes(self, brittleness_types, complications):
        """生成生活质量和结局指标"""
        data = {
            'eq5d_score': [],
            'eortc_qlqc30_score': [],
            'eortc_qlqpan26_score': [],
            'rehospitalization_reason': [],
            'survival_status': [],
            'survival_time_months': [],
            'complication_onset_time': [],
            'pancreatic_function_recovery_time': []
        }

        for i, bt in enumerate(brittleness_types):
            has_complications = (
                complications['postop_pancreatic_fistula_grade'][i] in ['B', 'C'] or
                complications['postop_infection_type'][i] != '无'
            )

            # 生活质量评分
            if bt == '低脆性' and not has_complications:
                eq5d = round(np.random.uniform(0.75, 0.95), 2)
                qlq_c30 = round(np.random.uniform(70, 90), 1)
                qlq_pan26 = round(np.random.uniform(15, 35), 1)
            elif bt == '中脆性' or (bt == '低脆性' and has_complications):
                eq5d = round(np.random.uniform(0.55, 0.80), 2)
                qlq_c30 = round(np.random.uniform(50, 75), 1)
                qlq_pan26 = round(np.random.uniform(30, 55), 1)
            else:
                eq5d = round(np.random.uniform(0.35, 0.65), 2)
                qlq_c30 = round(np.random.uniform(30, 60), 1)
                qlq_pan26 = round(np.random.uniform(50, 75), 1)

            data['eq5d_score'].append(eq5d)
            data['eortc_qlqc30_score'].append(qlq_c30)
            data['eortc_qlqpan26_score'].append(qlq_pan26)

            # 再住院
            if has_complications or bt == '高脆性':
                rehospitalization = np.random.choice([
                    '无',
                    '胰瘘相关',
                    '感染',
                    '血糖控制不佳',
                    '营养不良'
                ], p=[0.50, 0.20, 0.15, 0.10, 0.05])
            else:
                rehospitalization = np.random.choice(['无', '其他'], p=[0.85, 0.15])
            data['rehospitalization_reason'].append(rehospitalization)

            # 生存状态和时间
            survival = np.random.choice([0, 1], p=[0.15, 0.85])  # 85%生存率
            data['survival_status'].append(survival)
            if survival == 1:
                survival_months = np.random.randint(12, 60)
            else:
                survival_months = np.random.randint(3, 24)
            data['survival_time_months'].append(survival_months)

            # 并发症发生时间
            if has_complications:
                comp_time = f'术后{np.random.randint(1, 14)}天'
            else:
                comp_time = '无'
            data['complication_onset_time'].append(comp_time)

            # 胰腺功能恢复
            recovery_time = f'术后{np.random.randint(4, 24)}周部分恢复'
            data['pancreatic_function_recovery_time'].append(recovery_time)

        return data

    def generate_future_risk(self, brittleness_types, complications, postop_glycemic):
        """生成未来脆性恶化风险预测"""
        data = {
            'future_brittleness_risk_3m': [],
            'future_brittleness_risk_score': []
        }

        for i, bt in enumerate(brittleness_types):
            # 基础风险
            if bt == '低脆性':
                base_risk = 0.12
            elif bt == '中脆性':
                base_risk = 0.45
            else:
                base_risk = 0.78

            # 并发症影响
            if complications['postop_pancreatic_fistula_grade'][i] in ['B', 'C']:
                base_risk += 0.18
            if complications['dge_occurrence'][i] == 1:
                base_risk += 0.10
            if complications['postop_infection_type'][i] != '无':
                base_risk += 0.12

            # 术后72h血糖控制影响
            if postop_glycemic['postop_cgm_tir_72h'][i] < 50:
                base_risk += 0.15
            if postop_glycemic['postop_cgm_cv_72h'][i] > 45:
                base_risk += 0.12

            # 限制在0-1之间
            base_risk = max(0.05, min(0.95, base_risk))

            # 分类风险
            if base_risk < 0.30:
                risk_category = '低'
            elif base_risk < 0.65:
                risk_category = '中'
            else:
                risk_category = '高'

            data['future_brittleness_risk_3m'].append(risk_category)
            data['future_brittleness_risk_score'].append(round(base_risk, 3))

        return data

    def generate_complete_dataset(self):
        """生成完整数据集"""
        print("="*70)
        print("胰腺癌患者血糖脆性虚拟数据生成 - 完整版")
        print("="*70)
        print()

        all_data = {}

        # 1. 基本信息
        print("[1/15] 生成基本信息...")
        all_data.update(self.generate_basic_info())

        # 2. 详细糖尿病特征
        print("[2/15] 生成详细糖尿病特征...")
        diabetes_data = self.generate_diabetes_detailed()
        all_data.update(diabetes_data)
        brittleness_types = diabetes_data['brittleness_type']

        # 3. 心理社会因素
        print("[3/15] 生成心理社会因素...")
        all_data.update(self.generate_psychosocial_factors(brittleness_types))

        # 4. 术前完整血糖指标
        print("[4/15] 生成术前完整血糖指标...")
        all_data.update(self.generate_preop_glycemic_comprehensive(brittleness_types))

        # 5. 完整肿瘤特征
        print("[5/15] 生成完整肿瘤特征...")
        all_data.update(self.generate_tumor_comprehensive())

        # 6. 营养评估
        print("[6/15] 生成营养评估指标...")
        all_data.update(self.generate_nutrition_comprehensive(brittleness_types))

        # 7. 胰腺功能
        print("[7/15] 生成胰腺功能指标...")
        all_data.update(self.generate_pancreatic_function(brittleness_types))

        # 8. 胰岛功能
        print("[8/15] 生成胰岛功能评估...")
        all_data.update(self.generate_islet_function(brittleness_types))

        # 9. 炎症标志物
        print("[9/15] 生成炎症标志物...")
        all_data.update(self.generate_inflammation_markers(brittleness_types))

        # 10. 完整手术信息
        print("[10/15] 生成完整手术信息...")
        all_data.update(self.generate_surgery_comprehensive(brittleness_types))

        # 11. 术中血糖监测
        print("[11/15] 生成术中血糖监测数据...")
        all_data.update(self.generate_intraop_glycemic(brittleness_types))

        # 12. 完整术后并发症
        print("[12/15] 生成完整术后并发症...")
        complications = self.generate_postop_complications_comprehensive(brittleness_types)
        all_data.update(complications)

        # 13. 完整术后血糖轨迹
        print("[13/15] 生成完整术后血糖轨迹...")
        postop_glycemic = self.generate_postop_glycemic_comprehensive(
            brittleness_types, complications
        )
        all_data.update(postop_glycemic)

        # 14. 基因标志物
        print("[14/15] 生成基因标志物...")
        all_data.update(self.generate_genetic_markers())

        # 15. 生活质量和结局
        print("[15/15] 生成生活质量和结局指标...")
        all_data.update(self.generate_qol_and_outcomes(brittleness_types, complications))

        # 16. 未来风险预测
        print("[ + ] 生成未来风险预测...")
        all_data.update(self.generate_future_risk(
            brittleness_types, complications, postop_glycemic
        ))

        df = pd.DataFrame(all_data)

        print()
        print("="*70)
        print(f"✓ 成功生成 {len(df)} 例完整虚拟患者数据")
        print(f"✓ 总特征数: {len(df.columns)}")
        print("="*70)

        return df


def main():
    """主函数"""
    print("\n")

    # 生成数据
    simulator = CompletePancreaticCancerSimulator(n_patients=100)
    df = simulator.generate_complete_dataset()

    # 保存数据
    output_file = '虚拟患者数据_完整版.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ 数据已保存至: {output_file}")

    # 数据摘要
    print("\n" + "="*70)
    print("数据摘要")
    print("="*70)
    print(f"患者总数: {len(df)}")
    print(f"特征总数: {len(df.columns)}")
    print(f"\n脆性类型分布:")
    print(df['brittleness_type'].value_counts())
    print(f"\n未来3个月脆性恶化风险分布:")
    print(df['future_brittleness_risk_3m'].value_counts())

    # 关键指标统计
    print("\n术前/术后关键指标对比:")
    print(f"  术前平均HbA1c: {df['preop_hba1c'].mean():.2f}%")
    print(f"  术后3月平均HbA1c: {df['postop_hba1c_3m'].mean():.2f}%")
    print(f"  术前平均TIR: {df['preop_cgm_tir'].mean():.1f}%")
    print(f"  术后3月平均TIR: {df['postop_cgm_tir_3m'].mean():.1f}%")

    # 特征类别统计
    print(f"\n特征类别统计:")
    print(f"  糖尿病相关: ~15个字段")
    print(f"  心理社会: 6个字段")
    print(f"  术前CGM: 9个字段")
    print(f"  肿瘤特征: 6个字段")
    print(f"  营养评估: 8个字段")
    print(f"  胰腺功能: 8个字段")
    print(f"  胰岛功能: 4个字段")
    print(f"  炎症标志物: 3个字段")
    print(f"  手术信息: 16个字段")
    print(f"  术中血糖: 5个字段")
    print(f"  术后并发症: 14个字段")
    print(f"  术后血糖轨迹: 25个字段")
    print(f"  基因标志物: 6个字段")
    print(f"  生活质量和结局: 8个字段")
    print(f"  风险预测: 2个字段")

    print("\n" + "="*70)
    print("✓ 完整数据生成完成!")
    print("="*70)
    print()

    return df


if __name__ == "__main__":
    df = main()
