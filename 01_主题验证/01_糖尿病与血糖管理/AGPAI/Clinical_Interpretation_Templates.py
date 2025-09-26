#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临床解读标注模板系统
为AGP图表和血糖曲线提供标准化的临床解读标注模板
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json

class SeverityLevel(Enum):
    """严重程度级别"""
    CRITICAL = "critical"    # 需要立即处理
    WARNING = "warning"      # 需要关注
    INFO = "info"           # 信息提示
    POSITIVE = "positive"   # 积极表现

class PatternType(Enum):
    """血糖模式类型"""
    DAWN_PHENOMENON = "dawn_phenomenon"           # 黎明现象
    POSTPRANDIAL_PEAK = "postprandial_peak"     # 餐后峰值
    HYPOGLYCEMIA = "hypoglycemia"                # 低血糖
    HYPERGLYCEMIA = "hyperglycemia"              # 高血糖
    NOCTURNAL_INSTABILITY = "nocturnal_instability"  # 夜间不稳定
    HIGH_VARIABILITY = "high_variability"        # 高变异性
    GOOD_CONTROL = "good_control"                # 良好控制
    PLATEAU_PATTERN = "plateau_pattern"          # 平台期
    RAPID_CHANGE = "rapid_change"                # 快速变化
    EXERCISE_EFFECT = "exercise_effect"          # 运动影响
    MEDICATION_EFFECT = "medication_effect"      # 药物作用
    STRESS_RESPONSE = "stress_response"          # 应激反应

@dataclass
class AnnotationTemplate:
    """标注模板数据结构"""
    pattern_type: PatternType
    severity: SeverityLevel
    title: str
    description: str
    clinical_significance: str
    recommended_action: str
    follow_up: str
    evidence_level: str
    icon: str
    color: str

