#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CGM数据质量评估模块
在进行AGP分析前，先评估数据质量，确保分析结果的可靠性
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
import logging

from ..config.config_manager import ConfigManager

class CGMDataQualityAssessor:
    """CGM数据质量评估器"""
    
    def __init__(self):
        self.quality_criteria = {
            'minimum_days': 10,           # 最少天数
            'minimum_data_coverage': 70,  # 最低数据覆盖率(%)
            'maximum_gap_hours': 6,       # 最大连续缺失时间(小时)
            'minimum_daily_points': 60,   # 每日最少数据点数
            'glucose_range_min': 1.0,     # 血糖最小值(mmol/L)
            'glucose_range_max': 33.3,    # 血糖最大值(mmol/L)
            'maximum_duplicate_rate': 20, # 最大重复值比例(%)
            'maximum_outlier_rate': 5,    # 最大异常值比例(%)
            'minimum_variability': 0.5    # 最小变异系数
        }
    
    def assess_data_quality(self, cgm_data: pd.DataFrame, analysis_days: int = 14) -> Dict:
        """
        全面评估CGM数据质量
        
        Args:
            cgm_data: CGM数据DataFrame
            analysis_days: 分析天数
            
        Returns:
            数据质量评估结果
        """
        if cgm_data.empty:
            return self._generate_failed_assessment("数据为空")
        
        try:
            # 数据预处理
            clean_data = self._preprocess_data(cgm_data)
            
            # 执行各项质量检查
            quality_checks = {}
            
            # 1. 数据完整性检查
            quality_checks.update(self._check_data_completeness(clean_data, analysis_days))
            
            # 2. 时间序列连续性检查
            quality_checks.update(self._check_time_continuity(clean_data))
            
            # 3. 血糖值合理性检查
            quality_checks.update(self._check_glucose_validity(clean_data))
            
            # 4. 数据变异性检查
            quality_checks.update(self._check_data_variability(clean_data))
            
            # 5. 异常值检查
            quality_checks.update(self._check_outliers(clean_data))
            
            # 6. 重复值检查
            quality_checks.update(self._check_duplicates(clean_data))
            
            # 7. 传感器性能检查
            quality_checks.update(self._check_sensor_performance(clean_data))
            
            # 综合评估
            overall_assessment = self._calculate_overall_quality(quality_checks)
            
            return {
                'overall_quality': overall_assessment,
                'detailed_checks': quality_checks,
                'data_summary': self._generate_data_summary(clean_data),
                'recommendations': self._generate_recommendations(quality_checks),
                'usable_for_analysis': overall_assessment['is_acceptable'],
                'assessment_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"数据质量评估失败: {str(e)}")
            return self._generate_failed_assessment(f"评估过程出错: {str(e)}")
    
    def _preprocess_data(self, cgm_data: pd.DataFrame) -> pd.DataFrame:
        """数据预处理"""
        data = cgm_data.copy()
        
        # 确保时间戳列存在且格式正确
        if 'timestamp' not in data.columns:
            raise ValueError("缺少timestamp列")
        
        # 确保血糖列存在
        if 'glucose' not in data.columns:
            raise ValueError("缺少glucose列")
        
        # 转换数据类型
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['glucose'] = pd.to_numeric(data['glucose'], errors='coerce')
        
        # 按时间排序
        data = data.sort_values('timestamp').reset_index(drop=True)
        
        # 移除重复时间戳
        data = data.drop_duplicates(subset=['timestamp']).reset_index(drop=True)
        
        return data
    
    def _check_data_completeness(self, data: pd.DataFrame, analysis_days: int) -> Dict:
        """检查数据完整性"""
        checks = {}
        
        # 数据时间跨度
        time_span = (data['timestamp'].max() - data['timestamp'].min()).days
        checks['time_span_days'] = time_span
        checks['time_span_sufficient'] = time_span >= self.quality_criteria['minimum_days']
        
        # 数据点总数
        total_points = len(data)
        expected_points = analysis_days * 24 * 4  # 假设15分钟间隔
        checks['total_data_points'] = total_points
        checks['expected_data_points'] = expected_points
        checks['data_coverage_rate'] = (total_points / expected_points) * 100 if expected_points > 0 else 0
        checks['coverage_sufficient'] = checks['data_coverage_rate'] >= self.quality_criteria['minimum_data_coverage']
        
        # 每日数据点数
        daily_counts = data.groupby(data['timestamp'].dt.date).size()
        checks['daily_point_counts'] = daily_counts.to_dict()
        checks['min_daily_points'] = daily_counts.min()
        checks['max_daily_points'] = daily_counts.max()
        checks['avg_daily_points'] = daily_counts.mean()
        checks['daily_coverage_sufficient'] = daily_counts.min() >= self.quality_criteria['minimum_daily_points']
        
        # 有数据的天数
        unique_days = data['timestamp'].dt.date.nunique()
        checks['days_with_data'] = unique_days
        checks['days_sufficient'] = unique_days >= self.quality_criteria['minimum_days']
        
        return {'completeness': checks}
    
    def _check_time_continuity(self, data: pd.DataFrame) -> Dict:
        """检查时间序列连续性"""
        checks = {}
        
        # 计算时间间隔
        time_diffs = data['timestamp'].diff().dt.total_seconds() / 60  # 转换为分钟
        
        # 预期间隔(分钟)
        median_interval = time_diffs.median()
        checks['median_interval_minutes'] = median_interval
        
        # 识别数据缺失gap
        # 定义gap为超过正常间隔3倍的时间间隔
        normal_interval_threshold = median_interval * 3 if not pd.isna(median_interval) else 60
        gaps = time_diffs[time_diffs > normal_interval_threshold]
        
        checks['total_gaps'] = len(gaps)
        checks['max_gap_hours'] = gaps.max() / 60 if len(gaps) > 0 else 0
        checks['total_missing_hours'] = gaps.sum() / 60 if len(gaps) > 0 else 0
        checks['gap_acceptable'] = checks['max_gap_hours'] <= self.quality_criteria['maximum_gap_hours']
        
        # 间隔分布分析
        checks['interval_statistics'] = {
            'mean': time_diffs.mean(),
            'std': time_diffs.std(),
            'min': time_diffs.min(),
            'max': time_diffs.max(),
            'p95': time_diffs.quantile(0.95)
        }
        
        return {'continuity': checks}
    
    def _check_glucose_validity(self, data: pd.DataFrame) -> Dict:
        """检查血糖值合理性"""
        checks = {}
        glucose_values = data['glucose'].dropna()
        
        # 基础统计
        checks['glucose_statistics'] = {
            'count': len(glucose_values),
            'mean': glucose_values.mean(),
            'std': glucose_values.std(),
            'min': glucose_values.min(),
            'max': glucose_values.max(),
            'median': glucose_values.median()
        }
        
        # 范围检查
        checks['values_in_valid_range'] = len(glucose_values[
            (glucose_values >= self.quality_criteria['glucose_range_min']) & 
            (glucose_values <= self.quality_criteria['glucose_range_max'])
        ])
        checks['invalid_values_count'] = len(glucose_values) - checks['values_in_valid_range']
        checks['invalid_rate'] = (checks['invalid_values_count'] / len(glucose_values)) * 100
        checks['range_valid'] = checks['invalid_rate'] < 1  # 允许1%的无效值
        
        # 生理合理性检查
        checks['extreme_low_count'] = len(glucose_values[glucose_values < 2.2])  # <2.2 mmol/L
        checks['extreme_high_count'] = len(glucose_values[glucose_values > 22.2])  # >22.2 mmol/L
        checks['physiologically_reasonable'] = (checks['extreme_low_count'] + checks['extreme_high_count']) < len(glucose_values) * 0.02
        
        # 缺失值检查
        total_rows = len(data)
        missing_count = data['glucose'].isna().sum()
        checks['missing_values_count'] = missing_count
        checks['missing_rate'] = (missing_count / total_rows) * 100
        checks['missing_acceptable'] = checks['missing_rate'] < 10  # 允许10%缺失
        
        return {'validity': checks}
    
    def _check_data_variability(self, data: pd.DataFrame) -> Dict:
        """检查数据变异性"""
        checks = {}
        glucose_values = data['glucose'].dropna()
        
        # 变异系数
        cv = (glucose_values.std() / glucose_values.mean()) * 100 if glucose_values.mean() > 0 else 0
        checks['coefficient_of_variation'] = cv
        checks['variability_sufficient'] = cv >= self.quality_criteria['minimum_variability']
        
        # 血糖范围
        glucose_range = glucose_values.max() - glucose_values.min()
        checks['glucose_range'] = glucose_range
        checks['range_adequate'] = glucose_range > 2.0  # 至少2 mmol/L的变化
        
        # 唯一值数量
        unique_values = glucose_values.nunique()
        checks['unique_values_count'] = unique_values
        checks['unique_values_rate'] = (unique_values / len(glucose_values)) * 100
        checks['diversity_adequate'] = checks['unique_values_rate'] > 10  # 至少10%的值是唯一的
        
        return {'variability': checks}
    
    def _check_outliers(self, data: pd.DataFrame) -> Dict:
        """检查异常值"""
        checks = {}
        glucose_values = data['glucose'].dropna()
        
        # 使用IQR方法检测异常值
        Q1 = glucose_values.quantile(0.25)
        Q3 = glucose_values.quantile(0.75)
        IQR = Q3 - Q1
        
        # 定义异常值范围
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = glucose_values[(glucose_values < lower_bound) | (glucose_values > upper_bound)]
        checks['outlier_count'] = len(outliers)
        checks['outlier_rate'] = (len(outliers) / len(glucose_values)) * 100
        checks['outlier_acceptable'] = checks['outlier_rate'] <= self.quality_criteria['maximum_outlier_rate']
        
        # 极端异常值(超过3个IQR)
        extreme_lower = Q1 - 3 * IQR
        extreme_upper = Q3 + 3 * IQR
        extreme_outliers = glucose_values[(glucose_values < extreme_lower) | (glucose_values > extreme_upper)]
        checks['extreme_outlier_count'] = len(extreme_outliers)
        checks['extreme_outlier_rate'] = (len(extreme_outliers) / len(glucose_values)) * 100
        
        return {'outliers': checks}
    
    def _check_duplicates(self, data: pd.DataFrame) -> Dict:
        """检查重复值"""
        checks = {}
        glucose_values = data['glucose'].dropna()
        
        # 连续重复值检查
        consecutive_duplicates = 0
        max_consecutive = 0
        current_consecutive = 0
        
        for i in range(1, len(glucose_values)):
            if glucose_values.iloc[i] == glucose_values.iloc[i-1]:
                current_consecutive += 1
                consecutive_duplicates += 1
            else:
                max_consecutive = max(max_consecutive, current_consecutive)
                current_consecutive = 0
        
        max_consecutive = max(max_consecutive, current_consecutive)
        
        checks['consecutive_duplicates'] = consecutive_duplicates
        checks['max_consecutive_count'] = max_consecutive
        checks['consecutive_duplicate_rate'] = (consecutive_duplicates / len(glucose_values)) * 100
        checks['duplicates_acceptable'] = checks['consecutive_duplicate_rate'] <= self.quality_criteria['maximum_duplicate_rate']
        
        # 检查是否有过多的固定值
        value_counts = glucose_values.value_counts()
        most_common_value = value_counts.iloc[0] if not value_counts.empty else 0
        checks['most_common_value_count'] = most_common_value
        checks['most_common_value_rate'] = (most_common_value / len(glucose_values)) * 100
        checks['no_single_value_dominance'] = checks['most_common_value_rate'] < 30  # 单一值不超过30%
        
        return {'duplicates': checks}
    
    def _check_sensor_performance(self, data: pd.DataFrame) -> Dict:
        """检查传感器性能指标"""
        checks = {}
        glucose_values = data['glucose'].dropna()
        
        if len(glucose_values) < 10:
            return {'sensor_performance': {'insufficient_data': True}}
        
        # 计算一阶差分(血糖变化率)
        glucose_diff = glucose_values.diff().dropna()
        
        # 血糖变化率统计
        checks['glucose_change_stats'] = {
            'mean_change': glucose_diff.mean(),
            'std_change': glucose_diff.std(),
            'max_positive_change': glucose_diff.max(),
            'max_negative_change': glucose_diff.min()
        }
        
        # 传感器噪声评估(基于高频波动)
        if len(glucose_diff) > 5:
            # 计算连续变化方向改变的频率(噪声指标)
            sign_changes = np.sum(np.diff(np.sign(glucose_diff)) != 0)
            checks['noise_index'] = sign_changes / len(glucose_diff)
            checks['low_noise'] = checks['noise_index'] < 0.6  # 经验阈值
        
        # 传感器稳定性(基于长期趋势的一致性)
        # 使用移动平均来评估稳定性
        if len(glucose_values) >= 20:
            window_size = min(20, len(glucose_values) // 4)
            moving_avg = glucose_values.rolling(window=window_size, center=True).mean()
            residuals = glucose_values - moving_avg
            checks['sensor_precision'] = residuals.std()
            checks['good_precision'] = checks['sensor_precision'] < 2.0  # 标准偏差<2 mmol/L
        
        return {'sensor_performance': checks}
    
    def _calculate_overall_quality(self, quality_checks: Dict) -> Dict:
        """计算综合数据质量评分"""
        
        # 各项检查的权重
        weights = {
            'completeness': 0.25,
            'continuity': 0.20,
            'validity': 0.25,
            'variability': 0.10,
            'outliers': 0.10,
            'duplicates': 0.05,
            'sensor_performance': 0.05
        }
        
        scores = {}
        
        # 计算各项得分
        # 完整性得分
        completeness = quality_checks.get('completeness', {})
        completeness_score = 0
        if completeness.get('coverage_sufficient', False): completeness_score += 40
        if completeness.get('days_sufficient', False): completeness_score += 30
        if completeness.get('daily_coverage_sufficient', False): completeness_score += 30
        scores['completeness'] = completeness_score
        
        # 连续性得分
        continuity = quality_checks.get('continuity', {})
        continuity_score = 0
        if continuity.get('gap_acceptable', False): continuity_score += 60
        if continuity.get('total_gaps', 10) <= 5: continuity_score += 40  # 少于5个gap
        scores['continuity'] = continuity_score
        
        # 有效性得分
        validity = quality_checks.get('validity', {})
        validity_score = 0
        if validity.get('range_valid', False): validity_score += 30
        if validity.get('physiologically_reasonable', False): validity_score += 35
        if validity.get('missing_acceptable', False): validity_score += 35
        scores['validity'] = validity_score
        
        # 变异性得分
        variability = quality_checks.get('variability', {})
        variability_score = 0
        if variability.get('variability_sufficient', False): variability_score += 40
        if variability.get('range_adequate', False): variability_score += 30
        if variability.get('diversity_adequate', False): variability_score += 30
        scores['variability'] = variability_score
        
        # 异常值得分
        outliers = quality_checks.get('outliers', {})
        outlier_score = 0
        if outliers.get('outlier_acceptable', False): outlier_score += 60
        if outliers.get('extreme_outlier_rate', 100) < 1: outlier_score += 40
        scores['outliers'] = outlier_score
        
        # 重复值得分
        duplicates = quality_checks.get('duplicates', {})
        duplicate_score = 0
        if duplicates.get('duplicates_acceptable', False): duplicate_score += 50
        if duplicates.get('no_single_value_dominance', False): duplicate_score += 50
        scores['duplicates'] = duplicate_score
        
        # 传感器性能得分
        sensor = quality_checks.get('sensor_performance', {})
        sensor_score = 50  # 默认分数
        if sensor.get('low_noise', True): sensor_score += 25
        if sensor.get('good_precision', True): sensor_score += 25
        scores['sensor_performance'] = sensor_score
        
        # 计算加权总分
        total_score = sum(scores[key] * weights[key] for key in scores.keys())
        
        # 质量等级判断
        if total_score >= 80:
            quality_level = "优秀"
            is_acceptable = True
            description = "数据质量优秀，完全适合进行AGP分析"
        elif total_score >= 65:
            quality_level = "良好"  
            is_acceptable = True
            description = "数据质量良好，适合进行AGP分析"
        elif total_score >= 50:
            quality_level = "一般"
            is_acceptable = True
            description = "数据质量一般，可进行AGP分析但结果可信度有限"
        else:
            quality_level = "不合格"
            is_acceptable = False
            description = "数据质量不合格，不建议进行AGP分析"
        
        return {
            'total_score': round(total_score, 1),
            'quality_level': quality_level,
            'is_acceptable': is_acceptable,
            'description': description,
            'component_scores': scores
        }
    
    def _generate_data_summary(self, data: pd.DataFrame) -> Dict:
        """生成数据摘要"""
        glucose_values = data['glucose'].dropna()
        
        return {
            'total_records': len(data),
            'valid_glucose_records': len(glucose_values),
            'time_span': {
                'start': data['timestamp'].min().isoformat(),
                'end': data['timestamp'].max().isoformat(),
                'days': (data['timestamp'].max() - data['timestamp'].min()).days
            },
            'glucose_summary': {
                'mean': round(glucose_values.mean(), 2),
                'median': round(glucose_values.median(), 2),
                'std': round(glucose_values.std(), 2),
                'min': round(glucose_values.min(), 2),
                'max': round(glucose_values.max(), 2),
                'cv': round((glucose_values.std() / glucose_values.mean()) * 100, 1)
            }
        }
    
    def _generate_recommendations(self, quality_checks: Dict) -> List[str]:
        """生成数据质量改善建议"""
        recommendations = []
        
        # 基于各项检查结果生成建议
        completeness = quality_checks.get('completeness', {})
        if not completeness.get('coverage_sufficient', True):
            recommendations.append("数据覆盖率不足，建议延长CGM佩戴时间或检查设备工作状态")
        
        if not completeness.get('days_sufficient', True):
            recommendations.append("数据天数不足，建议收集至少10-14天的CGM数据")
        
        continuity = quality_checks.get('continuity', {})
        if not continuity.get('gap_acceptable', True):
            recommendations.append("存在较长的数据缺失间隔，建议检查CGM设备连接状态")
        
        validity = quality_checks.get('validity', {})
        if not validity.get('range_valid', True):
            recommendations.append("存在超出生理范围的血糖值，建议检查传感器校准")
        
        if not validity.get('missing_acceptable', True):
            recommendations.append("缺失值过多，建议检查传感器贴附状态和设备电量")
        
        variability = quality_checks.get('variability', {})
        if not variability.get('variability_sufficient', True):
            recommendations.append("血糖变异性过低，可能存在传感器故障或数据异常")
        
        outliers = quality_checks.get('outliers', {})
        if not outliers.get('outlier_acceptable', True):
            recommendations.append("异常值较多，建议检查传感器精度和患者活动记录")
        
        duplicates = quality_checks.get('duplicates', {})
        if not duplicates.get('duplicates_acceptable', True):
            recommendations.append("连续重复值过多，可能存在传感器卡滞问题")
        
        if not recommendations:
            recommendations.append("数据质量良好，无需特殊处理")
        
        return recommendations
    
    def _generate_failed_assessment(self, error_message: str) -> Dict:
        """生成失败评估结果"""
        return {
            'overall_quality': {
                'total_score': 0,
                'quality_level': '评估失败',
                'is_acceptable': False,
                'description': f'数据质量评估失败: {error_message}',
                'component_scores': {}
            },
            'detailed_checks': {},
            'data_summary': {},
            'recommendations': [f'请检查数据格式和完整性: {error_message}'],
            'usable_for_analysis': False,
            'assessment_timestamp': datetime.now().isoformat(),
            'error': error_message
        }
    
    def generate_quality_report(self, assessment_result: Dict) -> str:
        """生成可读的质量评估报告"""
        if not assessment_result.get('usable_for_analysis', False):
            return f"""
=== CGM数据质量评估报告 ===

❌ 数据质量: {assessment_result['overall_quality']['quality_level']}
📊 质量得分: {assessment_result['overall_quality']['total_score']}/100

⚠️ 评估结果: {assessment_result['overall_quality']['description']}

🔧 改善建议:
""" + '\n'.join(f"   • {rec}" for rec in assessment_result.get('recommendations', []))

        summary = assessment_result.get('data_summary', {})
        overall = assessment_result['overall_quality']
        
        report = f"""
=== CGM数据质量评估报告 ===

✅ 数据质量: {overall['quality_level']}
📊 质量得分: {overall['total_score']}/100
📈 数据概况: 共{summary.get('total_records', 0)}个记录，{summary.get('time_span', {}).get('days', 0)}天

📋 血糖数据摘要:
   • 平均血糖: {summary.get('glucose_summary', {}).get('mean', 0):.1f} mmol/L
   • 血糖范围: {summary.get('glucose_summary', {}).get('min', 0):.1f} - {summary.get('glucose_summary', {}).get('max', 0):.1f} mmol/L
   • 变异系数: {summary.get('glucose_summary', {}).get('cv', 0):.1f}%

🎯 质量分析:
"""
        
        # 添加各组件得分
        scores = overall.get('component_scores', {})
        score_descriptions = {
            'completeness': '数据完整性',
            'continuity': '时间连续性', 
            'validity': '数据有效性',
            'variability': '数据变异性',
            'outliers': '异常值控制',
            'duplicates': '重复值控制',
            'sensor_performance': '传感器性能'
        }
        
        for key, desc in score_descriptions.items():
            if key in scores:
                score = scores[key]
                status = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
                report += f"   {status} {desc}: {score}/100\n"
        
        report += f"\n🔧 建议事项:\n"
        for rec in assessment_result.get('recommendations', []):
            report += f"   • {rec}\n"
        
        report += f"\n📊 分析建议: {overall['description']}"
        
        return report


def main():
    """测试数据质量评估器"""
    from CGM_AGP_Analyzer_Agent import CGMDataReader
    
    # 创建质量评估器
    quality_assessor = CGMDataQualityAssessor()
    
    # 创建示例数据进行测试
    print("🔬 创建测试数据...")
    
    # 生成14天的模拟CGM数据
    dates = pd.date_range('2024-01-01', periods=14*24*4, freq='15min')
    glucose_values = 7 + 2 * np.sin(2 * np.pi * np.arange(len(dates)) / (24*4)) + 0.5 * np.random.randn(len(dates))
    glucose_values = np.clip(glucose_values, 3.0, 20.0)
    
    # 模拟一些数据质量问题
    # 1. 随机缺失一些数据点
    missing_indices = np.random.choice(len(dates), size=int(len(dates) * 0.05), replace=False)
    glucose_values[missing_indices] = np.nan
    
    # 2. 添加一些异常值
    outlier_indices = np.random.choice(len(dates), size=10, replace=False)
    glucose_values[outlier_indices] = np.random.choice([1.0, 25.0], size=10)
    
    # 3. 添加一些连续重复值
    duplicate_start = 100
    glucose_values[duplicate_start:duplicate_start+20] = 8.5
    
    test_data = pd.DataFrame({
        'timestamp': dates,
        'glucose': glucose_values,
        'device_info': 'test'
    })
    
    print(f"📊 生成测试数据: {len(test_data)}条记录")
    
    # 进行质量评估
    print("\n🔍 开始数据质量评估...")
    assessment = quality_assessor.assess_data_quality(test_data, analysis_days=14)
    
    # 生成报告
    report = quality_assessor.generate_quality_report(assessment)
    print(report)
    
    # 保存详细评估结果
    import json
    with open(f"CGM_Quality_Assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w', encoding='utf-8') as f:
        json.dump(assessment, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 详细评估结果已保存")
    
    # 返回是否可用于分析
    return assessment['usable_for_analysis']

if __name__ == "__main__":
    main()