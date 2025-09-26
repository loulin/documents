#!/usr/bin/env python3
"""
CGM集成模块 - 妊娠糖尿病风险评估
整合连续血糖监测数据，提供实时风险评估和预警
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class CGM_GDM_Integration:
    """CGM数据集成和GDM风险评估主类"""
    
    def __init__(self):
        self.pregnancy_glucose_targets = {
            'fasting': {
                'normal': 5.1,      # mmol/L
                'borderline': 5.5,
                'abnormal': 6.1
            },
            'post_meal_1h': {
                'normal': 10.0,     # mmol/L
                'borderline': 11.0,
                'abnormal': 12.0
            },
            'post_meal_2h': {
                'normal': 8.5,      # mmol/L
                'borderline': 9.5,
                'abnormal': 11.1
            },
            'bedtime': {
                'normal': 7.8,      # mmol/L
                'borderline': 8.5,
                'abnormal': 10.0
            }
        }
        
        self.gestational_adjustments = {
            'first_trimester': 1.0,    # 6-13周
            'second_trimester': 1.2,   # 14-27周
            'third_trimester': 1.5     # 28-40周
        }
    
    def process_cgm_data(self, cgm_raw_data: pd.DataFrame, gestational_week: int) -> Dict:
        """
        处理CGM原始数据
        
        Args:
            cgm_raw_data: CGM原始数据 (timestamp, glucose_value)
            gestational_week: 孕周
            
        Returns:
            处理后的CGM分析结果
        """
        
        print(f"📊 处理CGM数据 - 孕{gestational_week}周")
        
        # 数据清洗和预处理
        cleaned_data = self._clean_cgm_data(cgm_raw_data)
        
        # 基础统计分析
        basic_stats = self._calculate_basic_statistics(cleaned_data)
        
        # 血糖模式分析
        glucose_patterns = self._analyze_glucose_patterns(cleaned_data, gestational_week)
        
        # 风险评估
        risk_assessment = self._assess_gdm_risk(glucose_patterns, gestational_week)
        
        # 生成报告
        report = self._generate_cgm_report(basic_stats, glucose_patterns, risk_assessment)
        
        return {
            'basic_stats': basic_stats,
            'glucose_patterns': glucose_patterns,
            'risk_assessment': risk_assessment,
            'report': report,
            'gestational_week': gestational_week
        }
    
    def _clean_cgm_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """CGM数据清洗"""
        
        print("🧹 清洗CGM数据...")
        
        # 转换时间戳
        raw_data['timestamp'] = pd.to_datetime(raw_data['timestamp'])
        raw_data = raw_data.sort_values('timestamp')
        
        # 异常值处理
        glucose_col = 'glucose_value'
        
        # 移除明显异常值 (通常CGM范围 1.1-22.2 mmol/L)
        valid_range = (raw_data[glucose_col] >= 1.1) & (raw_data[glucose_col] <= 22.2)
        cleaned_data = raw_data[valid_range].copy()
        
        # 处理缺失值 - 线性插值
        cleaned_data[glucose_col] = cleaned_data[glucose_col].interpolate(method='linear')
        
        # 去除重复时间点
        cleaned_data = cleaned_data.drop_duplicates(subset=['timestamp'], keep='last')
        
        # 添加时间特征
        cleaned_data['hour'] = cleaned_data['timestamp'].dt.hour
        cleaned_data['day_of_week'] = cleaned_data['timestamp'].dt.dayofweek
        cleaned_data['date'] = cleaned_data['timestamp'].dt.date
        
        print(f"   ✅ 原始数据点: {len(raw_data)}")
        print(f"   ✅ 清洗后数据点: {len(cleaned_data)}")
        print(f"   ✅ 数据完整性: {len(cleaned_data)/len(raw_data)*100:.1f}%")
        
        return cleaned_data
    
    def _calculate_basic_statistics(self, data: pd.DataFrame) -> Dict:
        """计算基础统计指标"""
        
        glucose = data['glucose_value']
        
        stats = {
            'mean_glucose': glucose.mean(),
            'median_glucose': glucose.median(),
            'std_glucose': glucose.std(),
            'cv_glucose': (glucose.std() / glucose.mean()) * 100,  # 变异系数
            'min_glucose': glucose.min(),
            'max_glucose': glucose.max(),
            'glucose_range': glucose.max() - glucose.min(),
            'data_points': len(data),
            'monitoring_days': len(data['date'].unique())
        }
        
        # 时间范围内血糖分布
        stats['time_in_range'] = self._calculate_time_in_range(glucose)
        
        return stats
    
    def _calculate_time_in_range(self, glucose: pd.Series) -> Dict:
        """计算目标范围内时间(TIR)"""
        
        # 妊娠期目标范围
        target_range = (3.9, 7.8)  # mmol/L
        hypoglycemic = 3.9
        hyperglycemic_1 = 7.8
        hyperglycemic_2 = 10.0
        
        total_points = len(glucose)
        
        tir_stats = {
            'very_low': (glucose < 3.0).sum() / total_points * 100,          # <3.0
            'low': ((glucose >= 3.0) & (glucose < hypoglycemic)).sum() / total_points * 100,  # 3.0-3.9
            'target_range': ((glucose >= target_range[0]) & (glucose <= target_range[1])).sum() / total_points * 100,  # 3.9-7.8
            'high': ((glucose > hyperglycemic_1) & (glucose <= hyperglycemic_2)).sum() / total_points * 100,  # 7.8-10.0
            'very_high': (glucose > hyperglycemic_2).sum() / total_points * 100  # >10.0
        }
        
        return tir_stats
    
    def _analyze_glucose_patterns(self, data: pd.DataFrame, gestational_week: int) -> Dict:
        """分析血糖模式"""
        
        patterns = {}
        
        # 1. 黎明现象检测
        patterns['dawn_phenomenon'] = self._detect_dawn_phenomenon(data)
        
        # 2. 餐后血糖反应
        patterns['postprandial_response'] = self._analyze_postprandial_response(data)
        
        # 3. 夜间血糖稳定性
        patterns['overnight_stability'] = self._assess_overnight_stability(data)
        
        # 4. 血糖变异性分析
        patterns['glucose_variability'] = self._analyze_glucose_variability(data)
        
        # 5. 孕周特异性模式
        patterns['gestational_patterns'] = self._analyze_gestational_patterns(data, gestational_week)
        
        # 6. 日内血糖轮廓
        patterns['daily_profile'] = self._create_daily_glucose_profile(data)
        
        return patterns
    
    def _detect_dawn_phenomenon(self, data: pd.DataFrame) -> Dict:
        """检测黎明现象"""
        
        # 筛选凌晨3:00-7:00的数据
        dawn_data = data[(data['hour'] >= 3) & (data['hour'] <= 7)]
        
        if len(dawn_data) < 10:  # 数据不足
            return {'detected': False, 'reason': 'insufficient_data'}
        
        # 按日期分组分析
        daily_dawn = dawn_data.groupby('date')['glucose_value'].agg(['min', 'max', 'mean'])
        daily_dawn['rise'] = daily_dawn['max'] - daily_dawn['min']
        
        # 黎明现象判断标准
        significant_rises = daily_dawn['rise'] > 1.7  # mmol/L
        dawn_frequency = significant_rises.sum() / len(daily_dawn) * 100
        
        result = {
            'detected': dawn_frequency > 30,  # 30%以上的天数出现
            'frequency_percent': dawn_frequency,
            'average_rise': daily_dawn['rise'].mean(),
            'max_rise': daily_dawn['rise'].max(),
            'clinical_significance': self._classify_dawn_significance(daily_dawn['rise'].mean())
        }
        
        return result
    
    def _analyze_postprandial_response(self, data: pd.DataFrame) -> Dict:
        """分析餐后血糖反应"""
        
        # 定义餐时窗口
        meal_windows = {
            'breakfast': (7, 10),   # 7:00-10:00
            'lunch': (12, 15),      # 12:00-15:00  
            'dinner': (18, 21)      # 18:00-21:00
        }
        
        postprandial_analysis = {}
        
        for meal, (start_hour, end_hour) in meal_windows.items():
            meal_data = data[(data['hour'] >= start_hour) & (data['hour'] < end_hour)]
            
            if len(meal_data) < 5:
                postprandial_analysis[meal] = {'status': 'insufficient_data'}
                continue
            
            # 分析餐后血糖峰值
            daily_peaks = meal_data.groupby('date')['glucose_value'].max()
            
            analysis = {
                'average_peak': daily_peaks.mean(),
                'max_peak': daily_peaks.max(),
                'peak_frequency_above_target': (daily_peaks > self.pregnancy_glucose_targets['post_meal_1h']['normal']).sum(),
                'total_meal_days': len(daily_peaks),
                'abnormal_percentage': (daily_peaks > self.pregnancy_glucose_targets['post_meal_1h']['normal']).sum() / len(daily_peaks) * 100
            }
            
            # 风险分类
            if analysis['abnormal_percentage'] > 50:
                analysis['risk_level'] = 'high'
            elif analysis['abnormal_percentage'] > 25:
                analysis['risk_level'] = 'moderate'
            else:
                analysis['risk_level'] = 'low'
            
            postprandial_analysis[meal] = analysis
        
        return postprandial_analysis
    
    def _assess_overnight_stability(self, data: pd.DataFrame) -> Dict:
        """评估夜间血糖稳定性"""
        
        # 夜间时段定义 (22:00-06:00)
        overnight_data = data[((data['hour'] >= 22) | (data['hour'] <= 6))]
        
        if len(overnight_data) < 20:
            return {'status': 'insufficient_data'}
        
        # 按日期分组分析夜间血糖
        daily_overnight = overnight_data.groupby('date')['glucose_value'].agg([
            'min', 'max', 'mean', 'std'
        ])
        daily_overnight['range'] = daily_overnight['max'] - daily_overnight['min']
        
        stability_metrics = {
            'average_overnight_glucose': daily_overnight['mean'].mean(),
            'average_glucose_range': daily_overnight['range'].mean(),
            'coefficient_of_variation': daily_overnight['std'].mean() / daily_overnight['mean'].mean() * 100,
            'stable_nights_percentage': (daily_overnight['range'] <= 2.0).sum() / len(daily_overnight) * 100,
            'unstable_nights_percentage': (daily_overnight['range'] > 3.0).sum() / len(daily_overnight) * 100
        }
        
        # 稳定性评级
        if stability_metrics['stable_nights_percentage'] > 80:
            stability_metrics['stability_grade'] = 'excellent'
        elif stability_metrics['stable_nights_percentage'] > 60:
            stability_metrics['stability_grade'] = 'good'
        elif stability_metrics['stable_nights_percentage'] > 40:
            stability_metrics['stability_grade'] = 'fair'
        else:
            stability_metrics['stability_grade'] = 'poor'
        
        return stability_metrics
    
    def _analyze_glucose_variability(self, data: pd.DataFrame) -> Dict:
        """分析血糖变异性"""
        
        glucose = data['glucose_value']
        
        # 多种变异性指标
        variability_metrics = {
            'standard_deviation': glucose.std(),
            'coefficient_of_variation': (glucose.std() / glucose.mean()) * 100,
            'mean_amplitude_of_glycemic_excursions': self._calculate_mage(glucose),
            'continuous_overall_net_glycemic_action': self._calculate_conga(glucose),
            'glycemic_risk_assessment_diabetes_equation': self._calculate_grade(glucose)
        }
        
        # 变异性风险分层
        cv = variability_metrics['coefficient_of_variation']
        if cv < 36:
            variability_metrics['variability_risk'] = 'low'
        elif cv < 50:
            variability_metrics['variability_risk'] = 'moderate'
        else:
            variability_metrics['variability_risk'] = 'high'
        
        return variability_metrics
    
    def _calculate_mage(self, glucose: pd.Series) -> float:
        """计算平均血糖漂移幅度(MAGE)"""
        
        # 简化MAGE计算
        glucose_diff = glucose.diff().abs()
        mean_glucose = glucose.mean()
        std_glucose = glucose.std()
        
        # 定义显著变化阈值 (1个标准差)
        significant_changes = glucose_diff[glucose_diff > std_glucose]
        
        if len(significant_changes) == 0:
            return 0.0
        
        return significant_changes.mean()
    
    def _calculate_conga(self, glucose: pd.Series, n: int = 4) -> float:
        """计算连续净血糖作用值(CONGA)"""
        
        # CONGA-n: 每n小时血糖差值的标准差
        # 简化计算，假设每15分钟一个数据点
        step = n * 4  # n小时对应的数据点数
        
        if len(glucose) <= step:
            return 0.0
        
        differences = []
        for i in range(len(glucose) - step):
            diff = glucose.iloc[i + step] - glucose.iloc[i]
            differences.append(diff)
        
        return np.std(differences) if differences else 0.0
    
    def _calculate_grade(self, glucose: pd.Series) -> float:
        """计算血糖风险评估糖尿病方程(GRADE)"""
        
        # GRADE评分简化计算
        glucose_mg_dl = glucose * 18.018  # 转换为mg/dL
        
        # 计算每个血糖值的风险评分
        risk_scores = []
        for g in glucose_mg_dl:
            if g <= 180:
                risk = 425 * (np.log(g)**1.084 - 5.381)**2
            else:
                risk = 425 * (np.log(g)**1.084 - 5.381)**2
            risk_scores.append(risk)
        
        return np.mean(risk_scores)
    
    def _analyze_gestational_patterns(self, data: pd.DataFrame, gestational_week: int) -> Dict:
        """分析孕周特异性血糖模式"""
        
        # 确定妊娠期
        if gestational_week <= 13:
            trimester = 'first'
        elif gestational_week <= 27:
            trimester = 'second'
        else:
            trimester = 'third'
        
        # 孕期特异性分析
        gestational_analysis = {
            'current_trimester': trimester,
            'gestational_week': gestational_week,
            'trimester_adjustment_factor': self.gestational_adjustments.get(f'{trimester}_trimester', 1.0)
        }
        
        # 根据孕期调整目标值
        adjusted_targets = {}
        for target_type, values in self.pregnancy_glucose_targets.items():
            adjusted_targets[target_type] = {
                key: value * gestational_analysis['trimester_adjustment_factor']
                for key, value in values.items()
            }
        
        gestational_analysis['adjusted_targets'] = adjusted_targets
        
        # 孕期特异性风险评估
        glucose = data['glucose_value']
        
        # 根据孕期调整的目标范围符合率
        target_adherence = {}
        for target_type, targets in adjusted_targets.items():
            if target_type == 'fasting':
                # 空腹血糖 (假设6:00-8:00为空腹时段)
                fasting_data = data[(data['hour'] >= 6) & (data['hour'] <= 8)]['glucose_value']
                if len(fasting_data) > 0:
                    target_adherence[target_type] = (fasting_data <= targets['normal']).mean() * 100
            elif target_type.startswith('post_meal'):
                # 餐后血糖分析在前面已完成
                continue
            
        gestational_analysis['target_adherence'] = target_adherence
        
        return gestational_analysis
    
    def _create_daily_glucose_profile(self, data: pd.DataFrame) -> Dict:
        """创建日内血糖轮廓"""
        
        # 按小时分组计算平均血糖
        hourly_profile = data.groupby('hour')['glucose_value'].agg([
            'mean', 'std', 'min', 'max', 'count'
        ]).round(2)
        
        # 识别高血糖风险时段
        risk_hours = hourly_profile[hourly_profile['mean'] > 7.8].index.tolist()
        
        # 血糖波动最大的时段
        peak_variability_hour = hourly_profile['std'].idxmax()
        
        profile_analysis = {
            'hourly_profile': hourly_profile.to_dict(),
            'risk_hours': risk_hours,
            'peak_variability_hour': int(peak_variability_hour),
            'overall_pattern': self._classify_daily_pattern(hourly_profile)
        }
        
        return profile_analysis
    
    def _classify_daily_pattern(self, hourly_profile: pd.DataFrame) -> str:
        """分类日内血糖模式"""
        
        morning_avg = hourly_profile.loc[6:11, 'mean'].mean()    # 早晨
        afternoon_avg = hourly_profile.loc[12:17, 'mean'].mean() # 下午
        evening_avg = hourly_profile.loc[18:23, 'mean'].mean()   # 晚上
        
        max_period = max([
            ('morning', morning_avg),
            ('afternoon', afternoon_avg), 
            ('evening', evening_avg)
        ], key=lambda x: x[1])
        
        return f"{max_period[0]}_predominant"
    
    def _assess_gdm_risk(self, patterns: Dict, gestational_week: int) -> Dict:
        """基于CGM模式评估GDM风险"""
        
        risk_factors = []
        risk_score = 0
        
        # 1. 黎明现象风险
        if patterns['dawn_phenomenon'].get('detected', False):
            risk_factors.append('dawn_phenomenon')
            risk_score += 15
        
        # 2. 餐后血糖风险
        postprandial = patterns['postprandial_response']
        high_risk_meals = sum(1 for meal_data in postprandial.values() 
                             if isinstance(meal_data, dict) and meal_data.get('risk_level') == 'high')
        
        if high_risk_meals >= 2:
            risk_factors.append('multiple_postprandial_spikes')
            risk_score += 20
        elif high_risk_meals == 1:
            risk_factors.append('single_postprandial_spike')
            risk_score += 10
        
        # 3. 夜间不稳定
        overnight = patterns['overnight_stability']
        if isinstance(overnight, dict) and overnight.get('stability_grade') in ['fair', 'poor']:
            risk_factors.append('overnight_instability')
            risk_score += 10
        
        # 4. 血糖变异性
        variability = patterns['glucose_variability']
        if variability['variability_risk'] == 'high':
            risk_factors.append('high_glucose_variability')
            risk_score += 15
        elif variability['variability_risk'] == 'moderate':
            risk_factors.append('moderate_glucose_variability')
            risk_score += 8
        
        # 5. 孕周调整
        trimester_multiplier = self.gestational_adjustments.get(
            f"{'first' if gestational_week <= 13 else 'second' if gestational_week <= 27 else 'third'}_trimester", 1.0
        )
        risk_score = int(risk_score * trimester_multiplier)
        
        # 风险分层
        if risk_score >= 40:
            risk_level = 'high'
        elif risk_score >= 20:
            risk_level = 'moderate'
        elif risk_score >= 10:
            risk_level = 'mild'
        else:
            risk_level = 'low'
        
        risk_assessment = {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'gestational_week': gestational_week,
            'recommendations': self._generate_risk_recommendations(risk_level, risk_factors)
        }
        
        return risk_assessment
    
    def _generate_risk_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """生成风险管理建议"""
        
        recommendations = []
        
        # 基础建议
        if risk_level == 'high':
            recommendations.extend([
                "立即联系产科医生进行评估",
                "考虑进行标准OGTT确诊",
                "开始密集的血糖监测",
                "咨询内分泌科医生",
                "营养师制定孕期饮食计划"
            ])
        elif risk_level == 'moderate':
            recommendations.extend([
                "增加血糖监测频率",
                "预约产科医生复查",
                "注意饮食控制和体重管理",
                "考虑提前进行GDM筛查"
            ])
        elif risk_level == 'mild':
            recommendations.extend([
                "继续规律血糖监测",
                "维持健康的饮食习惯",
                "适当的孕期运动",
                "按时产检"
            ])
        else:  # low risk
            recommendations.extend([
                "保持当前良好的血糖控制",
                "继续健康的生活方式",
                "定期产检和血糖监测"
            ])
        
        # 针对性建议
        for factor in risk_factors:
            if factor == 'dawn_phenomenon':
                recommendations.append("考虑调整晚餐时间和内容，避免睡前高碳水化合物")
            elif 'postprandial' in factor:
                recommendations.append("控制餐后血糖：少量多餐，餐后适度活动")
            elif factor == 'overnight_instability':
                recommendations.append("注意睡眠质量，避免夜间低血糖")
            elif 'variability' in factor:
                recommendations.append("规律作息，稳定的饮食时间和内容")
        
        return recommendations
    
    def _generate_cgm_report(self, basic_stats: Dict, patterns: Dict, risk_assessment: Dict) -> str:
        """生成CGM分析报告"""
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          CGM血糖监测分析报告                                  ║
║                       妊娠糖尿病风险评估系统                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 基础统计信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   监测天数: {basic_stats['monitoring_days']} 天
   数据点数: {basic_stats['data_points']} 个
   平均血糖: {basic_stats['mean_glucose']:.1f} mmol/L
   血糖范围: {basic_stats['min_glucose']:.1f} - {basic_stats['max_glucose']:.1f} mmol/L
   变异系数: {basic_stats['cv_glucose']:.1f}%

🎯 目标范围时间(TIR)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   目标范围(3.9-7.8): {basic_stats['time_in_range']['target_range']:.1f}%
   高血糖时间(>7.8):  {basic_stats['time_in_range']['high'] + basic_stats['time_in_range']['very_high']:.1f}%
   低血糖时间(<3.9):  {basic_stats['time_in_range']['low'] + basic_stats['time_in_range']['very_low']:.1f}%

🌅 血糖模式分析
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   黎明现象: {'检出' if patterns['dawn_phenomenon'].get('detected') else '未检出'}
   夜间稳定性: {patterns['overnight_stability'].get('stability_grade', '数据不足')}
   血糖变异风险: {patterns['glucose_variability']['variability_risk']}

⚠️  风险评估结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   综合风险等级: {risk_assessment['risk_level'].upper()}
   风险评分: {risk_assessment['risk_score']}/100
   孕周: {risk_assessment['gestational_week']} 周

💡 专业建议
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        for i, recommendation in enumerate(risk_assessment['recommendations'], 1):
            report += f"   {i}. {recommendation}\n"
        
        report += f"""
