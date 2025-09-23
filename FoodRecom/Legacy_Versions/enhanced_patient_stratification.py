#!/usr/bin/env python3
"""
增强版患者分层和风险评估系统
基于多维度体检数据的精准营养干预分层策略
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math

class RiskLevel(Enum):
    """风险等级"""
    LOW = "低风险"
    MODERATE = "中等风险"
    HIGH = "高风险"
    VERY_HIGH = "极高风险"

class PatientStratum(Enum):
    """患者分层"""
    HEALTHY_YOUNG = "健康年轻人群"
    HEALTHY_MIDDLE_AGE = "健康中年人群"
    HEALTHY_ELDERLY = "健康老年人群"
    PREDIABETES = "糖尿病前期"
    DIABETES_EARLY = "糖尿病早期"
    DIABETES_MODERATE = "糖尿病中期"
    DIABETES_ADVANCED = "糖尿病晚期"
    HYPERTENSION_STAGE1 = "高血压1期"
    HYPERTENSION_STAGE2 = "高血压2期"
    DYSLIPIDEMIA_MILD = "轻度血脂异常"
    DYSLIPIDEMIA_SEVERE = "重度血脂异常"
    METABOLIC_SYNDROME = "代谢综合征"
    CARDIOVASCULAR_HIGH_RISK = "心血管高危"
    RENAL_DYSFUNCTION = "肾功能异常"
    MULTIPLE_COMORBIDITIES = "多重合并症"

@dataclass
class ComprehensiveLabResults:
    """全面的实验室检查结果"""
    # 基础代谢指标
    blood_glucose_fasting: Optional[float] = None  # 空腹血糖 mmol/L
    blood_glucose_2h: Optional[float] = None  # 餐后2小时血糖 mmol/L
    hba1c: Optional[float] = None  # 糖化血红蛋白 %

    # 血脂谱
    cholesterol_total: Optional[float] = None  # 总胆固醇 mmol/L
    cholesterol_ldl: Optional[float] = None  # LDL-C mmol/L
    cholesterol_hdl: Optional[float] = None  # HDL-C mmol/L
    triglycerides: Optional[float] = None  # 甘油三酯 mmol/L

    # 心血管指标
    blood_pressure_systolic: Optional[int] = None  # 收缩压 mmHg
    blood_pressure_diastolic: Optional[int] = None  # 舒张压 mmHg
    resting_heart_rate: Optional[int] = None  # 静息心率 bpm

    # 肾功能指标
    creatinine: Optional[float] = None  # 肌酐 μmol/L
    urea_nitrogen: Optional[float] = None  # 尿素氮 mmol/L
    uric_acid: Optional[float] = None  # 尿酸 μmol/L
    albumin_creatinine_ratio: Optional[float] = None  # 尿微量白蛋白/肌酐比值

    # 肝功能指标
    alt: Optional[float] = None  # 丙氨酸转氨酶 U/L
    ast: Optional[float] = None  # 天门冬氨酸转氨酶 U/L

    # 营养状态指标
    albumin: Optional[float] = None  # 白蛋白 g/L
    hemoglobin: Optional[float] = None  # 血红蛋白 g/L

    # 炎症指标
    crp: Optional[float] = None  # C反应蛋白 mg/L

    # 甲状腺功能
    tsh: Optional[float] = None  # 促甲状腺激素 mIU/L

    # 维生素和矿物质
    vitamin_d: Optional[float] = None  # 维生素D nmol/L
    vitamin_b12: Optional[float] = None  # 维生素B12 pmol/L
    folate: Optional[float] = None  # 叶酸 nmol/L
    iron: Optional[float] = None  # 铁 μmol/L

@dataclass
class RiskAssessment:
    """风险评估结果"""
    overall_risk: RiskLevel
    cardiovascular_risk: RiskLevel
    diabetes_risk: RiskLevel
    renal_risk: RiskLevel
    nutritional_risk: RiskLevel
    stratification: PatientStratum
    risk_factors: List[str]
    protective_factors: List[str]
    intervention_priority: int  # 1-5，数字越大优先级越高

class EnhancedPatientStratification:
    """增强版患者分层系统"""

    def __init__(self):
        self.age_categories = {
            (18, 35): "年轻成人",
            (35, 50): "中年",
            (50, 65): "中老年",
            (65, 100): "老年"
        }

    def comprehensive_risk_assessment(self, user_profile, lab_results: ComprehensiveLabResults) -> RiskAssessment:
        """全面风险评估"""

        # 1. 年龄风险评估
        age_risk = self._assess_age_risk(user_profile.age)

        # 2. 代谢风险评估
        metabolic_risk = self._assess_metabolic_risk(lab_results, user_profile)

        # 3. 心血管风险评估
        cv_risk = self._assess_cardiovascular_risk(lab_results, user_profile)

        # 4. 肾功能风险评估
        renal_risk = self._assess_renal_risk(lab_results)

        # 5. 营养状态风险评估
        nutritional_risk = self._assess_nutritional_risk(lab_results, user_profile)

        # 6. 综合分层
        stratification = self._determine_patient_stratum(
            user_profile, lab_results, metabolic_risk, cv_risk, renal_risk
        )

        # 7. 确定整体风险等级
        overall_risk = self._calculate_overall_risk([
            age_risk, metabolic_risk, cv_risk, renal_risk, nutritional_risk
        ])

        # 8. 识别风险因素和保护因素
        risk_factors, protective_factors = self._identify_risk_factors(
            user_profile, lab_results
        )

        # 9. 确定干预优先级
        intervention_priority = self._calculate_intervention_priority(
            overall_risk, stratification, risk_factors
        )

        return RiskAssessment(
            overall_risk=overall_risk,
            cardiovascular_risk=cv_risk,
            diabetes_risk=metabolic_risk,
            renal_risk=renal_risk,
            nutritional_risk=nutritional_risk,
            stratification=stratification,
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            intervention_priority=intervention_priority
        )

    def _assess_age_risk(self, age: int) -> RiskLevel:
        """年龄风险评估"""
        if age < 35:
            return RiskLevel.LOW
        elif age < 50:
            return RiskLevel.LOW
        elif age < 65:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.HIGH

    def _assess_metabolic_risk(self, lab_results: ComprehensiveLabResults, user_profile) -> RiskLevel:
        """代谢风险评估（糖尿病风险）"""
        risk_score = 0

        # 血糖指标
        if lab_results.blood_glucose_fasting:
            if lab_results.blood_glucose_fasting >= 7.0:
                risk_score += 3  # 糖尿病诊断标准
            elif lab_results.blood_glucose_fasting >= 6.1:
                risk_score += 2  # 空腹血糖受损
            elif lab_results.blood_glucose_fasting >= 5.6:
                risk_score += 1  # 轻度升高

        # 糖化血红蛋白
        if lab_results.hba1c:
            if lab_results.hba1c >= 6.5:
                risk_score += 3  # 糖尿病诊断标准
            elif lab_results.hba1c >= 6.0:
                risk_score += 2  # 糖尿病前期
            elif lab_results.hba1c >= 5.7:
                risk_score += 1  # 轻度升高

        # BMI风险
        bmi = user_profile.weight / ((user_profile.height / 100) ** 2)
        if bmi >= 28:
            risk_score += 2  # 肥胖
        elif bmi >= 24:
            risk_score += 1  # 超重

        # 年龄风险
        if user_profile.age >= 45:
            risk_score += 1

        # 转换为风险等级
        if risk_score >= 5:
            return RiskLevel.VERY_HIGH
        elif risk_score >= 3:
            return RiskLevel.HIGH
        elif risk_score >= 1:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW

    def _assess_cardiovascular_risk(self, lab_results: ComprehensiveLabResults, user_profile) -> RiskLevel:
        """心血管风险评估（基于中国心血管风险评估）"""
        risk_score = 0

        # 年龄评分
        age = user_profile.age
        if user_profile.gender == "男":
            if age >= 55:
                risk_score += 2
            elif age >= 45:
                risk_score += 1
        else:  # 女性
            if age >= 65:
                risk_score += 2
            elif age >= 55:
                risk_score += 1

        # 血压评分
        if lab_results.blood_pressure_systolic and lab_results.blood_pressure_diastolic:
            systolic = lab_results.blood_pressure_systolic
            diastolic = lab_results.blood_pressure_diastolic

            if systolic >= 180 or diastolic >= 110:
                risk_score += 3
            elif systolic >= 160 or diastolic >= 100:
                risk_score += 2
            elif systolic >= 140 or diastolic >= 90:
                risk_score += 1

        # 血脂评分
        if lab_results.cholesterol_total and lab_results.cholesterol_total >= 6.2:
            risk_score += 1
        if lab_results.cholesterol_ldl and lab_results.cholesterol_ldl >= 4.1:
            risk_score += 1
        if lab_results.cholesterol_hdl:
            if user_profile.gender == "男" and lab_results.cholesterol_hdl < 1.0:
                risk_score += 1
            elif user_profile.gender == "女" and lab_results.cholesterol_hdl < 1.3:
                risk_score += 1

        # 糖尿病
        if (lab_results.blood_glucose_fasting and lab_results.blood_glucose_fasting >= 7.0) or \
           (lab_results.hba1c and lab_results.hba1c >= 6.5):
            risk_score += 2

        # BMI
        bmi = user_profile.weight / ((user_profile.height / 100) ** 2)
        if bmi >= 28:
            risk_score += 1

        # 转换为风险等级
        if risk_score >= 6:
            return RiskLevel.VERY_HIGH
        elif risk_score >= 4:
            return RiskLevel.HIGH
        elif risk_score >= 2:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW

    def _assess_renal_risk(self, lab_results: ComprehensiveLabResults) -> RiskLevel:
        """肾功能风险评估"""
        risk_score = 0

        # 肌酐水平
        if lab_results.creatinine:
            if lab_results.creatinine > 177:  # >2.0 mg/dL
                risk_score += 3
            elif lab_results.creatinine > 133:  # >1.5 mg/dL
                risk_score += 2
            elif lab_results.creatinine > 115:  # >1.3 mg/dL
                risk_score += 1

        # 尿微量白蛋白
        if lab_results.albumin_creatinine_ratio:
            if lab_results.albumin_creatinine_ratio > 300:
                risk_score += 3
            elif lab_results.albumin_creatinine_ratio > 30:
                risk_score += 2
            elif lab_results.albumin_creatinine_ratio > 10:
                risk_score += 1

        # 尿酸
        if lab_results.uric_acid:
            if lab_results.uric_acid > 500:
                risk_score += 1

        if risk_score >= 4:
            return RiskLevel.VERY_HIGH
        elif risk_score >= 2:
            return RiskLevel.HIGH
        elif risk_score >= 1:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW

    def _assess_nutritional_risk(self, lab_results: ComprehensiveLabResults, user_profile) -> RiskLevel:
        """营养状态风险评估"""
        risk_score = 0

        # BMI评估
        bmi = user_profile.weight / ((user_profile.height / 100) ** 2)
        if bmi < 18.5:
            risk_score += 2  # 营养不良
        elif bmi > 32:
            risk_score += 2  # 重度肥胖
        elif bmi > 28:
            risk_score += 1  # 肥胖

        # 血红蛋白
        if lab_results.hemoglobin:
            if user_profile.gender == "男" and lab_results.hemoglobin < 120:
                risk_score += 1
            elif user_profile.gender == "女" and lab_results.hemoglobin < 110:
                risk_score += 1

        # 白蛋白
        if lab_results.albumin:
            if lab_results.albumin < 35:
                risk_score += 2
            elif lab_results.albumin < 40:
                risk_score += 1

        # 维生素D
        if lab_results.vitamin_d:
            if lab_results.vitamin_d < 50:
                risk_score += 1

        # 维生素B12
        if lab_results.vitamin_b12:
            if lab_results.vitamin_b12 < 150:
                risk_score += 1

        if risk_score >= 4:
            return RiskLevel.VERY_HIGH
        elif risk_score >= 2:
            return RiskLevel.HIGH
        elif risk_score >= 1:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW

    def _determine_patient_stratum(self, user_profile, lab_results: ComprehensiveLabResults,
                                 metabolic_risk: RiskLevel, cv_risk: RiskLevel,
                                 renal_risk: RiskLevel) -> PatientStratum:
        """确定患者分层"""

        age = user_profile.age

        # 检查是否有糖尿病
        has_diabetes = (lab_results.blood_glucose_fasting and lab_results.blood_glucose_fasting >= 7.0) or \
                      (lab_results.hba1c and lab_results.hba1c >= 6.5)

        # 检查是否为糖尿病前期
        has_prediabetes = not has_diabetes and \
                         ((lab_results.blood_glucose_fasting and 6.1 <= lab_results.blood_glucose_fasting < 7.0) or \
                          (lab_results.hba1c and 6.0 <= lab_results.hba1c < 6.5))

        # 检查是否有高血压
        has_hypertension = (lab_results.blood_pressure_systolic and lab_results.blood_pressure_systolic >= 140) or \
                          (lab_results.blood_pressure_diastolic and lab_results.blood_pressure_diastolic >= 90)

        # 检查是否有血脂异常
        has_dyslipidemia = (lab_results.cholesterol_total and lab_results.cholesterol_total >= 6.2) or \
                          (lab_results.cholesterol_ldl and lab_results.cholesterol_ldl >= 4.1) or \
                          (lab_results.triglycerides and lab_results.triglycerides >= 2.3)

        # 计算合并症数量
        comorbidities = sum([has_diabetes, has_hypertension, has_dyslipidemia,
                           renal_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]])

        # 分层逻辑
        if comorbidities >= 3:
            return PatientStratum.MULTIPLE_COMORBIDITIES
        elif has_diabetes:
            if metabolic_risk == RiskLevel.VERY_HIGH or cv_risk == RiskLevel.VERY_HIGH:
                return PatientStratum.DIABETES_ADVANCED
            elif metabolic_risk == RiskLevel.HIGH:
                return PatientStratum.DIABETES_MODERATE
            else:
                return PatientStratum.DIABETES_EARLY
        elif has_prediabetes:
            return PatientStratum.PREDIABETES
        elif has_hypertension:
            if lab_results.blood_pressure_systolic >= 160 or lab_results.blood_pressure_diastolic >= 100:
                return PatientStratum.HYPERTENSION_STAGE2
            else:
                return PatientStratum.HYPERTENSION_STAGE1
        elif has_dyslipidemia:
            if cv_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
                return PatientStratum.DYSLIPIDEMIA_SEVERE
            else:
                return PatientStratum.DYSLIPIDEMIA_MILD
        elif cv_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            return PatientStratum.CARDIOVASCULAR_HIGH_RISK
        elif renal_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            return PatientStratum.RENAL_DYSFUNCTION
        else:
            # 健康人群按年龄分层
            if age < 35:
                return PatientStratum.HEALTHY_YOUNG
            elif age < 65:
                return PatientStratum.HEALTHY_MIDDLE_AGE
            else:
                return PatientStratum.HEALTHY_ELDERLY

    def _calculate_overall_risk(self, risk_levels: List[RiskLevel]) -> RiskLevel:
        """计算整体风险等级"""
        risk_scores = {
            RiskLevel.LOW: 1,
            RiskLevel.MODERATE: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.VERY_HIGH: 4
        }

        # 计算加权平均风险分数
        total_score = sum(risk_scores[risk] for risk in risk_levels)
        avg_score = total_score / len(risk_levels)

        # 如果有任何极高风险，整体风险至少为高风险
        if RiskLevel.VERY_HIGH in risk_levels:
            avg_score = max(avg_score, 3.5)

        # 转换回风险等级
        if avg_score >= 3.5:
            return RiskLevel.VERY_HIGH
        elif avg_score >= 2.5:
            return RiskLevel.HIGH
        elif avg_score >= 1.5:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW

    def _identify_risk_factors(self, user_profile, lab_results: ComprehensiveLabResults) -> Tuple[List[str], List[str]]:
        """识别风险因素和保护因素"""
        risk_factors = []
        protective_factors = []

        # 年龄因素
        if user_profile.age >= 65:
            risk_factors.append("高龄（≥65岁）")
        elif user_profile.age < 35:
            protective_factors.append("年轻（<35岁）")

        # BMI因素
        bmi = user_profile.weight / ((user_profile.height / 100) ** 2)
        if bmi >= 28:
            risk_factors.append(f"肥胖（BMI: {bmi:.1f}）")
        elif bmi < 18.5:
            risk_factors.append(f"营养不良（BMI: {bmi:.1f}）")
        elif 18.5 <= bmi < 24:
            protective_factors.append(f"正常体重（BMI: {bmi:.1f}）")

        # 血糖因素
        if lab_results.blood_glucose_fasting:
            if lab_results.blood_glucose_fasting >= 7.0:
                risk_factors.append(f"糖尿病（空腹血糖: {lab_results.blood_glucose_fasting:.1f} mmol/L）")
            elif lab_results.blood_glucose_fasting >= 6.1:
                risk_factors.append(f"空腹血糖受损（{lab_results.blood_glucose_fasting:.1f} mmol/L）")
            elif lab_results.blood_glucose_fasting <= 5.6:
                protective_factors.append(f"正常血糖（{lab_results.blood_glucose_fasting:.1f} mmol/L）")

        # 血压因素
        if lab_results.blood_pressure_systolic and lab_results.blood_pressure_diastolic:
            sys = lab_results.blood_pressure_systolic
            dia = lab_results.blood_pressure_diastolic
            if sys >= 140 or dia >= 90:
                risk_factors.append(f"高血压（{sys}/{dia} mmHg）")
            elif sys < 120 and dia < 80:
                protective_factors.append(f"理想血压（{sys}/{dia} mmHg）")

        # 血脂因素
        if lab_results.cholesterol_ldl:
            if lab_results.cholesterol_ldl >= 4.1:
                risk_factors.append(f"LDL胆固醇升高（{lab_results.cholesterol_ldl:.1f} mmol/L）")
            elif lab_results.cholesterol_ldl < 2.6:
                protective_factors.append(f"理想LDL胆固醇（{lab_results.cholesterol_ldl:.1f} mmol/L）")

        if lab_results.cholesterol_hdl:
            hdl_threshold = 1.0 if user_profile.gender == "男" else 1.3
            if lab_results.cholesterol_hdl < hdl_threshold:
                risk_factors.append(f"HDL胆固醇偏低（{lab_results.cholesterol_hdl:.1f} mmol/L）")
            elif lab_results.cholesterol_hdl >= 1.6:
                protective_factors.append(f"高HDL胆固醇（{lab_results.cholesterol_hdl:.1f} mmol/L）")

        # 肾功能因素
        if lab_results.creatinine:
            if lab_results.creatinine > 133:
                risk_factors.append(f"肾功能受损（肌酐: {lab_results.creatinine} μmol/L）")

        # 营养状态因素
        if lab_results.albumin:
            if lab_results.albumin < 35:
                risk_factors.append(f"低蛋白血症（白蛋白: {lab_results.albumin} g/L）")
            elif lab_results.albumin >= 40:
                protective_factors.append(f"良好营养状态（白蛋白: {lab_results.albumin} g/L）")

        return risk_factors, protective_factors

    def _calculate_intervention_priority(self, overall_risk: RiskLevel,
                                       stratification: PatientStratum,
                                       risk_factors: List[str]) -> int:
        """计算干预优先级（1-5分，5分最高优先级）"""
        priority = 1

        # 基于整体风险等级
        risk_priority = {
            RiskLevel.LOW: 1,
            RiskLevel.MODERATE: 2,
            RiskLevel.HIGH: 4,
            RiskLevel.VERY_HIGH: 5
        }
        priority = max(priority, risk_priority[overall_risk])

        # 基于患者分层
        high_priority_strata = [
            PatientStratum.DIABETES_ADVANCED,
            PatientStratum.MULTIPLE_COMORBIDITIES,
            PatientStratum.CARDIOVASCULAR_HIGH_RISK,
            PatientStratum.HYPERTENSION_STAGE2
        ]

        if stratification in high_priority_strata:
            priority = 5
        elif stratification in [PatientStratum.DIABETES_MODERATE, PatientStratum.DYSLIPIDEMIA_SEVERE]:
            priority = max(priority, 4)
        elif stratification in [PatientStratum.DIABETES_EARLY, PatientStratum.PREDIABETES]:
            priority = max(priority, 3)

        # 基于风险因素数量
        if len(risk_factors) >= 5:
            priority = 5
        elif len(risk_factors) >= 3:
            priority = max(priority, 4)

        return priority

    def generate_stratification_report(self, user_profile, lab_results: ComprehensiveLabResults) -> str:
        """生成患者分层报告"""
        assessment = self.comprehensive_risk_assessment(user_profile, lab_results)

        report = f"""# 患者风险分层与评估报告

