#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
血糖分析工具函数
包含94个专业指标的计算函数和数据质量评估函数
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import entropy
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def calculate_mage(glucose_values, threshold_sd=1.0):
    """计算MAGE (Mean Amplitude of Glycemic Excursions)"""
    if len(glucose_values) < 3:
        return 0
    
    mean_glucose = np.mean(glucose_values)
    std_glucose = np.std(glucose_values)
    threshold = threshold_sd * std_glucose
    
    peaks = []
    troughs = []
    
    for i in range(1, len(glucose_values) - 1):
        if glucose_values[i] > glucose_values[i-1] and glucose_values[i] > glucose_values[i+1]:
            peaks.append(glucose_values[i])
        elif glucose_values[i] < glucose_values[i-1] and glucose_values[i] < glucose_values[i+1]:
            troughs.append(glucose_values[i])
    
    excursions = []
    for peak in peaks:
        for trough in troughs:
            if abs(peak - trough) > threshold:
                excursions.append(abs(peak - trough))
    
    return np.mean(excursions) if excursions else 0

def calculate_lbgi(glucose_values):
    """计算LBGI (Low Blood Glucose Index)"""
    glucose_mg_dl = glucose_values * 18.018
    f_values = 1.509 * (np.log(glucose_mg_dl) ** 1.084 - 5.381)
    rl_values = np.where(f_values < 0, 10 * f_values ** 2, 0)
    return np.mean(rl_values)

def calculate_hbgi(glucose_values):
    """计算HBGI (High Blood Glucose Index)"""
    glucose_mg_dl = glucose_values * 18.018
    f_values = 1.509 * (np.log(glucose_mg_dl) ** 1.084 - 5.381)
    rh_values = np.where(f_values > 0, 10 * f_values ** 2, 0)
    return np.mean(rh_values)

def calculate_adrr(glucose_values):
    """计算ADRR (Average Daily Risk Range)"""
    if len(glucose_values) < 24:
        return 0
    
    # 假设每15分钟一个读数，按24小时分组
    readings_per_day = 96  # 24 * 4
    days = len(glucose_values) // readings_per_day
    
    if days < 1:
        return 0
    
    daily_risks = []
    for day in range(days):
        start_idx = day * readings_per_day
        end_idx = (day + 1) * readings_per_day
        daily_glucose = glucose_values[start_idx:end_idx]
        
        lbgi = calculate_lbgi(daily_glucose)
        hbgi = calculate_hbgi(daily_glucose)
        daily_risks.append(max(lbgi, hbgi) - min(lbgi, hbgi))
    
    return np.mean(daily_risks)

def calculate_j_index(mean_glucose, std_glucose):
    """计算J指数"""
    return 0.324 * (mean_glucose + std_glucose) ** 2

