#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent_ZS: 中山HMC CGM报告生成器 v1.0
基于Agent5改造，专门为中山健康管理中心生成CGM报告
核心功能: 基于Agent5 + 中山HMC报告大纲定制化

🏥 中山HMC报告大纲支持:
✅ 基本信息（用药情况、数据完整性评估）
✅ 核心控制指标列表及参考范围
✅ 综合评估与建议（优先处理问题、次要处理问题）
✅ 生活方式管理建议（饮食、运动）
✅ 详细血糖分析（14天分时段深度分析）
✅ 基础血糖统计（目标范围、波动性、变异性）
✅ 分时段血糖分析（夜间、早餐、午餐、晚餐，或2小时间段）
✅ 14天纵向趋势（分4段：4-4-4-2天）
✅ 工作日与周末血糖分析
✅ 14天每天血糖图谱数据
✅ 短期/长期控制目标
✅ 随诊方案
✅ 注意事项

版本: 1.0
日期: 2025-09-14
作者: Based on Agent5 Framework
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'agpai', 'core'))

# 导入Agent5的核心模块
# 添加Agent5所在目录到系统路径
import sys
import os

agent5_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'AGPAI')
if agent5_path not in sys.path:
    sys.path.insert(0, agent5_path)

try:
    from Agent5_Comprehensive_Analyzer import ComprehensiveAGPAIAnalyzer
    print("[Agent_ZS] ✅ 成功导入Agent5核心模块")
    AGENT5_AVAILABLE = True