## 🏥 基本信息
- **姓名**: {user_profile.name}
- **年龄**: {user_profile.age}岁
- **性别**: {user_profile.gender}
- **BMI**: {user_profile.weight / ((user_profile.height / 100) ** 2):.1f}

## 🎯 风险分层结果
- **患者分层**: {assessment.stratification.value}
- **整体风险等级**: {assessment.overall_risk.value}
- **干预优先级**: {assessment.intervention_priority}/5

## 📊 多维度风险评估
| 风险维度 | 风险等级 | 说明 |
|----------|----------|------|
| 心血管风险 | {assessment.cardiovascular_risk.value} | 基于中国心血管风险评估标准 |
| 糖尿病风险 | {assessment.diabetes_risk.value} | 基于血糖、HbA1c和代谢指标 |
| 肾脏风险 | {assessment.renal_risk.value} | 基于肌酐、尿蛋白等指标 |
| 营养风险 | {assessment.nutritional_risk.value} | 基于BMI、血红蛋白、白蛋白等 |

## ⚠️ 主要风险因素
"""
        for risk_factor in assessment.risk_factors:
            report += f"- {risk_factor}\n"

        report += "\n## ✅ 保护因素\n"
        for protective_factor in assessment.protective_factors:
            report += f"- {protective_factor}\n"

        report += f"""
