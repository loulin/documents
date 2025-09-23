#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
糖尿病风险评估脚本
基于PreDiab.md文档实现的完整风险评估流程

适用人群：18-60岁成年非妊娠期未诊断糖尿病人群
作者：基于PreDiab.md技术文档
版本：1.0
"""

import math
import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "低风险"
    MEDIUM = "中风险"
    HIGH = "高风险"
    VERY_HIGH = "极高风险"

class DiabetesStatus(Enum):
    """糖尿病状态枚举"""
    NORMAL = "正常"
    PREDIABETES = "糖尿病前期"
    DIABETES = "糖尿病"
    EXCLUDE = "不适用人群"

@dataclass
class PatientData:
    """患者数据结构"""
    # 基本信息 (必填字段)
    age: int
    gender: str  # "男" 或 "女"
    
    # 体格测量 (必填字段)
    height: float  # cm
    weight: float  # kg
    waist_circumference: float  # cm
    systolic_bp: int  # mmHg
    diastolic_bp: int  # mmHg
    
    # 生化指标 (必填字段)
    fpg: float  # mmol/L
    hba1c: float  # %
    
    # 可选字段 (带默认值)
    is_pregnant: bool = False
    tg: Optional[float] = None  # mmol/L
    hdl_c: Optional[float] = None  # mmol/L
    ldl_c: Optional[float] = None  # mmol/L
    family_history_t2dm: str = "无"  # "无", "二级亲属", "一级亲属"
    history_gdm: bool = False
    history_cvd: bool = False
    history_pcos: bool = False
    exercise_minutes_per_week: int = 0
    smoking_status: str = "从不吸烟"  # "从不吸烟", "既往吸烟", "现在吸烟"
    alcohol_status: str = "不饮酒"  # "不饮酒", "适量饮酒", "过量饮酒"
    sleep_hours_per_day: float = 7.0

class DiabetesRiskAssessment:
    """糖尿病风险评估主类"""
    
    def __init__(self):
        self.assessment_date = datetime.datetime.now()
    
    def check_eligibility(self, patient: PatientData) -> Tuple[bool, str]:
        """检查患者是否适用本评估体系
        
        基于ADA/ISPAD 2024指南的年龄分层标准：
        - <10岁: 青春期前，糖尿病发病率极低
        - 10-18岁: 需要儿童青少年专用评估体系
        - ≥18岁: 适用成人评估体系
        """
        
        # 检查年龄范围(基于ADA/ISPAD 2024指南)
        if patient.age < 18:
            if patient.age < 10:
                return False, "学龄前儿童(<10岁)，青春期前糖尿病发病率极低，如有症状请咨询儿科内分泌专科"
            else:
                return False, "儿童青少年(10-18岁)，请使用儿童青少年专用2型糖尿病评估体系(基于青春期胰岛素抵抗特点)"
        
        if patient.age > 65:
            return False, "老年人群(>65岁)，建议使用老年人专用评估体系"
        
        # 检查妊娠状态
        if patient.is_pregnant:
            return False, "妊娠期女性，请使用GDM专用评估体系"
        
        # 检查是否已确诊糖尿病
        diabetes_status = self._check_diabetes_status(patient)
        if diabetes_status == DiabetesStatus.DIABETES:
            return False, f"已确诊糖尿病(FPG={patient.fpg} mmol/L, HbA1c={patient.hba1c}%)，不适用本评估系统"
        
        # 60-65岁特殊考虑
        if 60 <= patient.age <= 65:
            return True, "接近老年期人群(60-65岁)，可使用本评估体系，但需个体化调整"
        
        return True, "适用本评估体系"
    
    def _check_diabetes_status(self, patient: PatientData) -> DiabetesStatus:
        """检查糖尿病诊断状态"""
        
        # 糖尿病诊断标准
        if patient.fpg >= 7.0 or patient.hba1c >= 6.5:
            return DiabetesStatus.DIABETES
        
        # 糖尿病前期标准
        if (5.6 <= patient.fpg <= 6.9) or (5.7 <= patient.hba1c <= 6.4):
            return DiabetesStatus.PREDIABETES
        
        return DiabetesStatus.NORMAL
    
    def calculate_bmi(self, patient: PatientData) -> float:
        """计算BMI"""
        height_m = patient.height / 100
        return patient.weight / (height_m ** 2)
    
    def assess_metabolic_syndrome(self, patient: PatientData) -> Tuple[bool, List[str]]:
        """评估代谢综合征 (IDF 2005标准，中国修订版)"""
        
        components = []
        
        # 必备条件：中心性肥胖
        waist_threshold = 90 if patient.gender == "男" else 85
        central_obesity = patient.waist_circumference >= waist_threshold
        
        if not central_obesity:
            return False, ["不满足中心性肥胖必备条件"]
        
        components.append("中心性肥胖")
        
        # 其他组分
        additional_components = []
        
        # 甘油三酯
        if patient.tg is not None and patient.tg >= 1.7:
            additional_components.append("甘油三酯升高")
        
        # HDL胆固醇
        hdl_threshold = 1.04 if patient.gender == "男" else 1.30
        if patient.hdl_c is not None and patient.hdl_c < hdl_threshold:
            additional_components.append("HDL胆固醇降低")
        
        # 血压
        if patient.systolic_bp >= 130 or patient.diastolic_bp >= 85:
            additional_components.append("血压升高")
        
        # 空腹血糖
        if patient.fpg >= 5.6:
            additional_components.append("空腹血糖升高")
        
        # 诊断代谢综合征需要≥2个额外组分
        is_metabolic_syndrome = len(additional_components) >= 2
        
        if is_metabolic_syndrome:
            components.extend(additional_components)
        
        return is_metabolic_syndrome, components
    
    def calculate_risk_score(self, patient: PatientData) -> Tuple[int, Dict[str, int]]:
        """计算风险评分 (总分100分)"""
        
        scores = {}
        total_score = 0
        
        # 1. 年龄评分 (最高10分)
        if 18 <= patient.age <= 35:
            age_score = 0
        elif 36 <= patient.age <= 50:
            age_score = 5
        elif 51 <= patient.age <= 60:
            age_score = 10
        else:  # 60-65岁
            age_score = 10
        
        scores["年龄"] = age_score
        total_score += age_score
        
        # 2. BMI评分 (最高15分)
        bmi = self.calculate_bmi(patient)
        if bmi < 24:
            bmi_score = 0
        elif 24 <= bmi < 28:
            bmi_score = 5
        else:  # bmi >= 28
            bmi_score = 10
        
        scores["BMI"] = bmi_score
        total_score += bmi_score
        
        # 3. 腰围评分 (最高8分)
        if patient.gender == "男":
            if patient.waist_circumference < 90:
                waist_score = 0
            elif 90 <= patient.waist_circumference < 95:
                waist_score = 3
            else:
                waist_score = 8
        else:  # 女性
            if patient.waist_circumference < 85:
                waist_score = 0
            elif 85 <= patient.waist_circumference < 90:
                waist_score = 3
            else:
                waist_score = 8
        
        scores["腰围"] = waist_score
        total_score += waist_score
        
        # 4. FPG评分 (最高15分)
        if patient.fpg < 5.6:
            fpg_score = 0
        elif 5.6 <= patient.fpg <= 6.9:
            fpg_score = 15
        else:
            # 应该在适用性检查中被排除
            fpg_score = 15
        
        scores["FPG"] = fpg_score
        total_score += fpg_score
        
        # 5. HbA1c评分 (最高15分)
        if patient.hba1c < 5.7:
            hba1c_score = 0
        elif 5.7 <= patient.hba1c <= 6.4:
            hba1c_score = 15
        else:
            # 应该在适用性检查中被排除
            hba1c_score = 15
        
        scores["HbA1c"] = hba1c_score
        total_score += hba1c_score
        
        # 6. 血压评分 (最高8分)
        if patient.systolic_bp < 130 and patient.diastolic_bp < 85:
            bp_score = 0
        elif (130 <= patient.systolic_bp <= 139) or (85 <= patient.diastolic_bp <= 89):
            bp_score = 3
        else:  # >=140/90
            bp_score = 8
        
        scores["血压"] = bp_score
        total_score += bp_score
        
        # 7. 家族史评分 (最高8分)
        family_score_map = {"无": 0, "二级亲属": 3, "一级亲属": 8}
        family_score = family_score_map.get(patient.family_history_t2dm, 0)
        
        scores["家族史"] = family_score
        total_score += family_score
        
        # 8. 既往史评分 (最高8分)
        if patient.history_gdm or patient.history_cvd:
            history_score = 8
        elif patient.history_pcos:
            history_score = 5
        else:
            history_score = 0
        
        scores["既往史"] = history_score
        total_score += history_score
        
        # 9. 生活方式评分 (最高8分)
        lifestyle_score = self._calculate_lifestyle_score(patient)
        scores["生活方式"] = lifestyle_score
        total_score += lifestyle_score
        
        # 10. 血脂异常评分 (最高5分)
        lipid_score = self._calculate_lipid_score(patient)
        scores["血脂异常"] = lipid_score
        total_score += lipid_score
        
        return total_score, scores
    
    def _calculate_lifestyle_score(self, patient: PatientData) -> int:
        """计算生活方式评分"""
        unhealthy_factors = 0
        
        # 运动不足
        if patient.exercise_minutes_per_week < 150:
            unhealthy_factors += 1
        
        # 吸烟
        if patient.smoking_status == "现在吸烟":
            unhealthy_factors += 1
        
        # 过量饮酒
        if patient.alcohol_status == "过量饮酒":
            unhealthy_factors += 1
        
        # 睡眠异常
        if patient.sleep_hours_per_day < 6 or patient.sleep_hours_per_day > 9:
            unhealthy_factors += 1
        
        # 评分
        if unhealthy_factors == 0:
            return 0  # 健康
        elif unhealthy_factors <= 2:
            return 3  # 一般
        else:
            return 8  # 不良
    
    def _calculate_lipid_score(self, patient: PatientData) -> int:
        """计算血脂异常评分"""
        if patient.tg is None and patient.hdl_c is None:
            return 0
        
        abnormal_count = 0
        
        # TG异常
        if patient.tg is not None and patient.tg >= 1.7:
            abnormal_count += 1
        
        # HDL-C异常
        hdl_threshold = 1.04 if patient.gender == "男" else 1.30
        if patient.hdl_c is not None and patient.hdl_c < hdl_threshold:
            abnormal_count += 1
        
        # LDL-C异常
        if patient.ldl_c is not None and patient.ldl_c >= 3.4:
            abnormal_count += 1
        
        if abnormal_count == 0:
            return 0
        elif abnormal_count == 1:
            return 3  # 单项异常
        else:
            return 5  # 综合异常
    
    def determine_risk_level(self, total_score: int) -> RiskLevel:
        """根据总分确定风险等级"""
        if total_score <= 20:
            return RiskLevel.LOW
        elif total_score <= 40:
            return RiskLevel.MEDIUM
        elif total_score <= 60:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    def calculate_risk_probability(self, total_score: int) -> Dict[str, float]:
        """计算具体发病概率"""
        # 基于logistic回归模型: P = exp(-7.85 + 总分×0.08) / (1 + exp(-7.85 + 总分×0.08))
        logit = -7.85 + total_score * 0.08
        probability = math.exp(logit) / (1 + math.exp(logit))
        
        # 转换为不同时间窗口的风险
        # 1年风险 ≈ 5年风险 / 5
        # 3年风险 ≈ 5年风险 * 0.6
        risk_5_year = probability * 100  # 转换为百分比
        risk_3_year = risk_5_year * 0.6
        risk_1_year = risk_5_year / 5
        
        return {
            "1年发病率": round(risk_1_year, 1),
            "3年发病率": round(risk_3_year, 1),
            "5年发病率": round(risk_5_year, 1)
        }
    
    def get_management_recommendations(self, risk_level: RiskLevel, patient: PatientData) -> Dict[str, List[str]]:
        """获取管理建议"""
        
        recommendations = {
            "筛查频率": [],
            "生活方式干预": [],
            "检查项目": [],
            "专科咨询": [],
            "药物考虑": []
        }
        
        if risk_level == RiskLevel.LOW:
            recommendations["筛查频率"] = ["每3年筛查一次"]
            recommendations["生活方式干预"] = [
                "维持健康饮食结构",
                "规律运动≥150分钟/周",
                "体重管理",
                "戒烟限酒"
            ]
            recommendations["检查项目"] = ["基本生化指标", "风险因素评估"]
            
        elif risk_level == RiskLevel.MEDIUM:
            recommendations["筛查频率"] = ["每1-2年筛查一次"]
            recommendations["生活方式干预"] = [
                "结构化营养指导(每月1次)",
                "运动医师评估(每季度1次)",
                "行为改变支持(每2周1次)",
                "体重减轻5-10%"
            ]
            recommendations["检查项目"] = [
                "FPG、HbA1c、血脂",
                "OGTT(必要时)",
                "血压监测"
            ]
            recommendations["专科咨询"] = ["营养科", "内分泌科(必要时)"]
            
        elif risk_level == RiskLevel.HIGH:
            recommendations["筛查频率"] = ["每6-12个月筛查一次"]
            recommendations["生活方式干预"] = [
                "强化营养治疗(减少300-500kcal/天)",
                "有氧运动150-300分钟/周",
                "抗阻训练≥2次/周",
                "体重管理目标"
            ]
            recommendations["检查项目"] = [
                "FPG、HbA1c、血脂全套、ALT、AST、肌酐、eGFR",
                "OGTT、C肽评估",
                "心血管风险评估",
                "微血管病变筛查"
            ]
            recommendations["专科咨询"] = [
                "内分泌科",
                "营养科",
                "心血管科(必要时)"
            ]
            recommendations["药物考虑"] = [
                "二甲双胍(IGT+肥胖)",
                "阿卡波糖(餐后血糖异常)",
                "他汀类(血脂异常)"
            ]
            
        else:  # VERY_HIGH
            recommendations["筛查频率"] = ["每3-6个月筛查一次"]
            recommendations["生活方式干预"] = [
                "住院或门诊强化管理",
                "多学科团队干预",
                "家庭全面干预",
                "心理健康评估"
            ]
            recommendations["检查项目"] = [
                "自我血糖监测(每周2-3次)",
                "HbA1c每3个月检测",
                "完整代谢评估",
                "并发症全面筛查"
            ]
            recommendations["专科咨询"] = [
                "内分泌科(每月随访)",
                "专科护士",
                "营养师",
                "运动治疗师"
            ]
            recommendations["药物考虑"] = [
                "二甲双胍500-1000mg每日两次",
                "必要时联合用药",
                "心血管保护性药物"
            ]
        
        return recommendations
    
    def generate_report(self, patient: PatientData) -> Dict:
        """生成完整评估报告"""
        
        # 检查适用性
        is_eligible, eligibility_message = self.check_eligibility(patient)
        
        if not is_eligible:
            return {
                "评估日期": self.assessment_date.strftime("%Y-%m-%d %H:%M:%S"),
                "适用性": False,
                "消息": eligibility_message,
                "建议": "请使用相应的专用评估体系"
            }
        
        # 基本计算
        bmi = self.calculate_bmi(patient)
        diabetes_status = self._check_diabetes_status(patient)
        is_metabolic_syndrome, metabolic_components = self.assess_metabolic_syndrome(patient)
        
        # 风险评分
        total_score, score_details = self.calculate_risk_score(patient)
        risk_level = self.determine_risk_level(total_score)
        risk_probabilities = self.calculate_risk_probability(total_score)
        
        # 管理建议
        recommendations = self.get_management_recommendations(risk_level, patient)
        
        # 生成报告
        report = {
            "评估日期": self.assessment_date.strftime("%Y-%m-%d %H:%M:%S"),
            "适用性": True,
            "特殊说明": eligibility_message if "60-65岁" in eligibility_message else None,
            
            "患者基本信息": {
                "年龄": patient.age,
                "性别": patient.gender,
                "BMI": round(bmi, 1),
                "腰围": patient.waist_circumference,
                "血压": f"{patient.systolic_bp}/{patient.diastolic_bp}"
            },
            
            "糖尿病状态": diabetes_status.value,
            
            "代谢综合征": {
                "诊断": "是" if is_metabolic_syndrome else "否",
                "满足组分": metabolic_components
            },
            
            "风险评分": {
                "总分": total_score,
                "详细评分": score_details,
                "风险等级": risk_level.value
            },
            
            "发病风险": risk_probabilities,
            
            "管理建议": recommendations,
            
            "评估依据": "基于PreDiab.md技术文档 - 成年非妊娠期未诊断糖尿病人群风险评估体系"
        }
        
        return report

def main():
    """主函数 - 示例用法"""
    
    # 创建评估实例
    assessor = DiabetesRiskAssessment()
    
    # 示例患者数据
    patient = PatientData(
        age=45,
        gender="男",
        height=175,
        weight=80,
        waist_circumference=95,
        systolic_bp=135,
        diastolic_bp=85,
        fpg=6.2,
        hba1c=6.1,
        tg=2.1,
        hdl_c=0.9,
        family_history_t2dm="一级亲属",
        exercise_minutes_per_week=60,
        smoking_status="现在吸烟"
    )
    
    # 生成评估报告
    report = assessor.generate_report(patient)
    
    # 打印报告
    print("="*60)
    print("糖尿病风险评估报告")
    print("="*60)
    
    for key, value in report.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for k, v in value.items():
                if isinstance(v, dict):
                    print(f"  {k}:")
                    for kk, vv in v.items():
                        print(f"    {kk}: {vv}")
                elif isinstance(v, list):
                    print(f"  {k}:")
                    for item in v:
                        print(f"    - {item}")
                else:
                    print(f"  {k}: {v}")
        elif isinstance(value, list):
            print(f"\n{key}:")
            for item in value:
                print(f"  - {item}")
        else:
            print(f"{key}: {value}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()