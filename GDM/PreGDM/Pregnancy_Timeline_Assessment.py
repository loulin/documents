#!/usr/bin/env python3
"""
妊娠期时间线评估模块
基于孕周的动态GDM风险评估和管理策略
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
from dataclasses import dataclass
from enum import Enum

class PregnancyStage(Enum):
    """妊娠期阶段枚举"""
    PRECONCEPTION = "preconception"          # 孕前
    FIRST_TRIMESTER = "first_trimester"      # 孕早期 (0-13周)
    SECOND_TRIMESTER = "second_trimester"    # 孕中期 (14-27周)
    THIRD_TRIMESTER = "third_trimester"      # 孕晚期 (28-40周)
    POSTPARTUM = "postpartum"                # 产后

@dataclass
class TimelineEvent:
    """时间线事件数据类"""
    gestational_week: int
    event_type: str
    description: str
    risk_level: str
    action_required: bool
    recommendations: List[str]
    parameters: Dict

class PregnancyTimelineAssessment:
    """妊娠期时间线评估主类"""
    
    def __init__(self):
        """初始化时间线评估系统"""
        
        # 关键时间点定义
        self.key_timepoints = {
            'preconception': 0,
            'early_pregnancy': 8,
            'first_trimester_end': 13,
            'anatomy_scan': 20,
            'gdm_screening': 24,
            'third_trimester_start': 28,
            'growth_scan': 32,
            'term_preparation': 36,
            'term': 40,
            'postpartum_early': 42,  # 产后2周
            'postpartum_screening': 48  # 产后6-12周
        }
        
        # 每个阶段的风险调整因子
        self.stage_risk_multipliers = {
            PregnancyStage.PRECONCEPTION: 1.0,
            PregnancyStage.FIRST_TRIMESTER: 0.8,    # 胰岛素需求较低
            PregnancyStage.SECOND_TRIMESTER: 1.2,   # 胰岛素抵抗开始增加
            PregnancyStage.THIRD_TRIMESTER: 1.8,    # 胰岛素抵抗最高
            PregnancyStage.POSTPARTUM: 0.5          # 产后风险降低
        }
        
        # 标准筛查时间表
        self.standard_screening_schedule = {
            'preconception': {
                'tests': ['fasting_glucose', 'hba1c', 'bmi', 'family_history'],
                'frequency': 'once',
                'purpose': 'baseline_risk_assessment'
            },
            'first_visit': {
                'weeks': 6-10,
                'tests': ['fasting_glucose', 'random_glucose', 'urine_glucose'],
                'frequency': 'once',
                'purpose': 'early_diabetes_detection'
            },
            'standard_gdm_screening': {
                'weeks': 24-28,
                'tests': ['ogtt_75g'],
                'frequency': 'once',
                'purpose': 'gdm_diagnosis'
            },
            'high_risk_early_screening': {
                'weeks': 16-20,
                'tests': ['ogtt_75g', 'hba1c'],
                'frequency': 'once',
                'purpose': 'early_gdm_detection'
            },
            'postpartum_screening': {
                'weeks': 48-54,  # 产后6-12周
                'tests': ['ogtt_75g', 'hba1c'],
                'frequency': 'once',
                'purpose': 'diabetes_persistence_check'
            }
        }
    
    def create_personalized_timeline(self, patient_data: Dict) -> Dict:
        """创建个性化妊娠期评估时间线"""
        
        print(f"📅 创建个性化妊娠期评估时间线")
        print(f"患者ID: {patient_data.get('patient_id', 'Unknown')}")
        
        # 获取当前孕周和风险等级
        current_week = patient_data.get('current_pregnancy', {}).get('gestational_weeks', 0)
        baseline_risk = self._calculate_baseline_risk_score(patient_data)
        
        # 生成完整时间线
        timeline_events = []
        
        # 1. 孕前评估(如果适用)
        if current_week <= 0:
            timeline_events.extend(self._generate_preconception_events(patient_data, baseline_risk))
        
        # 2. 孕早期事件 (0-13周)
        timeline_events.extend(self._generate_first_trimester_events(patient_data, baseline_risk, current_week))
        
        # 3. 孕中期事件 (14-27周)  
        timeline_events.extend(self._generate_second_trimester_events(patient_data, baseline_risk, current_week))
        
        # 4. 孕晚期事件 (28-40周)
        timeline_events.extend(self._generate_third_trimester_events(patient_data, baseline_risk, current_week))
        
        # 5. 产后事件
        timeline_events.extend(self._generate_postpartum_events(patient_data, baseline_risk))
        
        # 按孕周排序
        timeline_events.sort(key=lambda x: x.gestational_week)
        
        # 生成时间线报告
        timeline_report = self._generate_timeline_report(timeline_events, patient_data, current_week)
        
        return {
            'patient_id': patient_data.get('patient_id'),
            'current_gestational_week': current_week,
            'baseline_risk_score': baseline_risk,
            'timeline_events': [self._event_to_dict(event) for event in timeline_events],
            'upcoming_events': self._get_upcoming_events(timeline_events, current_week),
            'overdue_events': self._get_overdue_events(timeline_events, current_week),
            'timeline_report': timeline_report,
            'next_critical_milestone': self._get_next_critical_milestone(timeline_events, current_week)
        }
    
    def _calculate_baseline_risk_score(self, patient_data: Dict) -> float:
        """计算基线风险评分"""
        
        # 简化的风险评分算法
        risk_score = 0
        
        # 年龄风险
        age = patient_data.get('demographic', {}).get('age', 25)
        if age >= 35:
            risk_score += 15
        elif age >= 30:
            risk_score += 8
        
        # BMI风险
        bmi = patient_data.get('anthropometric', {}).get('pre_pregnancy_bmi', 22)
        if bmi >= 30:
            risk_score += 20
        elif bmi >= 25:
            risk_score += 10
        
        # 家族史风险
        family_dm = patient_data.get('family_history', {}).get('diabetes_family_history', 'none')
        if family_dm == 'first_degree':
            risk_score += 20
        elif family_dm == 'second_degree':
            risk_score += 10
        
        # 既往GDM史
        previous_gdm = patient_data.get('obstetric_history', {}).get('previous_gdm', False)
        if previous_gdm:
            risk_score += 25
        
        # PCOS
        pcos = patient_data.get('medical_history', {}).get('pcos', False)
        if pcos:
            risk_score += 15
        
        return min(risk_score, 100)
    
    def _determine_risk_category(self, risk_score: float) -> str:
        """确定风险类别"""
        if risk_score >= 60:
            return 'very_high'
        elif risk_score >= 40:
            return 'high'
        elif risk_score >= 20:
            return 'moderate'
        else:
            return 'low'
    
    def _generate_preconception_events(self, patient_data: Dict, baseline_risk: float) -> List[TimelineEvent]:
        """生成孕前评估事件"""
        
        events = []
        risk_category = self._determine_risk_category(baseline_risk)
        
        # 孕前基础评估
        events.append(TimelineEvent(
            gestational_week=-4,  # 孕前4周
            event_type='preconception_assessment',
            description='孕前GDM风险评估',
            risk_level=risk_category,
            action_required=True,
            recommendations=[
                '完成孕前健康检查',
                '评估糖尿病风险因素',
                '开始叶酸补充',
                '体重管理指导'
            ],
            parameters={
                'required_tests': ['fasting_glucose', 'hba1c', 'bmi', 'blood_pressure'],
                'lifestyle_interventions': ['diet_counseling', 'exercise_plan', 'weight_management']
            }
        ))
        
        # 高风险患者的特殊准备
        if risk_category in ['high', 'very_high']:
            events.append(TimelineEvent(
                gestational_week=-2,
                event_type='high_risk_preparation',
                description='高风险患者孕前准备',
                risk_level=risk_category,
                action_required=True,
                recommendations=[
                    '内分泌科会诊',
                    '强化生活方式干预',
                    '考虑孕前血糖监测',
                    '制定孕期管理计划'
                ],
                parameters={
                    'specialist_referral': 'endocrinology',
                    'monitoring_frequency': 'weekly',
                    'target_weight_loss': '5-10%' if patient_data.get('anthropometric', {}).get('pre_pregnancy_bmi', 22) >= 25 else None
                }
            ))
        
        return events
    
    def _generate_first_trimester_events(self, patient_data: Dict, baseline_risk: float, current_week: int) -> List[TimelineEvent]:
        """生成孕早期评估事件"""
        
        events = []
        risk_category = self._determine_risk_category(baseline_risk)
        
        # 首次产检 (6-10周)
        events.append(TimelineEvent(
            gestational_week=8,
            event_type='first_prenatal_visit',
            description='首次产检及早期糖尿病筛查',
            risk_level=risk_category,
            action_required=current_week <= 10,
            recommendations=[
                '空腹血糖检测',
                '随机血糖检测',
                '尿糖检测',
                '建立孕期健康档案'
            ],
            parameters={
                'screening_tests': ['fasting_glucose', 'random_glucose', 'urine_glucose'],
                'risk_assessment': 'comprehensive',
                'follow_up_interval': '4_weeks'
            }
        ))
        
        # 高风险患者的早期监测
        if risk_category in ['high', 'very_high']:
            events.append(TimelineEvent(
                gestational_week=10,
                event_type='high_risk_early_monitoring',
                description='高风险患者早期血糖监测',
                risk_level=risk_category,
                action_required=current_week <= 12,
                recommendations=[
                    '开始家庭血糖监测',
                    '营养师会诊',
                    '体重增长监控',
                    '每2周随访'
                ],
                parameters={
                    'glucose_monitoring': 'self_monitoring',
                    'nutrition_counseling': True,
                    'weight_gain_target': self._calculate_weight_gain_target(patient_data, 10),
                    'follow_up_frequency': 'biweekly'
                }
            ))
        
        # 孕早期结束评估 (12-13周)
        events.append(TimelineEvent(
            gestational_week=13,
            event_type='first_trimester_completion',
            description='孕早期完成评估',
            risk_level=risk_category,
            action_required=current_week <= 14,
            recommendations=[
                '评估孕早期风险因素变化',
                '调整管理策略',
                '准备孕中期筛查',
                '继续生活方式管理'
            ],
            parameters={
                'risk_reassessment': True,
                'strategy_adjustment': True,
                'preparation_for_screening': True
            }
        ))
        
        return events
    
    def _generate_second_trimester_events(self, patient_data: Dict, baseline_risk: float, current_week: int) -> List[TimelineEvent]:
        """生成孕中期评估事件"""
        
        events = []
        risk_category = self._determine_risk_category(baseline_risk)
        
        # 孕中期开始评估 (14周)
        events.append(TimelineEvent(
            gestational_week=14,
            event_type='second_trimester_start',
            description='孕中期开始，胰岛素抵抗增加期',
            risk_level=risk_category,
            action_required=current_week <= 15,
            recommendations=[
                '注意血糖变化',
                '调整饮食结构',
                '增加体力活动',
                '监测体重增长'
            ],
            parameters={
                'insulin_resistance_increase': True,
                'dietary_adjustment': True,
                'exercise_modification': True,
                'weight_monitoring': 'weekly'
            }
        ))
        
        # 高风险患者早期筛查 (16-20周)
        if risk_category in ['high', 'very_high']:
            events.append(TimelineEvent(
                gestational_week=18,
                event_type='early_gdm_screening',
                description='高风险患者早期GDM筛查',
                risk_level=risk_category,
                action_required=current_week <= 20,
                recommendations=[
                    '进行75g OGTT',
                    '检测HbA1c',
                    '评估胰岛素抵抗',
                    '如阳性，立即开始治疗'
                ],
                parameters={
                    'ogtt_75g': True,
                    'hba1c_test': True,
                    'homa_ir_calculation': True,
                    'immediate_treatment_if_positive': True
                }
            ))
        
        # 解剖学超声检查 (20-22周)
        events.append(TimelineEvent(
            gestational_week=20,
            event_type='anatomy_ultrasound',
            description='解剖学超声检查及胎儿生长评估',
            risk_level=risk_category,
            action_required=current_week <= 22,
            recommendations=[
                '评估胎儿结构',
                '测量胎儿生长参数',
                '评估羊水量',
                '筛查胎儿异常'
            ],
            parameters={
                'fetal_anatomy_scan': True,
                'growth_parameters': ['BPD', 'HC', 'AC', 'FL'],
                'amniotic_fluid_assessment': True,
                'anomaly_screening': True
            }
        ))
        
        # 标准GDM筛查 (24-28周)
        events.append(TimelineEvent(
            gestational_week=26,
            event_type='standard_gdm_screening',
            description='标准GDM筛查 (24-28周)',
            risk_level=risk_category,
            action_required=current_week <= 28,
            recommendations=[
                '75g OGTT检查',
                '严格按照诊断标准',
                '如诊断GDM，立即启动治疗',
                '制定个体化管理方案'
            ],
            parameters={
                'ogtt_75g': True,
                'diagnostic_criteria': 'IADPSG',
                'immediate_treatment': True,
                'individualized_management': True,
                'screening_window': '24-28_weeks'
            }
        ))
        
        return events
    
    def _generate_third_trimester_events(self, patient_data: Dict, baseline_risk: float, current_week: int) -> List[TimelineEvent]:
        """生成孕晚期评估事件"""
        
        events = []
        risk_category = self._determine_risk_category(baseline_risk)
        
        # 孕晚期开始评估 (28周)
        events.append(TimelineEvent(
            gestational_week=28,
            event_type='third_trimester_start',
            description='孕晚期开始，胰岛素抵抗峰值期',
            risk_level=risk_category,
            action_required=current_week <= 29,
            recommendations=[
                '密切监测血糖',
                '评估胰岛素需求',
                '加强胎儿监护',
                '准备分娩计划'
            ],
            parameters={
                'glucose_monitoring': 'intensive',
                'insulin_requirement_assessment': True,
                'fetal_surveillance': 'increased',
                'delivery_planning': True
            }
        ))
        
        # 胎儿生长监测 (30-32周)
        events.append(TimelineEvent(
            gestational_week=32,
            event_type='fetal_growth_assessment',
            description='胎儿生长评估及巨大儿筛查',
            risk_level=risk_category,
            action_required=current_week <= 33,
            recommendations=[
                '超声评估胎儿体重',
                '计算胎儿体重百分位',
                '评估巨大儿风险',
                '调整血糖控制目标'
            ],
            parameters={
                'ultrasound_biometry': True,
                'estimated_fetal_weight': True,
                'macrosomia_risk_assessment': True,
                'glucose_target_adjustment': True
            }
        ))
        
        # 孕晚期综合评估 (34-36周)
        events.append(TimelineEvent(
            gestational_week=35,
            event_type='late_pregnancy_assessment',
            description='孕晚期综合评估',
            risk_level=risk_category,
            action_required=current_week <= 36,
            recommendations=[
                '评估血糖控制情况',
                '胎儿肺成熟度评估',
                '分娩方式决策',
                '新生儿科准备'
            ],
            parameters={
                'glucose_control_assessment': True,
                'fetal_lung_maturity': True,
                'delivery_mode_planning': True,
                'neonatal_care_preparation': True
            }
        ))
        
        # 足月准备 (37-38周)
        events.append(TimelineEvent(
            gestational_week=37,
            event_type='term_preparation',
            description='足月分娩准备',
            risk_level=risk_category,
            action_required=current_week <= 38,
            recommendations=[
                '最终血糖评估',
                '分娩方式确认',
                '产后血糖管理计划',
                '母乳喂养指导'
            ],
            parameters={
                'final_glucose_assessment': True,
                'delivery_mode_confirmation': True,
                'postpartum_glucose_plan': True,
                'breastfeeding_counseling': True
            }
        ))
        
        return events
    
    def _generate_postpartum_events(self, patient_data: Dict, baseline_risk: float) -> List[TimelineEvent]:
        """生成产后评估事件"""
        
        events = []
        risk_category = self._determine_risk_category(baseline_risk)
        
        # 产后早期评估 (产后48-72小时)
        events.append(TimelineEvent(
            gestational_week=41,  # 产后1周
            event_type='immediate_postpartum',
            description='产后早期血糖评估',
            risk_level='moderate',  # 产后风险降低
            action_required=True,
            recommendations=[
                '监测产后血糖变化',
                '调整胰岛素剂量(如使用)',
                '母乳喂养血糖影响评估',
                '新生儿血糖监测'
            ],
            parameters={
                'glucose_monitoring': 'frequent',
                'insulin_adjustment': True,
                'breastfeeding_effect': True,
                'neonatal_glucose_monitoring': True
            }
        ))
        
        # 产后6-12周筛查
        events.append(TimelineEvent(
            gestational_week=48,  # 产后6-12周
            event_type='postpartum_screening',
            description='产后糖尿病筛查',
            risk_level='moderate',
            action_required=True,
            recommendations=[
                '75g OGTT检查',
                'HbA1c检测',
                '评估糖尿病持续存在',
                '制定长期随访计划'
            ],
            parameters={
                'ogtt_75g': True,
                'hba1c_test': True,
                'diabetes_persistence_assessment': True,
                'long_term_follow_up_plan': True,
                'screening_window': '6-12_weeks_postpartum'
            }
        ))
        
        # 产后长期随访计划
        events.append(TimelineEvent(
            gestational_week=52,  # 产后1年
            event_type='long_term_follow_up',
            description='长期糖尿病风险管理',
            risk_level='low_to_moderate',
            action_required=True,
            recommendations=[
                '年度糖尿病筛查',
                '生活方式维持',
                '再次妊娠咨询',
                '心血管风险评估'
            ],
            parameters={
                'annual_screening': True,
                'lifestyle_maintenance': True,
                'preconception_counseling': True,
                'cardiovascular_risk_assessment': True
            }
        ))
        
        return events
    
    def _calculate_weight_gain_target(self, patient_data: Dict, gestational_week: int) -> Dict:
        """计算体重增长目标"""
        
        pre_pregnancy_bmi = patient_data.get('anthropometric', {}).get('pre_pregnancy_bmi', 22)
        
        # IOM体重增长指南
        if pre_pregnancy_bmi < 18.5:
            total_gain_range = (12.5, 18.0)
        elif pre_pregnancy_bmi < 25:
            total_gain_range = (11.5, 16.0)
        elif pre_pregnancy_bmi < 30:
            total_gain_range = (7.0, 11.5)
        else:
            total_gain_range = (5.0, 9.0)
        
        # 按孕周分配
        if gestational_week <= 13:
            week_factor = 0.1
        else:
            week_factor = 0.1 + (gestational_week - 13) * 0.9 / 27
        
        target_min = total_gain_range[0] * week_factor
        target_max = total_gain_range[1] * week_factor
        
        return {
            'target_range_kg': (target_min, target_max),
            'current_week': gestational_week,
            'total_pregnancy_target': total_gain_range
        }
    
    def _get_upcoming_events(self, events: List[TimelineEvent], current_week: int) -> List[Dict]:
        """获取即将到来的事件"""
        
        upcoming = [
            self._event_to_dict(event) for event in events
            if event.gestational_week > current_week and event.gestational_week <= current_week + 4
        ]
        
        return sorted(upcoming, key=lambda x: x['gestational_week'])
    
    def _get_overdue_events(self, events: List[TimelineEvent], current_week: int) -> List[Dict]:
        """获取过期事件"""
        
        overdue = [
            self._event_to_dict(event) for event in events
            if event.gestational_week < current_week and event.action_required
        ]
        
        return sorted(overdue, key=lambda x: x['gestational_week'], reverse=True)
    
    def _get_next_critical_milestone(self, events: List[TimelineEvent], current_week: int) -> Optional[Dict]:
        """获取下一个关键里程碑"""
        
        critical_events = [
            event for event in events
            if event.gestational_week > current_week and 
            event.event_type in ['standard_gdm_screening', 'early_gdm_screening', 'postpartum_screening']
        ]
        
        if critical_events:
            next_event = min(critical_events, key=lambda x: x.gestational_week)
            return self._event_to_dict(next_event)
        
        return None
    
    def _event_to_dict(self, event: TimelineEvent) -> Dict:
        """将TimelineEvent转换为字典"""
        
        return {
            'gestational_week': event.gestational_week,
            'event_type': event.event_type,
            'description': event.description,
            'risk_level': event.risk_level,
            'action_required': event.action_required,
            'recommendations': event.recommendations,
            'parameters': event.parameters
        }
    
    def _generate_timeline_report(self, events: List[TimelineEvent], patient_data: Dict, current_week: int) -> str:
        """生成时间线报告"""
        
        patient_id = patient_data.get('patient_id', 'Unknown')
        baseline_risk = self._calculate_baseline_risk_score(patient_data)
        risk_category = self._determine_risk_category(baseline_risk)
        
        # 统计事件
        total_events = len(events)
        completed_events = sum(1 for event in events if event.gestational_week < current_week)
        upcoming_events = sum(1 for event in events if current_week <= event.gestational_week <= current_week + 4)
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        妊娠期GDM风险评估时间线                                 ║
║                    Pregnancy GDM Risk Assessment Timeline                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

👤 患者信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   患者ID: {patient_id}
   当前孕周: {current_week} 周
   基线风险评分: {baseline_risk:.1f}/100
   风险类别: {risk_category.upper()}
   评估日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 时间线概览
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   总事件数: {total_events}
   已完成事件: {completed_events}
   即将到来的事件 (4周内): {upcoming_events}
   当前妊娠阶段: {self._get_current_pregnancy_stage(current_week)}

⏰ 即将到来的关键事件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        upcoming = self._get_upcoming_events(events, current_week)
        for i, event in enumerate(upcoming[:5], 1):
            weeks_away = event['gestational_week'] - current_week
            urgency = "🔴" if weeks_away <= 1 else "🟡" if weeks_away <= 2 else "🟢"
            report += f"\n   {urgency} 孕{event['gestational_week']}周 ({weeks_away}周后): {event['description']}"
        
        if not upcoming:
            report += "\n   ✅ 近期无需特殊检查"
        
        # 过期事件检查
        overdue = self._get_overdue_events(events, current_week)
        if overdue:
            report += f"\n\n⚠️  过期未完成事件\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            for event in overdue[:3]:
                weeks_overdue = current_week - event['gestational_week']
                report += f"\n   🔴 孕{event['gestational_week']}周 (过期{weeks_overdue}周): {event['description']}"
        
        # 下一个关键里程碑
        next_milestone = self._get_next_critical_milestone(events, current_week)
        if next_milestone:
            report += f"\n\n🎯 下一个关键里程碑\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            weeks_to_milestone = next_milestone['gestational_week'] - current_week
            report += f"\n   📅 孕{next_milestone['gestational_week']}周 ({weeks_to_milestone}周后)"
            report += f"\n   📋 {next_milestone['description']}"
            report += f"\n   ⚡ 重要性: 关键筛查时点"
        
        # 当前阶段管理要点
        current_stage_recommendations = self._get_current_stage_recommendations(current_week, risk_category)
        if current_stage_recommendations:
            report += f"\n\n💡 当前阶段管理要点\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            for i, rec in enumerate(current_stage_recommendations, 1):
                report += f"\n   {i}. {rec}"
        
        report += f"""

