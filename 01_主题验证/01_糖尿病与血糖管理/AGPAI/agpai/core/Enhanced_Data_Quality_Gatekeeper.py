#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强数据质量门控系统
在进行任何AGP分析前，严格评估数据质量，不合格数据直接拒绝分析并建议更换传感器
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import warnings
import logging
from enum import Enum

class DataQualityLevel(Enum):
    """数据质量等级"""
    EXCELLENT = "优秀"
    GOOD = "良好" 
    ACCEPTABLE = "可接受"
    POOR = "较差"
    UNACCEPTABLE = "不可接受"

class QualityGateAction(Enum):
    """质量门控决策"""
    PROCEED = "继续分析"
    PROCEED_WITH_WARNING = "警告下继续"
    REPAIR_AND_RETRY = "修复后重试"
    REPLACE_SENSOR = "更换传感器"
    REJECT_ANALYSIS = "拒绝分析"

class EnhancedDataQualityGatekeeper:
    """增强数据质量门控器"""
    
    def __init__(self):
        """初始化质量标准和阈值"""
        
        # 严格的质量标准 - 不可接受阈值
        self.unacceptable_thresholds = {
            'minimum_days': 7,                # 最少7天数据
            'minimum_coverage': 60,           # 最低60%覆盖率
            'maximum_gap_hours': 8,           # 最大连续缺失8小时
            'maximum_stuck_minutes': 120,     # 传感器卡死不超过2小时
            'maximum_drift_rate': 0.3,        # 漂移率不超过0.3 mmol/L/小时
            'minimum_variability': 1.0,       # 最小变异系数1%
            'maximum_delay_minutes': 90,      # 数据延迟不超过1.5小时
            'minimum_signal_quality': 0.3     # 信号质量最低0.3
        }
        
        # 可接受阈值
        self.acceptable_thresholds = {
            'minimum_days': 10,
            'minimum_coverage': 70,
            'maximum_gap_hours': 6,
            'maximum_stuck_minutes': 60,
            'maximum_drift_rate': 0.15,
            'minimum_variability': 2.0,
            'maximum_delay_minutes': 30,
            'minimum_signal_quality': 0.5
        }
        
        # 优秀阈值
        self.excellent_thresholds = {
            'minimum_days': 14,
            'minimum_coverage': 85,
            'maximum_gap_hours': 2,
            'maximum_stuck_minutes': 15,
            'maximum_drift_rate': 0.05,
            'minimum_variability': 5.0,
            'maximum_delay_minutes': 15,
            'minimum_signal_quality': 0.8
        }

    def evaluate_data_quality(self, cgm_data: pd.DataFrame, metadata: Dict = None) -> Dict:
        """
        主要质量评估入口 - 数据质量门控
        
        Args:
            cgm_data: CGM数据
            metadata: 元数据信息
            
        Returns:
            完整的质量评估结果和决策建议
        """
        
        logging.info("🚪 启动数据质量门控评估...")
        
        try:
            # Step 1: 数据预处理和基础验证
            preprocessed_data = self._preprocess_and_validate(cgm_data)
            if preprocessed_data is None:
                return self._generate_rejection_result("数据预处理失败")
            
            # Step 2: 执行全面质量检测
            quality_metrics = self._comprehensive_quality_assessment(preprocessed_data)
            
            # Step 3: 实时性和及时性检查
            timeliness_check = self._evaluate_data_timeliness(preprocessed_data)
            quality_metrics.update(timeliness_check)
            
            # Step 4: 传感器故障诊断
            sensor_health = self._diagnose_sensor_health(preprocessed_data)
            quality_metrics.update(sensor_health)
            
            # Step 5: 数据来源验证
            if metadata:
                source_validation = self._validate_data_source(preprocessed_data, metadata)
                quality_metrics.update(source_validation)
            
            # Step 6: 综合质量评估和决策
            final_assessment = self._make_quality_decision(quality_metrics)
            
            # Step 7: 生成详细报告
            quality_report = self._generate_quality_report(quality_metrics, final_assessment)
            
            # 记录质量门控结果
            self._log_gatekeeper_decision(final_assessment, quality_report)
            
            return quality_report
            
        except Exception as e:
            logging.error(f"质量门控评估异常: {str(e)}")
            return self._generate_rejection_result(f"评估过程异常: {str(e)}")

    def _comprehensive_quality_assessment(self, data: pd.DataFrame) -> Dict:
        """全面质量评估"""
        
        metrics = {}
        glucose_values = data['glucose'].dropna()
        
        # 1. 数据完整性评估
        metrics['completeness'] = self._assess_completeness(data)
        
        # 2. 时间连续性评估  
        metrics['continuity'] = self._assess_continuity(data)
        
        # 3. 数据有效性评估
        metrics['validity'] = self._assess_validity(glucose_values)
        
        # 4. 变异性评估
        metrics['variability'] = self._assess_variability(glucose_values)
        
        # 5. 异常值评估
        metrics['outliers'] = self._assess_outliers(glucose_values)
        
        return metrics

    def _evaluate_data_timeliness(self, data: pd.DataFrame) -> Dict:
        """评估数据及时性"""
        
        current_time = datetime.now()
        latest_data_time = pd.to_datetime(data['timestamp'].max())
        
        # 计算数据延迟
        delay_minutes = (current_time - latest_data_time).total_seconds() / 60
        
        # 评估实时性状态
        if delay_minutes <= 15:
            timeliness_status = "实时"
            timeliness_score = 100
        elif delay_minutes <= 30:
            timeliness_status = "准实时"
            timeliness_score = 80
        elif delay_minutes <= 60:
            timeliness_status = "延迟"
            timeliness_score = 60
        elif delay_minutes <= 90:
            timeliness_status = "严重延迟"
            timeliness_score = 30
        else:
            timeliness_status = "数据过期"
            timeliness_score = 0
        
        return {
            'timeliness': {
                'delay_minutes': delay_minutes,
                'status': timeliness_status,
                'score': timeliness_score,
                'is_acceptable': delay_minutes <= self.unacceptable_thresholds['maximum_delay_minutes'],
                'latest_timestamp': latest_data_time.isoformat(),
                'evaluation_time': current_time.isoformat()
            }
        }

    def _diagnose_sensor_health(self, data: pd.DataFrame) -> Dict:
        """传感器健康诊断"""
        
        glucose = data['glucose'].values
        timestamps = pd.to_datetime(data['timestamp'])
        
        diagnosis = {}
        
        # 1. 传感器卡死检测
        stuck_analysis = self._detect_sensor_stuck_advanced(glucose)
        diagnosis['sensor_stuck'] = stuck_analysis
        
        # 2. 传感器漂移检测
        drift_analysis = self._detect_sensor_drift_advanced(glucose, timestamps)
        diagnosis['sensor_drift'] = drift_analysis
        
        # 3. 信号质量评估
        signal_quality = self._assess_signal_quality(glucose)
        diagnosis['signal_quality'] = signal_quality
        
        # 4. 校准状态评估
        calibration_status = self._assess_calibration_status(glucose)
        diagnosis['calibration'] = calibration_status
        
        # 5. 传感器寿命评估
        lifetime_assessment = self._assess_sensor_lifetime(data)
        diagnosis['lifetime'] = lifetime_assessment
        
        return {'sensor_health': diagnosis}

    def _detect_sensor_stuck_advanced(self, glucose: np.ndarray) -> Dict:
        """高级传感器卡死检测"""
        
        consecutive_threshold = 0.1  # 0.1 mmol/L以内认为相同
        max_stuck_minutes = 0
        stuck_periods = []
        current_stuck = 0
        
        for i in range(1, len(glucose)):
            if abs(glucose[i] - glucose[i-1]) <= consecutive_threshold:
                current_stuck += 1
            else:
                if current_stuck > 0:
                    stuck_minutes = current_stuck * 15  # 假设15分钟间隔
                    if stuck_minutes >= 30:  # 记录30分钟以上的卡死
                        stuck_periods.append({
                            'start_index': i - current_stuck - 1,
                            'end_index': i - 1,
                            'duration_minutes': stuck_minutes,
                            'stuck_value': glucose[i-1]
                        })
                    max_stuck_minutes = max(max_stuck_minutes, stuck_minutes)
                current_stuck = 0
        
        # 检查末尾
        if current_stuck > 0:
            stuck_minutes = current_stuck * 15
            max_stuck_minutes = max(max_stuck_minutes, stuck_minutes)
        
        is_stuck = max_stuck_minutes > self.unacceptable_thresholds['maximum_stuck_minutes']
        severity = self._categorize_stuck_severity(max_stuck_minutes)
        
        return {
            'detected': is_stuck,
            'max_stuck_minutes': max_stuck_minutes,
            'stuck_periods': stuck_periods,
            'severity': severity,
            'is_acceptable': not is_stuck
        }

    def _detect_sensor_drift_advanced(self, glucose: np.ndarray, timestamps: pd.Series) -> Dict:
        """高级传感器漂移检测"""
        
        # 计算时间序列(小时)
        time_hours = np.array([(t - timestamps.iloc[0]).total_seconds() / 3600 for t in timestamps])
        
        # 整体线性趋势
        overall_slope = np.polyfit(time_hours, glucose, 1)[0]
        
        # 分段趋势分析
        segment_size = min(48, len(glucose) // 4)  # 12小时段
        segment_slopes = []
        
        if len(glucose) >= segment_size * 2:
            for i in range(0, len(glucose) - segment_size, segment_size // 2):
                end_idx = min(i + segment_size, len(glucose))
                segment_glucose = glucose[i:end_idx]
                segment_time = time_hours[i:end_idx]
                
                if len(segment_glucose) > 10:
                    slope = np.polyfit(segment_time, segment_glucose, 1)[0]
                    segment_slopes.append(slope)
        
        # 漂移评估
        drift_rate = abs(overall_slope)
        progressive_drift = np.std(segment_slopes) if segment_slopes else 0
        
        severity = self._categorize_drift_severity(drift_rate)
        is_acceptable = drift_rate <= self.unacceptable_thresholds['maximum_drift_rate']
        
        return {
            'detected': drift_rate > 0.05,  # 每小时漂移超过0.05
            'drift_rate_per_hour': drift_rate,
            'overall_slope': overall_slope,
            'progressive_drift': progressive_drift,
            'severity': severity,
            'is_acceptable': is_acceptable,
            'segment_slopes': segment_slopes
        }

    def _assess_signal_quality(self, glucose: np.ndarray) -> Dict:
        """信号质量评估"""
        
        # 1. 信噪比评估
        signal_mean = np.mean(glucose)
        noise_std = np.std(np.diff(glucose))  # 高频噪声
        snr = signal_mean / noise_std if noise_std > 0 else float('inf')
        
        # 2. 平滑度评估
        smoothness = self._calculate_smoothness_index(glucose)
        
        # 3. 数据一致性评估
        consistency = self._calculate_consistency_index(glucose)
        
        # 4. 综合信号质量评分
        quality_score = min(1.0, (snr / 20 + smoothness + consistency) / 3)
        
        return {
            'snr': snr,
            'smoothness': smoothness,
            'consistency': consistency,
            'quality_score': quality_score,
            'is_acceptable': quality_score >= self.unacceptable_thresholds['minimum_signal_quality']
        }

    def _make_quality_decision(self, quality_metrics: Dict) -> Dict:
        """做出质量门控决策"""
        
        # 收集所有质量检查结果
        checks = []
        critical_failures = []
        warnings = []
        
        # 数据完整性检查
        if not quality_metrics.get('completeness', {}).get('is_acceptable', False):
            critical_failures.append("数据完整性不足")
            
        # 时间连续性检查  
        if not quality_metrics.get('continuity', {}).get('is_acceptable', False):
            critical_failures.append("时间连续性不足")
            
        # 数据及时性检查
        if not quality_metrics.get('timeliness', {}).get('is_acceptable', False):
            critical_failures.append("数据不及时")
            
        # 传感器健康检查
        sensor_health = quality_metrics.get('sensor_health', {})
        
        if sensor_health.get('sensor_stuck', {}).get('detected', False):
            critical_failures.append("传感器卡死")
            
        if not sensor_health.get('sensor_drift', {}).get('is_acceptable', False):
            critical_failures.append("传感器严重漂移")
            
        if not sensor_health.get('signal_quality', {}).get('is_acceptable', False):
            critical_failures.append("信号质量过差")
        
        # 决策逻辑
        if len(critical_failures) >= 3:
            decision = QualityGateAction.REJECT_ANALYSIS
            recommendation = "数据质量严重不合格，强烈建议更换传感器"
            quality_level = DataQualityLevel.UNACCEPTABLE
            
        elif len(critical_failures) >= 1:
            if any("传感器" in failure for failure in critical_failures):
                decision = QualityGateAction.REPLACE_SENSOR
                recommendation = "检测到传感器故障，建议立即更换传感器"
                quality_level = DataQualityLevel.POOR
            else:
                decision = QualityGateAction.REPAIR_AND_RETRY
                recommendation = "数据质量不合格，请检查数据采集系统"
                quality_level = DataQualityLevel.POOR
                
        elif len(warnings) > 0:
            decision = QualityGateAction.PROCEED_WITH_WARNING
            recommendation = "数据质量可接受但存在警告，建议关注数据质量"
            quality_level = DataQualityLevel.ACCEPTABLE
            
        else:
            decision = QualityGateAction.PROCEED
            recommendation = "数据质量良好，可以进行分析"
            quality_level = DataQualityLevel.GOOD

        return {
            'decision': decision,
            'quality_level': quality_level,
            'recommendation': recommendation,
            'critical_failures': critical_failures,
            'warnings': warnings,
            'can_proceed': decision in [QualityGateAction.PROCEED, QualityGateAction.PROCEED_WITH_WARNING]
        }

    def _generate_quality_report(self, quality_metrics: Dict, assessment: Dict) -> Dict:
        """生成完整的质量报告"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'gatekeeper_version': '2.0',
            
            # 门控决策结果
            'gate_decision': {
                'action': assessment['decision'].value,
                'quality_level': assessment['quality_level'].value,
                'can_proceed_with_analysis': assessment['can_proceed'],
                'recommendation': assessment['recommendation']
            },
            
            # 详细质量指标
            'quality_metrics': quality_metrics,
            
            # 问题总结
            'issues_summary': {
                'critical_failures': assessment['critical_failures'],
                'warnings': assessment['warnings'],
                'total_issues': len(assessment['critical_failures']) + len(assessment['warnings'])
            },
            
            # 行动建议
            'action_items': self._generate_action_items(assessment),
            
            # 质量评分
            'overall_score': self._calculate_overall_quality_score(quality_metrics),
            
            # 下次检查建议
            'next_check_recommendation': self._recommend_next_check(assessment)
        }

    def _generate_action_items(self, assessment: Dict) -> List[Dict]:
        """生成行动建议"""
        
        action_items = []
        
        if assessment['decision'] == QualityGateAction.REPLACE_SENSOR:
            action_items.extend([
                {
                    'priority': 'CRITICAL',
                    'action': '立即更换CGM传感器',
                    'reason': '检测到传感器故障或严重异常',
                    'estimated_time': '15-30分钟'
                },
                {
                    'priority': 'HIGH',
                    'action': '校准新传感器',
                    'reason': '确保新传感器准确性',
                    'estimated_time': '2-4小时'
                },
                {
                    'priority': 'MEDIUM', 
                    'action': '监测新传感器24小时',
                    'reason': '验证新传感器工作状态',
                    'estimated_time': '24小时'
                }
            ])
            
        elif assessment['decision'] == QualityGateAction.REJECT_ANALYSIS:
            action_items.append({
                'priority': 'CRITICAL',
                'action': '停止当前分析并检查数据采集系统',
                'reason': '数据质量严重不合格',
                'estimated_time': '1-2小时'
            })
        
        return action_items

    def _log_gatekeeper_decision(self, assessment: Dict, report: Dict):
        """记录门控决策"""
        
        decision = assessment['decision']
        quality_level = assessment['quality_level']
        
        if decision == QualityGateAction.REJECT_ANALYSIS:
            logging.error(f"🚫 数据质量门控: 拒绝分析 - {assessment['recommendation']}")
            
        elif decision == QualityGateAction.REPLACE_SENSOR:
            logging.warning(f"🔄 数据质量门控: 建议更换传感器 - {assessment['recommendation']}")
            
        elif decision == QualityGateAction.PROCEED_WITH_WARNING:
            logging.info(f"⚠️ 数据质量门控: 警告下继续 - {assessment['recommendation']}")
            
        else:
            logging.info(f"✅ 数据质量门控: 质量合格，继续分析")

    # 辅助方法
    def _preprocess_and_validate(self, data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """数据预处理和基础验证"""
        if data.empty:
            return None
            
        if 'timestamp' not in data.columns or 'glucose' not in data.columns:
            return None
            
        try:
            data = data.copy()
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data['glucose'] = pd.to_numeric(data['glucose'], errors='coerce')
            data = data.sort_values('timestamp').reset_index(drop=True)
            return data
        except:
            return None

    def _assess_completeness(self, data: pd.DataFrame) -> Dict:
        """评估数据完整性"""
        time_span_days = (data['timestamp'].max() - data['timestamp'].min()).days
        return {
            'time_span_days': time_span_days,
            'is_acceptable': time_span_days >= self.unacceptable_thresholds['minimum_days']
        }

    def _assess_continuity(self, data: pd.DataFrame) -> Dict:
        """评估时间连续性"""  
        time_diffs = data['timestamp'].diff().dt.total_seconds() / 60
        max_gap_hours = time_diffs.max() / 60 if not time_diffs.empty else 0
        return {
            'max_gap_hours': max_gap_hours,
            'is_acceptable': max_gap_hours <= self.unacceptable_thresholds['maximum_gap_hours']
        }

    def _assess_validity(self, glucose: np.ndarray) -> Dict:
        """评估数据有效性"""
        valid_range = (glucose >= 1.0) & (glucose <= 33.3)
        valid_rate = np.sum(valid_range) / len(glucose) * 100
        return {
            'valid_rate': valid_rate,
            'is_acceptable': valid_rate >= 95
        }

    def _assess_variability(self, glucose: np.ndarray) -> Dict:
        """评估数据变异性"""
        cv = (np.std(glucose) / np.mean(glucose)) * 100 if np.mean(glucose) > 0 else 0
        return {
            'coefficient_variation': cv,
            'is_acceptable': cv >= self.unacceptable_thresholds['minimum_variability']
        }

    def _assess_outliers(self, glucose: np.ndarray) -> Dict:
        """评估异常值"""
        q75, q25 = np.percentile(glucose, [75, 25])
        iqr = q75 - q25
        outliers = np.sum((glucose < q25 - 1.5 * iqr) | (glucose > q75 + 1.5 * iqr))
        outlier_rate = (outliers / len(glucose)) * 100
        return {
            'outlier_rate': outlier_rate,
            'is_acceptable': outlier_rate <= 10
        }

    def _assess_calibration_status(self, glucose: np.ndarray) -> Dict:
        """评估校准状态"""
        # 简化的校准评估
        mean_glucose = np.mean(glucose)
        reasonable_range = 4.0 <= mean_glucose <= 15.0  # 合理的平均血糖范围
        
        return {
            'mean_glucose': mean_glucose,
            'in_reasonable_range': reasonable_range,
            'is_acceptable': reasonable_range
        }

    def _assess_sensor_lifetime(self, data: pd.DataFrame) -> Dict:
        """评估传感器寿命"""
        time_span = (data['timestamp'].max() - data['timestamp'].min()).days
        
        return {
            'current_age_days': time_span,
            'estimated_remaining_days': max(0, 14 - time_span),
            'replacement_due_soon': time_span >= 12,
            'is_acceptable': time_span <= 14
        }

    def _calculate_smoothness_index(self, glucose: np.ndarray) -> float:
        """计算平滑度指数"""
        if len(glucose) < 3:
            return 0.5
        
        second_diff = np.diff(glucose, n=2)
        smoothness = 1 / (1 + np.std(second_diff))
        return min(1.0, smoothness)

    def _calculate_consistency_index(self, glucose: np.ndarray) -> float:
        """计算一致性指数"""
        if len(glucose) < 10:
            return 0.5
            
        segments = np.array_split(glucose, min(5, len(glucose)//10))
        segment_means = [np.mean(seg) for seg in segments if len(seg) > 0]
        
        if len(segment_means) < 2:
            return 0.5
            
        consistency = 1 / (1 + np.std(segment_means) / np.mean(segment_means))
        return min(1.0, consistency)

    def _categorize_stuck_severity(self, stuck_minutes: float) -> str:
        """分类卡死严重程度"""
        if stuck_minutes >= 120:
            return "严重"
        elif stuck_minutes >= 60:
            return "中等"
        elif stuck_minutes >= 30:
            return "轻微"
        else:
            return "正常"

    def _categorize_drift_severity(self, drift_rate: float) -> str:
        """分类漂移严重程度"""
        if drift_rate >= 0.3:
            return "严重"
        elif drift_rate >= 0.15:
            return "中等"
        elif drift_rate >= 0.05:
            return "轻微"
        else:
            return "正常"

    def _calculate_overall_quality_score(self, metrics: Dict) -> float:
        """计算综合质量评分"""
        # 简化的综合评分算法
        scores = []
        
        # 各项指标权重评分
        if metrics.get('completeness', {}).get('is_acceptable'):
            scores.append(25)
        if metrics.get('continuity', {}).get('is_acceptable'):
            scores.append(25)
        if metrics.get('timeliness', {}).get('is_acceptable'):
            scores.append(20)
        if metrics.get('sensor_health', {}).get('signal_quality', {}).get('is_acceptable'):
            scores.append(30)
            
        return sum(scores)

    def _recommend_next_check(self, assessment: Dict) -> str:
        """建议下次检查时间"""
        if assessment['decision'] == QualityGateAction.REPLACE_SENSOR:
            return "更换传感器后立即检查"
        elif assessment['decision'] == QualityGateAction.REJECT_ANALYSIS:
            return "修复问题后重新评估"
        else:
            return "24小时后例行检查"

    def _generate_rejection_result(self, reason: str) -> Dict:
        """生成拒绝结果"""
        return {
            'timestamp': datetime.now().isoformat(),
            'gate_decision': {
                'action': QualityGateAction.REJECT_ANALYSIS.value,
                'quality_level': DataQualityLevel.UNACCEPTABLE.value,
                'can_proceed_with_analysis': False,
                'recommendation': f"数据质量检查失败: {reason}，请检查数据源并考虑更换传感器"
            },
            'issues_summary': {
                'critical_failures': [reason],
                'warnings': [],
                'total_issues': 1
            },
            'action_items': [{
                'priority': 'CRITICAL',
                'action': '检查传感器和数据采集系统',
                'reason': reason,
                'estimated_time': '30-60分钟'
            }]
        }