📅 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💻 系统版本: CGM-GDM Integration v1.0

注：本报告仅供临床参考，最终诊断需结合临床表现和其他检查结果。
"""
        
        return report
    
    def _classify_dawn_significance(self, average_rise: float) -> str:
        """分类黎明现象的临床意义"""
        if average_rise > 2.8:
            return 'severe'
        elif average_rise > 1.7:
            return 'moderate'
        elif average_rise > 1.0:
            return 'mild'
        else:
            return 'minimal'

class CGM_DataSimulator:
    """CGM数据模拟器 - 用于测试和演示"""
    
    def __init__(self):
        np.random.seed(42)
    
    def generate_pregnancy_cgm_data(self, days: int = 14, gestational_week: int = 24) -> pd.DataFrame:
        """生成妊娠期CGM模拟数据"""
        
        print(f"🔄 生成{days}天妊娠期CGM模拟数据 (孕{gestational_week}周)")
        
        # 时间序列
        start_date = datetime.now() - timedelta(days=days)
        timestamps = pd.date_range(start=start_date, periods=days*96, freq='15T')  # 每15分钟一个点
        
        glucose_values = []
        
        for i, timestamp in enumerate(timestamps):
            hour = timestamp.hour
            
            # 基础血糖水平（根据孕周调整）
            if gestational_week <= 13:
                base_glucose = 5.2
            elif gestational_week <= 27:
                base_glucose = 5.5
            else:
                base_glucose = 5.8
            
            # 日内血糖变化模式
            daily_pattern = self._get_daily_glucose_pattern(hour)
            
            # 添加噪声和个体变异
            noise = np.random.normal(0, 0.3)
            
            # 模拟特殊情况（如GDM高风险）
            if gestational_week > 24 and np.random.random() < 0.15:  # 15%概率出现高血糖
                glucose = base_glucose + daily_pattern + 2.0 + noise
            else:
                glucose = base_glucose + daily_pattern + noise
            
            # 确保在合理范围内
            glucose = max(3.0, min(15.0, glucose))
            glucose_values.append(glucose)
        
        # 创建DataFrame
        cgm_data = pd.DataFrame({
            'timestamp': timestamps,
            'glucose_value': glucose_values
        })
        
        print(f"   ✅ 生成数据点: {len(cgm_data)}")
        print(f"   ✅ 时间跨度: {cgm_data['timestamp'].min()} 至 {cgm_data['timestamp'].max()}")
        print(f"   ✅ 血糖范围: {min(glucose_values):.1f} - {max(glucose_values):.1f} mmol/L")
        
        return cgm_data
    
    def _get_daily_glucose_pattern(self, hour: int) -> float:
        """获取日内血糖变化模式"""
        
        # 模拟正常的日内血糖波动
        patterns = {
            # 夜间 (0-5)
            **{h: -0.5 for h in range(0, 6)},
            # 黎明 (6-8) - 轻微上升
            6: 0.0, 7: 0.3, 8: 0.5,
            # 早餐后 (9-11)
            9: 1.2, 10: 1.8, 11: 1.0,
            # 午前 (12)
            12: 0.2,
            # 午餐后 (13-15)
            13: 1.5, 14: 2.0, 15: 1.2,
            # 下午 (16-17)
            16: 0.5, 17: 0.3,
            # 晚餐后 (18-20)
            18: 1.8, 19: 2.2, 20: 1.5,
            # 晚间 (21-23)
            21: 0.8, 22: 0.2, 23: -0.2
        }
        
        return patterns.get(hour, 0.0)

# 主函数和使用示例
if __name__ == "__main__":
    print("🚀 启动CGM-GDM集成分析系统")
    print("=" * 80)
    
    # 创建CGM集成分析器
    cgm_analyzer = CGM_GDM_Integration()
    
    # 创建数据模拟器
    data_simulator = CGM_DataSimulator()
    
    # 模拟不同孕周的CGM数据
    gestational_weeks = [12, 24, 32]
    
    for week in gestational_weeks:
        print(f"\n📊 分析孕{week}周CGM数据")
        print("-" * 50)
        
        # 生成模拟数据
        cgm_data = data_simulator.generate_pregnancy_cgm_data(
            days=14, 
            gestational_week=week
        )
        
        # 执行CGM分析
        analysis_result = cgm_analyzer.process_cgm_data(cgm_data, week)
        
        # 显示分析报告
        print(analysis_result['report'])
        
        # 风险评估总结
        risk = analysis_result['risk_assessment']
        print(f"🎯 孕{week}周风险评估:")
        print(f"   风险等级: {risk['risk_level']}")
        print(f"   风险评分: {risk['risk_score']}/100")
        print(f"   主要风险因素: {', '.join(risk['risk_factors']) if risk['risk_factors'] else '无'}")
    
    print(f"\n✅ CGM-GDM集成分析完成")
    print("💡 该系统可为临床医生提供:")
    print("   📈 实时血糖模式识别")
    print("   ⚠️  早期GDM风险预警")
    print("   🎯 个体化管理建议")
    print("   📊 孕期血糖趋势分析")