📈 风险趋势分析
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   孕早期风险调整: ×{self.stage_risk_multipliers[PregnancyStage.FIRST_TRIMESTER]}
   孕中期风险调整: ×{self.stage_risk_multipliers[PregnancyStage.SECOND_TRIMESTER]}
   孕晚期风险调整: ×{self.stage_risk_multipliers[PregnancyStage.THIRD_TRIMESTER]}
   
   当前阶段风险: {baseline_risk * self._get_current_stage_multiplier(current_week):.1f}/100

📋 备注
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • 时间线基于当前最佳临床实践指南
   • 具体筛查时间可根据临床情况调整
   • 高风险患者需要更频繁的监测
   • 建议与产科和内分泌科医生讨论

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
系统版本: Pregnancy Timeline Assessment v1.0
"""
        
        return report
    
    def _get_current_pregnancy_stage(self, current_week: int) -> str:
        """获取当前妊娠阶段"""
        if current_week <= 0:
            return "孕前"
        elif current_week <= 13:
            return "孕早期"
        elif current_week <= 27:
            return "孕中期"
        elif current_week <= 40:
            return "孕晚期"
        else:
            return "产后"
    
    def _get_current_stage_multiplier(self, current_week: int) -> float:
        """获取当前阶段的风险调整因子"""
        if current_week <= 0:
            return self.stage_risk_multipliers[PregnancyStage.PRECONCEPTION]
        elif current_week <= 13:
            return self.stage_risk_multipliers[PregnancyStage.FIRST_TRIMESTER]
        elif current_week <= 27:
            return self.stage_risk_multipliers[PregnancyStage.SECOND_TRIMESTER]
        elif current_week <= 40:
            return self.stage_risk_multipliers[PregnancyStage.THIRD_TRIMESTER]
        else:
            return self.stage_risk_multipliers[PregnancyStage.POSTPARTUM]
    
    def _get_current_stage_recommendations(self, current_week: int, risk_category: str) -> List[str]:
        """获取当前阶段的管理建议"""
        
        recommendations = []
        
        if current_week <= 13:  # 孕早期
            recommendations.extend([
                "监测早期血糖变化",
                "建立健康的饮食习惯",
                "适度的孕期运动",
                "控制体重增长速度"
            ])
            
            if risk_category in ['high', 'very_high']:
                recommendations.extend([
                    "考虑家庭血糖监测",
                    "营养师专业指导"
                ])
        
        elif current_week <= 27:  # 孕中期
            recommendations.extend([
                "注意胰岛素抵抗增加",
                "监测餐后血糖反应",
                "准备标准GDM筛查",
                "关注胎儿生长发育"
            ])
            
            if risk_category in ['high', 'very_high']:
                recommendations.extend([
                    "考虑提前筛查",
                    "加强血糖监测"
                ])
        
        elif current_week <= 40:  # 孕晚期
            recommendations.extend([
                "密切监测血糖控制",
                "评估胎儿体重增长",
                "准备分娩计划",
                "产后血糖管理准备"
            ])
        
        return recommendations

# 使用示例
def create_sample_timeline_patient():
    """创建时间线评估示例患者"""
    
    return {
        'patient_id': 'TIMELINE_2024_001',
        'demographic': {
            'age': 32,
            'ethnicity': 'asian'
        },
        'anthropometric': {
            'pre_pregnancy_bmi': 26.5,
            'gestational_weight_gain': 6.0
        },
        'obstetric_history': {
            'previous_gdm': False,
            'macrosomia_history': True,
            'parity': 1
        },
        'family_history': {
            'diabetes_family_history': 'first_degree',
            'gdm_family_history': False
        },
        'medical_history': {
            'pcos': True,
            'metabolic_syndrome': False
        },
        'current_pregnancy': {
            'gestational_weeks': 20,
            'multiple_pregnancy': False,
            'estimated_fetal_weight_percentile': 75
        }
    }

if __name__ == "__main__":
    print("🚀 启动妊娠期时间线评估系统")
    print("=" * 80)
    
    # 创建时间线评估器
    timeline_assessor = PregnancyTimelineAssessment()
    
    # 使用示例患者
    sample_patient = create_sample_timeline_patient()
    
    print(f"📋 创建患者时间线: {sample_patient['patient_id']}")
    print(f"当前孕周: {sample_patient['current_pregnancy']['gestational_weeks']} 周")
    
    # 生成个性化时间线
    timeline_result = timeline_assessor.create_personalized_timeline(sample_patient)
    
    # 显示时间线报告
    print(timeline_result['timeline_report'])
    
    # 保存时间线到JSON
    output_file = f"/Users/williamsun/Documents/gplus/docs/GDM/PreGDM/pregnancy_timeline_{sample_patient['patient_id']}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(timeline_result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 时间线已保存至: {output_file}")
    print(f"✅ 妊娠期时间线评估演示完成")