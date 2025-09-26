#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 2: 血糖脆性临床顾问
专注于血糖脆性分型和个性化临床治疗建议
基于混沌分析和临床决策支持
"""

import pandas as pd
import numpy as np
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
import json
import warnings
warnings.filterwarnings('ignore')

class BrittlenessType(Enum):
    """血糖脆性分型"""
    CHAOTIC = "I型混沌脆性"
    QUASI_PERIODIC = "II型准周期脆性"  
    STOCHASTIC = "III型随机脆性"
    MEMORY_LOSS = "IV型记忆缺失脆性"
    FREQUENCY_DOMAIN = "V型频域脆性"
    STABLE = "稳定型"

class RiskLevel(Enum):
    """风险等级"""
    LOW = "低风险"
    MODERATE = "中等风险"
    HIGH = "高风险"
    CRITICAL = "极高风险"

@dataclass
class BrittlenessProfile:
    """脆性档案"""
    type: BrittlenessType
    severity_score: float
    chaos_indicators: dict
    risk_level: RiskLevel
    clinical_features: list
    treatment_strategy: str

@dataclass  
class ClinicalRecommendation:
    """临床建议"""
    category: str
    priority: str
    action: str
    rationale: str
    expected_outcome: str
    monitoring_plan: str
    contraindications: list = None

class BrittlenessClinicalAdvisor:
    """
    血糖脆性临床顾问 - Agent 2
    专注于血糖脆性分层和个性化治疗建议
    """
    
    def __init__(self):
        """初始化脆性临床顾问"""
        self.agent_name = "Brittleness Clinical Advisor"
        self.version = "1.0.0"
        self.description = "血糖脆性分型和个性化临床治疗建议系统"
        
        # 脆性分型阈值
        self.brittleness_thresholds = {
            'lyapunov_chaotic': 0.02,      # 混沌阈值
            'lyapunov_stable': -0.01,      # 稳定阈值
            'cv_high': 50,                 # 高变异阈值
            'cv_unstable': 36,             # 不稳定阈值
            'entropy_threshold': 0.6,      # 熵阈值
            'hurst_memory': 0.45,          # 记忆阈值 (调整至更合理的范围)
            'hurst_persistent': 0.55       # 持续性阈值
        }
        
        # 治疗策略库
        self.treatment_strategies = {
            BrittlenessType.CHAOTIC: {
                "primary_strategy": "混沌稳定化治疗",
                "insulin_approach": "保守减量",
                "target_hba1c": "8.0-8.5%",
                "monitoring": "24小时严密监控",
                "key_principles": ["避免强化治疗", "减少扰动", "预防极端事件"]
            },
            BrittlenessType.QUASI_PERIODIC: {
                "primary_strategy": "节律重建治疗",
                "insulin_approach": "时间优化给药",
                "target_hba1c": "7.5-8.0%",
                "monitoring": "重点监测Dawn现象",
                "key_principles": ["时间治疗学", "生活规律化", "节律同步"]
            },
            BrittlenessType.STOCHASTIC: {
                "primary_strategy": "智能化精准治疗",
                "insulin_approach": "考虑胰岛素泵",
                "target_hba1c": "7.0-7.5%",
                "monitoring": "连续CGM+算法",
                "key_principles": ["闭环系统", "实时调整", "AI辅助"]
            },
            BrittlenessType.MEMORY_LOSS: {
                "primary_strategy": "记忆重建治疗",
                "insulin_approach": "长效制剂优先",
                "target_hba1c": "7.0-7.5%", 
                "monitoring": "评估认知功能",
                "key_principles": ["GLP-1激动剂", "肝糖调节", "神经保护"]
            },
            BrittlenessType.FREQUENCY_DOMAIN: {
                "primary_strategy": "频域调制治疗",
                "insulin_approach": "昼夜节律考虑",
                "target_hba1c": "7.0-7.5%",
                "monitoring": "生物节律评估",
                "key_principles": ["光照治疗", "褪黑素", "时相调整"]
            },
            BrittlenessType.STABLE: {
                "primary_strategy": "维持优化治疗",
                "insulin_approach": "渐进精细调整",
                "target_hba1c": "6.5-7.0%",
                "monitoring": "常规监测",
                "key_principles": ["持续优化", "预防恶化", "生活质量"]
            }
        }
    
    def analyze_brittleness_profile(self, glucose_data: np.ndarray, 
                                  chaos_indicators: dict = None,
                                  patient_info: dict = None) -> BrittlenessProfile:
        """
        分析血糖脆性档案
        """
        print(f"🧬 {self.agent_name} 开始脆性分析...")
        
        # 1. 计算混沌指标
        if chaos_indicators is None:
            chaos_indicators = self._calculate_chaos_indicators(glucose_data)
        
        # 2. 脆性分型
        brittleness_type = self._classify_brittleness_type(chaos_indicators, glucose_data)
        
        # 3. 严重程度评分
        severity_score = self._calculate_severity_score(chaos_indicators, glucose_data)
        
        # 4. 风险等级评估
        risk_level = self._assess_risk_level(severity_score, chaos_indicators)
        
        # 5. 临床特征识别
        clinical_features = self._identify_clinical_features(brittleness_type, chaos_indicators)
        
        # 6. 治疗策略
        treatment_strategy = self._determine_treatment_strategy(brittleness_type)
        
        profile = BrittlenessProfile(
            type=brittleness_type,
            severity_score=severity_score,
            chaos_indicators=chaos_indicators,
            risk_level=risk_level,
            clinical_features=clinical_features,
            treatment_strategy=treatment_strategy
        )
        
        print(f"✅ 脆性分析完成: {brittleness_type.value}")
        return profile
    
    def _calculate_chaos_indicators(self, glucose_data: np.ndarray) -> dict:
        """计算混沌分析指标"""
        indicators = {}
        
        # Lyapunov指数
        indicators['lyapunov_exponent'] = self._calculate_lyapunov(glucose_data)
        
        # 近似熵
        indicators['approximate_entropy'] = self._calculate_approximate_entropy(glucose_data)
        
        # Shannon熵
        indicators['shannon_entropy'] = self._calculate_shannon_entropy(glucose_data)
        
        # Hurst指数
        indicators['hurst_exponent'] = self._calculate_hurst_exponent(glucose_data)
        
        # 分形维度
        indicators['fractal_dimension'] = self._calculate_fractal_dimension(glucose_data)
        
        # 关联维数
        indicators['correlation_dimension'] = self._calculate_correlation_dimension(glucose_data)
        
        # 最大Lyapunov指数稳定性
        indicators['lyapunov_stability'] = "stable" if indicators['lyapunov_exponent'] < 0 else "chaotic"
        
        return indicators
    
    def _classify_brittleness_type(self, chaos_indicators: dict, glucose_data: np.ndarray) -> BrittlenessType:
        """
        血糖脆性分型 - 改进版本
        基于多维混沌指标的稳健分类系统
        """
        lyapunov = chaos_indicators.get('lyapunov_exponent', 0)
        entropy = chaos_indicators.get('approximate_entropy', 0)
        hurst = chaos_indicators.get('hurst_exponent', 0.5)
        
        # 计算变异系数
        cv = (np.std(glucose_data) / np.mean(glucose_data)) * 100
        
        # 决策权重系统
        chaos_score = 0
        memory_score = 0
        variability_score = 0
        
        # 混沌特征评分
        if lyapunov > self.brittleness_thresholds['lyapunov_chaotic']:
            chaos_score += 2
        elif lyapunov > 0:
            chaos_score += 1
            
        if entropy > 0.8:
            chaos_score += 2
        elif entropy > self.brittleness_thresholds['entropy_threshold']:
            chaos_score += 1
            
        # 记忆特征评分 
        if hurst < self.brittleness_thresholds['hurst_memory']:
            memory_score = -2  # 强反持续性（记忆缺失）
        elif hurst > self.brittleness_thresholds['hurst_persistent']:
            memory_score = 2   # 强持续性（长程记忆）
        else:
            memory_score = 0   # 随机游走特性
            
        # 变异性评分
        if cv > 60:
            variability_score = 3  # 极高变异
        elif cv > self.brittleness_thresholds['cv_high']:
            variability_score = 2  # 高变异
        elif cv > self.brittleness_thresholds['cv_unstable']:
            variability_score = 1  # 中等变异
        else:
            variability_score = 0  # 低变异
        
        # 多维分类决策
        # I型混沌脆性：高混沌 + 极高变异
        if chaos_score >= 3 and variability_score >= 3:
            return BrittlenessType.CHAOTIC
            
        # III型随机脆性：高混沌 + 高变异 + 随机游走
        if chaos_score >= 2 and variability_score >= 2 and abs(memory_score) <= 1:
            return BrittlenessType.STOCHASTIC
            
        # IV型记忆缺失脆性：记忆缺失 + 中等以上变异
        if memory_score <= -1 and variability_score >= 1:
            return BrittlenessType.MEMORY_LOSS
            
        # V型频域脆性：低混沌但高变异 + 强持续性
        if lyapunov < self.brittleness_thresholds['lyapunov_stable'] and variability_score >= 1 and memory_score >= 1:
            return BrittlenessType.FREQUENCY_DOMAIN
            
        # 稳定型：低变异 + 稳定Lyapunov
        if variability_score == 0 and lyapunov < self.brittleness_thresholds['lyapunov_chaotic']:
            return BrittlenessType.STABLE
            
        # II型准周期脆性：其他情况（中等混沌特征）
        return BrittlenessType.QUASI_PERIODIC
    
    def _calculate_severity_score(self, chaos_indicators: dict, glucose_data: np.ndarray) -> float:
        """计算脆性严重程度评分 (0-100)"""
        lyapunov = abs(chaos_indicators.get('lyapunov_exponent', 0))
        entropy = chaos_indicators.get('approximate_entropy', 0)
        
        # 变异系数
        cv = (np.std(glucose_data) / np.mean(glucose_data)) * 100
        
        # 综合评分
        lyapunov_score = min(50, lyapunov * 1000)  # Lyapunov贡献最多50分
        entropy_score = entropy * 30  # 熵贡献最多30分
        cv_score = min(20, cv / 5)  # CV贡献最多20分
        
        total_score = lyapunov_score + entropy_score + cv_score
        
        return min(100, total_score)
    
    def _assess_risk_level(self, severity_score: float, chaos_indicators: dict) -> RiskLevel:
        """评估风险等级"""
        if severity_score >= 80:
            return RiskLevel.CRITICAL
        elif severity_score >= 60:
            return RiskLevel.HIGH
        elif severity_score >= 40:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def _identify_clinical_features(self, brittleness_type: BrittlenessType, 
                                  chaos_indicators: dict) -> list:
        """识别临床特征"""
        features = []
        
        if brittleness_type == BrittlenessType.CHAOTIC:
            features.extend([
                "血糖系统呈现混沌行为",
                "对治疗调整极度敏感",
                "存在严重低血糖风险",
                "血糖模式不可预测"
            ])
        
        elif brittleness_type == BrittlenessType.QUASI_PERIODIC:
            features.extend([
                "存在病理性血糖周期",
                "Dawn现象显著",
                "昼夜节律紊乱",
                "可识别的周期模式"
            ])
        
        elif brittleness_type == BrittlenessType.STOCHASTIC:
            features.extend([
                "血糖变化随机性强",
                "需要智能化管理",
                "可能存在神经病变",
                "传统治疗效果有限"
            ])
        
        elif brittleness_type == BrittlenessType.MEMORY_LOSS:
            features.extend([
                "血糖系统记忆功能缺失",
                "肝糖调节能力下降",
                "可能存在认知功能影响",
                "需要长效治疗"
            ])
        
        elif brittleness_type == BrittlenessType.FREQUENCY_DOMAIN:
            features.extend([
                "昼夜节律完全紊乱",
                "生物钟调节机制失效",
                "需要节律重建",
                "变异性虽高但系统相对稳定"
            ])
        
        else:  # STABLE
            features.extend([
                "血糖调节系统稳定",
                "治疗反应可预测",
                "适合精细化管理",
                "预后相对良好"
            ])
        
        return features
    
    def _determine_treatment_strategy(self, brittleness_type: BrittlenessType) -> str:
        """确定治疗策略"""
        strategy = self.treatment_strategies.get(brittleness_type, {})
        return strategy.get("primary_strategy", "个性化治疗")
    
    def generate_clinical_recommendations(self, profile: BrittlenessProfile,
                                        patient_info: dict = None) -> List[ClinicalRecommendation]:
        """
        生成个性化临床建议
        """
        recommendations = []
        strategy = self.treatment_strategies[profile.type]
        
        # 1. 胰岛素调整建议
        recommendations.append(ClinicalRecommendation(
            category="胰岛素治疗",
            priority="HIGH",
            action=f"采用{strategy['insulin_approach']}策略",
            rationale=f"{profile.type.value}需要特定的胰岛素治疗方式",
            expected_outcome="降低脆性相关风险，改善血糖稳定性",
            monitoring_plan=strategy['monitoring']
        ))
        
        # 2. 血糖目标设定
        recommendations.append(ClinicalRecommendation(
            category="血糖目标",
            priority="HIGH", 
            action=f"设定HbA1c目标为{strategy['target_hba1c']}",
            rationale=f"{profile.type.value}需要个性化的血糖控制目标",
            expected_outcome="平衡血糖控制与安全性",
            monitoring_plan="每3个月评估HbA1c和CGM数据"
        ))
        
        # 3. 监测计划
        recommendations.append(ClinicalRecommendation(
            category="监测管理",
            priority="MEDIUM",
            action=strategy['monitoring'],
            rationale="脆性血糖需要加强监测",
            expected_outcome="及时发现血糖异常，预防严重事件",
            monitoring_plan="根据脆性类型调整监测频率"
        ))
        
        # 4. 基于脆性类型的特殊建议
        if profile.type == BrittlenessType.CHAOTIC:
            recommendations.append(ClinicalRecommendation(
                category="安全措施",
                priority="CRITICAL",
                action="建立严格的低血糖预防协议",
                rationale="混沌系统存在极高的低血糖风险",
                expected_outcome="防止严重低血糖事件",
                monitoring_plan="24小时CGM监控，设置保守报警阈值",
                contraindications=["强化治疗", "快速剂量调整", "严格血糖目标"]
            ))
        
        elif profile.type == BrittlenessType.FREQUENCY_DOMAIN:
            recommendations.append(ClinicalRecommendation(
                category="节律治疗",
                priority="HIGH",
                action="实施光照治疗和生活节律干预",
                rationale="频域脆性需要重建生物节律",
                expected_outcome="恢复正常昼夜血糖节律",
                monitoring_plan="监测生物节律指标和血糖模式"
            ))
        
        elif profile.type == BrittlenessType.STOCHASTIC:
            recommendations.append(ClinicalRecommendation(
                category="技术支持",
                priority="HIGH",
                action="考虑胰岛素泵或闭环系统",
                rationale="随机脆性需要智能化治疗",
                expected_outcome="通过算法自动调整应对随机变化",
                monitoring_plan="连续CGM配合智能算法监测"
            ))
        
        # 5. 风险管理建议
        if profile.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append(ClinicalRecommendation(
                category="风险管理",
                priority="CRITICAL",
                action="制定个性化紧急预案",
                rationale=f"{profile.risk_level.value}需要特殊风险管理",
                expected_outcome="降低血糖相关不良事件风险",
                monitoring_plan="加强患者教育和家属培训"
            ))
        
        return recommendations
    
    def generate_brittleness_report(self, glucose_data: np.ndarray,
                                  patient_id: str = "Unknown",
                                  patient_info: dict = None) -> dict:
        """
        生成血糖脆性分析报告
        """
        print(f"🩺 {self.agent_name} 开始生成脆性报告...")
        
        # 1. 分析脆性档案
        profile = self.analyze_brittleness_profile(glucose_data, patient_info=patient_info)
        
        # 2. 生成临床建议
        recommendations = self.generate_clinical_recommendations(profile, patient_info)
        
        # 3. 预后评估
        prognosis = self._assess_prognosis(profile)
        
        # 4. 构建报告
        report = {
            'agent_info': {
                'name': self.agent_name,
                'version': self.version,
                'analysis_time': datetime.now().isoformat(),
                'patient_id': patient_id
            },
            'brittleness_profile': {
                'type': profile.type.value,
                'severity_score': profile.severity_score,
                'risk_level': profile.risk_level.value,
                'clinical_features': profile.clinical_features,
                'treatment_strategy': profile.treatment_strategy
            },
            'chaos_analysis': profile.chaos_indicators,
            'clinical_recommendations': [
                {
                    'category': rec.category,
                    'priority': rec.priority,
                    'action': rec.action,
                    'rationale': rec.rationale,
                    'expected_outcome': rec.expected_outcome,
                    'monitoring_plan': rec.monitoring_plan,
                    'contraindications': rec.contraindications or []
                }
                for rec in recommendations
            ],
            'prognosis_assessment': prognosis,
            'follow_up_plan': self._create_follow_up_plan(profile)
        }
        
        print(f"✅ 脆性报告生成完成")
        return report
    
    def _assess_prognosis(self, profile: BrittlenessProfile) -> dict:
        """评估预后"""
        prognosis_map = {
            BrittlenessType.STABLE: {
                'short_term': 'Excellent',
                'long_term': 'Good',
                'key_concerns': ['预防恶化', '维持现状']
            },
            BrittlenessType.QUASI_PERIODIC: {
                'short_term': 'Good',
                'long_term': 'Fair',
                'key_concerns': ['节律稳定', '预防混沌化']
            },
            BrittlenessType.STOCHASTIC: {
                'short_term': 'Fair',
                'long_term': 'Guarded',
                'key_concerns': ['并发症风险', '治疗复杂性']
            },
            BrittlenessType.CHAOTIC: {
                'short_term': 'Guarded',
                'long_term': 'Poor',
                'key_concerns': ['严重低血糖', '系统不稳定']
            },
            BrittlenessType.MEMORY_LOSS: {
                'short_term': 'Fair',
                'long_term': 'Guarded',
                'key_concerns': ['认知功能', '治疗依从性']
            },
            BrittlenessType.FREQUENCY_DOMAIN: {
                'short_term': 'Good',
                'long_term': 'Fair',
                'key_concerns': ['节律重建', '生活质量']
            }
        }
        
        return prognosis_map.get(profile.type, {
            'short_term': 'Unknown',
            'long_term': 'Unknown',
            'key_concerns': ['需要进一步评估']
        })
    
    def _create_follow_up_plan(self, profile: BrittlenessProfile) -> dict:
        """制定随访计划"""
        base_intervals = {
            BrittlenessType.CHAOTIC: {'clinic': '2-4周', 'cgm_review': '每周'},
            BrittlenessType.STOCHASTIC: {'clinic': '4-6周', 'cgm_review': '2周'},
            BrittlenessType.QUASI_PERIODIC: {'clinic': '6-8周', 'cgm_review': '2-4周'},
            BrittlenessType.MEMORY_LOSS: {'clinic': '4-6周', 'cgm_review': '2周'},
            BrittlenessType.FREQUENCY_DOMAIN: {'clinic': '6-8周', 'cgm_review': '2-4周'},
            BrittlenessType.STABLE: {'clinic': '3-6个月', 'cgm_review': '月度'}
        }
        
        intervals = base_intervals.get(profile.type, {'clinic': '6-8周', 'cgm_review': '月度'})
        
        return {
            'clinic_visit_interval': intervals['clinic'],
            'cgm_data_review': intervals['cgm_review'],
            'key_monitoring_points': [
                '脆性指标变化',
                '治疗反应评估',
                '不良事件监测',
                '生活质量评估'
            ],
            'adjustment_triggers': [
                '脆性类型改变',
                '严重程度恶化',
                '新出现安全事件'
            ]
        }
    
    # 混沌分析算法实现
    def _calculate_lyapunov(self, data: np.ndarray) -> float:
        """计算Lyapunov指数"""
        if len(data) < 10:
            return 0
        
        # 简化的Lyapunov指数计算
        diff_data = np.diff(data)
        if len(diff_data) < 2:
            return 0
        
        # 计算相邻差值的发散率
        divergences = []
        for i in range(1, len(diff_data)):
            if abs(diff_data[i-1]) > 1e-10:
                divergence = abs(diff_data[i] / diff_data[i-1])
                if divergence > 0:
                    divergences.append(np.log(divergence))
        
        if not divergences:
            return 0
        
        return np.mean(divergences)
    
    def _calculate_approximate_entropy(self, data: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """计算近似熵"""
        N = len(data)
        if N < m + 1:
            return 0
        
        def _maxdist(xi, xj):
            return max([abs(ua - va) for ua, va in zip(xi, xj)])
        
        def _phi(m):
            patterns = np.array([data[i:i+m] for i in range(N-m+1)])
            C = np.zeros(N-m+1)
            
            for i in range(N-m+1):
                template = patterns[i]
                matches = sum(1 for j in range(N-m+1) 
                            if _maxdist(template, patterns[j]) <= r * np.std(data))
                C[i] = matches / float(N-m+1)
            
            phi = np.mean([np.log(c) for c in C if c > 0])
            return phi
        
        return _phi(m) - _phi(m+1)
    
    def _calculate_shannon_entropy(self, data: np.ndarray, bins: int = 50) -> float:
        """计算Shannon熵"""
        hist, _ = np.histogram(data, bins=bins)
        hist = hist[hist > 0]
        prob = hist / np.sum(hist)
        return -np.sum(prob * np.log2(prob))
    
    def _calculate_hurst_exponent(self, data: np.ndarray) -> float:
        """
        计算Hurst指数 - 稳定版本
        使用多窗口R/S分析，提供更稳定的长程记忆特性度量
        """
        if len(data) < 20:
            return 0.5
        
        # 数据预处理：去趋势和标准化
        from scipy import signal
        detrended = signal.detrend(data)
        
        # 多时间窗口设计
        n = len(data)
        min_window = 10
        max_window = min(n // 4, 200)  # 限制最大窗口
        
        if max_window <= min_window:
            return 0.5
        
        # 对数等间距窗口大小
        window_sizes = np.unique(np.logspace(
            np.log10(min_window), 
            np.log10(max_window), 
            12
        ).astype(int))
        
        rs_values = []
        valid_windows = []
        
        for window_size in window_sizes:
            if window_size >= n or window_size < min_window:
                continue
                
            # 滑动窗口R/S分析
            rs_list = []
            num_windows = n - window_size + 1
            step = max(1, num_windows // 10)  # 最多取10个窗口
            
            for i in range(0, num_windows, step):
                segment = detrended[i:i + window_size]
                
                if len(segment) != window_size:
                    continue
                
                # 累积偏差序列
                mean_segment = np.mean(segment)
                cumulative_deviate = np.cumsum(segment - mean_segment)
                
                # R: 累积偏差的范围
                R = np.max(cumulative_deviate) - np.min(cumulative_deviate)
                
                # S: 标准差
                S = np.std(segment, ddof=1)  # 使用无偏标准差
                
                # R/S比值
                if S > 1e-10 and R > 1e-10:  # 避免数值问题
                    rs_list.append(R / S)
            
            if len(rs_list) >= 3:  # 至少需要3个有效样本
                rs_mean = np.mean(rs_list)
                if rs_mean > 0:
                    rs_values.append(rs_mean)
                    valid_windows.append(window_size)
        
        # 检查有效性
        if len(rs_values) < 3:
            return 0.5
        
        # 线性回归 log(R/S) vs log(n)
        log_windows = np.log(valid_windows)
        log_rs = np.log(rs_values)
        
        # 过滤无穷值和NaN
        valid_mask = np.isfinite(log_windows) & np.isfinite(log_rs)
        
        if np.sum(valid_mask) < 3:
            return 0.5
        
        # 稳健的线性拟合
        try:
            coeffs = np.polyfit(log_windows[valid_mask], log_rs[valid_mask], 1)
            hurst = coeffs[0]
            
            # Hurst指数合理性检查
            # 理论范围: 0 < H < 1
            # H = 0.5: 随机游走（无记忆）
            # H > 0.5: 长程正相关（趋势持续）
            # H < 0.5: 长程负相关（反趋势）
            hurst = max(0.05, min(0.95, hurst))
            
            return float(hurst)
            
        except (np.linalg.LinAlgError, ValueError):
            return 0.5
    
    def _calculate_fractal_dimension(self, data: np.ndarray) -> float:
        """计算分形维度"""
        # 简化的分形维度计算
        if len(data) < 4:
            return 1.5
        
        # 使用Higuchi方法的简化版本
        k_max = min(10, len(data) // 4)
        lk = []
        
        for k in range(1, k_max + 1):
            lm = []
            for m in range(k):
                indices = np.arange(m, len(data), k)
                if len(indices) < 2:
                    continue
                subset = data[indices]
                length = np.sum(np.abs(np.diff(subset))) * (len(data) - 1) / (len(indices) - 1) / k
                lm.append(length)
            
            if lm:
                lk.append(np.mean(lm))
        
        if len(lk) < 2:
            return 1.5
        
        # 拟合直线求斜率
        x = np.log(range(1, len(lk) + 1))
        y = np.log(lk)
        
        try:
            slope = np.polyfit(x, y, 1)[0]
            return 2 - slope
        except:
            return 1.5
    
    def _calculate_correlation_dimension(self, data: np.ndarray) -> float:
        """计算关联维数"""
        # 简化的关联维数计算
        if len(data) < 10:
            return 2.0
        
        # 使用简化的Grassberger-Procaccia算法
        m = 3  # 嵌入维数
        embedded = np.array([data[i:i+m] for i in range(len(data)-m+1)])
        
        if len(embedded) < 2:
            return 2.0
        
        # 计算距离矩阵
        distances = []
        for i in range(len(embedded)):
            for j in range(i+1, len(embedded)):
                dist = np.linalg.norm(embedded[i] - embedded[j])
                distances.append(dist)
        
        if not distances:
            return 2.0
        
        # 简化的关联维数估算
        distances = np.array(distances)
        median_dist = np.median(distances)
        
        if median_dist == 0:
            return 2.0
        
        correlation_sum = np.sum(distances < median_dist) / len(distances)
        
        if correlation_sum <= 0:
            return 2.0
        
        return np.log(correlation_sum) / np.log(median_dist / np.max(distances))

if __name__ == "__main__":
    # 测试代码
    advisor = BrittlenessClinicalAdvisor()
    print(f"✅ {advisor.agent_name} 初始化完成")
    print(f"🧬 支持6种血糖脆性类型分析")
    print(f"💊 提供个性化临床治疗建议")