class ClinicalInterpretationTemplates:
    """临床解读标注模板库"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.condition_thresholds = self._initialize_thresholds()
    
    def _initialize_thresholds(self) -> Dict:
        """初始化临床阈值"""
        return {
            'hypoglycemia': {
                'level1': 3.9,   # 低血糖警戒值
                'level2': 3.0,   # 严重低血糖
                'level3': 2.2    # 极重度低血糖
            },
            'hyperglycemia': {
                'level1': 10.0,  # 高血糖警戒值
                'level2': 13.9,  # 明显高血糖
                'level3': 16.7   # 严重高血糖
            },
            'variability': {
                'cv_low': 30,     # CV<30% 低变异
                'cv_moderate': 36, # CV<36% 中等变异
                'cv_high': 50     # CV>50% 高变异
            },
            'tir': {
                'excellent': 75,  # >75% 优秀
                'good': 70,       # 70-75% 良好
                'fair': 50,       # 50-70% 一般
                'poor': 50        # <50% 差
            },
            'dawn_phenomenon': {
                'mild': 1.0,      # 1-2 mmol/L/h 轻度
                'moderate': 2.0,  # 2-3 mmol/L/h 中度
                'severe': 3.0     # >3 mmol/L/h 重度
            }
        }
    
    def _initialize_templates(self) -> Dict[PatternType, AnnotationTemplate]:
        """初始化标注模板库"""
        templates = {}
        
        # 黎明现象模板
        templates[PatternType.DAWN_PHENOMENON] = AnnotationTemplate(
            pattern_type=PatternType.DAWN_PHENOMENON,
            severity=SeverityLevel.WARNING,
            title="黎明现象",
            description="凌晨4-8点血糖显著上升",
            clinical_significance="反映基础胰岛素不足或作用时效不当，可能导致全天血糖控制困难",
            recommended_action="调整长效胰岛素注射时间至睡前，或增加基础胰岛素剂量",
            follow_up="2周后复查CGM数据，评估调整效果",
            evidence_level="A级证据",
            icon="🌅",
            color="#FF8C00"
        )
        
        # 餐后峰值模板
        templates[PatternType.POSTPRANDIAL_PEAK] = AnnotationTemplate(
            pattern_type=PatternType.POSTPRANDIAL_PEAK,
            severity=SeverityLevel.WARNING,
            title="餐后血糖峰值过高",
            description="餐后2小时血糖峰值超过10.0 mmol/L",
            clinical_significance="提示餐时胰岛素剂量不足或注射时机不当，影响餐后血糖控制",
            recommended_action="优化餐时胰岛素剂量或提前15-30分钟注射",
            follow_up="调整后1周内监测餐后血糖变化",
            evidence_level="A级证据",
            icon="🍽️",
            color="#FF6B6B"
        )
        
        # 低血糖模板
        templates[PatternType.HYPOGLYCEMIA] = AnnotationTemplate(
            pattern_type=PatternType.HYPOGLYCEMIA,
            severity=SeverityLevel.CRITICAL,
            title="低血糖风险",
            description="血糖低于3.9 mmol/L或TBR>4%",
            clinical_significance="增加心血管事件风险，影响认知功能，可能导致严重并发症",
            recommended_action="立即减少胰岛素剂量，调整饮食时间，加强监测",
            follow_up="48小时内复查，确保低血糖事件消除",
            evidence_level="A级证据",
            icon="🚨",
            color="#DC143C"
        )
        
        # 高血糖模板
        templates[PatternType.HYPERGLYCEMIA] = AnnotationTemplate(
            pattern_type=PatternType.HYPERGLYCEMIA,
            severity=SeverityLevel.WARNING,
            title="持续高血糖",
            description="血糖持续超过13.9 mmol/L或TAR>25%",
            clinical_significance="增加急性并发症风险，加速慢性并发症进展",
            recommended_action="增加胰岛素剂量，评估感染或应激因素",
            follow_up="72小时内评估血糖改善情况",
            evidence_level="A级证据",
            icon="⚠️",
            color="#FFA500"
        )
        
        # 夜间不稳定模板
        templates[PatternType.NOCTURNAL_INSTABILITY] = AnnotationTemplate(
            pattern_type=PatternType.NOCTURNAL_INSTABILITY,
            severity=SeverityLevel.WARNING,
            title="夜间血糖不稳定",
            description="22:00-06:00血糖波动过大",
            clinical_significance="影响睡眠质量，可能存在基础胰岛素剂量或作用时间问题",
            recommended_action="重新评估基础胰岛素方案，排除Somogyi现象",
            follow_up="调整后1周内重点监测夜间血糖",
            evidence_level="B级证据",
            icon="🌙",
            color="#4B0082"
        )
        
        # 高变异性模板
        templates[PatternType.HIGH_VARIABILITY] = AnnotationTemplate(
            pattern_type=PatternType.HIGH_VARIABILITY,
            severity=SeverityLevel.INFO,
            title="血糖变异性高",
            description="血糖变异系数(CV)>36%",
            clinical_significance="增加低血糖和并发症风险，提示血糖管理不够稳定",
            recommended_action="规律化饮食和用药时间，加强血糖监测频率",
            follow_up="4周后重新评估变异性改善情况",
            evidence_level="A级证据",
            icon="📊",
            color="#8B4513"
        )
        
        # 良好控制模板
        templates[PatternType.GOOD_CONTROL] = AnnotationTemplate(
            pattern_type=PatternType.GOOD_CONTROL,
            severity=SeverityLevel.POSITIVE,
            title="血糖控制良好",
            description="TIR>70%，血糖稳定在目标范围",
            clinical_significance="表明当前治疗方案有效，有助于减少并发症风险",
            recommended_action="维持当前治疗方案，继续健康生活方式",
            follow_up="3个月后常规复查",
            evidence_level="A级证据",
            icon="✅",
            color="#228B22"
        )
        
        # 快速变化模板
        templates[PatternType.RAPID_CHANGE] = AnnotationTemplate(
            pattern_type=PatternType.RAPID_CHANGE,
            severity=SeverityLevel.WARNING,
            title="血糖快速变化",
            description="血糖变化率>5 mmol/L/h",
            clinical_significance="可能存在胰岛素作用过强或饮食不当，增加血糖波动风险",
            recommended_action="检查胰岛素注射技术，调整碳水化合物摄入",
            follow_up="1周内重点监测血糖变化速率",
            evidence_level="B级证据",
            icon="⚡",
            color="#FF4500"
        )
        
        # 运动影响模板
        templates[PatternType.EXERCISE_EFFECT] = AnnotationTemplate(
            pattern_type=PatternType.EXERCISE_EFFECT,
            severity=SeverityLevel.INFO,
            title="运动相关血糖变化",
            description="运动前后血糖显著变化",
            clinical_significance="运动对血糖的积极影响，但需要防范运动后低血糖",
            recommended_action="运动前适当加餐或减少胰岛素，运动后监测血糖",
            follow_up="建立个体化运动血糖管理方案",
            evidence_level="A级证据",
            icon="🏃",
            color="#32CD32"
        )
        
        return templates
    
    def get_template_by_pattern(self, pattern_type: PatternType) -> AnnotationTemplate:
        """根据模式类型获取标注模板"""
        return self.templates.get(pattern_type)
    
    def get_dynamic_annotation(self, pattern_type: PatternType, metrics: Dict) -> Dict:
        """根据具体指标生成动态标注"""
        template = self.get_template_by_pattern(pattern_type)
        if not template:
            return None
        
        # 根据具体数值调整严重程度和建议
        dynamic_annotation = {
            'pattern_type': pattern_type.value,
            'severity': template.severity.value,
            'title': template.title,
            'icon': template.icon,
            'color': template.color,
            'description': self._customize_description(template, metrics),
            'clinical_significance': template.clinical_significance,
            'recommended_action': self._customize_action(template, metrics),
            'follow_up': template.follow_up,
            'evidence_level': template.evidence_level
        }
        
        # 根据指标值动态调整严重程度
        if pattern_type == PatternType.HYPOGLYCEMIA:
            min_glucose = metrics.get('min_glucose', 4.0)
            if min_glucose < 2.2:
                dynamic_annotation['severity'] = SeverityLevel.CRITICAL.value
                dynamic_annotation['title'] = "⚠️ 极重度低血糖"
            elif min_glucose < 3.0:
                dynamic_annotation['severity'] = SeverityLevel.CRITICAL.value
                dynamic_annotation['title'] = "🚨 严重低血糖"
        
        elif pattern_type == PatternType.DAWN_PHENOMENON:
            slope = metrics.get('dawn_slope', 0)
            if slope > 3.0:
                dynamic_annotation['severity'] = SeverityLevel.CRITICAL.value
                dynamic_annotation['title'] = "⚠️ 重度黎明现象"
        
        return dynamic_annotation
    
    def _customize_description(self, template: AnnotationTemplate, metrics: Dict) -> str:
        """根据具体指标定制描述"""
        base_description = template.description
        
        if template.pattern_type == PatternType.DAWN_PHENOMENON:
            slope = metrics.get('dawn_slope', 0)
            return f"{base_description} (上升速率: {slope:.1f} mmol/L/h)"
        
        elif template.pattern_type == PatternType.POSTPRANDIAL_PEAK:
            peak_height = metrics.get('peak_height', 0)
            return f"{base_description} (峰值高度: +{peak_height:.1f} mmol/L)"
        
        elif template.pattern_type == PatternType.HYPOGLYCEMIA:
            tbr = metrics.get('tbr_percentage', 0)
            return f"{base_description} (TBR: {tbr:.1f}%)"
        
        elif template.pattern_type == PatternType.HIGH_VARIABILITY:
            cv = metrics.get('cv_glucose', 0)
            return f"{base_description} (CV: {cv:.1f}%)"
        
        return base_description
    
    def _customize_action(self, template: AnnotationTemplate, metrics: Dict) -> str:
        """根据具体指标定制建议行动"""
        base_action = template.recommended_action
        
        if template.pattern_type == PatternType.HYPOGLYCEMIA:
            tbr = metrics.get('tbr_percentage', 0)
            if tbr > 10:
                return "紧急减少胰岛素剂量50%，增加监测频率，必要时暂停胰岛素注射"
            elif tbr > 7:
                return "显著减少胰岛素剂量25-30%，调整饮食时间"
        
        elif template.pattern_type == PatternType.DAWN_PHENOMENON:
            slope = metrics.get('dawn_slope', 0)
            if slope > 3.0:
                return "考虑更换长效胰岛素种类或增加基础胰岛素剂量30%"
            elif slope > 2.0:
                return "增加长效胰岛素剂量15-20%或调整注射时间"
        
        return base_action
    
    def generate_comprehensive_interpretation(self, analysis_results: Dict) -> Dict:
        """生成综合临床解读"""
        
        interpretation = {
            'overall_assessment': self._assess_overall_control(analysis_results),
            'priority_issues': self._identify_priority_issues(analysis_results),
            'positive_findings': self._identify_positive_findings(analysis_results),
            'action_plan': self._generate_action_plan(analysis_results),
            'patient_education_points': self._generate_education_points(analysis_results)
        }
        
        return interpretation
    
    def _assess_overall_control(self, results: Dict) -> Dict:
        """评估整体血糖控制水平"""
        tir = results.get('tir_percentage', 0)
        tbr = results.get('tbr_percentage', 0)
        tar = results.get('tar_percentage', 0)
        cv = results.get('cv_glucose', 50)
        
        # 综合评分算法
        score = 0
        
        # TIR评分 (0-40分)
        if tir >= 75:
            score += 40
        elif tir >= 70:
            score += 35
        elif tir >= 60:
            score += 25
        elif tir >= 50:
            score += 15
        else:
            score += 5
        
        # 安全性评分 (0-30分)
        if tbr <= 1:
            score += 30
        elif tbr <= 4:
            score += 20
        elif tbr <= 7:
            score += 10
        else:
            score += 0
        
        # 变异性评分 (0-30分)
        if cv <= 30:
            score += 30
        elif cv <= 36:
            score += 25
        elif cv <= 42:
            score += 15
        else:
            score += 5
        
        # 确定控制水平
        if score >= 85:
            level = "优秀"
            description = "血糖控制达到理想水平，继续保持"
            color = "#228B22"
        elif score >= 70:
            level = "良好" 
            description = "血糖控制基本达标，有进一步优化空间"
            color = "#32CD32"
        elif score >= 50:
            level = "一般"
            description = "血糖控制不够理想，需要调整治疗方案"
            color = "#FFA500"
        else:
            level = "需要改善"
            description = "血糖控制不佳，需要重新制定治疗策略"
            color = "#DC143C"
        
        return {
            'score': score,
            'level': level,
            'description': description,
            'color': color,
            'tir': f"{tir:.1f}%",
            'tbr': f"{tbr:.1f}%", 
            'cv': f"{cv:.1f}%"
        }
    
    def _identify_priority_issues(self, results: Dict) -> List[Dict]:
        """识别优先处理的问题"""
        issues = []
        
        # 严重低血糖
        tbr = results.get('tbr_percentage', 0)
        if tbr > 4:
            severity = 'critical' if tbr > 10 else 'warning'
            issues.append({
                'priority': 1,
                'severity': severity,
                'issue': '低血糖风险过高',
                'description': f'TBR达到{tbr:.1f}%，超过4%安全阈值',
                'immediate_action': '立即减少胰岛素剂量，加强监测'
            })
        
        # 严重高血糖
        tar = results.get('tar_percentage', 0)
        if tar > 50:
            issues.append({
                'priority': 2,
                'severity': 'warning',
                'issue': '高血糖时间过长',
                'description': f'TAR达到{tar:.1f}%，远超过25%目标',
                'immediate_action': '评估并增加胰岛素剂量'
            })
        
        # 血糖变异性过高
        cv = results.get('cv_glucose', 0)
        if cv > 50:
            issues.append({
                'priority': 3,
                'severity': 'warning',
                'issue': '血糖变异性极高',
                'description': f'CV达到{cv:.1f}%，远超过36%目标',
                'immediate_action': '规范饮食和用药时间，增加监测'
            })
        
        return sorted(issues, key=lambda x: x['priority'])
    
    def _identify_positive_findings(self, results: Dict) -> List[Dict]:
        """识别积极表现"""
        positive = []
        
        tir = results.get('tir_percentage', 0)
        tbr = results.get('tbr_percentage', 0)
        cv = results.get('cv_glucose', 50)
        
        if tir >= 70:
            positive.append({
                'finding': f'TIR达标 ({tir:.1f}%)',
                'significance': '血糖控制达到国际标准'
            })
        
        if tbr <= 1:
            positive.append({
                'finding': f'低血糖风险极低 ({tbr:.1f}%)',
                'significance': '安全性控制优秀'
            })
        
        if cv <= 30:
            positive.append({
                'finding': f'血糖变异性理想 ({cv:.1f}%)',
                'significance': '血糖稳定性优秀'
            })
        
        return positive
    
    def _generate_action_plan(self, results: Dict) -> List[Dict]:
        """生成行动计划"""
        plan = []
        
        # 基于分析结果生成具体行动项
        tbr = results.get('tbr_percentage', 0)
        if tbr > 4:
            plan.append({
                'timeline': '立即',
                'action': '减少胰岛素剂量',
                'details': '减少基础和餐时胰岛素剂量20-30%',
                'monitoring': '48小时内密切监测血糖'
            })
        
        dawn_slope = results.get('dawn_curve_slope', 0)
        if dawn_slope > 1.5:
            plan.append({
                'timeline': '1周内',
                'action': '调整长效胰岛素',
                'details': '将长效胰岛素改为睡前注射或增加剂量',
                'monitoring': '监测凌晨4-8点血糖变化'
            })
        
        cv = results.get('cv_glucose', 0)
        if cv > 36:
            plan.append({
                'timeline': '持续进行',
                'action': '规律化管理',
                'details': '固定饮食和用药时间，增加监测频率',
                'monitoring': '4周后重新评估变异性'
            })
        
        return plan
    
    def _generate_education_points(self, results: Dict) -> List[Dict]:
        """生成患者教育要点"""
        education = []
        
        tbr = results.get('tbr_percentage', 0)
        if tbr > 1:
            education.append({
                'topic': '低血糖预防',
                'key_points': [
                    '学会识别低血糖症状',
                    '随身携带快速糖源',
                    '运动前适当加餐',
                    '避免过量胰岛素注射'
                ]
            })
        
        tar = results.get('tar_percentage', 0)
        if tar > 25:
            education.append({
                'topic': '餐后血糖管理',
                'key_points': [
                    '控制碳水化合物摄入量',
                    '餐前15-30分钟注射胰岛素',
                    '餐后适当轻度活动',
                    '学会计算碳水化合物'
                ]
            })
        
        cv = results.get('cv_glucose', 0)
        if cv > 36:
            education.append({
                'topic': '血糖稳定性管理',
                'key_points': [
                    '保持规律的作息时间',
                    '固定三餐时间和内容',
                    '按时按量注射胰岛素',
                    '学会应对特殊情况'
                ]
            })
        
        return education

def demo_clinical_templates():
    """演示临床解读模板系统"""
    
    # 初始化模板系统
    template_system = ClinicalInterpretationTemplates()
    
    # 模拟分析结果
    analysis_results = {
        'tir_percentage': 65.2,
        'tbr_percentage': 6.8,
        'tar_percentage': 28.0,
        'cv_glucose': 42.5,
        'mean_glucose': 9.8,
        'dawn_curve_slope': 2.3,
        'morning_peak_height': 6.5,
        'nocturnal_curve_flatness': 0.6
    }
    
    print("=== 临床解读模板系统演示 ===\n")
    
    # 生成综合解读
    interpretation = template_system.generate_comprehensive_interpretation(analysis_results)
    
    # 显示整体评估
    overall = interpretation['overall_assessment']
    print("📊 整体血糖控制评估:")
    print(f"   控制水平: {overall['level']} ({overall['score']}/100分)")
    print(f"   评估说明: {overall['description']}")
    print(f"   TIR: {overall['tir']}, TBR: {overall['tbr']}, CV: {overall['cv']}\n")
    
    # 显示优先问题
    if interpretation['priority_issues']:
        print("🚨 优先处理问题:")
        for issue in interpretation['priority_issues']:
            severity_icon = {'critical': '🔴', 'warning': '🟡'}.get(issue['severity'], '📋')
            print(f"   {severity_icon} [{issue['priority']}] {issue['issue']}")
            print(f"      {issue['description']}")
            print(f"      立即行动: {issue['immediate_action']}\n")
    
    # 显示积极表现
    if interpretation['positive_findings']:
        print("✅ 积极表现:")
        for finding in interpretation['positive_findings']:
            print(f"   • {finding['finding']} - {finding['significance']}")
        print()
    
    # 显示行动计划
    if interpretation['action_plan']:
        print("📋 具体行动计划:")
        for i, action in enumerate(interpretation['action_plan'], 1):
            print(f"   {i}. [{action['timeline']}] {action['action']}")
            print(f"      具体措施: {action['details']}")
            print(f"      监测要求: {action['monitoring']}\n")
    
    # 显示患者教育
    if interpretation['patient_education_points']:
        print("📚 患者教育要点:")
        for edu in interpretation['patient_education_points']:
            print(f"   📖 {edu['topic']}:")
            for point in edu['key_points']:
                print(f"      • {point}")
            print()
    
    # 演示单个模式的动态标注
    print("🔍 单个模式动态标注示例:")
    
    # 黎明现象标注
    dawn_metrics = {'dawn_slope': 2.3}
    dawn_annotation = template_system.get_dynamic_annotation(PatternType.DAWN_PHENOMENON, dawn_metrics)
    print(f"   {dawn_annotation['icon']} {dawn_annotation['title']}")
    print(f"   描述: {dawn_annotation['description']}")
    print(f"   建议: {dawn_annotation['recommended_action']}\n")
    
    # 低血糖标注
    hypo_metrics = {'tbr_percentage': 6.8, 'min_glucose': 3.2}
    hypo_annotation = template_system.get_dynamic_annotation(PatternType.HYPOGLYCEMIA, hypo_metrics)
    print(f"   {hypo_annotation['icon']} {hypo_annotation['title']}")
    print(f"   描述: {hypo_annotation['description']}")
    print(f"   建议: {hypo_annotation['recommended_action']}")
    
    return interpretation

if __name__ == "__main__":
    demo_clinical_templates()