## 🎯 营养干预建议

基于您的风险分层（{assessment.stratification.value}），建议采用以下营养干预策略：

### 优先干预目标
"""

        # 根据不同分层给出具体建议
        if assessment.stratification == PatientStratum.DIABETES_ADVANCED:
            report += """
1. **严格血糖控制**: 碳水化合物40-45%，优选低升糖指数食物
2. **心血管保护**: 限制饱和脂肪<7%，增加ω-3脂肪酸
3. **肾脏保护**: 蛋白质0.8-1.0g/kg，控制磷和钾摄入
4. **体重管理**: 如需减重，每周减重0.25-0.5kg
"""
        elif assessment.stratification == PatientStratum.HYPERTENSION_STAGE2:
            report += """
1. **血压控制**: 钠摄入<1500mg/天，增加钾摄入3500mg/天
2. **DASH饮食**: 增加蔬果、全谷物、低脂乳制品
3. **体重控制**: 维持健康BMI 18.5-23.9
4. **限制酒精**: 男性<25g/天，女性<15g/天
"""
        elif assessment.stratification == PatientStratum.PREDIABETES:
            report += """
1. **预防糖尿病**: 碳水化合物45-50%，选择复合碳水化合物
2. **体重管理**: 如超重，减重5-10%
3. **增加纤维**: 目标25-35g/天
4. **规律运动**: 配合营养干预，每周150分钟中等强度运动
"""
        else:
            report += """
