#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多维度CGMS异常检测方法间约束干扰分析系统
分析各检测维度之间的相互影响、约束关系和冲突解决
"""

import numpy as np
import pandas as pd
from scipy import stats
from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class InterDimensionalConstraintAnalyzer:
    """多维度约束干扰分析器"""

    def __init__(self):
        # 定义各维度之间的理论关系
        self.interdependency_matrix = {
            'statistical': {
                'conflicts_with': ['pattern_based'],  # 统计异常vs模式正常
                'supports': ['physiological'],        # 统计异常通常支持生理异常
                'influenced_by': ['ml_based'],        # ML结果影响统计判断
                'influences': ['temporal'],           # 统计特征影响时序判断
            },
            'pattern_based': {
                'conflicts_with': ['statistical', 'frequency'],  # 模式vs统计/频域冲突
                'supports': ['temporal'],             # 模式支持时序分析
                'influenced_by': ['frequency'],       # 频域影响模式识别
                'influences': ['ml_based'],           # 模式特征训练ML
            },
            'frequency': {
                'conflicts_with': ['pattern_based'],  # 频域vs模式可能冲突
                'supports': ['temporal'],             # 频域支持时序
                'influenced_by': [],                  # 相对独立
                'influences': ['pattern_based'],      # 频域信息影响模式
            },
            'ml_based': {
                'conflicts_with': [],                # ML相对中性
                'supports': ['statistical'],         # ML可以支持统计判断
                'influenced_by': ['all_methods'],     # 受所有方法影响
                'influences': ['final_decision'],     # 影响最终决策
            },
            'physiological': {
                'conflicts_with': ['statistical'],   # 生理合理vs统计异常
                'supports': [],                      # 生理约束相对独立
                'influenced_by': [],                 # 基于医学知识
                'influences': ['all_methods'],       # 影响所有方法的权重
            },
            'temporal': {
                'conflicts_with': [],               # 时序相对独立
                'supports': ['pattern_based'],      # 支持模式识别
                'influenced_by': ['statistical', 'pattern_based', 'frequency'],
                'influences': ['ml_based'],         # 时序特征影响ML
            }
        }

    def analyze_constraint_relationships(self, detection_results):
        """分析约束关系"""
        print("🔗 分析各检测维度之间的约束关系")
        print("=" * 60)

        constraint_analysis = {}
        method_results = detection_results['method_results']

        # 1. 直接冲突分析
        conflicts = self._analyze_direct_conflicts(method_results)
        constraint_analysis['direct_conflicts'] = conflicts

        # 2. 支持-反对关系分析
        support_analysis = self._analyze_support_relationships(method_results)
        constraint_analysis['support_relationships'] = support_analysis

        # 3. 影响强度分析
        influence_analysis = self._analyze_influence_strength(method_results)
        constraint_analysis['influence_strength'] = influence_analysis

        return constraint_analysis

    def _analyze_direct_conflicts(self, method_results):
        """分析直接冲突"""
        conflicts = []

        # 统计学 vs 生理学冲突
        stat_anomalies = set(method_results.get('statistical', {}).get('anomalies', []))
        physio_anomalies = set(method_results.get('physiological', {}).get('anomalies', []))

        stat_only = stat_anomalies - physio_anomalies
        if len(stat_only) > 0:
            conflicts.append({
                'type': '统计-生理冲突',
                'description': '统计学检测为异常但生理学认为正常',
                'conflict_points': list(stat_only),
                'severity': 'medium',
                'resolution': '优先考虑生理学合理性'
            })

        # 模式识别 vs 频域分析冲突
        pattern_anomalies = set(method_results.get('pattern_based', {}).get('anomalies', []))
        freq_anomalies = set(method_results.get('frequency', {}).get('anomalies', []))

        pattern_only = pattern_anomalies - freq_anomalies
        freq_only = freq_anomalies - pattern_anomalies

        if len(pattern_only) > 10:  # 模式检测很多，频域很少
            conflicts.append({
                'type': '模式-频域冲突',
                'description': '模式识别发现异常但频域分析正常',
                'conflict_points': list(pattern_only),
                'severity': 'low',
                'resolution': '可能是非周期性模式异常，优先模式识别'
            })

        return conflicts

    def _analyze_support_relationships(self, method_results):
        """分析支持关系"""
        support_relationships = {}

        # 检查各方法对的重叠程度
        method_pairs = [
            ('statistical', 'physiological', '统计-生理一致性'),
            ('pattern_based', 'temporal', '模式-时序一致性'),
            ('frequency', 'temporal', '频域-时序一致性'),
            ('ml_based', 'statistical', 'ML-统计一致性')
        ]

        for method1, method2, name in method_pairs:
            anomalies1 = set(method_results.get(method1, {}).get('anomalies', []))
            anomalies2 = set(method_results.get(method2, {}).get('anomalies', []))

            if len(anomalies1) > 0 and len(anomalies2) > 0:
                overlap = anomalies1 & anomalies2
                overlap_ratio = len(overlap) / min(len(anomalies1), len(anomalies2))

                support_relationships[name] = {
                    'overlap_count': len(overlap),
                    'overlap_ratio': overlap_ratio,
                    'support_strength': 'high' if overlap_ratio > 0.7 else 'medium' if overlap_ratio > 0.3 else 'low',
                    'overlapping_points': list(overlap)
                }

        return support_relationships

    def _analyze_influence_strength(self, method_results):
        """分析影响强度"""
        influence_matrix = np.zeros((6, 6))  # 6x6 方法影响矩阵
        method_names = ['statistical', 'pattern_based', 'frequency', 'ml_based', 'physiological', 'temporal']

        for i, method_i in enumerate(method_names):
            anomalies_i = set(method_results.get(method_i, {}).get('anomalies', []))

            for j, method_j in enumerate(method_names):
                if i != j:
                    anomalies_j = set(method_results.get(method_j, {}).get('anomalies', []))

                    if len(anomalies_i) > 0 and len(anomalies_j) > 0:
                        # 计算影响强度：i方法检出的异常有多少被j方法支持
                        support_count = len(anomalies_i & anomalies_j)
                        influence_strength = support_count / len(anomalies_i)
                        influence_matrix[i, j] = influence_strength

        return {
            'influence_matrix': influence_matrix,
            'method_names': method_names,
            'dominant_influencer': method_names[np.argmax(np.sum(influence_matrix, axis=1))],
            'most_influenced': method_names[np.argmax(np.sum(influence_matrix, axis=0))]
        }

    def identify_interference_patterns(self, glucose_data, detection_results):
        """识别干扰模式"""
        print("\n⚡ 识别各维度间的干扰模式")
        print("=" * 60)

        interference_patterns = {}

        # 1. 数据依赖干扰
        data_interference = self._analyze_data_dependency_interference(glucose_data, detection_results)
        interference_patterns['data_dependency'] = data_interference

        # 2. 阈值竞争干扰
        threshold_interference = self._analyze_threshold_competition(detection_results)
        interference_patterns['threshold_competition'] = threshold_interference

        # 3. 特征空间重叠干扰
        feature_interference = self._analyze_feature_overlap_interference(glucose_data)
        interference_patterns['feature_overlap'] = feature_interference

        return interference_patterns

    def _analyze_data_dependency_interference(self, glucose_data, detection_results):
        """分析数据依赖干扰"""
        interference = {}

        # 采样率依赖
        time_intervals = np.diff(range(len(glucose_data)))  # 简化时间间隔
        irregular_sampling = np.std(time_intervals) > 0

        if irregular_sampling:
            interference['sampling_rate'] = {
                'affected_methods': ['frequency', 'temporal', 'pattern_based'],
                'severity': 'high',
                'description': '不规律采样影响频域和时序分析',
                'solution': '数据预处理：插值或重采样'
            }

        # 窗口大小依赖
        short_data = len(glucose_data) < 50
        if short_data:
            interference['window_size'] = {
                'affected_methods': ['pattern_based', 'frequency', 'ml_based'],
                'severity': 'medium',
                'description': '数据长度不足影响模式识别和频域分析',
                'solution': '调整窗口大小或等待更多数据'
            }

        return interference

    def _analyze_threshold_competition(self, detection_results):
        """分析阈值竞争"""
        competition = {}
        method_results = detection_results['method_results']

        # 计算各方法的检出率
        total_points = max([len(result.get('anomalies', [])) for result in method_results.values()]) or 1

        detection_rates = {}
        for method, result in method_results.items():
            rate = len(result.get('anomalies', [])) / total_points
            detection_rates[method] = rate

        # 识别过敏感和过保守的方法
        mean_rate = np.mean(list(detection_rates.values()))
        std_rate = np.std(list(detection_rates.values()))

        over_sensitive = [method for method, rate in detection_rates.items()
                         if rate > mean_rate + std_rate]
        under_sensitive = [method for method, rate in detection_rates.items()
                          if rate < mean_rate - std_rate]

        competition['sensitivity_imbalance'] = {
            'over_sensitive_methods': over_sensitive,
            'under_sensitive_methods': under_sensitive,
            'balance_score': 1 - std_rate / (mean_rate + 1e-6),
            'recommendation': '调整过敏感方法的阈值'
        }

        return competition

    def _analyze_feature_overlap_interference(self, glucose_data):
        """分析特征空间重叠干扰"""
        overlap = {}

        # 统计学和ML的特征重叠
        # 两者都使用统计特征，可能产生冗余
        overlap['statistical_ml'] = {
            'overlap_type': 'feature_redundancy',
            'severity': 'medium',
            'description': '统计学特征与ML特征空间重叠',
            'impact': '可能导致过度权重统计异常',
            'solution': 'ML中减少统计特征权重或使用特征选择'
        }

        # 模式识别和时序分析的重叠
        # 两者都分析时间相关模式
        overlap['pattern_temporal'] = {
            'overlap_type': 'temporal_pattern_redundancy',
            'severity': 'low',
            'description': '模式识别与时序分析在时间模式上重叠',
            'impact': '时间相关异常可能被双重计算',
            'solution': '在集成时调整这两种方法的权重'
        }

        return overlap

    def design_constraint_resolution_framework(self, constraint_analysis, interference_patterns):
        """设计约束解决框架"""
        print("\n🛠️ 设计约束解决框架")
        print("=" * 60)

        resolution_framework = {
            'conflict_resolution_rules': {},
            'weight_adjustment_strategy': {},
            'decision_hierarchy': {},
            'adaptive_mechanisms': {}
        }

        # 1. 冲突解决规则
        resolution_framework['conflict_resolution_rules'] = {
            'statistical_vs_physiological': {
                'rule': 'physiological_priority',
                'logic': '生理学合理性优先于统计异常',
                'implementation': 'if physio_normal and stat_abnormal: reduce_stat_weight(0.5)'
            },
            'pattern_vs_frequency': {
                'rule': 'pattern_priority_for_non_periodic',
                'logic': '非周期性异常优先模式识别',
                'implementation': 'if freq_normal and pattern_abnormal: confirm_non_periodic()'
            },
            'ml_vs_rule_based': {
                'rule': 'interpretable_priority',
                'logic': '可解释方法优先于黑盒ML',
                'implementation': 'if ml_only_detection: require_supporting_evidence()'
            }
        }

        # 2. 权重调整策略
        resolution_framework['weight_adjustment_strategy'] = {
            'conflict_based_adjustment': {
                'high_conflict_methods': 'reduce_weight(-0.2)',
                'supportive_methods': 'increase_weight(+0.1)',
                'independent_methods': 'maintain_weight()'
            },
            'performance_based_adjustment': {
                'high_false_positive': 'reduce_weight(-0.3)',
                'high_false_negative': 'increase_sensitivity()',
                'balanced_performance': 'maintain_weight()'
            }
        }

        # 3. 决策层级
        resolution_framework['decision_hierarchy'] = {
            'tier_1_critical': ['physiological'],  # 生理安全最优先
            'tier_2_reliable': ['statistical', 'pattern_based'],  # 可解释方法
            'tier_3_supportive': ['temporal', 'frequency'],  # 支持性方法
            'tier_4_ml': ['ml_based']  # ML作为辅助决策
        }

        # 4. 自适应机制
        resolution_framework['adaptive_mechanisms'] = {
            'dynamic_threshold': 'adjust_based_on_conflict_history()',
            'method_reliability_tracking': 'update_weights_based_on_performance()',
            'context_aware_resolution': 'apply_clinical_context_rules()',
            'feedback_incorporation': 'learn_from_clinical_feedback()'
        }

        return resolution_framework

    def implement_optimized_ensemble(self, glucose_data, timestamps, resolution_framework):
        """实现优化的集成检测器"""
        print("\n🚀 实现约束感知的优化集成检测器")
        print("=" * 60)

        # 基础权重
        base_weights = {
            'statistical': 0.20,
            'pattern_based': 0.25,
            'frequency': 0.10,
            'ml_based': 0.15,
            'physiological': 0.25,
            'temporal': 0.05
        }

        # 模拟各方法的检测结果
        method_detections = self._simulate_method_detections(glucose_data)

        # 应用约束解决框架
        optimized_results = self._apply_constraint_resolution(
            method_detections, base_weights, resolution_framework
        )

        # 生成最终异常点
        final_anomalies = self._generate_final_anomalies(optimized_results)

        print(f"📊 优化集成结果:")
        print(f"  原始检测总数: {sum(len(det) for det in method_detections.values())}")
        print(f"  冲突解决后: {len(final_anomalies)} 个确认异常")
        print(f"  约束一致性: {optimized_results['consistency_score']:.3f}")

        return {
            'final_anomalies': final_anomalies,
            'method_contributions': optimized_results['method_contributions'],
            'conflict_resolutions': optimized_results['conflict_resolutions'],
            'consistency_score': optimized_results['consistency_score']
        }

    def _simulate_method_detections(self, glucose_data):
        """模拟各方法检测结果"""
        detections = {}

        # 统计学检测
        z_scores = np.abs(stats.zscore(glucose_data))
        detections['statistical'] = np.where(z_scores > 2.5)[0].tolist()

        # 生理学检测
        detections['physiological'] = np.where((glucose_data < 60) | (glucose_data > 250))[0].tolist()

        # 模式检测（简化）
        pattern_anomalies = []
        for i in range(1, len(glucose_data)):
            if abs(glucose_data[i] - glucose_data[i-1]) > 30:
                pattern_anomalies.append(i)
        detections['pattern_based'] = pattern_anomalies

        # 其他方法简化实现
        detections['frequency'] = []
        detections['ml_based'] = np.random.choice(len(glucose_data), size=5, replace=False).tolist()
        detections['temporal'] = []

        return detections

    def _apply_constraint_resolution(self, method_detections, base_weights, resolution_framework):
        """应用约束解决"""
        resolved_weights = base_weights.copy()
        conflict_resolutions = []

        # 检测冲突
        stat_set = set(method_detections['statistical'])
        physio_set = set(method_detections['physiological'])

        # 统计-生理冲突解决
        stat_only = stat_set - physio_set
        if len(stat_only) > 0:
            resolved_weights['statistical'] *= 0.7  # 降低统计学权重
            conflict_resolutions.append({
                'conflict': 'statistical_vs_physiological',
                'resolution': 'reduced_statistical_weight',
                'affected_points': list(stat_only)
            })

        # 计算一致性评分
        all_detections = set()
        for detections in method_detections.values():
            all_detections.update(detections)

        method_agreement = {}
        for point in all_detections:
            agreement_count = sum(1 for detections in method_detections.values()
                                if point in detections)
            method_agreement[point] = agreement_count

        consistency_score = np.mean(list(method_agreement.values())) / len(method_detections)

        return {
            'resolved_weights': resolved_weights,
            'method_contributions': method_agreement,
            'conflict_resolutions': conflict_resolutions,
            'consistency_score': consistency_score
        }

    def _generate_final_anomalies(self, optimized_results):
        """生成最终异常点列表"""
        # 根据方法一致性和权重决定最终异常
        final_anomalies = []
        contributions = optimized_results['method_contributions']

        for point, agreement_count in contributions.items():
            if agreement_count >= 2:  # 至少两种方法同意
                final_anomalies.append(point)

        return sorted(final_anomalies)

def demonstrate_constraint_analysis():
    """演示约束分析系统"""
    print("🔗 多维度CGMS异常检测约束干扰分析演示")
    print("=" * 80)

    analyzer = InterDimensionalConstraintAnalyzer()

    # 创建模拟数据
    np.random.seed(42)
    glucose_data = 120 + np.cumsum(np.random.normal(0, 3, 100))

    # 添加一些特定模式来演示约束关系
    glucose_data[30] = 300    # 统计异常但可能生理正常（餐后）
    glucose_data[50:55] = 95  # 模式平稳但统计正常
    glucose_data[80] = 40     # 生理异常，应该统计也异常

    # 模拟检测结果
    detection_results = {
        'method_results': {
            'statistical': {'anomalies': [30, 80]},
            'physiological': {'anomalies': [80]},  # 只有真正极值
            'pattern_based': {'anomalies': [30, 50, 51, 52, 53, 54]},
            'frequency': {'anomalies': []},
            'ml_based': {'anomalies': [30, 45, 80]},
            'temporal': {'anomalies': [45, 80]}
        }
    }

    print(f"📊 模拟数据和检测结果:")
    for method, result in detection_results['method_results'].items():
        print(f"  {method}: {len(result['anomalies'])} 个异常")

    # 1. 约束关系分析
    constraint_analysis = analyzer.analyze_constraint_relationships(detection_results)

    print(f"\n📈 约束关系分析结果:")
    for conflict in constraint_analysis['direct_conflicts']:
        print(f"  🔥 {conflict['type']}: {conflict['description']}")
        print(f"     解决方案: {conflict['resolution']}")

    # 2. 干扰模式识别
    interference_patterns = analyzer.identify_interference_patterns(glucose_data, detection_results)

    print(f"\n⚡ 干扰模式识别:")
    for interference_type, details in interference_patterns.items():
        print(f"  {interference_type}: {len(details)} 种干扰")

    # 3. 约束解决框架
    resolution_framework = analyzer.design_constraint_resolution_framework(
        constraint_analysis, interference_patterns
    )

    # 4. 优化集成实现
    optimized_result = analyzer.implement_optimized_ensemble(
        glucose_data, None, resolution_framework
    )

    print(f"\n✨ 约束感知优化完成！")
    print(f"最终异常点数: {len(optimized_result['final_anomalies'])}")
    print(f"方法一致性评分: {optimized_result['consistency_score']:.3f}")

    return optimized_result

if __name__ == "__main__":
    demonstrate_constraint_analysis()