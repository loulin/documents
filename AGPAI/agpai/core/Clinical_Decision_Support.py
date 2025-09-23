"""
血糖混沌分析临床决策支持系统
基于混沌分析为临床医生提供个性化治疗决策建议
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json
import warnings
warnings.filterwarnings('ignore')

class RiskLevel(Enum):
    """风险等级"""
    LOW = "低风险"
    MODERATE = "中等风险"  
    HIGH = "高风险"
    CRITICAL = "极高风险"

class TreatmentUrgency(Enum):
    """治疗紧急程度"""
    ROUTINE = "常规随访"
    EXPEDITED = "加急处理"
    URGENT = "紧急处理"
    EMERGENCY = "立即处理"

@dataclass
class ClinicalAlert:
    """临床预警"""
    alert_type: str
    severity: RiskLevel
    message: str
    recommendation: str
    evidence: Dict
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class TreatmentRecommendation:
    """治疗建议"""
    category: str  # 胰岛素调整、生活方式、监测频率等
    priority: int  # 1-5 优先级
    action: str
    rationale: str
    expected_outcome: str
    monitoring_plan: str
    contraindications: List[str] = None
    
class ClinicalDecisionSupport:
    """
    临床决策支持系统
    """
    
    def __init__(self):
        # 决策规则库
        self.decision_rules = self.load_decision_rules()
        # 治疗方案库
        self.treatment_protocols = self.load_treatment_protocols()
        # 风险评估标准
        self.risk_criteria = self.load_risk_criteria()
        
    def load_decision_rules(self) -> Dict:
        """
        加载决策规则库
        """
        return {
            "brittleness_rules": {
                "I型混沌脆性": {
                    "primary_strategy": "保守稳定",
                    "insulin_adjustment": "谨慎减量",
                    "monitoring": "24小时监护",
                    "target_hba1c": "8.0-8.5%",
                    "avoid": ["强化治疗", "快速调整"]
                },
                "II型准周期脆性": {
                    "primary_strategy": "时间治疗学",
                    "insulin_adjustment": "时间优化",
                    "monitoring": "重点监测Dawn现象",
                    "target_hba1c": "7.5-8.0%",
                    "focus": ["给药时间", "生活规律"]
                },
                "III型随机脆性": {
                    "primary_strategy": "智能化管理",
                    "insulin_adjustment": "考虑胰岛素泵",
                    "monitoring": "频繁监测",
                    "target_hba1c": "7.5-8.0%",
                    "recommend": ["闭环系统", "神经评估"]
                },
                "IV型记忆缺失脆性": {
                    "primary_strategy": "重建稳态",
                    "insulin_adjustment": "长效制剂优先",
                    "monitoring": "评估认知功能",
                    "target_hba1c": "7.0-7.5%",
                    "focus": ["GLP-1激动剂", "肝糖调节"]
                },
                "V型频域脆性": {
                    "primary_strategy": "节律重建",
                    "insulin_adjustment": "昼夜节律考虑",
                    "monitoring": "生物节律评估",
                    "target_hba1c": "7.0-7.5%",
                    "recommend": ["光照治疗", "褪黑素"]
                },
                "稳定型": {
                    "primary_strategy": "维持优化",
                    "insulin_adjustment": "渐进调整",
                    "monitoring": "常规监测",
                    "target_hba1c": "6.5-7.0%",
                    "focus": ["持续优化", "预防恶化"]
                }
            },
            
            "emergency_rules": {
                "lyapunov_critical": {
                    "threshold": 0.15,
                    "action": "立即降低治疗强度",
                    "urgency": TreatmentUrgency.EMERGENCY
                },
                "cv_critical": {
                    "threshold": 60,
                    "action": "紧急稳定血糖",
                    "urgency": TreatmentUrgency.URGENT
                },
                "severe_hypoglycemia_risk": {
                    "threshold": 3.0,  # mmol/L
                    "action": "立即调整胰岛素",
                    "urgency": TreatmentUrgency.EMERGENCY
                }
            }
        }
    
    def load_treatment_protocols(self) -> Dict:
        """
        加载治疗方案库
        """
        return {
            "insulin_protocols": {
                "conservative": {
                    "description": "保守治疗方案",
                    "basal_adjustment": "小幅调整(10-20%)",
                    "bolus_strategy": "保守计算",
                    "target_range": "6.0-10.0 mmol/L",
                    "suitable_for": ["混沌脆性", "高变异患者"]
                },
                "intensive": {
                    "description": "强化治疗方案", 
                    "basal_adjustment": "精细调整",
                    "bolus_strategy": "精确计算",
                    "target_range": "4.4-7.8 mmol/L",
                    "suitable_for": ["稳定型", "低风险患者"]
                },
                "pump_therapy": {
                    "description": "胰岛素泵治疗",
                    "indication": "随机脆性，频繁低血糖",
                    "advantages": "精确给药，可调基础率",
                    "monitoring": "加强CGM监测"
                }
            },
            
            "lifestyle_protocols": {
                "chaos_management": {
                    "diet": "规律进餐，稳定碳水",
                    "exercise": "温和有氧运动",
                    "sleep": "规律作息，充足睡眠",
                    "stress": "压力管理，放松训练"
                },
                "rhythm_restoration": {
                    "light_therapy": "明亮光照治疗",
                    "meal_timing": "固定进餐时间",
                    "sleep_hygiene": "严格睡眠卫生",
                    "social_rhythm": "社交节律稳定"
                }
            }
        }
    
    def load_risk_criteria(self) -> Dict:
        """
        加载风险评估标准
        """
        return {
            "immediate_risks": {
                "severe_hypoglycemia": {"threshold": 3.0, "risk": RiskLevel.CRITICAL},
                "extreme_hyperglycemia": {"threshold": 20.0, "risk": RiskLevel.CRITICAL},
                "chaos_index_critical": {"threshold": 0.2, "risk": RiskLevel.CRITICAL}
            },
            
            "short_term_risks": {
                "high_variability": {"threshold": 50, "risk": RiskLevel.HIGH},
                "poor_tir": {"threshold": 50, "risk": RiskLevel.HIGH},
                "frequent_lows": {"threshold": 10, "risk": RiskLevel.MODERATE}  # %时间
            },
            
            "long_term_risks": {
                "chaos_persistence": {"duration_days": 7, "risk": RiskLevel.HIGH},
                "brittleness_progression": {"severity_increase": 2, "risk": RiskLevel.HIGH}
            }
        }
    
    def analyze_patient_data(self, glucose_data: List[float], patient_info: Dict = None) -> Dict:
        """
        分析患者数据
        """
        # 计算所有指标
        traditional_metrics = self.calculate_traditional_metrics(glucose_data)
        chaos_metrics = self.calculate_chaos_metrics(glucose_data)
        brittleness_type = self.classify_brittleness(traditional_metrics, chaos_metrics)
        risk_assessment = self.assess_risks(traditional_metrics, chaos_metrics, brittleness_type)
        
        return {
            "traditional_metrics": traditional_metrics,
            "chaos_metrics": chaos_metrics,
            "brittleness_type": brittleness_type,
            "risk_assessment": risk_assessment,
            "patient_info": patient_info or {}
        }
    
    def generate_clinical_alerts(self, analysis_results: Dict) -> List[ClinicalAlert]:
        """
        生成临床预警
        """
        alerts = []
        
        traditional_metrics = analysis_results["traditional_metrics"]
        chaos_metrics = analysis_results["chaos_metrics"]
        brittleness_type = analysis_results["brittleness_type"]
        
        # 混沌脆性预警
        if "混沌脆性" in brittleness_type:
            alerts.append(ClinicalAlert(
                alert_type="血糖系统混沌",
                severity=RiskLevel.CRITICAL,
                message="患者血糖系统处于混沌状态，系统极不稳定",
                recommendation="立即调整为保守治疗目标，避免强化治疗",
                evidence={
                    "lyapunov_index": chaos_metrics["lyapunov"],
                    "cv_percent": traditional_metrics["CV"],
                    "brittleness_type": brittleness_type
                }
            ))
        
        # 高变异性预警
        if traditional_metrics["CV"] > 50:
            alerts.append(ClinicalAlert(
                alert_type="极高血糖变异性",
                severity=RiskLevel.HIGH,
                message=f"血糖变异系数{traditional_metrics['CV']:.1f}%，远超安全范围",
                recommendation="优化胰岛素方案，考虑胰岛素泵治疗",
                evidence={"cv_percent": traditional_metrics["CV"]}
            ))
        
        # TIR不达标预警
        if traditional_metrics["TIR"] < 50:
            alerts.append(ClinicalAlert(
                alert_type="TIR严重不达标",
                severity=RiskLevel.HIGH,
                message=f"目标范围时间仅{traditional_metrics['TIR']:.1f}%",
                recommendation="全面重新评估治疗方案",
                evidence={"tir_percent": traditional_metrics["TIR"]}
            ))
        
        # 低血糖风险预警
        if traditional_metrics["time_below_70"] > 10:
            alerts.append(ClinicalAlert(
                alert_type="高低血糖风险",
                severity=RiskLevel.HIGH,
                message=f"低血糖时间{traditional_metrics['time_below_70']:.1f}%，安全性堪忧",
                recommendation="减少胰岛素剂量，加强低血糖预防",
                evidence={"hypoglycemia_time": traditional_metrics["time_below_70"]}
            ))
        
        return alerts
    
    def generate_treatment_recommendations(self, analysis_results: Dict, 
                                         patient_history: Dict = None) -> List[TreatmentRecommendation]:
        """
        生成治疗建议
        """
        recommendations = []
        
        brittleness_type = analysis_results["brittleness_type"]
        traditional_metrics = analysis_results["traditional_metrics"]
        chaos_metrics = analysis_results["chaos_metrics"]
        
        # 基于脆性类型的核心建议
        brittleness_rules = self.decision_rules["brittleness_rules"].get(brittleness_type, {})
        
        if brittleness_type == "I型混沌脆性":
            recommendations.extend([
                TreatmentRecommendation(
                    category="胰岛素调整",
                    priority=1,
                    action="立即降低胰岛素剂量20-30%，采用保守治疗目标",
                    rationale="混沌系统对微小变化极度敏感，强化治疗可能导致系统崩溃",
                    expected_outcome="减少极端血糖事件，提高系统稳定性",
                    monitoring_plan="24小时CGM监护，每日评估混沌指标",
                    contraindications=["强化治疗", "快速剂量调整"]
                ),
                TreatmentRecommendation(
                    category="监测管理",
                    priority=1,
                    action="建立24小时监护，设置宽松的血糖报警范围",
                    rationale="混沌系统需要密切监控以防止严重事件",
                    expected_outcome="及时发现血糖异常，预防危险事件",
                    monitoring_plan="连续CGM，每4小时检查"
                )
            ])
            
        elif brittleness_type == "II型准周期脆性":
            recommendations.extend([
                TreatmentRecommendation(
                    category="时间治疗",
                    priority=1,
                    action="调整胰岛素给药时间，重点管理Dawn现象",
                    rationale="准周期脆性存在病理性但可识别的周期模式",
                    expected_outcome="打破病理周期，建立正常血糖节律",
                    monitoring_plan="重点监测4-8点血糖变化"
                ),
                TreatmentRecommendation(
                    category="生活方式",
                    priority=2,
                    action="建立严格规律的作息和进餐时间",
                    rationale="规律的生活节律有助于稳定血糖周期",
                    expected_outcome="减少周期性血糖波动",
                    monitoring_plan="记录生活节律与血糖关系"
                )
            ])
            
        elif brittleness_type == "III型随机脆性":
            recommendations.extend([
                TreatmentRecommendation(
                    category="设备治疗",
                    priority=1,
                    action="考虑胰岛素泵治疗，最好是闭环系统",
                    rationale="随机脆性需要智能化的实时调整",
                    expected_outcome="通过算法自动调整应对随机变化",
                    monitoring_plan="连续CGM配合智能算法"
                ),
                TreatmentRecommendation(
                    category="并发症筛查",
                    priority=2,
                    action="全面评估自主神经功能和认知功能",
                    rationale="随机脆性可能与神经病变相关",
                    expected_outcome="识别并处理潜在并发症",
                    monitoring_plan="神经功能定期评估"
                )
            ])
        
        # 基于传统指标的补充建议
        if traditional_metrics["TIR"] < 70:
            recommendations.append(TreatmentRecommendation(
                category="血糖目标",
                priority=2,
                action=f"当前TIR {traditional_metrics['TIR']:.1f}%，需要优化治疗方案",
                rationale="TIR不达标影响长期预后",
                expected_outcome="提高TIR至70%以上",
                monitoring_plan="每周评估TIR变化"
            ))
        
        if traditional_metrics["CV"] > 36:
            recommendations.append(TreatmentRecommendation(
                category="血糖稳定",
                priority=2,
                action=f"变异系数{traditional_metrics['CV']:.1f}%过高，需改善稳定性",
                rationale="高变异性增加低血糖风险和心血管并发症",
                expected_outcome="降低CV至36%以下",
                monitoring_plan="每周监测血糖变异性"
            ))
        
        return recommendations
    
    def create_decision_support_report(self, glucose_data: List[float], 
                                     patient_info: Dict = None,
                                     patient_history: Dict = None) -> Dict:
        """
        创建临床决策支持报告
        """
        # 分析患者数据
        analysis_results = self.analyze_patient_data(glucose_data, patient_info)
        
        # 生成预警和建议
        clinical_alerts = self.generate_clinical_alerts(analysis_results)
        treatment_recommendations = self.generate_treatment_recommendations(
            analysis_results, patient_history)
        
        # 确定治疗紧急程度
        urgency = self.determine_treatment_urgency(clinical_alerts, analysis_results)
        
        # 生成总结和优先级
        summary = self.generate_clinical_summary(analysis_results, clinical_alerts, 
                                               treatment_recommendations)
        
        report = {
            "报告生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "患者信息": patient_info or {},
            "分析结果": {
                "脆性类型": analysis_results["brittleness_type"],
                "风险评估": analysis_results["risk_assessment"],
                "关键指标": {
                    "TIR": analysis_results["traditional_metrics"]["TIR"],
                    "CV": analysis_results["traditional_metrics"]["CV"],
                    "Lyapunov指数": analysis_results["chaos_metrics"]["lyapunov"],
                    "近似熵": analysis_results["chaos_metrics"]["approximate_entropy"]
                }
            },
            "临床预警": [
                {
                    "类型": alert.alert_type,
                    "严重程度": alert.severity.value,
                    "消息": alert.message,
                    "建议": alert.recommendation,
                    "证据": alert.evidence
                } for alert in clinical_alerts
            ],
            "治疗建议": [
                {
                    "类别": rec.category,
                    "优先级": rec.priority,
                    "行动": rec.action,
                    "理由": rec.rationale,
                    "预期结果": rec.expected_outcome,
                    "监测计划": rec.monitoring_plan,
                    "禁忌症": rec.contraindications or []
                } for rec in treatment_recommendations
            ],
            "治疗紧急程度": urgency.value,
            "临床总结": summary,
            "后续随访计划": self.generate_followup_plan(analysis_results, urgency)
        }
        
        return report
    
    def determine_treatment_urgency(self, alerts: List[ClinicalAlert], 
                                  analysis_results: Dict) -> TreatmentUrgency:
        """
        确定治疗紧急程度
        """
        if any(alert.severity == RiskLevel.CRITICAL for alert in alerts):
            return TreatmentUrgency.EMERGENCY
        elif any(alert.severity == RiskLevel.HIGH for alert in alerts):
            return TreatmentUrgency.URGENT
        elif analysis_results["traditional_metrics"]["TIR"] < 50:
            return TreatmentUrgency.EXPEDITED
        else:
            return TreatmentUrgency.ROUTINE
    
    def generate_clinical_summary(self, analysis_results: Dict, alerts: List[ClinicalAlert], 
                                recommendations: List[TreatmentRecommendation]) -> str:
        """
        生成临床总结
        """
        brittleness = analysis_results["brittleness_type"]
        tir = analysis_results["traditional_metrics"]["TIR"]
        cv = analysis_results["traditional_metrics"]["CV"]
        
        summary_parts = []
        
        # 脆性类型总结
        if "混沌脆性" in brittleness:
            summary_parts.append("⚠️ 患者血糖系统处于混沌状态，需要立即采用保守治疗策略")
        elif "脆性" in brittleness:
            summary_parts.append(f"患者表现为{brittleness}，需要特殊管理策略")
        else:
            summary_parts.append(f"患者血糖调节为{brittleness}")
        
        # 控制质量总结
        if tir >= 70 and cv < 36:
            summary_parts.append("✅ 血糖控制质量良好")
        elif tir < 50 or cv > 50:
            summary_parts.append("❌ 血糖控制质量差，需要重新评估治疗方案")
        else:
            summary_parts.append("⚠️ 血糖控制质量一般，有改善空间")
        
        # 风险总结
        if len(alerts) >= 3:
            summary_parts.append("🚨 存在多个高风险因素，需要综合干预")
        elif len(alerts) >= 1:
            summary_parts.append("⚠️ 存在需要关注的风险因素")
        
        # 治疗建议总结
        high_priority_recs = [r for r in recommendations if r.priority == 1]
        if high_priority_recs:
            summary_parts.append(f"🎯 有{len(high_priority_recs)}项高优先级治疗建议需要立即执行")
        
        return " ".join(summary_parts)
    
    def generate_followup_plan(self, analysis_results: Dict, urgency: TreatmentUrgency) -> Dict:
        """
        生成随访计划
        """
        brittleness = analysis_results["brittleness_type"]
        
        if urgency == TreatmentUrgency.EMERGENCY:
            return {
                "下次随访": "24-48小时内",
                "监测频率": "连续CGM + 每日评估",
                "重点关注": ["系统稳定性", "极端血糖事件", "混沌指标变化"],
                "评估指标": ["Lyapunov指数", "CV", "TIR", "低血糖事件"]
            }
        elif urgency == TreatmentUrgency.URGENT:
            return {
                "下次随访": "1周内",
                "监测频率": "CGM + 每周评估",
                "重点关注": ["治疗反应", "脆性类型变化", "预警指标"],
                "评估指标": ["TIR改善", "CV降低", "脆性分型稳定"]
            }
        elif urgency == TreatmentUrgency.EXPEDITED:
            return {
                "下次随访": "2周内",
                "监测频率": "CGM + 双周评估",
                "重点关注": ["治疗效果", "血糖稳定性"],
                "评估指标": ["TIR提升", "变异性改善"]
            }
        else:
            return {
                "下次随访": "1个月内",
                "监测频率": "常规CGM + 月度评估",
                "重点关注": ["维持现状", "预防恶化"],
                "评估指标": ["指标稳定性", "长期趋势"]
            }
    
    def calculate_traditional_metrics(self, glucose_data: List[float]) -> Dict:
        """计算传统指标（与之前相同）"""
        glucose_array = np.array(glucose_data)
        
        mean_glucose = np.mean(glucose_array)
        std_glucose = np.std(glucose_array)
        cv = (std_glucose / mean_glucose) * 100
        
        tir = np.sum((glucose_array >= 3.9) & (glucose_array <= 10.0)) / len(glucose_array) * 100
        time_below_70 = np.sum(glucose_array < 3.9) / len(glucose_array) * 100
        time_very_low = np.sum(glucose_array < 3.0) / len(glucose_array) * 100
        time_above_180 = np.sum(glucose_array > 10.0) / len(glucose_array) * 100
        
        return {
            "mean_glucose": mean_glucose,
            "CV": cv,
            "TIR": tir,
            "time_below_70": time_below_70,
            "time_very_low": time_very_low,
            "time_above_180": time_above_180
        }
    
    def calculate_chaos_metrics(self, glucose_data: List[float]) -> Dict:
        """计算混沌指标（与之前相同）"""
        glucose_array = np.array(glucose_data)
        
        try:
            # Lyapunov指数
            rate_changes = np.diff(glucose_array)
            divergence = []
            for i in range(len(rate_changes)-1):
                if abs(rate_changes[i]) > 0.01:
                    ratio = abs(rate_changes[i+1]) / abs(rate_changes[i])
                    if ratio > 0:
                        divergence.append(np.log(ratio))
            
            lyapunov = np.mean(divergence) if divergence else 0
            
            # 近似熵
            def approximate_entropy(data, m=2, r=0.2):
                N = len(data)
                if N < 10:
                    return 0
                
                def _maxdist(xi, xj):
                    return max([abs(ua - va) for ua, va in zip(xi, xj)])
                
                patterns = [data[i:i+m] for i in range(N-m+1)]
                C = []
                
                for i in range(len(patterns)):
                    matches = sum(1 for j, pattern in enumerate(patterns) 
                                if _maxdist(patterns[i], pattern) <= r * np.std(data))
                    C.append(matches / len(patterns))
                
                phi_m = np.mean([np.log(c) for c in C if c > 0])
                
                patterns_m1 = [data[i:i+m+1] for i in range(N-m)]
                C_m1 = []
                
                for i in range(len(patterns_m1)):
                    matches = sum(1 for j, pattern in enumerate(patterns_m1) 
                                if _maxdist(patterns_m1[i], pattern) <= r * np.std(data))
                    C_m1.append(matches / len(patterns_m1))
                
                phi_m1 = np.mean([np.log(c) for c in C_m1 if c > 0])
                
                return phi_m - phi_m1
            
            approx_entropy = approximate_entropy(glucose_array)
            
            return {
                "lyapunov": lyapunov,
                "approximate_entropy": approx_entropy
            }
            
        except Exception:
            return {"lyapunov": 0, "approximate_entropy": 0}
    
    def classify_brittleness(self, traditional_metrics: Dict, chaos_metrics: Dict) -> str:
        """分类脆性（与之前相同）"""
        cv = traditional_metrics["CV"]
        lyapunov = chaos_metrics["lyapunov"]
        approx_entropy = chaos_metrics["approximate_entropy"]
        
        if lyapunov > 0.1 and cv > 40:
            return "I型混沌脆性"
        elif lyapunov > 0.01 and cv > 30:
            return "II型准周期脆性"
        elif cv > 35 and approx_entropy > 0.6:
            return "III型随机脆性"
        elif approx_entropy > 0.5:
            return "IV型记忆缺失脆性"
        elif cv < 25:
            return "稳定型"
        else:
            return "中等不稳定型"
    
    def assess_risks(self, traditional_metrics: Dict, chaos_metrics: Dict, 
                    brittleness_type: str) -> Dict:
        """评估风险"""
        risks = {
            "immediate_risks": [],
            "short_term_risks": [],
            "long_term_risks": []
        }
        
        # 即时风险
        if chaos_metrics["lyapunov"] > 0.2:
            risks["immediate_risks"].append("系统混沌崩溃风险")
        if traditional_metrics["CV"] > 60:
            risks["immediate_risks"].append("极端血糖变异风险")
        if traditional_metrics["time_very_low"] > 2:
            risks["immediate_risks"].append("严重低血糖风险")
        
        # 短期风险
        if traditional_metrics["TIR"] < 50:
            risks["short_term_risks"].append("血糖控制恶化风险")
        if "混沌脆性" in brittleness_type:
            risks["short_term_risks"].append("治疗反应不可预测风险")
        
        # 长期风险
        if traditional_metrics["CV"] > 36:
            risks["long_term_risks"].append("心血管并发症风险增加")
        if "脆性" in brittleness_type:
            risks["long_term_risks"].append("微血管并发症风险")
        
        return risks

def demonstrate_clinical_decision_support():
    """
    演示临床决策支持系统
    """
    print("="*80)
    print("血糖混沌分析临床决策支持系统演示")
    print("="*80)
    
    # 创建决策支持系统
    cds = ClinicalDecisionSupport()
    
    # 模拟三种不同的患者场景
    scenarios = [
        {
            "name": "场景1：混沌脆性患者",
            "patient_info": {"patient_id": "P001", "age": 45, "diabetes_duration": 15},
            "glucose_data": generate_chaotic_glucose_data()
        },
        {
            "name": "场景2：稳定控制患者", 
            "patient_info": {"patient_id": "P002", "age": 35, "diabetes_duration": 8},
            "glucose_data": generate_stable_glucose_data()
        },
        {
            "name": "场景3：高变异患者",
            "patient_info": {"patient_id": "P003", "age": 60, "diabetes_duration": 20},
            "glucose_data": generate_high_variability_data()
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}")
        print("="*50)
        
        # 生成决策支持报告
        report = cds.create_decision_support_report(
            scenario["glucose_data"],
            scenario["patient_info"]
        )
        
        # 显示关键结果
        print(f"患者: {report['患者信息']['patient_id']}")
        print(f"脆性类型: {report['分析结果']['脆性类型']}")
        print(f"TIR: {report['分析结果']['关键指标']['TIR']:.1f}%")
        print(f"CV: {report['分析结果']['关键指标']['CV']:.1f}%")
        print(f"治疗紧急程度: {report['治疗紧急程度']}")
        
        print(f"\n📋 临床预警 ({len(report['临床预警'])}个):")
        for i, alert in enumerate(report['临床预警'], 1):
            print(f"  {i}. {alert['严重程度']} - {alert['类型']}")
            print(f"     {alert['消息']}")
        
        print(f"\n🎯 治疗建议 (前3项):")
        for i, rec in enumerate(report['治疗建议'][:3], 1):
            print(f"  {i}. [{rec['类别']}] 优先级{rec['优先级']}")
            print(f"     行动: {rec['行动']}")
            print(f"     理由: {rec['理由']}")
        
        print(f"\n📅 随访计划:")
        followup = report['后续随访计划']
        print(f"  下次随访: {followup['下次随访']}")
        print(f"  监测频率: {followup['监测频率']}")
        print(f"  重点关注: {', '.join(followup['重点关注'])}")
        
        print(f"\n💡 临床总结:")
        print(f"  {report['临床总结']}")
        
    # 保存示例报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/Users/williamsun/Documents/gplus/docs/AGPAI/agpai/reports/Clinical_Decision_Support_Demo_{timestamp}.json"
    
    # 生成最后一个场景的完整报告作为示例
    sample_report = cds.create_decision_support_report(
        scenarios[-1]["glucose_data"],
        scenarios[-1]["patient_info"]
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n示例决策支持报告已保存至: {output_file}")
    print("="*80)

def generate_chaotic_glucose_data() -> List[float]:
    """生成混沌脆性血糖数据"""
    np.random.seed(42)
    glucose = []
    val = 8.0
    for i in range(96):
        # 混沌映射 + 极端波动
        r = 3.9
        val = r * (val/20) * (1 - val/20) * 20
        val += np.random.normal(0, 3)
        if np.random.random() < 0.15:  # 高概率极端值
            val += np.random.uniform(-8, 10)
        glucose.append(np.clip(val, 2, 20))
    return glucose

def generate_stable_glucose_data() -> List[float]:
    """生成稳定控制血糖数据"""
    np.random.seed(123)
    glucose = []
    for i in range(96):
        t = i * 0.25
        val = 7.2 + 0.8*np.sin(2*np.pi*t/24) + np.random.normal(0, 0.5)
        glucose.append(np.clip(val, 6, 9))
    return glucose

def generate_high_variability_data() -> List[float]:
    """生成高变异性血糖数据"""
    np.random.seed(456)
    glucose = []
    val = 9.0
    for i in range(96):
        val += np.random.normal(0, 2.8)
        if np.random.random() < 0.08:
            val += np.random.uniform(-5, 6)
        glucose.append(np.clip(val, 3, 16))
    return glucose

if __name__ == "__main__":
    demonstrate_clinical_decision_support()