1. **维持健康**: 平衡膳食，多样化食物选择
2. **预防疾病**: 控制体重，限制钠盐和饱和脂肪
3. **营养充足**: 确保微量营养素充足
4. **生活方式**: 规律运动，戒烟限酒
"""

        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        report += f"""
### 监测指标
根据您的风险等级，建议监测频率：
- **体重**: 每周1次
- **血压**: {"每日1次" if assessment.cardiovascular_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH] else "每周2-3次"}
- **血糖**: {"每日监测" if assessment.diabetes_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH] else "每周1-2次"}
- **实验室检查**: {"3个月1次" if assessment.overall_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH] else "6个月1次"}

---
*报告生成时间: {current_time}*
*本报告基于循证医学证据，具体治疗方案请咨询专科医生*
"""

        return report

# 示例使用
if __name__ == "__main__":
    # 示例患者数据
    from dataclasses import dataclass

    @dataclass
    class ExampleUser:
        name: str = "示例患者"
        age: int = 55
        gender: str = "男"
        height: float = 170
        weight: float = 80

    # 创建分层系统
    stratification_system = EnhancedPatientStratification()

    # 示例实验室结果
    lab_results = ComprehensiveLabResults(
        blood_glucose_fasting=8.2,
        hba1c=7.5,
        cholesterol_total=5.8,
        cholesterol_ldl=3.8,
        cholesterol_hdl=1.1,
        triglycerides=2.1,
        blood_pressure_systolic=145,
        blood_pressure_diastolic=92,
        creatinine=95,
        albumin=42,
        hemoglobin=135
    )

    user = ExampleUser()

    # 生成分层报告
    report = stratification_system.generate_stratification_report(user, lab_results)

    # 保存报告
    with open("/Users/williamsun/Documents/gplus/docs/FoodRecom/患者风险分层报告_示例.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("✅ 增强版患者分层系统创建完成")
    print("📄 示例分层报告已生成: 患者风险分层报告_示例.md")