def calculate_modd(glucose_values, timestamps):
    """计算MODD (Mean of Daily Differences)"""
    df = pd.DataFrame({'timestamp': timestamps, 'glucose': glucose_values})
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['hour_minute'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M')
    
    daily_profiles = df.pivot_table(values='glucose', index='hour_minute', columns='date', aggfunc='mean')
    
    if daily_profiles.shape[1] < 2:
        return 0
    
    differences = []
    for i in range(daily_profiles.shape[1] - 1):
        day1 = daily_profiles.iloc[:, i].dropna()
        day2 = daily_profiles.iloc[:, i + 1].dropna()
        common_times = day1.index.intersection(day2.index)
        
        if len(common_times) > 0:
            diff = np.abs(day1[common_times] - day2[common_times])
            differences.extend(diff.values)
    
    return np.mean(differences) if differences else 0

def calculate_dawn_phenomenon(df):
    """计算黎明现象"""
    dawn_hours = df[df['hour'].between(4, 8)]
    pre_dawn_hours = df[df['hour'].between(2, 4)]
    
    if len(dawn_hours) > 0 and len(pre_dawn_hours) > 0:
        dawn_avg = dawn_hours['glucose'].mean()
        pre_dawn_avg = pre_dawn_hours['glucose'].mean()
        dawn_magnitude = dawn_avg - pre_dawn_avg
        dawn_detected = dawn_magnitude > 1.1  # >1.1 mmol/L 认为有黎明现象
        return dawn_magnitude, dawn_detected
    
    return 0, False

def calculate_night_stability(df):
    """计算夜间血糖稳定性"""
    night_data = df[(df['hour'] >= 23) | (df['hour'] < 6)]
    if len(night_data) > 0:
        return night_data['glucose'].std()
    return 0

def calculate_circadian_amplitude(glucose_values):
    """计算昼夜节律幅度"""
    return np.max(glucose_values) - np.min(glucose_values)

def find_peak_nadir_hours(df):
    """找到血糖峰值和低谷时间"""
    hourly_avg = df.groupby('hour')['glucose'].mean()
    peak_hour = hourly_avg.idxmax()
    nadir_hour = hourly_avg.idxmin()
    return str(peak_hour), str(nadir_hour)

def calculate_time_period_avg(df, start_hour, end_hour):
    """计算特定时间段的平均血糖"""
    period_data = df[df['hour'].between(start_hour, end_hour)]
    return period_data['glucose'].mean() if len(period_data) > 0 else 0

def calculate_meal_spike(df, start_hour, end_hour):
    """计算餐后血糖峰值和升幅"""
    period_data = df[df['hour'].between(start_hour, end_hour)]
    if len(period_data) > 0:
        max_glucose = period_data['glucose'].max()
        min_glucose = period_data['glucose'].min()
        spike = max_glucose - min_glucose
        return max_glucose, spike
    return 0, 0

def count_hypoglycemic_episodes(glucose_values, timestamps):
    """统计低血糖事件"""
    hypo_episodes = 0
    severe_hypo_episodes = 0
    
    in_hypo = False
    in_severe_hypo = False
    
    for glucose in glucose_values:
        if glucose < 3.9:
            if not in_hypo:
                hypo_episodes += 1
                in_hypo = True
        else:
            in_hypo = False
            
        if glucose < 3.0:
            if not in_severe_hypo:
                severe_hypo_episodes += 1
                in_severe_hypo = True
        else:
            in_severe_hypo = False
    
    return hypo_episodes, severe_hypo_episodes

def count_hyperglycemic_episodes(glucose_values, timestamps):
    """统计高血糖事件"""
    hyper_episodes = 0
    severe_hyper_episodes = 0
    
    in_hyper = False
    in_severe_hyper = False
    
    for glucose in glucose_values:
        if glucose > 10.0:
            if not in_hyper:
                hyper_episodes += 1
                in_hyper = True
        else:
            in_hyper = False
            
        if glucose > 13.9:
            if not in_severe_hyper:
                severe_hyper_episodes += 1
                in_severe_hyper = True
        else:
            in_severe_hyper = False
    
    return hyper_episodes, severe_hyper_episodes

def calculate_episode_durations(glucose_values, timestamps):
    """计算事件持续时间"""
    # 简化计算：假设每个事件持续时间
    hypo_count = np.sum(glucose_values < 3.9)
    hyper_count = np.sum(glucose_values > 10.0)
    
    avg_hypo_duration = hypo_count * 15  # 假设15分钟间隔
    avg_hyper_duration = hyper_count * 15
    
    return avg_hypo_duration, avg_hyper_duration

def calculate_total_episode_times(glucose_values, timestamps):
    """计算总的事件时间"""
    hypo_time = np.sum(glucose_values < 3.9) * 15  # 分钟
    hyper_time = np.sum(glucose_values > 10.0) * 15
    return hypo_time, hyper_time

def count_nocturnal_hypoglycemia(df):
    """统计夜间低血糖事件"""
    night_data = df[(df['hour'] >= 23) | (df['hour'] < 6)]
    return np.sum(night_data['glucose'] < 3.9)

def count_postprandial_hyperglycemia(df):
    """统计餐后高血糖事件"""
    # 餐后时间段：7-9, 12-14, 18-20
    meal_periods = [
        df[df['hour'].between(7, 9)],
        df[df['hour'].between(12, 14)],
        df[df['hour'].between(18, 20)]
    ]
    
    total_events = 0
    for period_data in meal_periods:
        total_events += np.sum(period_data['glucose'] > 10.0)
    
    return total_events

def calculate_glycemic_control_score(glucose_values):
    """计算血糖控制评分"""
    tir = np.mean((glucose_values >= 3.9) & (glucose_values <= 10.0)) * 100
    cv = (np.std(glucose_values) / np.mean(glucose_values)) * 100
    
    # 简化评分系统
    tir_score = min(tir / 70, 1.0)  # TIR目标70%
    cv_score = max(0, (36 - cv) / 36)  # CV目标<36%
    
    return (tir_score + cv_score) / 2

def calculate_glucose_exposure(glucose_values, threshold, above=True):
    """计算血糖暴露"""
    if above:
        exposure = np.sum(glucose_values[glucose_values > threshold] - threshold)
    else:
        exposure = np.sum(threshold - glucose_values[glucose_values < threshold])
    
    return exposure

# 复杂性分析函数
def calculate_fractal_dimension(glucose_values):
    """计算分形维数"""
    if len(glucose_values) < 10:
        return 1.5
    
    # 简化的Higuchi算法
    k_max = min(len(glucose_values) // 4, 20)
    lk_values = []
    
    for k in range(1, k_max + 1):
        lk = 0
        for m in range(k):
            if m + k < len(glucose_values):
                curve_length = 0
                for i in range(m, len(glucose_values) - k, k):
                    if i + k < len(glucose_values):
                        curve_length += abs(glucose_values[i + k] - glucose_values[i])
                lk += curve_length
        lk_values.append(lk / k)
    
    if len(lk_values) > 1:
        x = np.log(range(1, len(lk_values) + 1))
        y = np.log(lk_values)
        slope, _ = np.polyfit(x, y, 1)
        return 2 - slope
    
    return 1.5

def calculate_hurst_exponent(glucose_values):
    """计算Hurst指数"""
    if len(glucose_values) < 10:
        return 0.5
    
    try:
        n = len(glucose_values)
        rs_values = []
        
        for lag in range(2, min(n // 4, 20)):
            y = glucose_values[:n//lag*lag].reshape(-1, lag)
            rs_mean = []
            
            for segment in y:
                mean_segment = np.mean(segment)
                cumsum = np.cumsum(segment - mean_segment)
                r = np.max(cumsum) - np.min(cumsum)
                s = np.std(segment)
                if s > 0:
                    rs_mean.append(r / s)
            
            if rs_mean:
                rs_values.append(np.mean(rs_mean))
        
        if len(rs_values) > 1:
            x = np.log(range(2, len(rs_values) + 2))
            y = np.log(rs_values)
            slope, _ = np.polyfit(x, y, 1)
            return slope
    except:
        pass
    
    return 0.5

def calculate_shannon_entropy(glucose_values):
    """计算Shannon熵"""
    if len(glucose_values) < 5:
        return 5.0
    
    # 离散化血糖值
    bins = np.linspace(np.min(glucose_values), np.max(glucose_values), 20)
    hist, _ = np.histogram(glucose_values, bins=bins)
    probs = hist / np.sum(hist)
    probs = probs[probs > 0]  # 移除零概率
    
    return entropy(probs, base=2)

def calculate_approximate_entropy(glucose_values, m=2, r=None):
    """计算近似熵"""
    if len(glucose_values) < 10:
        return 0.8
    
    n = len(glucose_values)
    if r is None:
        r = 0.2 * np.std(glucose_values)
    
    def maxdist(xi, xj, n, m):
        return max([abs(ua - va) for ua, va in zip(xi, xj)])
    
    def phi(m):
        patterns = np.array([glucose_values[i:i + m] for i in range(n - m + 1)])
        c = np.zeros(n - m + 1)
        
        for i in range(n - m + 1):
            template_i = patterns[i]
            for j in range(n - m + 1):
                if maxdist(template_i, patterns[j], n, m) <= r:
                    c[i] += 1.0
        
        c = c / (n - m + 1.0)
        phi_m = np.mean([np.log(c[i]) for i in range(n - m + 1) if c[i] > 0])
        return phi_m
    
    try:
        return phi(m) - phi(m + 1)
    except:
        return 0.8

def calculate_sample_entropy(glucose_values, m=2, r=None):
    """计算样本熵"""
    if len(glucose_values) < 10:
        return 0.6
    
    n = len(glucose_values)
    if r is None:
        r = 0.2 * np.std(glucose_values)
    
    def maxdist(xi, xj):
        return max([abs(ua - va) for ua, va in zip(xi, xj)])
    
    def phi(m):
        patterns = np.array([glucose_values[i:i + m] for i in range(n - m + 1)])
        count = 0
        
        for i in range(n - m):
            template_i = patterns[i]
            for j in range(i + 1, n - m + 1):
                if maxdist(template_i, patterns[j]) <= r:
                    count += 1
        
        return count
    
    try:
        a = phi(m)
        b = phi(m + 1)
        if a > 0:
            return np.log(a / b) if b > 0 else np.log(a)
        return 0.6
    except:
        return 0.6

def calculate_lyapunov_exponent(glucose_values):
    """计算Lyapunov指数（简化版）"""
    if len(glucose_values) < 20:
        return -0.9
    
    try:
        # 简化的Wolf算法
        n = len(glucose_values)
        lyap_values = []
        
        for i in range(1, min(n - 5, 50)):
            distances = []
            for j in range(n - i):
                if j + i < n:
                    distances.append(abs(glucose_values[j + i] - glucose_values[j]))
            
            if distances and np.mean(distances) > 0:
                lyap_values.append(np.log(np.mean(distances)))
        
        if len(lyap_values) > 1:
            return np.mean(np.diff(lyap_values))
    except:
        pass
    
    return -0.9

def calculate_correlation_dimension(glucose_values):
    """计算关联维数（简化版）"""
    return 2.0  # 简化返回

def calculate_spectral_analysis(glucose_values):
    """计算频谱分析指标"""
    if len(glucose_values) < 10:
        return 0.5, 0.02
    
    try:
        # FFT分析
        fft = np.fft.fft(glucose_values - np.mean(glucose_values))
        power = np.abs(fft) ** 2
        freqs = np.fft.fftfreq(len(glucose_values))
        
        # 计算频谱熵
        power_normalized = power / np.sum(power)
        power_normalized = power_normalized[power_normalized > 0]
        spectral_entropy = entropy(power_normalized, base=2)
        
        # 主导频率
        dominant_freq = freqs[np.argmax(power[1:]) + 1]  # 跳过DC分量
        
        return spectral_entropy, abs(dominant_freq)
    except:
        return 0.5, 0.02

def calculate_complexity_score(glucose_values):
    """计算综合复杂性评分"""
    if len(glucose_values) < 10:
        return 0.5
    
    # 综合多个复杂性指标
    cv = (np.std(glucose_values) / np.mean(glucose_values)) * 100
    complexity = min(cv / 50, 1.0)  # 归一化
    
    return complexity

def evaluate_data_quality(df):
    """评估数据质量"""
    glucose_values = df['glucose'].values
    timestamps = df['timestamp'].values
    
    # 计算各项质量指标
    completeness = len(df)
    time_span = (df['timestamp'].max() - df['timestamp'].min()).days + 1
    
    # 数据连续性检查
    time_diffs = pd.to_datetime(df['timestamp']).diff().dt.total_seconds() / 60  # 分钟
    max_gap = time_diffs.max() if not time_diffs.isna().all() else 0
    
    # 数据有效性
    valid_readings = np.sum((glucose_values >= 2.0) & (glucose_values <= 25.0))
    validity_rate = (valid_readings / len(glucose_values)) * 100
    
    # 变异性
    cv = (np.std(glucose_values) / np.mean(glucose_values)) * 100
    
    # 异常值检测
    q1, q3 = np.percentile(glucose_values, [25, 75])
    iqr = q3 - q1
    outliers = np.sum((glucose_values < q1 - 1.5 * iqr) | (glucose_values > q3 + 1.5 * iqr))
    outlier_rate = (outliers / len(glucose_values)) * 100
    
    # 传感器健康状态模拟
    stuck_periods = detect_sensor_stuck(glucose_values)
    
    return {
        "数据质量评估": {
            "数据完整性": {
                "总读数": completeness,
                "监测天数": time_span,
                "每日平均读数": completeness / time_span,
                "完整性评级": "优秀" if completeness / time_span >= 80 else "良好" if completeness / time_span >= 60 else "需改善"
            },
            "数据连续性": {
                "最大时间间隔": f"{max_gap:.1f}分钟",
                "连续性评级": "优秀" if max_gap <= 60 else "良好" if max_gap <= 180 else "需改善"
            },
            "数据有效性": {
                "有效率": f"{validity_rate:.1f}%",
                "有效性评级": "优秀" if validity_rate >= 95 else "良好" if validity_rate >= 90 else "需改善"
            },
            "数据变异性": {
                "变异系数": f"{cv:.1f}%",
                "变异性评级": "正常" if cv <= 50 else "偏高"
            },
            "异常值检测": {
                "异常值比例": f"{outlier_rate:.1f}%",
                "异常值评级": "优秀" if outlier_rate <= 5 else "需关注"
            },
            "传感器健康": {
                "卡值检测": f"检测到{len(stuck_periods)}个疑似卡值时段",
                "传感器状态": "正常" if len(stuck_periods) <= 3 else "需关注"
            }
        },
        "质量总评": {
            "整体评级": get_overall_quality_rating(completeness/time_span, max_gap, validity_rate, outlier_rate),
            "建议": generate_quality_recommendations(completeness/time_span, max_gap, validity_rate, outlier_rate)
        }
    }

def detect_sensor_stuck(glucose_values, min_duration=3):
    """检测传感器卡值"""
    stuck_periods = []
    current_value = None
    start_idx = 0
    count = 0
    
    for i, value in enumerate(glucose_values):
        if value == current_value:
            count += 1
        else:
            if count >= min_duration:
                stuck_periods.append({
                    "start_index": start_idx,
                    "end_index": i - 1,
                    "duration_minutes": count * 15,  # 假设15分钟间隔
                    "stuck_value": current_value
                })
            current_value = value
            start_idx = i
            count = 1
    
    # 检查最后一个序列
    if count >= min_duration:
        stuck_periods.append({
            "start_index": start_idx,
            "end_index": len(glucose_values) - 1,
            "duration_minutes": count * 15,
            "stuck_value": current_value
        })
    
    return stuck_periods

def get_overall_quality_rating(readings_per_day, max_gap, validity_rate, outlier_rate):
    """获取整体质量评级"""
    score = 0
    
    # 完整性评分
    if readings_per_day >= 80:
        score += 25
    elif readings_per_day >= 60:
        score += 20
    else:
        score += 10
    
    # 连续性评分
    if max_gap <= 60:
        score += 25
    elif max_gap <= 180:
        score += 20
    else:
        score += 10
    
    # 有效性评分
    if validity_rate >= 95:
        score += 25
    elif validity_rate >= 90:
        score += 20
    else:
        score += 10
    
    # 异常值评分
    if outlier_rate <= 5:
        score += 25
    elif outlier_rate <= 10:
        score += 20
    else:
        score += 10
    
    if score >= 90:
        return "优秀"
    elif score >= 70:
        return "良好"
    elif score >= 50:
        return "可接受"
    else:
        return "需改善"

def generate_quality_recommendations(readings_per_day, max_gap, validity_rate, outlier_rate):
    """生成质量改善建议"""
    recommendations = []
    
    if readings_per_day < 60:
        recommendations.append("建议增加血糖监测频率，目标每日读数≥80次")
    
    if max_gap > 180:
        recommendations.append("检测到较长时间间隔，建议检查传感器连接状态")
    
    if validity_rate < 90:
        recommendations.append("发现无效读数较多，建议检查传感器校准")
    
    if outlier_rate > 10:
        recommendations.append("异常值较多，建议检查传感器位置和使用环境")
    
    if not recommendations:
        recommendations.append("数据质量良好，建议继续保持当前监测模式")
    
    return recommendations