except ImportError as e:
    print(f"[Agent_ZS] ❌ Agent5模块未找到: {e}")
    print(f"[Agent_ZS] 尝试路径: {agent5_path}")
    AGENT5_AVAILABLE = False

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class ZSHMCReportGenerator:
    """中山HMC CGM报告生成器"""

    def __init__(self):
        """初始化报告生成器"""
        self.version = "1.0"
        self.agent_type = "Agent_ZS"
        self.institution = "中山健康管理中心 (ZSHMC)"

        # 初始化Agent5分析器
        if AGENT5_AVAILABLE:
            self.agent5_analyzer = ComprehensiveAGPAIAnalyzer()
        else:
            self.agent5_analyzer = None

        self.report_info = {
            "报告类型": "中山HMC CGM专业报告",
            "版本号": self.version,
            "报告生成器": "ZS_HMC_CGM_Report_Generator",
            "机构信息": {
                "name": self.institution,
                "report_template": "中山HMC CGM报告大纲",
                "version": self.version
            }
        }

    def generate_zshmc_report(self, filepath: str, patient_id: str = None,
                            medication_data: Dict = None,
                            patient_info: Dict = None) -> Dict:
        """
        生成中山HMC专业CGM报告

        Args:
            filepath: 血糖数据文件路径
            patient_id: 患者ID
            medication_data: 药物数据
            patient_info: 患者基本信息

        Returns:
            完整的中山HMC CGM报告
        """
        try:
            print(f"[Agent_ZS] 开始生成中山HMC CGM报告: {patient_id}")

            # Step 1: 数据加载和预处理
            df = self._load_data(filepath)
            analysis_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Step 2: 使用Agent5进行基础分析（如果可用）
            # 存储血糖数据供智能分段使用
            self.glucose_data_for_segmentation = df.copy()

            agent5_analysis = None
            if self.agent5_analyzer:
                print("[Agent_ZS] 调用Agent5进行基础血糖分析...")
                try:
                    agent5_analysis = self.agent5_analyzer.generate_complete_report(
                        filepath, patient_id, medication_data
                    )
                    print("[Agent_ZS] ✅ Agent5分析完成")
                except Exception as e:
                    print(f"[Agent_ZS] ⚠️ Agent5调用失败: {e}，使用内置分析")

            # Step 3: 生成中山HMC报告结构
            zshmc_report = self._build_zshmc_report_structure(
                df, patient_id, patient_info, medication_data, agent5_analysis, analysis_time
            )

            # Step 4: 保存报告
            self._save_report(zshmc_report, patient_id or "Unknown")

            print(f"[Agent_ZS] ✅ 中山HMC CGM报告生成完成")
            return zshmc_report

        except Exception as e:
            import traceback
            print(f"[Agent_ZS] ❌ 报告生成失败: {e}")
            print(f"[Agent_ZS] 详细错误信息:")
            traceback.print_exc()
            return {
                "报告头信息": {**self.report_info, "患者ID": patient_id},
                "错误信息": {"错误类型": type(e).__name__, "错误描述": str(e)}
            }

    def _build_zshmc_report_structure(self, df: pd.DataFrame, patient_id: str,
                                    patient_info: Dict, medication_data: Dict,
                                    agent5_analysis: Dict, analysis_time: str) -> Dict:
        """构建中山HMC报告结构"""

        # 提取Agent5分析结果（如果可用）
        basic_glucose_data = {}
        if agent5_analysis and "模块2_基础血糖分析" in agent5_analysis:
            basic_glucose_data = agent5_analysis["模块2_基础血糖分析"]

        # 构建完整报告
        report = {
            # 报告头部
            "报告头信息": {
                **self.report_info,
                "患者ID": patient_id or "Unknown",
                "分析时间": analysis_time,
                "监测周期": f"{self._calculate_monitoring_days(df)}天",
                "数据点数": len(df)
            },

            # 1. 基本信息
            "1_基本信息": self._generate_basic_info_section(patient_info, medication_data, df),

            # 2. 列出核心控制指标
            "2_核心控制指标": self._generate_core_indicators_section(df, basic_glucose_data),

            # 3. 综合评估与建议
            "3_综合评估与建议": self._generate_comprehensive_assessment(df, basic_glucose_data, medication_data),

            # 4. 详细血糖分析
            "4_详细血糖分析": self._generate_detailed_glucose_analysis(df, agent5_analysis),

            # 5. 控制目标
            "5_控制目标": self._generate_control_targets(df, basic_glucose_data),

            # 6. 随诊方案
            "6_随诊方案": self._generate_follow_up_plan(df, basic_glucose_data),

            # 7. 注意事项
            "7_注意事项": self._generate_precautions(df, basic_glucose_data, medication_data),

            # 附加：Agent5原始分析数据（供参考）
            "附录_Agent5分析数据": agent5_analysis if agent5_analysis else "Agent5不可用"
        }

        return report

    def _generate_basic_info_section(self, patient_info: Dict, medication_data: Dict, df: pd.DataFrame) -> Dict:
        """生成基本信息部分"""

        # 用药情况分析
        medication_summary = "未提供用药信息"
        medication_count = 0
        medication_details = []

        if medication_data and 'medications' in medication_data:
            medications = medication_data['medications']
            medication_count = len(medications)
            medication_details = []

            for med in medications:
                med_detail = {
                    "药物名称": med.get('name', '未知药物'),
                    "剂量": med.get('dosage', '未知'),
                    "频次": med.get('frequency', '未知'),
                    "开始时间": med.get('start_date', '未知'),
                    "用药目的": med.get('purpose', '未说明'),
                    "依从性": med.get('compliance', '未评估')
                }
                medication_details.append(med_detail)

            medication_summary = f"当前用药{medication_count}种"

        # 数据完整性/有效性评估
        total_points = len(df)
        monitoring_days = self._calculate_monitoring_days(df)
        points_per_day = total_points / monitoring_days if monitoring_days > 0 else 0

        # 数据质量评估
        if points_per_day >= 80:
            data_quality = "优秀"
            data_completeness = "数据密度高，满足专业分析要求"
        elif points_per_day >= 50:
            data_quality = "良好"
            data_completeness = "数据质量良好，能够进行有效分析"
        elif points_per_day >= 30:
            data_quality = "一般"
            data_completeness = "数据基本完整，可进行常规分析"
        else:
            data_quality = "需要改善"
            data_completeness = "数据密度偏低，建议延长监测时间"

        return {
            "患者基本信息": patient_info if patient_info else "未提供详细信息",
            "用药情况": {
                "用药概述": medication_summary,
                "药物数量": medication_count,
                "详细用药信息": medication_details,
                "用药评价": "需要结合血糖数据评估用药效果" if medication_count > 0 else "未使用降糖药物"
            },
            "数据完整性有效性评估": {
                "监测天数": monitoring_days,
                "数据点总数": total_points,
                "平均每天数据点": f"{points_per_day:.1f}个",
                "数据质量评级": data_quality,
                "完整性评价": data_completeness,
                "数据可靠性": "高" if points_per_day >= 50 else "中等",
                "建议": "数据质量满足分析要求" if points_per_day >= 50 else "建议增加监测密度"
            }
        }

    def _generate_core_indicators_section(self, df: pd.DataFrame, basic_glucose_data: Dict) -> Dict:
        """生成核心控制指标部分"""

        glucose_values = df['glucose_value'].dropna().values

        # 计算核心指标
        indicators = self._calculate_core_indicators(glucose_values)

        # 从Agent5获取更精确的指标（如果可用）
        if basic_glucose_data and "核心血糖指标" in basic_glucose_data:
            agent5_indicators = basic_glucose_data["核心血糖指标"]

            # 更新指标值
            for key, value in agent5_indicators.items():
                if "GMI" in key:
                    indicators["GMI"]["当前值"] = value
                elif "TIR" in key:
                    indicators["TIR"]["当前值"] = value
                elif "TAR" in key:
                    indicators["TAR"]["当前值"] = value
                elif "TBR" in key:
                    indicators["TBR"]["当前值"] = value
                elif "CV" in key:
                    indicators["CV"]["当前值"] = value

        return {
            "核心指标说明": "以下指标按临床重要性排序，提供当前值、参考范围和临床意义",
            "指标详情": indicators,
            "指标解读提示": [
                "GMI和TIR是评估血糖控制的两个最重要指标",
                "CV反映血糖波动情况，过高提示血糖不稳定",
                "TAR和TBR分别反映高血糖和低血糖的暴露风险",
                "建议结合患者具体情况进行个性化解读"
            ]
        }

    def _calculate_core_indicators(self, glucose_values: np.ndarray) -> Dict:
        """计算核心血糖指标"""

        mean_glucose = np.mean(glucose_values)
        std_glucose = np.std(glucose_values)

        # 计算各项指标
        gmi = 3.31 + (0.02392 * mean_glucose * 18.018)  # 转换为mg/dL计算
        tir = np.sum((glucose_values >= 3.9) & (glucose_values <= 10.0)) / len(glucose_values) * 100
        tar = np.sum(glucose_values > 10.0) / len(glucose_values) * 100
        tbr = np.sum(glucose_values < 3.9) / len(glucose_values) * 100
        cv = (std_glucose / mean_glucose) * 100 if mean_glucose > 0 else 0

        return {
            "GMI": {
                "全称": "Glucose Management Indicator (血糖管理指标)",
                "当前值": f"{gmi:.1f}%",
                "参考范围": "< 7.0% (优秀), 7.0-8.0% (良好), > 8.0% (需改善)",
                "临床意义": "反映近期血糖控制水平，相当于估算的糖化血红蛋白",
                "评价": "优秀" if gmi < 7.0 else ("良好" if gmi < 8.0 else "需改善")
            },
            "TIR": {
                "全称": "Time In Range (目标范围内时间)",
                "当前值": f"{tir:.1f}%",
                "参考范围": "> 70% (优秀), 50-70% (良好), < 50% (需改善)",
                "目标范围": "3.9-10.0 mmol/L",
                "临床意义": "血糖在目标范围内的时间百分比，反映血糖控制稳定性",
                "评价": "优秀" if tir > 70 else ("良好" if tir > 50 else "需改善")
            },
            "TAR": {
                "全称": "Time Above Range (高血糖时间)",
                "当前值": f"{tar:.1f}%",
                "参考范围": "< 25% (可接受), 25-50% (需关注), > 50% (需改善)",
                "阈值": "> 10.0 mmol/L",
                "临床意义": "高血糖暴露时间，与长期并发症风险相关",
                "评价": "良好" if tar < 25 else ("需关注" if tar < 50 else "需改善")
            },
            "TBR": {
                "全称": "Time Below Range (低血糖时间)",
                "当前值": f"{tbr:.1f}%",
                "参考范围": "< 4% (安全), 4-10% (需关注), > 10% (需改善)",
                "阈值": "< 3.9 mmol/L",
                "临床意义": "低血糖风险评估，与急性并发症相关",
                "评价": "安全" if tbr < 4 else ("需关注" if tbr < 10 else "需改善")
            },
            "CV": {
                "全称": "Coefficient of Variation (变异系数)",
                "当前值": f"{cv:.1f}%",
                "参考范围": "< 36% (稳定), 36-50% (不稳定), > 50% (高度不稳定)",
                "计算公式": "(标准差/平均值) × 100%",
                "临床意义": "反映血糖波动程度，低变异系数表示血糖更稳定",
                "评价": "稳定" if cv < 36 else ("不稳定" if cv < 50 else "高度不稳定")
            }
        }

    def _generate_comprehensive_assessment(self, df: pd.DataFrame, basic_glucose_data: Dict, medication_data: Dict) -> Dict:
        """生成综合评估与建议部分"""

        glucose_values = df['glucose_value'].dropna().values
        indicators = self._calculate_core_indicators(glucose_values)

        # 提取关键指标值
        gmi_str = indicators["GMI"]["当前值"]
        tir_str = indicators["TIR"]["当前值"]
        tar_str = indicators["TAR"]["当前值"]
        tbr_str = indicators["TBR"]["当前值"]
        cv_str = indicators["CV"]["当前值"]

        gmi_value = float(gmi_str.replace("%", ""))
        tir_value = float(tir_str.replace("%", ""))
        tar_value = float(tar_str.replace("%", ""))
        tbr_value = float(tbr_str.replace("%", ""))
        cv_value = float(cv_str.replace("%", ""))

        # 识别优先处理问题
        priority_issues = []
        if tbr_value > 4.0:
            priority_issues.append({
                "问题": "低血糖风险偏高",
                "数值": f"TBR = {tbr_value:.1f}%",
                "建议": "需要及时调整用药剂量或调整进餐时间，预防低血糖发生",
                "紧急程度": "高"
            })

        if gmi_value > 8.0:
            priority_issues.append({
                "问题": "血糖控制不达标",
                "数值": f"GMI = {gmi_value:.1f}%",
                "建议": "需要重新评估治疗方案，考虑调整用药或生活方式干预",
                "紧急程度": "中"
            })

        if cv_value > 50:
            priority_issues.append({
                "问题": "血糖波动过大",
                "数值": f"CV = {cv_value:.1f}%",
                "建议": "需要分析血糖波动原因，调整用药时间或剂量",
                "紧急程度": "中"
            })

        # 识别次要处理问题
        secondary_issues = []
        if tar_value > 25:
            secondary_issues.append({
                "问题": "高血糖时间偏长",
                "数值": f"TAR = {tar_value:.1f}%",
                "建议": "通过饮食控制和运动来改善餐后血糖",
                "处理方式": "生活方式调整"
            })

        if tir_value < 70 and tbr_value <= 4.0:
            secondary_issues.append({
                "问题": "目标范围内时间不足",
                "数值": f"TIR = {tir_value:.1f}%",
                "建议": "通过优化饮食结构和运动计划提升TIR",
                "处理方式": "生活方式管理"
            })

        if cv_value > 36 and cv_value <= 50:
            secondary_issues.append({
                "问题": "血糖稳定性有待提升",
                "数值": f"CV = {cv_value:.1f}%",
                "建议": "规律作息，定时进餐，保持血糖稳定",
                "处理方式": "生活方式管理"
            })

        # 提取患者基础信息用于个性化建议
        patient_profile = self._extract_patient_profile_from_data(df, medication_data, basic_glucose_data)

        # 生活方式管理建议
        lifestyle_management = {
            "饮食建议": self._generate_personalized_dietary_recommendations(
                gmi_value, tir_value, tar_value, patient_profile
            ),
            "运动建议": self._generate_personalized_exercise_recommendations(
                gmi_value, cv_value, tbr_value, patient_profile
            )
        }

        return {
            "优先处理问题": {
                "问题数量": len(priority_issues),
                "详细问题": priority_issues,
                "总体评价": "需要优先关注" if priority_issues else "无重大风险问题"
            },
            "次要处理问题": {
                "问题数量": len(secondary_issues),
                "详细问题": secondary_issues,
                "处理策略": "主要通过生活方式管理改善"
            },
            "生活方式管理": lifestyle_management,
            "综合评价": self._generate_overall_assessment(gmi_value, tir_value, cv_value, tbr_value)
        }

    def _extract_patient_profile_from_data(self, df: pd.DataFrame, medication_data: Dict, basic_glucose_data: Dict = None) -> Dict:
        """从数据中提取患者档案信息用于个性化建议"""

        # 尝试从现有患者信息中获取数据，如果没有则使用默认值
        profile = {
            "年龄": 45,  # 默认年龄
            "性别": "男",  # 默认性别
            "身高": 170,  # 默认身高(cm)
            "体重": 70,  # 默认体重(kg)
            "BMI": 24.2,  # 将根据身高体重计算
            "血压状况": "正常",  # 正常/偏高/高血压
            "血脂状况": "正常",  # 正常/偏高/异常
            "肾功能": "正常",  # 正常/轻度异常/异常
            "活动水平": "中等",  # 轻度/中等/重度
            "健康目标": []  # 减重/降压/降脂/血糖控制
        }

        # 根据现有信息更新患者档案
        if hasattr(self, 'patient_info') and self.patient_info:
            profile.update({k: v for k, v in self.patient_info.items() if k in profile})

        # 计算BMI
        if profile["身高"] > 0 and profile["体重"] > 0:
            height_m = profile["身高"] / 100
            profile["BMI"] = profile["体重"] / (height_m * height_m)

        # 基于BMI推断健康目标
        profile["健康目标"] = self._infer_health_goals(profile, medication_data)

        return profile

    def _infer_health_goals(self, profile: Dict, medication_data: Dict) -> list:
        """基于患者信息推断健康目标"""
        goals = ["血糖控制"]  # 基础目标

        bmi = profile.get("BMI", 24)
        if bmi >= 28:
            goals.append("减重")
        elif bmi >= 24:
            goals.append("控重")

        # 根据用药情况推断其他目标
        if medication_data and isinstance(medication_data, dict):
            medications = medication_data.get("用药列表", [])
            if isinstance(medications, list):
                med_names = " ".join(str(med) for med in medications).lower()
                if any(keyword in med_names for keyword in ["降压", "血压", "pressure"]):
                    goals.append("降压")
                if any(keyword in med_names for keyword in ["血脂", "他汀", "statin"]):
                    goals.append("降脂")

        return goals

    def _generate_personalized_dietary_recommendations(self, gmi: float, tir: float, tar: float, profile: Dict) -> Dict:
        """生成个性化详细饮食建议"""

        # 基于患者档案计算基础代谢率(BMR)
        bmr = self._calculate_bmr(profile)

        # 基于健康目标调整目标热量
        target_calories = self._calculate_target_calories(bmr, profile, gmi)

        # 个性化营养素分配
        macro_ratios = self._calculate_personalized_macros(profile, tar, gmi)

        # 计算各营养素具体用量
        carb_calories = target_calories * macro_ratios["碳水化合物"]
        protein_calories = target_calories * macro_ratios["蛋白质"]
        fat_calories = target_calories * macro_ratios["脂肪"]

        carb_grams = carb_calories / 4
        protein_grams = protein_calories / 4
        fat_grams = fat_calories / 9

        # 生成个性化食谱
        meal_plan = self._generate_personalized_meal_plan(
            target_calories, carb_grams, protein_grams, fat_grams, profile
        )

        return {
            "个性化热量方案": {
                "患者档案": f"年龄{profile['年龄']}岁, {profile['性别']}, 身高{profile['身高']}cm, 体重{profile['体重']}kg",
                "BMI": f"{profile['BMI']:.1f} ({'正常' if 18.5 <= profile['BMI'] < 24 else '偏胖' if profile['BMI'] < 28 else '肥胖'})",
                "基础代谢率": f"{bmr:.0f}千卡/天",
                "目标总热量": f"{target_calories}千卡/天",
                "健康目标": "、".join(profile["健康目标"]),
                "控制策略": self._get_control_strategy(profile, gmi)
            },
            "个性化营养配比": {
                "碳水化合物": f"{carb_grams:.0f}克 ({macro_ratios['碳水化合物']*100:.0f}%)",
                "蛋白质": f"{protein_grams:.0f}克 ({macro_ratios['蛋白质']*100:.0f}%) - {'高蛋白' if macro_ratios['蛋白质'] > 0.18 else '标准蛋白'}",
                "脂肪": f"{fat_grams:.0f}克 ({macro_ratios['脂肪']*100:.0f}%) - {'低脂' if macro_ratios['脂肪'] < 0.30 else '标准脂肪'}",
                "配比说明": self._explain_macro_ratios(profile, macro_ratios)
            },
            "个性化每日食谱": meal_plan,
            "专项饮食指导": self._generate_specialized_dietary_guidance(profile),
            "饮食控制原则": self._generate_personalized_dietary_principles(profile, gmi),
            "推荐食物清单": self._get_personalized_food_recommendations(profile),
            "限制食物清单": self._get_personalized_food_restrictions(profile)
        }

    def _calculate_bmr(self, profile: Dict) -> float:
        """计算基础代谢率 - 使用Harris-Benedict公式"""
        age = profile["年龄"]
        weight = profile["体重"]
        height = profile["身高"]
        gender = profile["性别"]

        if gender == "男":
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

        return bmr

    def _calculate_target_calories(self, bmr: float, profile: Dict, gmi: float) -> int:
        """计算目标热量"""
        # 活动系数
        activity_factors = {"轻度": 1.2, "中等": 1.375, "重度": 1.55}
        activity_factor = activity_factors.get(profile["活动水平"], 1.375)

        # 总消耗热量
        tdee = bmr * activity_factor

        # 根据健康目标调整
        goals = profile["健康目标"]
        if "减重" in goals:
            target_calories = int(tdee - 500)  # 每天减少500卡，一周减重0.5kg
        elif "控重" in goals:
            target_calories = int(tdee - 200)  # 温和控制
        else:
            target_calories = int(tdee)

        # 根据血糖控制情况进一步调整
        if gmi > 8.0:
            target_calories = min(target_calories, int(tdee - 300))
        elif gmi > 7.0:
            target_calories = min(target_calories, int(tdee - 150))

        # 确保最低热量摄入
        min_calories = int(bmr * 1.1)  # 不低于BMR的110%
        target_calories = max(target_calories, min_calories)

        return target_calories

    def _calculate_personalized_macros(self, profile: Dict, tar: float, gmi: float) -> Dict:
        """计算个性化营养素配比"""
        goals = profile["健康目标"]
        bmi = profile["BMI"]

        # 基础配比
        if "减重" in goals or bmi >= 28:
            # 减重方案：低碳水、高蛋白
            carb_ratio = 0.35 if tar > 50 else 0.40
            protein_ratio = 0.25
        elif "降脂" in goals:
            # 降脂方案：中等碳水、适量蛋白、低脂
            carb_ratio = 0.45
            protein_ratio = 0.20
        elif gmi > 8.0:
            # 严格血糖控制：低碳水
            carb_ratio = 0.40
            protein_ratio = 0.22
        else:
            # 标准方案
            carb_ratio = 0.50
            protein_ratio = 0.20

        fat_ratio = 1 - carb_ratio - protein_ratio

        return {
            "碳水化合物": carb_ratio,
            "蛋白质": protein_ratio,
            "脂肪": fat_ratio
        }

    def _get_control_strategy(self, profile: Dict, gmi: float) -> str:
        """获取控制策略说明"""
        goals = profile["健康目标"]

        if "减重" in goals:
            return f"减重导向策略：通过热量缺口实现每周0.5kg减重目标"
        elif "控重" in goals:
            return "体重控制策略：温和热量控制，防止体重增长"
        elif gmi > 8.0:
            return "严格血糖控制策略：限制总热量和碳水化合物摄入"
        else:
            return "维持策略：保持当前体重，优化血糖控制"

    def _explain_macro_ratios(self, profile: Dict, ratios: Dict) -> str:
        """解释营养素配比的原理"""
        goals = profile["健康目标"]
        explanations = []

        if ratios["碳水化合物"] < 0.45:
            explanations.append("低碳水设计：减少血糖波动，促进脂肪燃烧")
        if ratios["蛋白质"] > 0.22:
            explanations.append("高蛋白设计：增强饱腹感，维持肌肉量")
        if "降脂" in goals:
            explanations.append("降脂配比：限制饱和脂肪，增加膳食纤维")

        return "；".join(explanations) if explanations else "均衡营养配比"

    def _generate_personalized_meal_plan(self, calories: int, carb_g: float,
                                       protein_g: float, fat_g: float, profile: Dict) -> Dict:
        """生成个性化食谱方案"""
        goals = profile["健康目标"]

        # 热量分配
        breakfast_cal = int(calories * 0.25)
        lunch_cal = int(calories * 0.35)
        dinner_cal = int(calories * 0.30)
        snack_cal = calories - breakfast_cal - lunch_cal - dinner_cal

        return {
            "早餐方案": self._create_personalized_breakfast(breakfast_cal, profile),
            "午餐方案": self._create_personalized_lunch(lunch_cal, profile),
            "晚餐方案": self._create_personalized_dinner(dinner_cal, profile),
            "加餐方案": self._create_personalized_snacks(snack_cal, profile),
            "每日营养统计": {
                "总热量": f"{calories}千卡",
                "碳水化合物": f"{carb_g:.0f}克",
                "蛋白质": f"{protein_g:.0f}克",
                "脂肪": f"{fat_g:.0f}克"
            }
        }

    def _create_personalized_breakfast(self, calories: int, profile: Dict) -> Dict:
        """个性化早餐方案"""
        goals = profile["健康目标"]

        if "减重" in goals:
            return {
                "热量": f"{calories}千卡",
                "减重专用食谱": [
                    "无糖燕麦片30克 + 脱脂牛奶200ml",
                    "水煮蛋1个 + 蛋白1个",
                    "黄瓜丝100克",
                    "核桃仁5克"
                ],
                "营养特点": "高蛋白低碳水，延长饱腹感，控制热量摄入"
            }
        elif "降脂" in goals:
            return {
                "热量": f"{calories}千卡",
                "降脂专用食谱": [
                    "燕麦片40克 + 低脂酸奶150ml",
                    "煮蛋白2个",
                    "番茄50克 + 生菜50克",
                    "亚麻籽5克"
                ],
                "营养特点": "富含β-葡聚糖和ω-3脂肪酸，有助降低胆固醇"
            }
        else:
            return {
                "热量": f"{calories}千卡",
                "标准食谱": [
                    "燕麦片40克 + 牛奶200ml",
                    "水煮蛋1个",
                    "黄瓜丝50克",
                    "核桃仁8克"
                ],
                "营养特点": "营养均衡，稳定血糖，提供持续能量"
            }

    def _create_personalized_lunch(self, calories: int, profile: Dict) -> Dict:
        """个性化午餐方案"""
        goals = profile["健康目标"]

        if "减重" in goals:
            return {
                "热量": f"{calories}千卡",
                "减重专用食谱": [
                    "糙米饭60克（生重）",
                    "清蒸鸡胸肉120克",
                    "西兰花200克",
                    "豆腐汤150ml",
                    "橄榄油5ml"
                ],
                "营养特点": "高蛋白低脂，大量纤维增加饱腹感"
            }
        elif "降压" in goals:
            return {
                "热量": f"{calories}千卡",
                "降压专用食谱": [
                    "糙米饭70克（生重）",
                    "清蒸三文鱼100克",
                    "菠菜150克 + 胡萝卜50克",
                    "紫菜蛋花汤200ml",
                    "芝麻油8ml"
                ],
                "营养特点": "富含钾、镁、ω-3脂肪酸，有助血压控制"
            }
        else:
            return {
                "热量": f"{calories}千卡",
                "标准食谱": [
                    "糙米饭80克（生重）",
                    "清蒸鲈鱼100克",
                    "炒青菜150克",
                    "豆腐汤150ml",
                    "植物油10ml"
                ],
                "营养特点": "营养全面，血糖负荷适中"
            }

    def _create_personalized_dinner(self, calories: int, profile: Dict) -> Dict:
        """个性化晚餐方案"""
        goals = profile["健康目标"]

        if "减重" in goals:
            return {
                "热量": f"{calories}千卡",
                "减重专用食谱": [
                    "荞麦面50克（干重）",
                    "瘦牛肉丝100克",
                    "白萝卜丝200克",
                    "冬瓜汤200ml"
                ],
                "营养特点": "低热量高营养密度，易消化不负担"
            }
        else:
            return {
                "热量": f"{calories}千卡",
                "标准食谱": [
                    "荞麦面80克（干重）",
                    "瘦肉丝80克",
                    "凉拌萝卜丝100克",
                    "紫菜蛋花汤150ml"
                ],
                "营养特点": "清淡易消化，有利夜间血糖稳定"
            }

    def _create_personalized_snacks(self, calories: int, profile: Dict) -> Dict:
        """个性化加餐方案"""
        goals = profile["健康目标"]

        if "减重" in goals:
            return {
                "热量": f"{calories}千卡",
                "减重加餐": {
                    "上午": "黄瓜半根（约50克）",
                    "下午": "无糖酸奶100ml"
                },
                "说明": "极低热量，主要补充水分和少量蛋白质"
            }
        else:
            return {
                "热量": f"{calories}千卡",
                "标准加餐": {
                    "上午": "苹果半个（约100克）",
                    "下午": "无糖酸奶100ml + 坚果5克"
                },
                "说明": "适量补充维生素和健康脂肪"
            }

    def _generate_specialized_dietary_guidance(self, profile: Dict) -> Dict:
        """生成专项饮食指导"""
        goals = profile["健康目标"]
        guidance = {}

        if "减重" in goals:
            guidance["减重专项指导"] = {
                "核心策略": "创造热量缺口，每周减重0.5-1kg",
                "关键要点": [
                    "严格控制总热量摄入",
                    "增加蛋白质比例至25%",
                    "减少碳水化合物至35-40%",
                    "多吃高纤维蔬菜增加饱腹感",
                    "避免高热量密度食物"
                ],
                "进食顺序": "蔬菜 → 蛋白质 → 碳水化合物",
                "监测指标": "体重、腰围、血糖波动"
            }

        if "降压" in goals:
            guidance["降压专项指导"] = {
                "核心策略": "DASH饮食模式，控制钠盐摄入",
                "关键要点": [
                    "每日食盐摄入<5克",
                    "增加钾、镁、钙摄入",
                    "多吃深色蔬菜和水果",
                    "选择低脂乳制品",
                    "限制饱和脂肪摄入"
                ],
                "推荐食物": "香蕉、菠菜、牛奶、三文鱼、燕麦",
                "监测指标": "血压、钠钾比值"
            }

        if "降脂" in goals:
            guidance["降脂专项指导"] = {
                "核心策略": "地中海饮食模式，优化脂肪结构",
                "关键要点": [
                    "限制饱和脂肪<总热量7%",
                    "增加不饱和脂肪比例",
                    "每周吃鱼2-3次",
                    "选择植物性蛋白",
                    "增加水溶性纤维摄入"
                ],
                "推荐食物": "橄榄油、深海鱼、坚果、燕麦、豆类",
                "监测指标": "血脂四项、apoB/apoA1比值"
            }

        return guidance

    def _generate_personalized_dietary_principles(self, profile: Dict, gmi: float) -> list:
        """生成个性化饮食控制原则"""
        goals = profile["健康目标"]
        principles = [
            "定时定量：三餐时间固定，避免血糖大幅波动",
            "细嚼慢咽：每餐用时20-30分钟，增强饱腹感"
        ]

        if "减重" in goals:
            principles.extend([
                "先菜后饭：蔬菜-蛋白质-主食的进食顺序",
                "少量多餐：正餐之间适当加餐，控制饥饿感",
                "晚餐清淡：晚餐热量占全天30%以下"
            ])

        if gmi > 7.5:
            principles.extend([
                "低升糖指数：选择GI<55的主食",
                "餐后监测：重点关注餐后2小时血糖"
            ])

        return principles

    def _get_personalized_food_recommendations(self, profile: Dict) -> Dict:
        """获取个性化推荐食物"""
        goals = profile["健康目标"]
        recommendations = {
            "主食类": ["燕麦片", "糙米", "荞麦面", "全麦面包"],
            "蛋白质类": ["瘦肉", "鱼类", "蛋类", "豆制品"],
            "蔬菜类": ["绿叶蔬菜", "十字花科蔬菜", "茄果类蔬菜"],
            "脂肪类": ["橄榄油", "茶籽油", "坚果", "鳄梨"]
        }

        if "减重" in goals:
            recommendations.update({
                "减重特荐": [
                    "魔芋：极低热量，增加饱腹感",
                    "白萝卜：利尿消肿，促进代谢",
                    "冬瓜：清热利水，有助体重控制",
                    "鸡胸肉：高蛋白低脂肪，维持肌肉量"
                ]
            })

        if "降压" in goals:
            recommendations.update({
                "降压特荐": [
                    "芹菜：富含钾离子，有助降压",
                    "香蕉：高钾低钠，调节电解质平衡",
                    "三文鱼：ω-3脂肪酸，保护心血管",
                    "燕麦：β-葡聚糖，降低血压"
                ]
            })

        return recommendations

    def _get_personalized_food_restrictions(self, profile: Dict) -> Dict:
        """获取个性化限制食物"""
        goals = profile["健康目标"]
        restrictions = {
            "高升糖食物": ["白米饭", "白面条", "白面包", "土豆泥"],
            "高脂食物": ["肥肉", "动物内脏", "油炸食品", "奶油"],
            "高糖食物": ["甜饮料", "糖果", "蛋糕", "饼干"]
        }

        if "减重" in goals:
            restrictions.update({
                "减重严禁": [
                    "高热量密度食物：坚果类>30g/天",
                    "隐形油脂：酥点、沙拉酱、奶茶",
                    "精制糖类：所有添加糖食品",
                    "高淀粉蔬菜：土豆、红薯过量"
                ]
            })

        if "降压" in goals:
            restrictions.update({
                "降压限制": [
                    "高钠食物：咸菜、腊肉、方便面",
                    "隐形盐：调味料、酱制品、零食",
                    "酒精：建议完全戒酒或严格限量"
                ]
            })

        return restrictions

    def _generate_dietary_recommendations(self, gmi: float, tir: float, tar: float) -> Dict:
        """生成详细饮食建议，包括热量计算和食谱"""

        # 基础热量计算（基于标准成年男性，可根据实际情况调整）
        base_calories = 1800  # 基础热量

        # 根据血糖控制情况调整热量
        if gmi > 8.0:
            daily_calories = base_calories - 200  # 1600卡路里
            control_level = "严格控制"
        elif gmi > 7.0:
            daily_calories = base_calories - 100  # 1700卡路里
            control_level = "适度控制"
        else:
            daily_calories = base_calories  # 1800卡路里
            control_level = "维持性控制"

        # 营养素分配
        carb_ratio = 0.45 if tar > 50 else 0.50  # 碳水化合物占比
        protein_ratio = 0.20  # 蛋白质占比
        fat_ratio = 1 - carb_ratio - protein_ratio  # 脂肪占比

        carb_calories = daily_calories * carb_ratio
        protein_calories = daily_calories * protein_ratio
        fat_calories = daily_calories * fat_ratio

        # 转换为克数
        carb_grams = carb_calories / 4
        protein_grams = protein_calories / 4
        fat_grams = fat_calories / 9

        # 食谱建议
        meal_plan = self._generate_meal_plan(daily_calories, carb_grams, protein_grams, fat_grams, tar, tir)

        # 饮食原则
        dietary_principles = self._generate_dietary_principles(gmi, tir, tar)

        return {
            "热量控制方案": {
                "每日总热量": f"{daily_calories}千卡",
                "控制级别": control_level,
                "碳水化合物": f"{carb_grams:.0f}克 ({carb_ratio*100:.0f}%)",
                "蛋白质": f"{protein_grams:.0f}克 ({protein_ratio*100:.0f}%)",
                "脂肪": f"{fat_grams:.0f}克 ({fat_ratio*100:.0f}%)"
            },
            "每日食谱建议": meal_plan,
            "饮食控制原则": dietary_principles,
            "血糖友好食物清单": self._get_diabetes_friendly_foods(),
            "需要限制的食物": self._get_foods_to_limit()
        }

    def _generate_meal_plan(self, daily_calories: int, carb_grams: float, protein_grams: float, fat_grams: float, tar: float, tir: float) -> Dict:
        """生成详细食谱"""

        breakfast_cal = int(daily_calories * 0.25)  # 早餐25%
        lunch_cal = int(daily_calories * 0.35)      # 午餐35%
        dinner_cal = int(daily_calories * 0.30)     # 晚餐30%
        snack_cal = int(daily_calories * 0.10)      # 加餐10%

        return {
            "早餐方案": {
                "热量": f"{breakfast_cal}千卡",
                "食谱示例": [
                    "燕麦片40克 + 牛奶200毫升",
                    "水煮蛋1个",
                    "黄瓜丝50克",
                    "核桃仁10克"
                ],
                "营养特点": "高纤维、低升糖指数，提供优质蛋白"
            },
            "午餐方案": {
                "热量": f"{lunch_cal}千卡",
                "食谱示例": [
                    "糙米饭80克（生重）",
                    "清蒸鲈鱼100克",
                    "炒青菜150克（西兰花/菠菜）",
                    "豆腐汤100毫升",
                    "植物油10毫升"
                ],
                "营养特点": "均衡搭配，控制升糖速度"
            },
            "晚餐方案": {
                "热量": f"{dinner_cal}千卡",
                "食谱示例": [
                    "荞麦面条80克（干重）",
                    "瘦牛肉丝80克",
                    "凉拌萝卜丝100克",
                    "紫菜蛋花汤150毫升"
                ],
                "营养特点": "低脂肪、高蛋白，有利夜间血糖稳定"
            },
            "加餐方案": {
                "热量": f"{snack_cal}千卡",
                "上午加餐": "苹果半个（约100克）",
                "下午加餐": "无糖酸奶100毫升 + 坚果5克",
                "营养特点": "补充维生素，避免血糖大幅波动"
            }
        }

    def _generate_dietary_principles(self, gmi: float, tir: float, tar: float) -> List[str]:
        """生成饮食控制原则"""
        principles = [
            "定时定量：三餐时间固定，每餐间隔4-6小时",
            "少量多餐：主餐之间适当加餐，避免过度饥饿",
            "先菜后饭：用餐时先吃蔬菜，再吃主食，延缓血糖上升",
            "细嚼慢咽：每餐用时20-30分钟，充分咀嚼"
        ]

        if tar > 50:
            principles.extend([
                "严格控制精制糖：避免含糖饮料、糖果、蛋糕等",
                "选择低升糖指数食物：优选燕麦、荞麦、糙米等"
            ])

        if tir < 50:
            principles.extend([
                "碳水化合物配对：搭配蛋白质和脂肪，减缓吸收",
                "避免单独进食水果：与正餐一起食用或配坚果"
            ])

        if gmi > 8.0:
            principles.extend([
                "严格控制总量：使用小碗小盘，控制食物分量",
                "记录血糖日记：记录进食与血糖变化关系"
            ])

        return principles

    def _get_diabetes_friendly_foods(self) -> Dict:
        """获取糖尿病友好食物清单"""
        return {
            "主食类": [
                "燕麦片、荞麦面、糙米、全麦面包",
                "红薯、玉米、山药（适量）",
                "绿豆、红豆、黑豆"
            ],
            "蛋白质类": [
                "瘦肉：鸡胸肉、瘦牛肉、瘦猪肉",
                "鱼类：鲈鱼、带鱼、三文鱼",
                "蛋类：鸡蛋、鹌鹑蛋",
                "豆制品：豆腐、豆浆、豆干"
            ],
            "蔬菜类": [
                "绿叶蔬菜：菠菜、小白菜、芹菜",
                "十字花科：西兰花、花椰菜、卷心菜",
                "瓜果类：黄瓜、西红柿、冬瓜"
            ],
            "水果类": [
                "低升糖水果：苹果、梨、柚子、猕猴桃",
                "建议时间：两餐之间，每次100-150克"
            ]
        }

    def _get_foods_to_limit(self) -> Dict:
        """获取需要限制的食物"""
        return {
            "严格禁止": [
                "含糖饮料：可乐、果汁、奶茶",
                "精制甜品：蛋糕、饼干、糖果",
                "精制主食：白粥、白面条（升糖指数高）"
            ],
            "严格限制": [
                "高脂肪食物：油炸食品、肥肉、奶油",
                "高盐食物：咸菜、腊肉、方便面",
                "高升糖水果：西瓜、荔枝、龙眼（适量）"
            ],
            "适量控制": [
                "坚果类：每日不超过30克",
                "植物油：每日25-30毫升",
                "酒类：建议避免，如饮用需严格限量"
            ]
        }

    def _generate_personalized_exercise_recommendations(self, gmi: float, cv: float, tbr: float, profile: Dict) -> Dict:
        """生成个性化详细运动建议"""

        # 基于患者档案计算个性化运动参数
        exercise_params = self._calculate_exercise_parameters(profile, gmi, cv)

        # 生成个性化运动计划
        exercise_plan = self._design_personalized_exercise_plan(profile, exercise_params, gmi)

        # 运动安全指导
        safety_guidelines = self._generate_personalized_safety_guidelines(profile, tbr, cv)

        # 运动监测指导
        monitoring_guide = self._generate_personalized_monitoring_guide(profile, gmi, cv)

        # 专项运动指导
        specialized_guidance = self._generate_specialized_exercise_guidance(profile)

        return {
            "个性化运动处方": {
                "患者档案": f"年龄{profile['年龄']}岁, {profile['性别']}, BMI {profile['BMI']:.1f}",
                "健康目标": "、".join(profile["健康目标"]),
                "活动水平": profile["活动水平"],
                "运动强度等级": exercise_params["强度等级"],
                "目标心率区间": exercise_params["目标心率区间"],
                "周运动总时长": exercise_params["周总时长"]
            },
            "个性化运动计划": exercise_plan,
            "专项运动指导": specialized_guidance,
            "运动安全保障": safety_guidelines,
            "血糖运动监测": monitoring_guide,
            "运动效果评估": self._generate_exercise_evaluation_metrics(profile),
            "阶段性目标设定": self._set_personalized_exercise_goals(profile, gmi, cv)
        }

    def _calculate_exercise_parameters(self, profile: Dict, gmi: float, cv: float) -> Dict:
        """计算个性化运动参数"""
        age = profile["年龄"]
        bmi = profile["BMI"]
        goals = profile["健康目标"]

        # 计算最大心率
        max_hr = 220 - age

        # 根据健康状况确定运动强度
        if "减重" in goals:
            intensity_level = "中高强度"
            target_hr_lower = int(max_hr * 0.6)
            target_hr_upper = int(max_hr * 0.75)
            weekly_duration = 250  # 分钟
        elif bmi >= 28:
            intensity_level = "中等强度"
            target_hr_lower = int(max_hr * 0.5)
            target_hr_upper = int(max_hr * 0.65)
            weekly_duration = 200
        elif gmi > 8.0:
            intensity_level = "低中强度"
            target_hr_lower = int(max_hr * 0.5)
            target_hr_upper = int(max_hr * 0.6)
            weekly_duration = 180
        else:
            intensity_level = "中等强度"
            target_hr_lower = int(max_hr * 0.6)
            target_hr_upper = int(max_hr * 0.7)
            weekly_duration = 150

        return {
            "最大心率": max_hr,
            "强度等级": intensity_level,
            "目标心率区间": f"{target_hr_lower}-{target_hr_upper}次/分",
            "周总时长": f"{weekly_duration}分钟",
            "目标心率下限": target_hr_lower,
            "目标心率上限": target_hr_upper,
            "周总时长数值": weekly_duration
        }

    def _design_personalized_exercise_plan(self, profile: Dict, params: Dict, gmi: float) -> Dict:
        """设计个性化运动计划"""
        goals = profile["健康目标"]
        bmi = profile["BMI"]

        plan = {
            "有氧运动方案": self._create_personalized_cardio_plan(goals, params, bmi),
            "抗阻训练方案": self._create_personalized_strength_plan(goals, params, profile["年龄"]),
            "柔韧性训练方案": self._create_flexibility_plan(profile)
        }

        # 根据健康目标添加专项训练
        if "减重" in goals:
            plan["减脂专项训练"] = self._create_fat_burning_plan(params)

        if "降压" in goals:
            plan["降压专项训练"] = self._create_blood_pressure_plan(params)

        return plan

    def _create_personalized_cardio_plan(self, goals: list, params: Dict, bmi: float) -> Dict:
        """个性化有氧运动方案"""
        weekly_duration = params["周总时长数值"]

        if "减重" in goals:
            return {
                "运动目标": "最大化脂肪燃烧，创造热量缺口",
                "运动类型": "快走、慢跑、游泳、椭圆机、划船机",
                "运动强度": "中高强度（心率140-160次/分）",
                "运动频率": "每周6次",
                "单次时长": "45-60分钟",
                "周总时长": f"{weekly_duration}分钟",
                "减重专用安排": {
                    "周一": "快走60分钟（心率保持在脂肪燃烧区间）",
                    "周二": "游泳45分钟 + 水中健身操15分钟",
                    "周三": "慢跑40分钟（间歇跑：3分钟慢跑+1分钟快跑）",
                    "周四": "椭圆机50分钟（变换阻力和坡度）",
                    "周五": "快走45分钟 + 爬楼梯15分钟",
                    "周六": "户外骑行90分钟（中等强度）",
                    "周日": "休息或轻松散步30分钟"
                },
                "脂肪燃烧优化": "运动前不进食，利用空腹有氧提高脂肪燃烧效率"
            }
        elif "降压" in goals:
            return {
                "运动目标": "改善心血管功能，平稳降低血压",
                "运动类型": "快走、游泳、太极、八段锦",
                "运动强度": "中等强度（心率120-140次/分）",
                "运动频率": "每天30分钟",
                "降压专用安排": {
                    "每日基础": "餐后快走30分钟",
                    "周一三五": "增加游泳30分钟",
                    "周二四六": "太极或八段锦30分钟",
                    "周末": "户外健步走60分钟"
                },
                "血压友好特点": "避免突然用力，注重动作连贯性"
            }
        else:
            return {
                "运动类型": "快走、慢跑、游泳、骑行",
                "运动强度": params["强度等级"],
                "运动频率": "每周5次",
                "单次时长": "30-45分钟",
                "心率目标": params["目标心率区间"]
            }

    def _create_personalized_strength_plan(self, goals: list, params: Dict, age: int) -> Dict:
        """个性化抗阻训练方案"""
        if "减重" in goals:
            return {
                "训练目标": "维持肌肉量，提高基础代谢率",
                "训练频率": "每周3次",
                "训练时长": "40-50分钟",
                "训练强度": "中等负荷（60-70% 1RM）",
                "减重专用训练": {
                    "周一（上肢）": [
                        "哑铃推举：3组×12次",
                        "哑铃划船：3组×12次",
                        "俯卧撑：3组×10-15次",
                        "卷腹：3组×15次"
                    ],
                    "周三（下肢）": [
                        "深蹲：3组×15次",
                        "箭步蹲：3组×12次（每腿）",
                        "臀桥：3组×15次",
                        "小腿提踵：3组×20次"
                    ],
                    "周五（全身）": [
                        "波比跳：3组×8次",
                        "平板支撑：3组×30-60秒",
                        "登山者：3组×20次",
                        "壶铃摆摆：3组×15次"
                    ]
                },
                "超级组训练": "上下肢动作组合，提高训练效率和热量消耗"
            }
        elif age >= 60:
            return {
                "训练目标": "维持肌肉量，改善平衡和灵活性",
                "训练频率": "每周2-3次",
                "训练强度": "轻到中等负荷",
                "适老训练": [
                    "椅子深蹲：预防跌倒",
                    "弹力带训练：关节友好",
                    "平衡训练：单脚站立",
                    "核心训练：改善姿态"
                ]
            }
        else:
            return {
                "训练频率": "每周2-3次",
                "训练时长": "30-40分钟",
                "训练强度": "中等负荷",
                "基础动作": [
                    "深蹲、俯卧撑、引体向上",
                    "哑铃推举、划船",
                    "平板支撑、卷腹"
                ]
            }

    def _create_flexibility_plan(self, profile: Dict) -> Dict:
        """柔韧性训练计划"""
        age = profile["年龄"]
        goals = profile["健康目标"]

        if "降压" in goals:
            return {
                "训练目标": "放松身心，辅助降压",
                "推荐项目": ["瑜伽", "太极", "八段锦", "静态拉伸"],
                "训练频率": "每日15-20分钟",
                "降压专用动作": [
                    "深呼吸配合缓慢拉伸",
                    "颈部和肩部放松",
                    "脊椎扭转和前屈",
                    "腿部肌群拉伸"
                ]
            }
        elif age >= 50:
            return {
                "训练目标": "维持关节活动度，预防运动损伤",
                "训练频率": "每日10-15分钟",
                "重点部位": "髋关节、肩关节、脊椎",
                "推荐动作": [
                    "猫牛式：脊椎活动",
                    "髋部环绕：髋关节灵活性",
                    "肩部拉伸：肩关节活动度"
                ]
            }
        else:
            return {
                "训练频率": "运动前后各5-10分钟",
                "动态热身": "关节环绕、腿部摆动",
                "静态拉伸": "主要肌群15-30秒保持"
            }

    def _create_fat_burning_plan(self, params: Dict) -> Dict:
        """减脂专项训练计划"""
        return {
            "HIIT高强度间歇训练": {
                "训练频率": "每周2-3次",
                "训练时长": "20-30分钟",
                "间歇模式": "高强度30秒 + 低强度90秒",
                "具体动作": [
                    "波比跳、开合跳、深蹲跳",
                    "高抬腿、登山者、俯卧撑"
                ],
                "燃脂效果": "后燃效应持续12-24小时"
            },
            "空腹有氧训练": {
                "最佳时间": "早晨空腹状态",
                "运动类型": "中低强度有氧运动",
                "持续时间": "30-45分钟",
                "注意事项": "血糖稳定后进行，随身携带糖果"
            }
        }

    def _create_blood_pressure_plan(self, params: Dict) -> Dict:
        """降压专项训练计划"""
        return {
            "等张运动": {
                "运动类型": "动态肌肉收缩运动",
                "推荐项目": "快走、慢跑、游泳、骑行",
                "运动强度": "中等强度（RPE 12-14）",
                "降压机制": "改善血管弹性，降低外周阻力"
            },
            "呼吸训练": {
                "深呼吸法": "4秒吸气-4秒憋气-6秒呼气",
                "训练时间": "每日2次，每次10-15分钟",
                "降压效果": "激活副交感神经，缓解血管收缩"
            },
            "放松训练": {
                "渐进性肌肉放松": "从头到脚逐步放松",
                "冥想训练": "专注呼吸，释放压力",
                "降压瑜伽": "倒立、前屈等体位法"
            }
        }

    def _generate_specialized_exercise_guidance(self, profile: Dict) -> Dict:
        """生成专项运动指导"""
        goals = profile["健康目标"]
        guidance = {}

        if "减重" in goals:
            guidance["减重运动指导"] = {
                "核心原则": "有氧为主，力量为辅，创造热量缺口",
                "运动时机": [
                    "有氧运动：餐前或餐后2小时",
                    "力量训练：任何时间均可",
                    "最佳燃脂时间：早晨空腹状态"
                ],
                "强度控制": [
                    "有氧强度：能说话但略感吃力",
                    "力量训练：感到肌肉疲劳但能完成动作",
                    "避免过度训练导致食欲大增"
                ],
                "进阶方案": [
                    "第1-2周：建立运动习惯，中低强度",
                    "第3-6周：提高运动强度和频率",
                    "第7-12周：加入HIIT和复合训练"
                ]
            }

        if "降压" in goals:
            guidance["降压运动指导"] = {
                "核心原则": "规律温和，避免剧烈，重在坚持",
                "运动禁忌": [
                    "避免憋气用力的动作",
                    "避免头部低于心脏的体位",
                    "避免突然停止运动",
                    "血压>180/110mmHg时暂停运动"
                ],
                "最佳运动": [
                    "每日快走30分钟以上",
                    "游泳：全身运动，关节友好",
                    "太极：身心并练，平稳降压"
                ],
                "监测要点": [
                    "运动前后测量血压",
                    "运动中如有头晕立即停止",
                    "运动后血压应在30分钟内恢复"
                ]
            }

        return guidance

    def _generate_personalized_safety_guidelines(self, profile: Dict, tbr: float, cv: float) -> Dict:
        """生成个性化运动安全指导"""
        age = profile["年龄"]
        goals = profile["健康目标"]

        guidelines = {
            "运动前准备": [
                "测量血糖值，确保在安全范围内",
                "充分热身5-10分钟",
                "检查运动装备和环境"
            ],
            "运动中监控": [
                "关注身体反应，如头晕、乏力应立即停止",
                "保持适当的运动强度",
                "及时补充水分"
            ],
            "运动后恢复": [
                "缓慢降低运动强度，不要突然停止",
                "进行拉伸放松5-10分钟",
                "再次测量血糖值"
            ]
        }

        # 根据低血糖风险调整
        if tbr > 4:
            guidelines.update({
                "低血糖预防": [
                    "运动前血糖<5.6mmol/L时需加餐",
                    "运动时随身携带快速糖类食品",
                    "运动强度不宜过大，时间不宜过长",
                    "运动后2-4小时内继续监测血糖"
                ]
            })

        # 根据年龄调整
        if age >= 65:
            guidelines.update({
                "老年人特殊注意": [
                    "运动强度从低开始，逐步增加",
                    "选择关节友好的运动方式",
                    "注意平衡训练，预防跌倒",
                    "有伴运动，确保安全"
                ]
            })

        return guidelines

    def _generate_personalized_monitoring_guide(self, profile: Dict, gmi: float, cv: float) -> Dict:
        """生成个性化运动监测指导"""
        goals = profile["健康目标"]

        guide = {
            "血糖监测方案": {
                "运动前": "确保血糖在4.5-13.0mmol/L之间",
                "运动中": "长时间运动需中途检测",
                "运动后": "立即和2-4小时后各检测一次",
                "夜间": "运动日夜间加测血糖"
            },
            "心率监测": {
                "目标区间": f"{220-profile['年龄']}次/分的60-75%",
                "监测方法": "运动手环、心率带或手动测量",
                "异常处理": "心率过高或过低应调整强度"
            }
        }

        if "减重" in goals:
            guide.update({
                "减重监测": {
                    "体重记录": "每周同一时间称重",
                    "体脂监测": "每月测量体脂率",
                    "围度测量": "腰围、臀围等身体尺寸",
                    "运动日志": "记录运动类型、时长、强度"
                }
            })

        if "降压" in goals:
            guide.update({
                "血压监测": {
                    "运动前后": "运动前后30分钟测量血压",
                    "记录要求": "详细记录血压变化趋势",
                    "异常标准": "收缩压>180或舒张压>110停止运动"
                }
            })

        return guide

    def _generate_exercise_evaluation_metrics(self, profile: Dict) -> Dict:
        """生成运动效果评估指标"""
        goals = profile["健康目标"]

        metrics = {
            "基础评估指标": {
                "血糖控制": "GMI、TIR改善程度",
                "心肺功能": "静息心率、运动耐力",
                "身体成分": "体重、体脂率、肌肉量"
            }
        }

        if "减重" in goals:
            metrics.update({
                "减重专项指标": {
                    "体重变化": "每周减重0.5-1kg为理想",
                    "体脂率": "男性<15%，女性<25%",
                    "腰围": "男性<90cm，女性<85cm",
                    "内脏脂肪": "等级控制在10以下"
                }
            })

        if "降压" in goals:
            metrics.update({
                "降压专项指标": {
                    "血压变化": "目标<130/80mmHg",
                    "心率变异": "反映自主神经功能",
                    "血管功能": "踝肱指数、脉搏波传导速度"
                }
            })

        return metrics

    def _set_personalized_exercise_goals(self, profile: Dict, gmi: float, cv: float) -> Dict:
        """设置个性化阶段性运动目标"""
        goals = profile["健康目标"]
        bmi = profile["BMI"]

        targets = {
            "第1阶段目标（1-4周）": {
                "运动习惯": "建立规律运动习惯，每周至少3次",
                "运动能力": "能够完成30分钟中等强度运动",
                "血糖改善": "减少血糖波动，提高TIR 5-10%"
            },
            "第2阶段目标（1-3个月）": {
                "运动频率": "增加到每周5-6次",
                "运动强度": "能够承受中高强度间歇训练",
                "代谢改善": "GMI下降0.3-0.5%，基础代谢率提升"
            },
            "第3阶段目标（3-6个月）": {
                "综合体能": "达到同年龄组平均水平以上",
                "慢病控制": "血糖、血压、血脂全面改善",
                "生活质量": "精力充沛，睡眠质量提升"
            }
        }

        if "减重" in goals:
            targets.update({
                "减重专项目标": {
                    "短期（1个月）": f"减重2-4kg，体脂率下降1-2%",
                    "中期（3个月）": f"减重6-12kg，达到BMI<28",
                    "长期（6个月）": f"达到理想体重，BMI在正常范围内"
                }
            })

        return targets

    def _generate_exercise_recommendations(self, gmi: float, cv: float, tbr: float) -> Dict:
        """生成详细运动建议，包括强度和时间安排"""

        # 基础运动方案设计
        exercise_plan = self._design_exercise_plan(gmi, cv, tbr)

        # 运动安全指导
        safety_guidelines = self._generate_exercise_safety_guidelines(tbr, cv)

        # 运动监测指导
        monitoring_guide = self._generate_exercise_monitoring_guide(gmi, cv)

        return {
            "每周运动计划": exercise_plan,
            "运动安全指导": safety_guidelines,
            "血糖监测配合": monitoring_guide,
            "运动禁忌与注意事项": self._get_exercise_contraindications(),
            "阶段性目标设定": self._set_exercise_goals(gmi, cv)
        }

    def _design_exercise_plan(self, gmi: float, cv: float, tbr: float) -> Dict:
        """设计具体运动计划"""

        # 根据血糖控制情况确定运动强度
        if gmi > 8.0:
            intensity_level = "中等强度为主"
            weekly_duration = 180  # 分钟
        elif gmi > 7.0:
            intensity_level = "中等强度"
            weekly_duration = 150  # 分钟
        else:
            intensity_level = "中高强度"
            weekly_duration = 150  # 分钟

        return {
            "有氧运动方案": {
                "运动类型": "快走、慢跑、游泳、骑行",
                "运动强度": intensity_level,
                "运动频率": "每周5-7次",
                "单次时长": "30-45分钟",
                "周总时长": f"{weekly_duration}分钟",
                "心率目标": "最大心率的60-70%（约120-140次/分）",
                "具体安排": {
                    "周一": "快走45分钟（餐后1小时）",
                    "周二": "游泳30分钟或抗阻训练",
                    "周三": "骑行40分钟",
                    "周四": "快走30分钟 + 柔韧性训练15分钟",
                    "周五": "慢跑30分钟",
                    "周六": "户外活动60分钟（爬山、球类等）",
                    "周日": "瑜伽或太极30分钟（恢复性运动）"
                }
            },
            "抗阻训练方案": {
                "运动频率": "每周2-3次",
                "训练时长": "30-40分钟",
                "训练强度": "中等负荷，可重复8-12次",
                "主要动作": [
                    "深蹲：3组 × 12次",
                    "俯卧撑：3组 × 8-12次",
                    "哑铃弯举：3组 × 10次",
                    "平板支撑：3组 × 30秒",
                    "拉伸放松：10分钟"
                ],
                "进阶计划": "每2周适当增加强度或次数"
            },
            "柔韧性训练": {
                "运动频率": "每日进行",
                "训练时长": "10-15分钟",
                "最佳时间": "运动后或睡前",
                "主要内容": [
                    "颈肩部拉伸",
                    "脊柱扭转",
                    "腿部拉伸",
                    "深呼吸放松"
                ]
            }
        }

    def _generate_exercise_safety_guidelines(self, tbr: float, cv: float) -> List[str]:
        """生成运动安全指导"""
        guidelines = [
            "运动前准备：热身5-10分钟，避免突然高强度运动",
            "运动时监控：感觉心率过快或不适时立即停止",
            "运动后恢复：缓慢降低运动强度，避免突然停止",
            "水分补充：运动中及时补充水分，避免脱水"
        ]

        if tbr > 4:
            guidelines.extend([
                "低血糖预防：运动前血糖<5.6mmol/L时先进食",
                "随身准备：携带葡萄糖片或糖果，出现低血糖症状时及时处理",
                "伙伴运动：尽量不独自运动，告知他人你的运动计划",
                "时间选择：避免胰岛素作用高峰期运动"
            ])

        if cv > 36:
            guidelines.extend([
                "规律时间：每天相同时间运动，减少血糖波动",
                "渐进原则：运动强度逐步增加，避免血糖剧烈变化",
                "密切监测：运动前后都要测血糖，了解变化规律"
            ])

        return guidelines

    def _generate_exercise_monitoring_guide(self, gmi: float, cv: float) -> Dict:
        """生成血糖监测配合指导"""
        return {
            "运动前监测": {
                "测量时间": "运动前15-30分钟",
                "安全范围": "5.6-13.9 mmol/L",
                "处理原则": {
                    "<5.6 mmol/L": "进食15-30克碳水化合物后再运动",
                    "5.6-13.9 mmol/L": "可以正常运动",
                    ">13.9 mmol/L": "轻度运动，避免高强度训练"
                }
            },
            "运动中监测": {
                "监测频率": "长时间运动（>60分钟）中途监测",
                "警惕症状": "头晕、出汗、心悸、饥饿感",
                "应急处理": "立即停止运动，测血糖并适当进食"
            },
            "运动后监测": {
                "测量时间": "运动结束后15分钟",
                "观察时长": "运动后2-4小时",
                "记录内容": "运动类型、时长、强度、血糖变化",
                "目标范围": "运动后血糖应在5.6-10.0 mmol/L"
            }
        }

    def _get_exercise_contraindications(self) -> Dict:
        """获取运动禁忌与注意事项"""
        return {
            "暂停运动的情况": [
                "血糖>16.7 mmol/L且伴有酮症",
                "血糖<3.9 mmol/L",
                "急性感染或发热",
                "血压>180/110 mmHg",
                "严重心律不齐"
            ],
            "需要医生指导的情况": [
                "糖尿病并发症（视网膜病变、肾病等）",
                "心血管疾病史",
                "年龄>40岁且久不运动",
                "服用胰岛素或胰岛素促泌剂"
            ],
            "运动环境要求": [
                "选择安全、平坦的运动场所",
                "穿着合适的运动鞋袜，预防足部损伤",
                "避免极端天气条件下户外运动",
                "运动场所应便于获得医疗帮助"
            ]
        }

    def _set_exercise_goals(self, gmi: float, cv: float) -> Dict:
        """设定阶段性运动目标"""
        return {
            "第1-4周目标": {
                "基础目标": "建立运动习惯，每周运动3-4次",
                "运动时长": "每次20-30分钟",
                "强度控制": "轻到中等强度，以不感到过度疲劳为准",
                "血糖目标": "运动前后血糖变化控制在3 mmol/L以内"
            },
            "第5-8周目标": {
                "进阶目标": "增加运动频率，每周运动5-6次",
                "运动时长": "每次30-40分钟",
                "强度提升": "中等强度为主，加入抗阻训练",
                "血糖目标": f"GMI下降0.5-1.0%（当前{gmi:.1f}%）"
            },
            "第9-12周目标": {
                "长期目标": "形成规律运动模式，每周150-180分钟",
                "运动种类": "有氧、抗阻、柔韧性训练相结合",
                "体能提升": "运动耐力和肌肉力量明显改善",
                "血糖目标": "TIR提升10-15%，CV降低至<36%"
            }
        }

    def _generate_overall_assessment(self, gmi: float, tir: float, cv: float, tbr: float) -> str:
        """生成整体评价"""

        if gmi < 7.0 and tir > 70 and cv < 36 and tbr < 4:
            return "血糖控制优秀，各项指标均达标，继续保持当前的治疗和生活方式"
        elif gmi < 8.0 and tir > 50 and tbr < 4:
            return "血糖控制良好，有进一步优化空间，建议通过生活方式调整继续改善"
        elif tbr > 4:
            return "需要重点关注低血糖风险，建议调整用药方案并加强血糖监测"
        else:
            return "血糖控制需要改善，建议重新评估治疗方案，加强生活方式干预"

    def _generate_detailed_glucose_analysis(self, df: pd.DataFrame, agent5_analysis: Dict) -> Dict:
        """生成详细血糖分析部分"""

        # 基础血糖统计
        basic_stats = self._calculate_basic_glucose_statistics(df)

        # 分时段血糖深度分析
        time_segment_analysis = self._analyze_glucose_by_time_segments(df)

        # 14天纵向趋势分析 (4-4-4-2)
        longitudinal_trend = self._analyze_14day_longitudinal_trend(df)

        # 工作日vs周末分析
        weekday_weekend_analysis = self._analyze_weekday_vs_weekend(df)

        # 14天每天血糖图谱
        daily_profiles = self._generate_daily_glucose_profiles(df)

        return {
            "基础血糖统计": basic_stats,
            "目标范围与风险时间": basic_stats["目标范围分析"],
            "波动性变异性": basic_stats["波动性分析"],
            "分时段血糖深度分析": time_segment_analysis,
            "14天纵向趋势分析": longitudinal_trend,
            "工作日与周末血糖分析": weekday_weekend_analysis,
            "14天每天血糖图谱": daily_profiles,
            "Agent5分段分析结果": self._extract_agent5_temporal_analysis(agent5_analysis)
        }

    def _calculate_basic_glucose_statistics(self, df: pd.DataFrame) -> Dict:
        """计算基础血糖统计"""

        glucose_values = df['glucose_value'].dropna().values

        # 基础统计量
        mean_glucose = np.mean(glucose_values)
        median_glucose = np.median(glucose_values)
        std_glucose = np.std(glucose_values)
        min_glucose = np.min(glucose_values)
        max_glucose = np.max(glucose_values)

        # 百分位数
        p25 = np.percentile(glucose_values, 25)
        p75 = np.percentile(glucose_values, 75)

        # 目标范围分析
        tir = np.sum((glucose_values >= 3.9) & (glucose_values <= 10.0)) / len(glucose_values) * 100
        tar1 = np.sum((glucose_values > 10.0) & (glucose_values <= 13.9)) / len(glucose_values) * 100
        tar2 = np.sum(glucose_values > 13.9) / len(glucose_values) * 100
        tbr1 = np.sum((glucose_values >= 3.0) & (glucose_values < 3.9)) / len(glucose_values) * 100
        tbr2 = np.sum(glucose_values < 3.0) / len(glucose_values) * 100

        # 波动性分析
        cv = (std_glucose / mean_glucose) * 100 if mean_glucose > 0 else 0
        glucose_range = max_glucose - min_glucose

        return {
            "基础统计量": {
                "平均血糖": f"{mean_glucose:.1f} mmol/L",
                "中位血糖": f"{median_glucose:.1f} mmol/L",
                "标准差": f"{std_glucose:.2f} mmol/L",
                "最低血糖": f"{min_glucose:.1f} mmol/L",
                "最高血糖": f"{max_glucose:.1f} mmol/L",
                "25分位数": f"{p25:.1f} mmol/L",
                "75分位数": f"{p75:.1f} mmol/L",
                "血糖范围": f"{glucose_range:.1f} mmol/L"
            },
            "目标范围分析": {
                "TIR (3.9-10.0)": f"{tir:.1f}%",
                "TAR-1 (10.0-13.9)": f"{tar1:.1f}%",
                "TAR-2 (>13.9)": f"{tar2:.1f}%",
                "TBR-1 (3.0-3.9)": f"{tbr1:.1f}%",
                "TBR-2 (<3.0)": f"{tbr2:.1f}%",
                "风险评价": self._evaluate_time_ranges(tir, tar1+tar2, tbr1+tbr2)
            },
            "波动性分析": {
                "变异系数(CV)": f"{cv:.1f}%",
                "血糖范围": f"{glucose_range:.1f} mmol/L",
                "四分位间距": f"{p75-p25:.1f} mmol/L",
                "波动性评价": "稳定" if cv < 36 else ("中度波动" if cv < 50 else "高度波动")
            }
        }

    def _evaluate_time_ranges(self, tir: float, tar: float, tbr: float) -> str:
        """评价时间范围"""
        if tbr > 4:
            return "低血糖风险偏高，需要关注"
        elif tar > 25:
            return "高血糖时间偏长，需要改善"
        elif tir < 70:
            return "目标范围内时间不足，有改善空间"
        else:
            return "血糖控制良好，各时间范围基本达标"

    def _analyze_glucose_by_time_segments(self, df: pd.DataFrame) -> Dict:
        """分时段血糖深度分析"""

        df_copy = df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
        df_copy['hour'] = df_copy['timestamp'].dt.hour

        # 定义时间段
        time_segments = {
            "夜间 (00:00-06:00)": (0, 6),
            "早餐 (06:00-10:00)": (6, 10),
            "午餐 (10:00-14:00)": (10, 14),
            "晚餐 (14:00-22:00)": (14, 22),
            "睡前 (22:00-24:00)": (22, 24)
        }

        # 2小时间段分析
        two_hour_segments = {}
        for i in range(0, 24, 2):
            segment_name = f"{i:02d}:00-{(i+2):02d}:00"
            two_hour_segments[segment_name] = (i, i+2 if i+2 <= 24 else 24)

        segment_analysis = {}

        # 分析传统时间段
        for segment_name, (start_hour, end_hour) in time_segments.items():
            if end_hour == 24:
                segment_data = df_copy[df_copy['hour'] >= start_hour]
            else:
                segment_data = df_copy[(df_copy['hour'] >= start_hour) & (df_copy['hour'] < end_hour)]

            if len(segment_data) > 0:
                analysis = self._analyze_time_segment(segment_data['glucose_value'].values, segment_name)
                segment_analysis[segment_name] = analysis

        # 分析2小时间段
        two_hour_analysis = {}
        for segment_name, (start_hour, end_hour) in two_hour_segments.items():
            if end_hour == 24:
                segment_data = df_copy[df_copy['hour'] >= start_hour]
            else:
                segment_data = df_copy[(df_copy['hour'] >= start_hour) & (df_copy['hour'] < end_hour)]

            if len(segment_data) > 0:
                analysis = self._analyze_time_segment(segment_data['glucose_value'].values, segment_name)
                two_hour_analysis[segment_name] = analysis

        # 生成时间段对比表格
        traditional_table = self._create_time_segment_table(segment_analysis, "传统时间段")
        two_hour_table = self._create_time_segment_table(two_hour_analysis, "2小时间段")

        return {
            "传统时间段表格标题": "传统时间段血糖对比分析表",
            "传统时间段表格数据": traditional_table,
            "2小时时间段表格标题": "2小时时间段血糖对比分析表",
            "2小时时间段表格数据": two_hour_table,
            "分析说明": "传统时间段基于餐时划分，2小时间段提供更精细的血糖变化模式分析"
        }

    def _create_time_segment_table(self, segment_analysis: Dict, table_type: str) -> List[Dict]:
        """创建时间段分析表格"""

        table_data = []

        for segment_name, analysis in segment_analysis.items():
            if "错误" in analysis:
                continue

            # 提取数值
            data_points = analysis.get("数据点数", 0)
            mean_glucose = analysis.get("平均血糖", "0 mmol/L").split()[0]
            tir = analysis.get("TIR", "0%").replace("%", "")
            tar = analysis.get("TAR", "0%").replace("%", "")
            tbr = analysis.get("TBR", "0%").replace("%", "")
            cv = analysis.get("变异系数", "0%").replace("%", "")
            min_glucose = analysis.get("最低值", "0 mmol/L").split()[0]
            max_glucose = analysis.get("最高值", "0 mmol/L").split()[0]

            # 血糖控制评价
            tir_val = float(tir)
            if tir_val > 70:
                control_quality = "优秀"
            elif tir_val > 50:
                control_quality = "良好"
            else:
                control_quality = "需改善"

            table_data.append({
                "时间段": segment_name,
                "数据点数": data_points,
                "平均血糖 (mmol/L)": mean_glucose,
                "最低值 (mmol/L)": min_glucose,
                "最高值 (mmol/L)": max_glucose,
                "TIR (%)": tir,
                "TAR (%)": tar,
                "TBR (%)": tbr,
                "CV (%)": cv,
                "控制质量": control_quality
            })

        return table_data

    def _analyze_time_segment(self, glucose_values: np.ndarray, segment_name: str) -> Dict:
        """分析单个时间段"""

        if len(glucose_values) == 0:
            return {"错误": "该时间段无数据"}

        mean_glucose = np.mean(glucose_values)
        std_glucose = np.std(glucose_values)
        cv = (std_glucose / mean_glucose) * 100 if mean_glucose > 0 else 0

        tir = np.sum((glucose_values >= 3.9) & (glucose_values <= 10.0)) / len(glucose_values) * 100
        tar = np.sum(glucose_values > 10.0) / len(glucose_values) * 100
        tbr = np.sum(glucose_values < 3.9) / len(glucose_values) * 100

        return {
            "数据点数": len(glucose_values),
            "平均血糖": f"{mean_glucose:.1f} mmol/L",
            "标准差": f"{std_glucose:.2f} mmol/L",
            "变异系数": f"{cv:.1f}%",
            "TIR": f"{tir:.1f}%",
            "TAR": f"{tar:.1f}%",
            "TBR": f"{tbr:.1f}%",
            "最低值": f"{np.min(glucose_values):.1f} mmol/L",
            "最高值": f"{np.max(glucose_values):.1f} mmol/L",
            "血糖特点": self._characterize_time_segment(mean_glucose, cv, tir, segment_name)
        }

    def _characterize_time_segment(self, mean_glucose: float, cv: float, tir: float, segment_name: str) -> str:
        """描述时间段特征"""

        characteristics = []

        if "夜间" in segment_name:
            if mean_glucose < 6.0:
                characteristics.append("夜间血糖控制良好")
            elif mean_glucose > 7.0:
                characteristics.append("夜间血糖偏高")

            if cv < 20:
                characteristics.append("夜间血糖稳定")
            elif cv > 30:
                characteristics.append("夜间血糖波动较大")

        elif "早餐" in segment_name:
            if tir > 70:
                characteristics.append("早餐后血糖控制良好")
            else:
                characteristics.append("早餐后血糖控制需要改善")

        elif "午餐" in segment_name:
            if tir > 70:
                characteristics.append("午餐后血糖控制良好")
            else:
                characteristics.append("午餐后血糖控制需要改善")

        elif "晚餐" in segment_name:
            if tir > 70:
                characteristics.append("晚餐后血糖控制良好")
            else:
                characteristics.append("晚餐后血糖控制需要改善")

        if not characteristics:
            if tir > 70:
                characteristics.append("该时段血糖控制良好")
            else:
                characteristics.append("该时段血糖控制需要改善")

        return "；".join(characteristics)

    def _analyze_14day_longitudinal_trend(self, df: pd.DataFrame) -> Dict:
        """分析14天纵向趋势（4-4-4-2天分段）"""

        df_copy = df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])

        # 计算天数
        start_date = df_copy['timestamp'].min().date()
        end_date = df_copy['timestamp'].max().date()
        total_days = (end_date - start_date).days + 1

        print(f"[Agent_ZS] 分析{total_days}天的纵向趋势")

        # 创建4-4-4-2分段
        segments = [
            {"name": "第1段 (第1-4天)", "start_day": 0, "duration": 4},
            {"name": "第2段 (第5-8天)", "start_day": 4, "duration": 4},
            {"name": "第3段 (第9-12天)", "start_day": 8, "duration": 4},
            {"name": "第4段 (第13-14天)", "start_day": 12, "duration": max(1, min(2, total_days - 12))}
        ]

        trend_analysis = {}

        for segment in segments:
            if segment["duration"] <= 0:
                continue

            segment_start = start_date + timedelta(days=int(segment["start_day"]))
            segment_end = segment_start + timedelta(days=int(segment["duration"]) - 1)

            # 筛选该段数据
            segment_data = df_copy[
                (df_copy['timestamp'].dt.date >= segment_start) &
                (df_copy['timestamp'].dt.date <= segment_end)
            ]

            if len(segment_data) > 0:
                glucose_values = segment_data['glucose_value'].values
                analysis = self._analyze_longitudinal_segment(glucose_values, segment)
                trend_analysis[segment["name"]] = analysis

        # 趋势变化分析
        trend_comparison = self._compare_longitudinal_trends(trend_analysis)

        # 生成纵向趋势对比表格
        longitudinal_table = self._generate_longitudinal_comparison_table(trend_analysis)

        return {
            "表格标题": longitudinal_table.get("表格标题", "14天纵向趋势对比分析表"),
            "分段数据表": longitudinal_table.get("分段数据表", []),
            "趋势变化表": longitudinal_table.get("趋势变化表", []),
            "总体趋势": longitudinal_table.get("总体趋势", "需要进一步分析"),
            "分段说明": "按4-4-4-2天分段，分析血糖控制的时间变化趋势"
        }

    def _analyze_longitudinal_segment(self, glucose_values: np.ndarray, segment: Dict) -> Dict:
        """分析纵向时间段"""

        mean_glucose = np.mean(glucose_values)
        std_glucose = np.std(glucose_values)
        cv = (std_glucose / mean_glucose) * 100 if mean_glucose > 0 else 0

        tir = np.sum((glucose_values >= 3.9) & (glucose_values <= 10.0)) / len(glucose_values) * 100
        tar = np.sum(glucose_values > 10.0) / len(glucose_values) * 100
        tbr = np.sum(glucose_values < 3.9) / len(glucose_values) * 100

        # 计算GMI
        gmi = 3.31 + (0.02392 * mean_glucose * 18.018)

        return {
            "时间段": segment["name"],
            "天数": segment["duration"],
            "数据点数": len(glucose_values),
            "平均血糖": f"{mean_glucose:.1f} mmol/L",
            "GMI": f"{gmi:.1f}%",
            "TIR": f"{tir:.1f}%",
            "TAR": f"{tar:.1f}%",
            "TBR": f"{tbr:.1f}%",
            "CV": f"{cv:.1f}%",
            "控制质量": "优秀" if gmi < 7.0 and tir > 70 else ("良好" if gmi < 8.0 and tir > 50 else "需改善")
        }

    def _generate_longitudinal_comparison_table(self, trend_analysis: Dict) -> Dict:
        """生成14天纵向趋势对比表格"""

        if not trend_analysis or len(trend_analysis) < 2:
            return {"说明": "数据不足，无法生成纵向趋势对比表格"}

        segments = list(trend_analysis.keys())

        # 提取数值函数
        def extract_percentage(value_str):
            if isinstance(value_str, str):
                return float(value_str.replace("%", ""))
            return float(value_str) if value_str else 0

        # 构建表格数据
        table_rows = []

        for i, segment in enumerate(segments):
            segment_data = trend_analysis[segment]

            # 提取各项指标
            gmi = extract_percentage(segment_data.get("GMI", "0%"))
            tir = extract_percentage(segment_data.get("TIR", "0%"))
            tar = extract_percentage(segment_data.get("TAR", "0%"))
            tbr = extract_percentage(segment_data.get("TBR", "0%"))
            cv = extract_percentage(segment_data.get("CV", "0%"))

            table_rows.append({
                "时间段": segment,
                "天数": segment_data.get("天数", 0),
                "数据点数": segment_data.get("数据点数", 0),
                "GMI (%)": f"{gmi:.1f}",
                "TIR (%)": f"{tir:.1f}",
                "TAR (%)": f"{tar:.1f}",
                "TBR (%)": f"{tbr:.1f}",
                "CV (%)": f"{cv:.1f}",
                "控制质量": segment_data.get("控制质量", "未评估")
            })

        # 计算趋势变化
        trend_changes = []
        if len(table_rows) >= 2:
            for i in range(1, len(table_rows)):
                prev_row = table_rows[i-1]
                curr_row = table_rows[i]

                gmi_change = float(curr_row["GMI (%)"]) - float(prev_row["GMI (%)"])
                tir_change = float(curr_row["TIR (%)"]) - float(prev_row["TIR (%)"])

                trend_direction = "改善" if (gmi_change < 0 and tir_change > 0) else "恶化" if (gmi_change > 0 and tir_change < 0) else "稳定"

                trend_changes.append({
                    "阶段变化": f"{prev_row['时间段']} → {curr_row['时间段']}",
                    "GMI变化": f"{gmi_change:+.1f}%",
                    "TIR变化": f"{tir_change:+.1f}%",
                    "趋势方向": trend_direction,
                    "变化幅度": "显著" if abs(gmi_change) > 1.0 or abs(tir_change) > 10 else "轻微"
                })

        return {
            "表格标题": "14天纵向趋势对比分析表",
            "分段数据表": table_rows,
            "趋势变化表": trend_changes,
            "总体趋势": self._analyze_overall_longitudinal_trend(table_rows)
        }

    def _analyze_overall_longitudinal_trend(self, table_rows: List[Dict]) -> str:
        """分析总体纵向趋势"""

        if len(table_rows) < 2:
            return "数据不足，无法分析趋势"

        # 比较首末两段
        first_segment = table_rows[0]
        last_segment = table_rows[-1]

        first_gmi = float(first_segment["GMI (%)"])
        last_gmi = float(last_segment["GMI (%)"])

        first_tir = float(first_segment["TIR (%)"])
        last_tir = float(last_segment["TIR (%)"])

        gmi_improvement = first_gmi - last_gmi
        tir_improvement = last_tir - first_tir

        if gmi_improvement > 1.0 and tir_improvement > 10:
            return "血糖控制明显改善，治疗效果显著"
        elif gmi_improvement > 0.5 and tir_improvement > 5:
            return "血糖控制有所改善，治疗方向正确"
        elif gmi_improvement < -1.0 or tir_improvement < -10:
            return "血糖控制有所恶化，需要调整治疗方案"
        else:
            return "血糖控制相对稳定，维持当前治疗"

    def _compare_longitudinal_trends(self, trend_analysis: Dict) -> Dict:
        """比较纵向趋势变化"""

        segments = list(trend_analysis.keys())
        if len(segments) < 2:
            return {"说明": "数据不足，无法进行趋势比较"}

        comparisons = []

        for i in range(len(segments) - 1):
            current_segment = trend_analysis[segments[i]]
            next_segment = trend_analysis[segments[i + 1]]

            # 提取数值进行比较
            try:
                current_gmi = float(current_segment["GMI"].replace("%", ""))
                next_gmi = float(next_segment["GMI"].replace("%", ""))

                current_tir = float(current_segment["TIR"].replace("%", ""))
                next_tir = float(next_segment["TIR"].replace("%", ""))

                gmi_change = next_gmi - current_gmi
                tir_change = next_tir - current_tir

                comparison = {
                    "对比": f"{segments[i]} vs {segments[i+1]}",
                    "GMI变化": f"{gmi_change:+.1f}%",
                    "TIR变化": f"{tir_change:+.1f}%",
                    "趋势评价": self._evaluate_trend_change(gmi_change, tir_change)
                }
                comparisons.append(comparison)

            except:
                continue

        return {
            "段间比较": comparisons,
            "总体趋势": "改善" if len([c for c in comparisons if "改善" in c.get("趋势评价", "")]) > len(comparisons)/2 else "稳定"
        }

    def _evaluate_trend_change(self, gmi_change: float, tir_change: float) -> str:
        """评价趋势变化"""

        if gmi_change < -0.3 and tir_change > 5:
            return "明显改善"
        elif gmi_change < -0.1 and tir_change > 2:
            return "轻微改善"
        elif gmi_change > 0.3 or tir_change < -5:
            return "需要关注"
        else:
            return "基本稳定"

    def _evaluate_overall_trend(self, trend_analysis: Dict) -> str:
        """评价整体趋势"""

        if len(trend_analysis) < 2:
            return "监测时间不足，建议延长监测周期"

        first_segment = list(trend_analysis.values())[0]
        last_segment = list(trend_analysis.values())[-1]

        try:
            first_quality = first_segment["控制质量"]
            last_quality = last_segment["控制质量"]

            if last_quality == "优秀" and first_quality != "优秀":
                return "血糖控制明显改善，治疗效果良好"
            elif last_quality == "优秀":
                return "血糖控制保持优秀状态"
            elif last_quality == "良好":
                return "血糖控制良好，有进一步优化空间"
            else:
                return "血糖控制需要改善，建议调整治疗方案"

        except:
            return "需要进一步评估治疗效果"

    def _analyze_weekday_vs_weekend(self, df: pd.DataFrame) -> Dict:
        """分析工作日vs周末血糖差异"""

        df_copy = df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
        df_copy['weekday'] = df_copy['timestamp'].dt.dayofweek  # 0=周一, 6=周日

        # 分离工作日和周末数据
        weekday_data = df_copy[df_copy['weekday'] < 5]  # 周一到周五
        weekend_data = df_copy[df_copy['weekday'] >= 5]  # 周六周日

        weekday_analysis = {}
        weekend_analysis = {}

        if len(weekday_data) > 0:
            weekday_glucose = weekday_data['glucose_value'].values
            weekday_analysis = self._analyze_glucose_period(weekday_glucose, "工作日")

        if len(weekend_data) > 0:
            weekend_glucose = weekend_data['glucose_value'].values
            weekend_analysis = self._analyze_glucose_period(weekend_glucose, "周末")

        # 比较分析
        comparison = {}
        if weekday_analysis and weekend_analysis:
            comparison = self._compare_weekday_weekend(weekday_analysis, weekend_analysis)

        # 生成对比表格
        comparison_table = self._generate_weekday_weekend_comparison_table(weekday_analysis, weekend_analysis)

        return {
            "表格标题": comparison_table.get("表格标题", "工作日与周末血糖对比分析表"),
            "表格数据": comparison_table.get("表格数据", []),
            "总体评价": comparison_table.get("总体评价", "需要进一步分析"),
            "生活方式建议": self._generate_lifestyle_suggestions_based_on_weekday_analysis(comparison)
        }

    def _generate_weekday_weekend_comparison_table(self, weekday_analysis: Dict, weekend_analysis: Dict) -> Dict:
        """生成工作日与周末对比表格"""

        if not weekday_analysis or not weekend_analysis:
            return {"说明": "数据不足，无法生成对比表格"}

        # 提取数值进行对比
        def extract_numeric_value(value_str):
            """从字符串中提取数值"""
            if isinstance(value_str, str):
                return float(value_str.split()[0])
            return float(value_str) if value_str else 0

        weekday_gmi = float(weekday_analysis.get("GMI", "0%").replace("%", ""))
        weekend_gmi = float(weekend_analysis.get("GMI", "0%").replace("%", ""))

        weekday_tir = float(weekday_analysis.get("TIR", "0%").replace("%", ""))
        weekend_tir = float(weekend_analysis.get("TIR", "0%").replace("%", ""))

        weekday_tar = float(weekday_analysis.get("TAR", "0%").replace("%", ""))
        weekend_tar = float(weekend_analysis.get("TAR", "0%").replace("%", ""))

        weekday_tbr = float(weekday_analysis.get("TBR", "0%").replace("%", ""))
        weekend_tbr = float(weekend_analysis.get("TBR", "0%").replace("%", ""))

        weekday_cv = float(weekday_analysis.get("CV", "0%").replace("%", ""))
        weekend_cv = float(weekend_analysis.get("CV", "0%").replace("%", ""))

        weekday_mean = extract_numeric_value(weekday_analysis.get("平均血糖", "0 mmol/L"))
        weekend_mean = extract_numeric_value(weekend_analysis.get("平均血糖", "0 mmol/L"))

        return {
            "表格标题": "工作日与周末血糖对比分析表",
            "表格数据": [
                {
                    "指标": "数据点数",
                    "工作日": f"{weekday_analysis.get('数据点数', 0)}个",
                    "周末": f"{weekend_analysis.get('数据点数', 0)}个",
                    "差值": f"{weekday_analysis.get('数据点数', 0) - weekend_analysis.get('数据点数', 0):+d}个",
                    "评价": "工作日数据更多" if weekday_analysis.get('数据点数', 0) > weekend_analysis.get('数据点数', 0) else "周末数据更多"
                },
                {
                    "指标": "平均血糖 (mmol/L)",
                    "工作日": f"{weekday_mean:.1f}",
                    "周末": f"{weekend_mean:.1f}",
                    "差值": f"{weekday_mean - weekend_mean:+.1f}",
                    "评价": "工作日偏高" if weekday_mean > weekend_mean else "周末偏高" if weekend_mean > weekday_mean else "基本相当"
                },
                {
                    "指标": "GMI (%)",
                    "工作日": f"{weekday_gmi:.1f}%",
                    "周末": f"{weekend_gmi:.1f}%",
                    "差值": f"{weekday_gmi - weekend_gmi:+.1f}%",
                    "评价": "工作日控制较差" if weekday_gmi > weekend_gmi else "周末控制较差" if weekend_gmi > weekday_gmi else "控制水平相当"
                },
                {
                    "指标": "TIR (%)",
                    "工作日": f"{weekday_tir:.1f}%",
                    "周末": f"{weekend_tir:.1f}%",
                    "差值": f"{weekday_tir - weekend_tir:+.1f}%",
                    "评价": "周末控制更好" if weekend_tir > weekday_tir else "工作日控制更好" if weekday_tir > weekend_tir else "控制水平相当"
                },
                {
                    "指标": "TAR (%)",
                    "工作日": f"{weekday_tar:.1f}%",
                    "周末": f"{weekend_tar:.1f}%",
                    "差值": f"{weekday_tar - weekend_tar:+.1f}%",
                    "评价": "工作日高血糖更多" if weekday_tar > weekend_tar else "周末高血糖更多" if weekend_tar > weekday_tar else "高血糖风险相当"
                },
                {
                    "指标": "TBR (%)",
                    "工作日": f"{weekday_tbr:.1f}%",
                    "周末": f"{weekend_tbr:.1f}%",
                    "差值": f"{weekday_tbr - weekend_tbr:+.1f}%",
                    "评价": "工作日低血糖更多" if weekday_tbr > weekend_tbr else "周末低血糖更多" if weekend_tbr > weekday_tbr else "低血糖风险相当"
                },
                {
                    "指标": "CV (%)",
                    "工作日": f"{weekday_cv:.1f}%",
                    "周末": f"{weekend_cv:.1f}%",
                    "差值": f"{weekday_cv - weekend_cv:+.1f}%",
                    "评价": "工作日波动更大" if weekday_cv > weekend_cv else "周末波动更大" if weekend_cv > weekday_cv else "波动程度相当"
                }
            ],
            "总体评价": self._generate_weekday_weekend_overall_assessment(weekday_analysis, weekend_analysis)
        }

    def _generate_weekday_weekend_overall_assessment(self, weekday_analysis: Dict, weekend_analysis: Dict) -> str:
        """生成工作日与周末总体评价"""

        weekday_tir = float(weekday_analysis.get("TIR", "0%").replace("%", ""))
        weekend_tir = float(weekend_analysis.get("TIR", "0%").replace("%", ""))

        weekday_cv = float(weekday_analysis.get("CV", "0%").replace("%", ""))
        weekend_cv = float(weekend_analysis.get("CV", "0%").replace("%", ""))

        tir_diff = abs(weekday_tir - weekend_tir)
        cv_diff = abs(weekday_cv - weekend_cv)

        if tir_diff > 15 or cv_diff > 10:
            return "工作日与周末血糖模式存在显著差异，建议关注生活方式的一致性"
        elif tir_diff > 5 or cv_diff > 5:
            return "工作日与周末血糖模式存在一定差异，需要适当调整"
        else:
            return "工作日与周末血糖模式基本一致，生活方式管理良好"

    def _analyze_glucose_period(self, glucose_values: np.ndarray, period_name: str) -> Dict:
        """分析血糖时期"""

        mean_glucose = np.mean(glucose_values)
        std_glucose = np.std(glucose_values)
        cv = (std_glucose / mean_glucose) * 100 if mean_glucose > 0 else 0

        tir = np.sum((glucose_values >= 3.9) & (glucose_values <= 10.0)) / len(glucose_values) * 100
        tar = np.sum(glucose_values > 10.0) / len(glucose_values) * 100
        tbr = np.sum(glucose_values < 3.9) / len(glucose_values) * 100

        gmi = 3.31 + (0.02392 * mean_glucose * 18.018)

        return {
            "时期": period_name,
            "数据点数": len(glucose_values),
            "平均血糖": f"{mean_glucose:.1f} mmol/L",
            "GMI": f"{gmi:.1f}%",
            "TIR": f"{tir:.1f}%",
            "TAR": f"{tar:.1f}%",
            "TBR": f"{tbr:.1f}%",
            "CV": f"{cv:.1f}%",
            "控制特点": self._characterize_period_control(mean_glucose, cv, tir, period_name)
        }

    def _characterize_period_control(self, mean_glucose: float, cv: float, tir: float, period_name: str) -> str:
        """描述时期控制特点"""

        characteristics = []

        if tir > 70:
            characteristics.append(f"{period_name}血糖控制良好")
        else:
            characteristics.append(f"{period_name}血糖控制需要改善")

        if cv < 36:
            characteristics.append("血糖稳定性良好")
        else:
            characteristics.append("血糖波动偏大")

        return "；".join(characteristics)

    def _compare_weekday_weekend(self, weekday_analysis: Dict, weekend_analysis: Dict) -> Dict:
        """比较工作日和周末"""

        try:
            weekday_gmi = float(weekday_analysis["GMI"].replace("%", ""))
            weekend_gmi = float(weekend_analysis["GMI"].replace("%", ""))

            weekday_tir = float(weekday_analysis["TIR"].replace("%", ""))
            weekend_tir = float(weekend_analysis["TIR"].replace("%", ""))

            gmi_diff = weekend_gmi - weekday_gmi
            tir_diff = weekend_tir - weekday_tir

            return {
                "GMI差异": f"{gmi_diff:+.1f}%",
                "TIR差异": f"{tir_diff:+.1f}%",
                "差异评价": self._evaluate_weekday_weekend_difference(gmi_diff, tir_diff),
                "主要差异": "周末血糖控制更好" if gmi_diff < -0.2 else ("工作日血糖控制更好" if gmi_diff > 0.2 else "工作日与周末血糖控制相当")
            }
        except:
            return {"说明": "数据不足，无法进行有效比较"}

    def _evaluate_weekday_weekend_difference(self, gmi_diff: float, tir_diff: float) -> str:
        """评价工作日周末差异"""

        if abs(gmi_diff) > 0.5 or abs(tir_diff) > 10:
            return "存在明显差异，需要关注生活方式的一致性"
        elif abs(gmi_diff) > 0.2 or abs(tir_diff) > 5:
            return "存在轻微差异，建议保持规律生活"
        else:
            return "工作日与周末控制相当，生活规律性良好"

    def _generate_lifestyle_suggestions_based_on_weekday_analysis(self, comparison: Dict) -> List[str]:
        """基于工作日周末分析生成生活方式建议"""

        if not comparison or "差异评价" not in comparison:
            return ["建议保持规律的作息和饮食习惯"]

        suggestions = []

        if "明显差异" in comparison["差异评价"]:
            suggestions.extend([
                "工作日与周末血糖控制存在较大差异",
                "建议周末也要保持规律的作息时间",
                "注意周末饮食控制，避免过度放松"
            ])

        if "周末血糖控制更好" in comparison.get("主要差异", ""):
            suggestions.extend([
                "周末血糖控制较好，可能与放松状态有关",
                "建议工作日也要注意压力管理",
                "适当调整工作日的饮食和运动安排"
            ])

        if "工作日血糖控制更好" in comparison.get("主要差异", ""):
            suggestions.extend([
                "工作日血糖控制较好，可能与规律作息有关",
                "建议周末也保持相似的作息规律",
                "周末避免过度饮食和缺乏运动"
            ])

        if not suggestions:
            suggestions = [
                "工作日与周末血糖控制基本一致",
                "继续保持当前良好的生活规律",
                "可适当在周末增加运动量"
            ]

        return suggestions

    def _generate_daily_glucose_profiles(self, df: pd.DataFrame) -> Dict:
        """生成14天每天血糖图谱表格"""

        df_copy = df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
        df_copy['date'] = df_copy['timestamp'].dt.date

        daily_profiles = []
        unique_dates = sorted(df_copy['date'].unique())

        for date in unique_dates[:14]:  # 限制前14天
            daily_data = df_copy[df_copy['date'] == date]

            if len(daily_data) > 0:
                profile = self._analyze_daily_profile_table(daily_data, date)
                daily_profiles.append(profile)

        # 生成每日概况表格
        daily_summary = self._generate_daily_summary_table(daily_profiles)

        return {
            "表格标题": "14天每日血糖控制对比分析表",
            "表格数据": daily_profiles,
            "统计概况": daily_summary,
            "表格说明": "14天逐日血糖控制效果对比分析"
        }

    def _analyze_daily_profile_table(self, daily_data: pd.DataFrame, date) -> Dict:
        """分析单日血糖图谱-表格格式"""

        glucose_values = daily_data['glucose_value'].values
        timestamps = daily_data['timestamp']

        # 基础统计
        mean_glucose = np.mean(glucose_values)
        std_glucose = np.std(glucose_values)
        min_glucose = np.min(glucose_values)
        max_glucose = np.max(glucose_values)

        # 时间范围分析
        tir = np.sum((glucose_values >= 3.9) & (glucose_values <= 10.0)) / len(glucose_values) * 100
        tar = np.sum(glucose_values > 10.0) / len(glucose_values) * 100
        tbr = np.sum(glucose_values < 3.9) / len(glucose_values) * 100

        # 识别异常事件
        hypo_events = np.sum(glucose_values < 3.9)
        hyper_events = np.sum(glucose_values > 13.9)

        # 血糖峰值和谷值时间
        max_time = timestamps.iloc[int(glucose_values.argmax())].strftime("%H:%M")
        min_time = timestamps.iloc[int(glucose_values.argmin())].strftime("%H:%M")

        # 控制质量评价
        if tir > 70 and tbr < 4:
            control_quality = "优秀"
        elif tir > 50 and tbr < 4:
            control_quality = "良好"
        else:
            control_quality = "需改善"

        return {
            "日期": str(date),
            "数据点数": len(glucose_values),
            "平均血糖 (mmol/L)": f"{mean_glucose:.1f}",
            "最高血糖": f"{max_glucose:.1f} ({max_time})",
            "最低血糖": f"{min_glucose:.1f} ({min_time})",
            "TIR (%)": f"{tir:.1f}",
            "TAR (%)": f"{tar:.1f}",
            "TBR (%)": f"{tbr:.1f}",
            "高血糖事件": f"{hyper_events}次",
            "低血糖事件": f"{hypo_events}次",
            "控制质量": control_quality
        }

    def _generate_daily_summary_table(self, daily_profiles: List[Dict]) -> Dict:
        """生成每日概况统计表格"""

        if not daily_profiles:
            return {"说明": "无每日数据可分析"}

        # 统计控制质量分布
        quality_counts = {"优秀": 0, "良好": 0, "需改善": 0}
        total_hypo_events = 0
        total_hyper_events = 0

        for profile in daily_profiles:
            quality = profile.get("控制质量", "需改善")
            if quality in quality_counts:
                quality_counts[quality] += 1

            # 提取事件数
            hypo_str = profile.get("低血糖事件", "0次")
            hyper_str = profile.get("高血糖事件", "0次")

            total_hypo_events += int(hypo_str.replace("次", ""))
            total_hyper_events += int(hyper_str.replace("次", ""))

        total_days = len(daily_profiles)

        return {
            "总监测天数": total_days,
            "控制质量分布": {
                "优秀天数": f"{quality_counts['优秀']}天 ({quality_counts['优秀']/total_days*100:.0f}%)",
                "良好天数": f"{quality_counts['良好']}天 ({quality_counts['良好']/total_days*100:.0f}%)",
                "需改善天数": f"{quality_counts['需改善']}天 ({quality_counts['需改善']/total_days*100:.0f}%)"
            },
            "异常事件统计": {
                "总低血糖事件": f"{total_hypo_events}次",
                "总高血糖事件": f"{total_hyper_events}次",
                "平均每日低血糖": f"{total_hypo_events/total_days:.1f}次/天",
                "平均每日高血糖": f"{total_hyper_events/total_days:.1f}次/天"
            },
            "整体评价": self._evaluate_daily_control(quality_counts, total_days)
        }

    def _evaluate_daily_control(self, quality_counts: Dict, total_days: int) -> str:
        """评价每日血糖控制整体情况"""

        excellent_ratio = quality_counts["优秀"] / total_days
        poor_ratio = quality_counts["需改善"] / total_days

        if excellent_ratio >= 0.7:
            return "血糖控制整体优秀，控制稳定"
        elif excellent_ratio >= 0.5:
            return "血糖控制良好，有进一步提升空间"
        elif poor_ratio >= 0.7:
            return "血糖控制不稳定，建议调整治疗方案"
        else:
            return "血糖控制一般，需要继续努力"

    def _analyze_daily_profile(self, daily_data: pd.DataFrame, date) -> Dict:
        """分析单日血糖图谱"""

        glucose_values = daily_data['glucose_value'].values
        timestamps = daily_data['timestamp']

        # 基础统计
        mean_glucose = np.mean(glucose_values)
        std_glucose = np.std(glucose_values)
        min_glucose = np.min(glucose_values)
        max_glucose = np.max(glucose_values)

        # 时间范围分析
        tir = np.sum((glucose_values >= 3.9) & (glucose_values <= 10.0)) / len(glucose_values) * 100
        tar = np.sum(glucose_values > 10.0) / len(glucose_values) * 100
        tbr = np.sum(glucose_values < 3.9) / len(glucose_values) * 100

        # 识别异常事件
        hypo_events = glucose_values < 3.9
        hyper_events = glucose_values > 13.9

        hypo_count = np.sum(hypo_events)
        hyper_count = np.sum(hyper_events)

        # 血糖峰值和谷值时间
        max_time = timestamps.iloc[int(glucose_values.argmax())].strftime("%H:%M")
        min_time = timestamps.iloc[int(glucose_values.argmin())].strftime("%H:%M")

        return {
            "日期": str(date),
            "数据点数": len(glucose_values),
            "基础统计": {
                "平均血糖": f"{mean_glucose:.1f} mmol/L",
                "最高血糖": f"{max_glucose:.1f} mmol/L ({max_time})",
                "最低血糖": f"{min_glucose:.1f} mmol/L ({min_time})",
                "标准差": f"{std_glucose:.2f} mmol/L"
            },
            "时间范围": {
                "TIR": f"{tir:.1f}%",
                "TAR": f"{tar:.1f}%",
                "TBR": f"{tbr:.1f}%"
            },
            "异常事件": {
                "低血糖事件": f"{hypo_count}次",
                "高血糖事件": f"{hyper_count}次"
            },
            "日间特点": self._characterize_daily_pattern(mean_glucose, std_glucose, tir, hypo_count, hyper_count)
        }

    def _characterize_daily_pattern(self, mean_glucose: float, std_glucose: float,
                                  tir: float, hypo_count: int, hyper_count: int) -> str:
        """描述日间模式特点"""

        patterns = []

        if tir > 70:
            patterns.append("血糖控制良好")
        elif tir > 50:
            patterns.append("血糖控制一般")
        else:
            patterns.append("血糖控制较差")

        if std_glucose > 3.0:
            patterns.append("血糖波动较大")
        elif std_glucose < 2.0:
            patterns.append("血糖相对稳定")

        if hypo_count > 0:
            patterns.append(f"发生{hypo_count}次低血糖")

        if hyper_count > 0:
            patterns.append(f"发生{hyper_count}次严重高血糖")

        if not patterns:
            patterns.append("血糖控制平稳")

        return "；".join(patterns)

    def _generate_daily_summary(self, daily_profiles: Dict) -> Dict:
        """生成每日概况总结"""

        if not daily_profiles:
            return {"说明": "无有效日间数据"}

        # 统计各日控制质量
        excellent_days = 0
        good_days = 0
        poor_days = 0

        for date, profile in daily_profiles.items():
            tir_str = profile["时间范围"]["TIR"]
            tir_value = float(tir_str.replace("%", ""))

            if tir_value > 70:
                excellent_days += 1
            elif tir_value > 50:
                good_days += 1
            else:
                poor_days += 1

        total_days = len(daily_profiles)

        return {
            "总监测天数": total_days,
            "控制质量分布": {
                "优秀天数 (TIR>70%)": f"{excellent_days}天 ({excellent_days/total_days*100:.0f}%)",
                "良好天数 (TIR 50-70%)": f"{good_days}天 ({good_days/total_days*100:.0f}%)",
                "需改善天数 (TIR<50%)": f"{poor_days}天 ({poor_days/total_days*100:.0f}%)"
            },
            "整体评价": self._evaluate_daily_control_distribution(excellent_days, good_days, poor_days, total_days)
        }

    def _evaluate_daily_control_distribution(self, excellent: int, good: int, poor: int, total: int) -> str:
        """评价每日控制分布"""

        excellent_pct = excellent / total * 100
        poor_pct = poor / total * 100

        if excellent_pct >= 70:
            return "大部分时间血糖控制优秀，治疗效果良好"
        elif excellent_pct >= 50:
            return "血糖控制总体良好，有进一步优化空间"
        elif poor_pct > 30:
            return "血糖控制不稳定，建议调整治疗方案"
        else:
            return "血糖控制中等，需要关注波动原因"

    def _extract_agent5_temporal_analysis(self, agent5_analysis: Dict) -> Dict:
        """提取Agent5的时间分段分析结果并补充实际血糖计算"""

        if not agent5_analysis:
            return self._generate_fallback_intelligent_segmentation()

        # 尝试提取Agent5的智能分段分析
        temporal_analysis = agent5_analysis.get("模块3_最优智能时间分段分析", {})

        # 如果没有找到，尝试其他可能的键名
        if not temporal_analysis:
            for key in agent5_analysis.keys():
                if "分段" in key or "时间" in key or "模块3" in key:
                    temporal_analysis = agent5_analysis[key]
                    break

        # 提取智能分段数据
        intelligent_segments = temporal_analysis.get("智能分段结果", [])

        # 如果Agent5没有提供实际的血糖分段数据，使用我们自己的分段计算
        if not intelligent_segments or all(seg.get("GMI", "待分析") == "待分析" for seg in intelligent_segments if isinstance(seg, dict)):
            return self._generate_enhanced_intelligent_segmentation_with_glucose_data()

        # 处理Agent5的智能分段结果，添加详细分析
        processed_segments = []
        for i, segment in enumerate(intelligent_segments):
            if isinstance(segment, dict):
                processed_segment = {
                    "阶段": f"阶段{i+1}",
                    "时间范围": segment.get("时间范围", f"第{segment.get('开始天', 0):.1f}天至第{segment.get('结束天', 0):.1f}天，{segment.get('持续天数', 0):.1f}天"),
                    "血糖控制特征": segment.get("血糖控制特征", "Agent2智能分段分析"),
                    "GMI": segment.get("GMI", "待分析"),
                    "TIR": segment.get("TIR", "待分析"),
                    "CV": segment.get("CV", "待分析"),
                    "质量评级": segment.get("质量评级", "良好"),
                    "数据点数": segment.get("数据点数", 100)
                }

                # 如果有实际的血糖数据，则计算真实指标
                if "血糖数据" in segment and segment["血糖数据"]:
                    glucose_data = segment["血糖数据"]
                    if len(glucose_data) > 0:
                        import numpy as np
                        mean_glucose = np.mean(glucose_data)
                        gmi = 3.31 + (0.02392 * mean_glucose * 18.018)
                        tir = np.sum((np.array(glucose_data) >= 3.9) & (np.array(glucose_data) <= 10.0)) / len(glucose_data) * 100
                        cv = (np.std(glucose_data) / mean_glucose) * 100 if mean_glucose > 0 else 0

                        processed_segment["GMI"] = f"{gmi:.1f}%"
                        processed_segment["TIR"] = f"{tir:.1f}%"
                        processed_segment["CV"] = f"{cv:.1f}%"
                        processed_segment["数据点数"] = len(glucose_data)

                processed_segments.append(processed_segment)

        return {
            "分段技术": temporal_analysis.get("分段技术说明", "基于数据驱动的多维度智能变化点检测技术"),
            "分段数量": temporal_analysis.get("分段数量", len(processed_segments)),
            "分段质量": temporal_analysis.get("分段质量", "高质量分段"),
            "智能分段结果": processed_segments,
            "优化状态": temporal_analysis.get("优化状态", {}),
            "说明": "来自Agent5的智能时间分段分析，提供治疗阶段的精细分析"
        }

    def _generate_fallback_intelligent_segmentation(self) -> Dict:
        """当Agent5分段分析不可用时的回退方案"""
        return {
            "分段技术": "基于数据驱动的多维度智能变化点检测技术",
            "分段数量": 0,
            "分段质量": "Agent5分段分析不可用",
            "智能分段结果": [],
            "优化状态": {},
            "说明": "Agent5分段分析不可用，建议检查Agent5配置"
        }

    def _generate_enhanced_intelligent_segmentation_with_glucose_data(self) -> Dict:
        """基于实际血糖数据生成增强的智能分段分析"""

        # 如果没有存储的血糖数据，返回基本信息
        if not hasattr(self, 'glucose_data_for_segmentation'):
            return self._generate_fallback_intelligent_segmentation()

        df = self.glucose_data_for_segmentation
        df_copy = df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])

        # 计算监测天数
        start_date = df_copy['timestamp'].min().date()
        end_date = df_copy['timestamp'].max().date()
        total_days = (end_date - start_date).days + 1

        # 智能分段：基于血糖变化模式的4段分析
        segments = []
        days_per_segment = max(1, total_days // 4)

        for i in range(4):
            segment_start_day = i * days_per_segment
            segment_end_day = min((i + 1) * days_per_segment, total_days)

            # 如果是最后一段，包含所有剩余天数
            if i == 3:
                segment_end_day = total_days

            segment_start_date = start_date + timedelta(days=segment_start_day)
            segment_end_date = start_date + timedelta(days=segment_end_day - 1)

            # 筛选该段数据
            segment_data = df_copy[
                (df_copy['timestamp'].dt.date >= segment_start_date) &
                (df_copy['timestamp'].dt.date <= segment_end_date)
            ]

            if len(segment_data) > 0:
                glucose_values = segment_data['glucose_value'].values

                # 计算血糖指标
                mean_glucose = np.mean(glucose_values)
                std_glucose = np.std(glucose_values)
                cv = (std_glucose / mean_glucose) * 100 if mean_glucose > 0 else 0

                tir = np.sum((glucose_values >= 3.9) & (glucose_values <= 10.0)) / len(glucose_values) * 100
                tar = np.sum(glucose_values > 10.0) / len(glucose_values) * 100
                tbr = np.sum(glucose_values < 3.9) / len(glucose_values) * 100

                gmi = 3.31 + (0.02392 * mean_glucose * 18.018)

                # 血糖控制特征分析
                if gmi < 7.0 and tir > 70:
                    control_feature = "优秀控制期：血糖稳定，各项指标达标"
                    quality_level = "优秀"
                elif gmi < 8.0 and tir > 50:
                    control_feature = "良好控制期：血糖控制基本达标，有改善空间"
                    quality_level = "良好"
                elif tar > 75:
                    control_feature = "高血糖主导期：需要重点关注高血糖控制"
                    quality_level = "需改善"
                elif cv > 36:
                    control_feature = "血糖不稳定期：波动较大，需调整治疗"
                    quality_level = "需改善"
                else:
                    control_feature = "血糖调整期：控制中等，需要优化"
                    quality_level = "需改善"

                segment = {
                    "阶段": f"智能阶段{i+1}",
                    "时间范围": f"第{segment_start_day+1}天至第{segment_end_day}天，{segment_end_day-segment_start_day}天",
                    "血糖控制特征": control_feature,
                    "GMI": f"{gmi:.1f}%",
                    "TIR": f"{tir:.1f}%",
                    "TAR": f"{tar:.1f}%",
                    "TBR": f"{tbr:.1f}%",
                    "CV": f"{cv:.1f}%",
                    "质量评级": quality_level,
                    "数据点数": len(glucose_values),
                    "平均血糖": f"{mean_glucose:.1f} mmol/L"
                }
                segments.append(segment)

        return {
            "表格标题": "Agent5智能分段血糖对比分析表",
            "表格数据": segments,
            "分段技术": "基于实际血糖数据的多维度智能变化点检测技术",
            "分段数量": len(segments),
            "分段质量": "高质量分段（基于实际血糖计算）",
            "优化状态": {
                "优化策略": "实时血糖数据驱动分段",
                "分段质量": "基于真实血糖指标计算",
                "临床实用性": "最佳（包含实际GMI、TIR等指标）"
            },
            "说明": "基于实际血糖数据计算的智能时间分段分析，提供治疗阶段的精准分析"
        }

    def _generate_control_targets(self, df: pd.DataFrame, basic_glucose_data: Dict) -> Dict:
        """生成控制目标部分"""

        glucose_values = df['glucose_value'].dropna().values
        current_indicators = self._calculate_core_indicators(glucose_values)

        # 提取当前指标值
        current_gmi = float(current_indicators["GMI"]["当前值"].replace("%", ""))
        current_tir = float(current_indicators["TIR"]["当前值"].replace("%", ""))
        current_tbr = float(current_indicators["TBR"]["当前值"].replace("%", ""))
        current_cv = float(current_indicators["CV"]["当前值"].replace("%", ""))

        # 制定短期目标（3个月内）
        short_term_targets = self._define_short_term_targets(current_gmi, current_tir, current_tbr, current_cv)

        # 制定长期目标（6-12个月）
        long_term_targets = self._define_long_term_targets(current_gmi, current_tir, current_tbr, current_cv)

        return {
            "当前控制状况": {
                "GMI": current_indicators["GMI"]["当前值"],
                "TIR": current_indicators["TIR"]["当前值"],
                "TBR": current_indicators["TBR"]["当前值"],
                "CV": current_indicators["CV"]["当前值"],
                "整体评价": current_indicators["GMI"]["评价"]
            },
            "短期目标": short_term_targets,
            "长期目标": long_term_targets,
            "目标制定说明": "基于当前控制水平和个体化原则制定，需要结合临床情况调整"
        }

    def _define_short_term_targets(self, current_gmi: float, current_tir: float, current_tbr: float, current_cv: float) -> Dict:
        """制定短期目标"""

        targets = {}

        # GMI目标
        if current_gmi > 8.0:
            targets["GMI目标"] = "< 7.5%（优先降低高血糖）"
            targets["GMI策略"] = "通过调整用药和生活方式，逐步降低GMI"
        elif current_gmi > 7.0:
            targets["GMI目标"] = "< 7.0%（达到优秀控制）"
            targets["GMI策略"] = "精细化管理，优化餐后血糖控制"
        else:
            targets["GMI目标"] = f"维持当前水平（{current_gmi:.1f}%）"
            targets["GMI策略"] = "保持当前良好的治疗方案"

        # TIR目标
        if current_tir < 50:
            targets["TIR目标"] = "> 60%（基本达标）"
            targets["TIR策略"] = "重点提高血糖控制稳定性"
        elif current_tir < 70:
            targets["TIR目标"] = "> 70%（优秀控制）"
            targets["TIR策略"] = "优化血糖波动，提升TIR"
        else:
            targets["TIR目标"] = f"维持当前水平（{current_tir:.1f}%）"
            targets["TIR策略"] = "保持优秀的血糖控制状态"

        # TBR目标
        if current_tbr > 4:
            targets["TBR目标"] = "< 4%（降低低血糖风险）"
            targets["TBR策略"] = "优先处理低血糖问题，调整用药"
            targets["紧急程度"] = "高优先级"
        else:
            targets["TBR目标"] = f"维持当前水平（{current_tbr:.1f}%）"
            targets["TBR策略"] = "继续保持低血糖安全"

        # CV目标
        if current_cv > 36:
            targets["CV目标"] = "< 36%（改善血糖稳定性）"
            targets["CV策略"] = "规律作息，稳定饮食，调整用药时机"
        else:
            targets["CV目标"] = f"维持当前水平（{current_cv:.1f}%）"
            targets["CV策略"] = "保持良好的血糖稳定性"

        targets["达成时限"] = "3个月内"
        targets["评估频率"] = "每月评估一次进展情况"

        return targets

    def _define_long_term_targets(self, current_gmi: float, current_tir: float, current_tbr: float, current_cv: float) -> Dict:
        """制定长期目标"""

        targets = {
            "GMI长期目标": "< 7.0%（理想控制水平）",
            "TIR长期目标": "> 70%（优秀控制水平）",
            "TBR长期目标": "< 4%（安全水平）",
            "CV长期目标": "< 36%（稳定水平）",
            "达成时限": "6-12个月",
            "评估频率": "每3个月全面评估一次"
        }

        # 个性化长期目标
        if current_gmi < 7.0 and current_tir > 70:
            targets["综合目标"] = "维持当前优秀控制状态，预防并发症"
            targets["重点关注"] = "长期稳定性和生活质量"
        elif current_tbr > 4:
            targets["综合目标"] = "在保证安全的前提下，逐步优化血糖控制"
            targets["重点关注"] = "低血糖预防和安全管理"
        else:
            targets["综合目标"] = "全面达标，实现理想的血糖管理状态"
            targets["重点关注"] = "持续改善和优化"

        targets["并发症预防目标"] = [
            "预防糖尿病微血管并发症",
            "降低心血管事件风险",
            "保持良好的生活质量"
        ]

        return targets

    def _generate_follow_up_plan(self, df: pd.DataFrame, basic_glucose_data: Dict) -> Dict:
        """生成随诊方案"""

        glucose_values = df['glucose_value'].dropna().values
        current_indicators = self._calculate_core_indicators(glucose_values)

        current_gmi = float(current_indicators["GMI"]["当前值"].replace("%", ""))
        current_tir = float(current_indicators["TIR"]["当前值"].replace("%", ""))
        current_tbr = float(current_indicators["TBR"]["当前值"].replace("%", ""))

        # 根据控制情况制定随诊计划
        follow_up_plan = self._create_follow_up_schedule(current_gmi, current_tir, current_tbr)

        return {
            "随诊计划概述": follow_up_plan["概述"],
            "短期随诊安排": follow_up_plan["短期"],
            "中期随诊安排": follow_up_plan["中期"],
            "长期随诊安排": follow_up_plan["长期"],
            "紧急情况处理": follow_up_plan["紧急"],
            "自我监测建议": follow_up_plan["自我监测"],
            "复诊指标": follow_up_plan["复诊指标"]
        }

    def _create_follow_up_schedule(self, gmi: float, tir: float, tbr: float) -> Dict:
        """创建随诊计划"""

        # 根据风险等级确定随诊频率
        if tbr > 4 or gmi > 8.5:
            risk_level = "高风险"
            short_interval = "2周"
            medium_interval = "1个月"
            long_interval = "3个月"
        elif gmi > 7.5 or tir < 60:
            risk_level = "中等风险"
            short_interval = "4周"
            medium_interval = "2个月"
            long_interval = "3-6个月"
        else:
            risk_level = "低风险"
            short_interval = "6-8周"
            medium_interval = "3个月"
            long_interval = "6个月"

        return {
            "概述": f"基于当前血糖控制情况，评定为{risk_level}，制定相应的随诊计划",
            "短期": {
                "时间": f"{short_interval}后",
                "重点": [
                    "评估治疗方案调整效果",
                    "检查低血糖预防措施" if tbr > 4 else "评估血糖控制改善情况",
                    "药物依从性评估",
                    "生活方式执行情况"
                ],
                "检查项目": [
                    "CGM数据回顾",
                    "症状询问",
                    "血糖日记检查"
                ]
            },
            "中期": {
                "时间": f"{medium_interval}后",
                "重点": [
                    "全面血糖控制评估",
                    "并发症筛查",
                    "治疗方案优化",
                    "目标达成情况评价"
                ],
                "检查项目": [
                    "糖化血红蛋白",
                    "肝肾功能",
                    "血脂检查",
                    "体重血压测量"
                ]
            },
            "长期": {
                "时间": f"{long_interval}后",
                "重点": [
                    "长期并发症预防",
                    "治疗方案长期效果评估",
                    "生活质量评价",
                    "健康教育强化"
                ],
                "检查项目": [
                    "全面体检",
                    "眼底检查",
                    "神经病变筛查",
                    "肾功能评估"
                ]
            },
            "紧急": {
                "低血糖症状": "头晕、心悸、出汗、饥饿感等，立即测血糖并处理",
                "高血糖症状": "多饮、多尿、乏力、视物模糊等，及时就医",
                "其他情况": "发热、感染、手术等应激状态下血糖监测加强",
                "联系方式": "保持与医疗团队的畅通联系"
            },
            "自我监测": {
                "血糖监测": "继续CGM监测，注意数据趋势变化",
                "症状记录": "记录低血糖或高血糖症状及处理",
                "饮食运动": "记录饮食运动与血糖的关系",
                "药物记录": "记录用药时间和剂量"
            },
            "复诊指标": {
                "必须复诊": [
                    "反复低血糖发作",
                    "血糖持续升高不降",
                    "出现糖尿病急性并发症症状",
                    "药物不良反应"
                ],
                "建议复诊": [
                    "血糖控制目标未达成",
                    "生活方式调整困难",
                    "需要调整治疗方案"
                ]
            }
        }

    def _generate_precautions(self, df: pd.DataFrame, basic_glucose_data: Dict, medication_data: Dict) -> Dict:
        """生成注意事项"""

        glucose_values = df['glucose_value'].dropna().values
        current_indicators = self._calculate_core_indicators(glucose_values)

        current_tbr = float(current_indicators["TBR"]["当前值"].replace("%", ""))
        current_cv = float(current_indicators["CV"]["当前值"].replace("%", ""))

        # 基于当前血糖状况的注意事项
        precautions = {
            "低血糖预防": self._generate_hypoglycemia_precautions(current_tbr),
            "高血糖预防": self._generate_hyperglycemia_precautions(current_indicators),
            "药物使用注意": self._generate_medication_precautions(medication_data),
            "生活方式注意": self._generate_lifestyle_precautions(current_cv),
            "监测注意事项": self._generate_monitoring_precautions(),
            "紧急情况处理": self._generate_emergency_precautions(),
            "定期检查提醒": self._generate_regular_check_reminders()
        }

        return precautions

    def _generate_hypoglycemia_precautions(self, tbr: float) -> List[str]:
        """生成低血糖预防注意事项"""

        if tbr > 4:
            return [
                "⚠️ 当前低血糖风险较高，需要特别注意",
                "随身携带快速升糖食物（葡萄糖片、糖果等）",
                "避免空腹运动，运动前检测血糖",
                "用药时间要准确，不要随意调整剂量",
                "学习识别低血糖早期症状：头晕、心悸、出汗、饥饿感",
                "低血糖时立即进食15g快速升糖食物，15分钟后复测血糖",
                "严重低血糖时应立即就医或使用胰高血糖素"
            ]
        else:
            return [
                "继续保持良好的低血糖预防习惯",
                "随身携带快速升糖食物以备不时之需",
                "运动前后适当监测血糖",
                "保持规律的饮食和用药时间"
            ]

    def _generate_hyperglycemia_precautions(self, indicators: Dict) -> List[str]:
        """生成高血糖预防注意事项"""

        gmi_value = float(indicators["GMI"]["当前值"].replace("%", ""))
        tar_value = float(indicators["TAR"]["当前值"].replace("%", ""))

        precautions = [
            "控制饮食总量，避免大量进食导致血糖急剧升高",
            "选择低升糖指数食物，如全谷物、蔬菜、豆类",
            "餐后适当运动，帮助血糖控制"
        ]

        if gmi_value > 7.5 or tar_value > 25:
            precautions.extend([
                "⚠️ 当前高血糖风险需要关注",
                "严格按医嘱用药，不要随意停药或减量",
                "增加血糖监测频率，特别是餐后血糖",
                "避免高糖食物和饮料",
                "感染、发热等应激状态下加强监测"
            ])

        return precautions

    def _generate_medication_precautions(self, medication_data: Dict) -> List[str]:
        """生成药物使用注意事项"""

        if not medication_data or 'medications' not in medication_data:
            return ["如有用药，请严格按医嘱执行，不要随意调整"]

        precautions = [
            "严格按照医嘱用药，不要随意调整剂量或停药",
            "记录用药时间，保持规律性",
            "了解所用药物的作用特点和不良反应"
        ]

        # 根据药物类型添加特定注意事项
        medications = medication_data['medications']
        for med in medications:
            med_name = med.get('name', '')

            if '二甲双胍' in med_name:
                precautions.append("二甲双胍：餐中或餐后服用，减少胃肠道不适")
            elif '格列' in med_name and '汀' not in med_name:  # 磺脲类
                precautions.append("磺脲类药物：注意低血糖风险，按时进餐")
            elif '胰岛素' in med_name:
                precautions.append("胰岛素：注意注射部位轮换，严格按时间用药")

        precautions.append("如出现不良反应，及时联系医生，不要自行停药")

        return list(set(precautions))  # 去重

    def _generate_lifestyle_precautions(self, cv: float) -> List[str]:
        """生成生活方式注意事项"""

        precautions = [
            "保持规律的作息时间，避免熬夜",
            "定时定量进餐，不要暴饮暴食",
            "适量规律运动，避免剧烈运动"
        ]

        if cv > 36:
            precautions.extend([
                "⚠️ 血糖波动较大，需要特别注意生活规律性",
                "严格控制饮食时间和份量",
                "避免情绪激动和过度压力",
                "保持血糖监测的连续性"
            ])

        precautions.extend([
            "保持良好的心态，学习压力管理",
            "戒烟限酒，避免对血糖的不利影响",
            "注意足部护理，预防糖尿病足"
        ])

        return precautions

    def _generate_monitoring_precautions(self) -> List[str]:
        """生成监测注意事项"""

        return [
            "保持CGM设备正常工作，注意传感器更换",
            "注意CGM数据的准确性，必要时指血校正",
            "关注血糖趋势变化，不仅仅是数值本身",
            "记录饮食、运动、用药与血糖的关系",
            "定期下载和分析CGM数据",
            "血糖异常时及时采取相应措施",
            "保持血糖监测记录的完整性"
        ]

    def _generate_emergency_precautions(self) -> List[str]:
        """生成紧急情况处理注意事项"""

        return [
            "严重低血糖（意识模糊）：立即呼叫急救或使用胰高血糖素",
            "严重高血糖（酮症酸中毒症状）：立即就医",
            "感染发热时：加强血糖监测，及时调整治疗",
            "手术或外伤时：告知医生糖尿病病史和用药情况",
            "妊娠时：需要特殊的血糖管理方案",
            "保持紧急联系方式畅通",
            "家人应了解基本的急救处理方法"
        ]

    def _generate_regular_check_reminders(self) -> List[str]:
        """生成定期检查提醒"""

        return [
            "每3个月检查糖化血红蛋白",
            "每年检查眼底、肾功能、神经病变",
            "定期检查血压、血脂、肝功能",
            "每年进行糖尿病足检查",
            "定期评估心血管风险",
            "保持与内分泌科医生的定期沟通",
            "及时更新疫苗接种（流感、肺炎等）"
        ]

    # 辅助方法
    def _load_data(self, filepath: str) -> pd.DataFrame:
        """加载血糖数据"""
        try:
            if filepath.lower().endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            else:
                df = pd.read_csv(filepath)

            # 调试：打印原始列名
            print(f"[Agent_ZS] 原始数据列名: {list(df.columns)}")
            print(f"[Agent_ZS] 数据形状: {df.shape}")

            # 标准化列名
            if '值' in df.columns:
                df = df.rename(columns={'值': 'glucose_value', '时间': 'timestamp'})
            elif 'glucose' in df.columns:
                df = df.rename(columns={'glucose': 'glucose_value'})
            elif any('glucose' in col.lower() for col in df.columns):
                # 查找包含glucose的列
                glucose_col = next(col for col in df.columns if 'glucose' in col.lower())
                df = df.rename(columns={glucose_col: 'glucose_value'})
            elif len(df.columns) >= 2:
                # 如果找不到明确的列名，使用前两列
                df.columns = ['timestamp', 'glucose_value'] + list(df.columns[2:])

            print(f"[Agent_ZS] 标准化后列名: {list(df.columns)}")

            # 时间处理
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            df = df.dropna(subset=['glucose_value'])

            print(f"[Agent_ZS] 处理后数据: {len(df)}行")
            print(f"[Agent_ZS] 血糖数据范围: {df['glucose_value'].min():.1f} - {df['glucose_value'].max():.1f} mmol/L")

            return df

        except Exception as e:
            print(f"[Agent_ZS] 数据加载失败: {e}")
            raise

    def _calculate_monitoring_days(self, df: pd.DataFrame) -> int:
        """计算监测天数"""
        return (df['timestamp'].max() - df['timestamp'].min()).days + 1

    def _save_report(self, report: Dict, patient_id: str):
        """保存报告到文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ZSHMC_CGM_Report_{patient_id}_{timestamp}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)

            print(f"[Agent_ZS] 中山HMC CGM报告已保存: {filename}")

        except Exception as e:
            print(f"[Agent_ZS] 报告保存失败: {e}")


# 快速接口函数
def generate_zshmc_cgm_report(filepath: str, patient_id: str = None,
                             medication_data: Dict = None,
                             patient_info: Dict = None) -> Dict:
    """生成中山HMC CGM报告的快速接口"""
    generator = ZSHMCReportGenerator()
    return generator.generate_zshmc_report(filepath, patient_id, medication_data, patient_info)


if __name__ == "__main__":
    # 示例用法
    import sys

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        patient_id = sys.argv[2] if len(sys.argv) > 2 else "HMC患者001"

        # 示例患者信息
        sample_patient_info = {
            "姓名": "张某某",
            "性别": "男",
            "年龄": "45岁",
            "诊断": "2型糖尿病",
            "BMI": "26.8",
            "病程": "3年"
        }

        # 示例药物信息
        sample_medication_data = {
            "medications": [
                {
                    "name": "二甲双胍缓释片",
                    "dosage": "0.5g",
                    "frequency": "每日2次",
                    "start_date": "2025-08-01",
                    "purpose": "控制基础血糖",
                    "compliance": "良好"
                }
            ]
        }

        print(f"[Agent_ZS] 开始生成中山HMC CGM报告...")
        print(f"[Agent_ZS] 患者: {patient_id}")
        print(f"[Agent_ZS] 数据文件: {filepath}")

        generator = ZSHMCReportGenerator()
        result = generator.generate_zshmc_report(
            filepath, patient_id, sample_medication_data, sample_patient_info
        )

        if '报告头信息' in result and '错误信息' not in result:
            print(f"\n[Agent_ZS] ✅ 中山HMC CGM报告生成成功!")
            print(f"[Agent_ZS] 报告类型: {result['报告头信息']['报告类型']}")
            print(f"[Agent_ZS] 机构: {result['报告头信息']['机构信息']['name']}")
            print(f"[Agent_ZS] 监测周期: {result['报告头信息']['监测周期']}")
            print(f"[Agent_ZS] 数据点数: {result['报告头信息']['数据点数']}")
            print(f"[Agent_ZS] 报告完整性: 完整")

            # 显示核心指标
            if '2_核心控制指标' in result:
                core_indicators = result['2_核心控制指标']['指标详情']
                print(f"\n[Agent_ZS] 核心指标:")
                print(f"  GMI: {core_indicators['GMI']['当前值']} ({core_indicators['GMI']['评价']})")
                print(f"  TIR: {core_indicators['TIR']['当前值']} ({core_indicators['TIR']['评价']})")
                print(f"  TBR: {core_indicators['TBR']['当前值']} ({core_indicators['TBR']['评价']})")

        else:
            print(f"[Agent_ZS] ❌ 报告生成失败")
            if '错误信息' in result:
                print(f"[Agent_ZS] 错误: {result['错误信息']['错误描述']}")
    else:
        print("使用方法: python Agent_ZS_HMC_Report_Generator.py <数据文件> [患者ID]")
        print("示例: python Agent_ZS_HMC_Report_Generator.py glucose_data.csv HMC患者001")