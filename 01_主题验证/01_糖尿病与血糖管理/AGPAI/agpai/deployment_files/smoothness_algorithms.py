"""
AGP血糖平滑度计算算法集合
包含多种平滑度计算方法的Python实现
"""

import numpy as np
import pandas as pd
from scipy import signal, stats
from scipy.fft import fft, fftfreq
import warnings
warnings.filterwarnings('ignore')

class AGPSmoothness:
    """AGP血糖平滑度计算类"""
    
    def __init__(self, glucose_data, timestamps=None):
        """
        初始化
        glucose_data: 血糖数据数组
        timestamps: 时间戳数组（可选）
        """
        self.glucose = np.array(glucose_data)
        self.timestamps = timestamps
        self.n = len(self.glucose)
        
    def first_order_difference_smoothness(self):
        """一阶差分平滑度方法"""
        methods = {}
        
        # 1. 连续差值变异系数
        diff_values = np.diff(self.glucose)
        if len(diff_values) > 0 and np.mean(np.abs(diff_values)) != 0:
            methods['cv_diff'] = np.std(diff_values) / np.mean(np.abs(diff_values))
        else:
            methods['cv_diff'] = 0
            
        # 2. 平均绝对差值 (MAD)
        methods['mad'] = np.mean(np.abs(diff_values)) if len(diff_values) > 0 else 0
        
        # 3. 标准化一阶差分
        if np.mean(self.glucose) != 0:
            methods['norm_diff'] = np.std(diff_values) / np.mean(self.glucose)
        else:
            methods['norm_diff'] = 0
            
        return methods
    
    def second_order_difference_smoothness(self):
        """二阶差分平滑度方法"""
        methods = {}
        
        if self.n >= 3:
            # 二阶差分 (加速度)
            second_diff = self.glucose[:-2] - 2*self.glucose[1:-1] + self.glucose[2:]
            
            # 1. 二阶导数方差
            methods['second_diff_var'] = np.var(second_diff)
            
            # 2. 曲率平滑指数
            mean_curvature = np.mean(np.abs(second_diff))
            methods['curvature_smoothness'] = 1 / (1 + mean_curvature)
        else:
            methods['second_diff_var'] = 0
            methods['curvature_smoothness'] = 1
            
        return methods
    
    def moving_average_smoothness(self, window=5):
        """移动平均平滑度方法"""
        methods = {}
        
        # 计算移动平均
        if self.n >= window:
            # 使用pandas计算移动平均，更稳健
            moving_avg = pd.Series(self.glucose).rolling(window=window, center=True).mean().values
            
            # 去除NaN值
            valid_idx = ~np.isnan(moving_avg)
            if np.sum(valid_idx) > 0:
                glucose_valid = self.glucose[valid_idx]
                moving_avg_valid = moving_avg[valid_idx]
                
                # 1. 移动平均偏差
                methods['mad_ma'] = np.mean(np.abs(glucose_valid - moving_avg_valid))
                
                # 2. 趋势一致性指数
                if len(glucose_valid) > 1:
                    correlation = np.corrcoef(glucose_valid, moving_avg_valid)[0, 1]
                    methods['trend_consistency'] = correlation if not np.isnan(correlation) else 0
                else:
                    methods['trend_consistency'] = 1
            else:
                methods['mad_ma'] = 0
                methods['trend_consistency'] = 1
        else:
            methods['mad_ma'] = 0
            methods['trend_consistency'] = 1
            
        return methods
    
    def frequency_domain_smoothness(self):
        """频域平滑度方法"""
        methods = {}
        
        if self.n >= 8:  # FFT需要足够的数据点
            # 计算FFT
            fft_vals = fft(self.glucose)
            freqs = fftfreq(self.n)
            power = np.abs(fft_vals)**2
            
            # 只考虑正频率
            pos_freqs = freqs[:self.n//2]
            pos_power = power[:self.n//2]
            
            if len(pos_power) > 1:
                # 1. 高频能量比例
                total_energy = np.sum(pos_power)
                if total_energy > 0:
                    # 定义高频为后50%的频率
                    high_freq_energy = np.sum(pos_power[len(pos_power)//2:])
                    methods['high_freq_ratio'] = high_freq_energy / total_energy
                else:
                    methods['high_freq_ratio'] = 0
                
                # 2. 频谱集中度 (越小越集中在低频)
                if np.sum(pos_power) > 0:
                    methods['spectral_centroid'] = np.sum(pos_freqs * pos_power) / np.sum(pos_power)
                else:
                    methods['spectral_centroid'] = 0
                
                # 3. 谱平坦度 (越接近0越平滑)
                if np.all(pos_power > 0):
                    geometric_mean = stats.gmean(pos_power)
                    arithmetic_mean = np.mean(pos_power)
                    methods['spectral_flatness'] = geometric_mean / arithmetic_mean if arithmetic_mean > 0 else 0
                else:
                    methods['spectral_flatness'] = 0
            else:
                methods['high_freq_ratio'] = 0
                methods['spectral_centroid'] = 0
                methods['spectral_flatness'] = 0
        else:
            methods['high_freq_ratio'] = 0
            methods['spectral_centroid'] = 0
            methods['spectral_flatness'] = 0
            
        return methods
    
    def statistical_smoothness(self):
        """统计学平滑度方法"""
        methods = {}
        
        # 1. 自相关衰减 (lag=1的自相关系数)
        if self.n > 2:
            autocorr = np.correlate(self.glucose - np.mean(self.glucose), 
                                   self.glucose - np.mean(self.glucose), mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            if len(autocorr) > 1 and autocorr[0] != 0:
                normalized_autocorr = autocorr / autocorr[0]
                if len(normalized_autocorr) > 1:
                    lag1_autocorr = abs(normalized_autocorr[1])
                    methods['autocorr_decay'] = -np.log(lag1_autocorr) if lag1_autocorr > 0 else 0
                else:
                    methods['autocorr_decay'] = 0
            else:
                methods['autocorr_decay'] = 0
        else:
            methods['autocorr_decay'] = 0
        
        # 2. 近似熵 (ApEn)
        methods['approximate_entropy'] = self._approximate_entropy(self.glucose)
        
        return methods
    
    def _approximate_entropy(self, data, m=2, r=None):
        """计算近似熵"""
        if r is None:
            r = 0.2 * np.std(data)
        
        N = len(data)
        if N < m + 1:
            return 0
        
        def _maxdist(xi, xj, m):
            return max([abs(ua - va) for ua, va in zip(xi, xj)])
        
        def _phi(m):
            patterns = np.array([data[i:i + m] for i in range(N - m + 1)])
            phi_list = []
            
            for i in range(N - m + 1):
                template = patterns[i]
                matches = sum([1 for pattern in patterns if _maxdist(template, pattern, m) <= r])
                if matches > 0:
                    phi_list.append(np.log(matches / (N - m + 1)))
            
            return np.mean(phi_list) if phi_list else 0
        
        return abs(_phi(m) - _phi(m + 1))
    
    def glucose_specific_smoothness(self):
        """血糖特异性平滑度方法"""
        methods = {}
        
        # 1. 血糖平滑指数 (基于MAGE)
        mage = self._calculate_mage()
        mean_glucose = np.mean(self.glucose)
        if mean_glucose > 0:
            methods['glucose_smoothness_index'] = 1 - (mage / mean_glucose)
        else:
            methods['glucose_smoothness_index'] = 0
        
        # 2. 连续血糖平滑度 (基于CONGA)
        conga = self._calculate_conga()
        methods['continuous_glucose_smoothness'] = 1 / (1 + conga)
        
        # 3. 变异系数倒数
        cv = np.std(self.glucose) / mean_glucose if mean_glucose > 0 else 0
        methods['cv_inverse'] = 1 / cv if cv > 0 else float('inf')
        
        return methods
    
    def _calculate_mage(self):
        """计算MAGE (Mean Amplitude of Glycemic Excursions)"""
        if self.n < 3:
            return 0
        
        # 找到所有峰值和谷值
        peaks, _ = signal.find_peaks(self.glucose)
        valleys, _ = signal.find_peaks(-self.glucose)
        
        # 合并并排序所有转折点
        turning_points = np.sort(np.concatenate([peaks, valleys]))
        
        if len(turning_points) < 2:
            return 0
        
        # 计算转折点之间的差值
        glucose_at_turns = self.glucose[turning_points]
        excursions = np.abs(np.diff(glucose_at_turns))
        
        # 只考虑大于1SD的波动
        sd = np.std(self.glucose)
        significant_excursions = excursions[excursions > sd]
        
        return np.mean(significant_excursions) if len(significant_excursions) > 0 else 0
    
    def _calculate_conga(self, hours=1):
        """计算CONGA (Continuous Overlapping Net Glycemic Action)"""
        # 假设数据每5分钟一个点，1小时=12个点
        lag = max(1, int(hours * 12))
        
        if self.n <= lag:
            return 0
        
        differences = []
        for i in range(self.n - lag):
            diff = self.glucose[i + lag] - self.glucose[i]
            differences.append(diff)
        
        return np.std(differences) if differences else 0
    
    def agp_specific_smoothness(self, percentiles=[25, 50, 75]):
        """AGP特异性平滑度"""
        methods = {}
        
        # 模拟24小时AGP数据 (假设按小时统计)
        if self.n >= 24:
            # 重新整理为24小时格式
            hours = 24
            hourly_glucose = []
            
            for h in range(hours):
                start_idx = int(h * self.n / hours)
                end_idx = int((h + 1) * self.n / hours)
                if end_idx > start_idx:
                    hourly_glucose.append(self.glucose[start_idx:end_idx])
                else:
                    hourly_glucose.append([self.glucose[start_idx]])
            
            # 计算每小时的分位数
            hourly_percentiles = {}
            for p in percentiles:
                hourly_percentiles[p] = [np.percentile(hour_data, p) for hour_data in hourly_glucose]
            
            # 1. 分位数带平滑度
            iqr_widths = np.array(hourly_percentiles[75]) - np.array(hourly_percentiles[25])
            methods['quantile_band_smoothness'] = 1 - np.var(iqr_widths) / np.mean(iqr_widths)**2 if np.mean(iqr_widths) > 0 else 0
            
            # 2. 中位数曲线平滑度
            median_curve = np.array(hourly_percentiles[50])
            median_smoothness = self._calculate_curve_smoothness(median_curve)
            methods['median_curve_smoothness'] = median_smoothness
            
            # 3. 百分位线一致性
            correlations = []
            for i, p1 in enumerate(percentiles):
                for j, p2 in enumerate(percentiles):
                    if i < j:
                        corr = np.corrcoef(hourly_percentiles[p1], hourly_percentiles[p2])[0, 1]
                        if not np.isnan(corr):
                            correlations.append(corr)
            
            methods['percentile_consistency'] = np.mean(correlations) if correlations else 0
        else:
            methods['quantile_band_smoothness'] = 0
            methods['median_curve_smoothness'] = 0
            methods['percentile_consistency'] = 0
        
        return methods
    
    def _calculate_curve_smoothness(self, curve):
        """计算曲线平滑度"""
        if len(curve) < 3:
            return 1
        
        # 计算曲率
        dx = np.diff(curve)
        ddx = np.diff(dx)
        
        # 平均曲率
        mean_curvature = np.mean(np.abs(ddx))
        return 1 / (1 + mean_curvature)
    
    def comprehensive_smoothness_score(self):
        """综合平滑度评分"""
        # 计算所有类型的平滑度
        first_order = self.first_order_difference_smoothness()
        second_order = self.second_order_difference_smoothness()
        moving_avg = self.moving_average_smoothness()
        frequency = self.frequency_domain_smoothness()
        statistical = self.statistical_smoothness()
        glucose_specific = self.glucose_specific_smoothness()
        agp_specific = self.agp_specific_smoothness()
        
        # 权重设置 (可以根据临床需要调整)
        weights = {
            'cv_diff': 0.15,           # 一阶差分变异
            'curvature_smoothness': 0.15,  # 曲率平滑度
            'trend_consistency': 0.10,     # 趋势一致性
            'high_freq_ratio': 0.10,      # 高频比例 (取反)
            'glucose_smoothness_index': 0.20,  # 血糖平滑指数
            'median_curve_smoothness': 0.15,   # 中位数曲线平滑度
            'autocorr_decay': 0.15        # 自相关衰减
        }
        
        # 标准化处理 (将不同指标统一到0-1范围，1表示最平滑)
        normalized_scores = {}
        
        # CV差分 (越小越平滑)
        normalized_scores['cv_diff'] = max(0, 1 - first_order.get('cv_diff', 1) / 2)
        
        # 曲率平滑度 (直接使用)
        normalized_scores['curvature_smoothness'] = second_order.get('curvature_smoothness', 0)
        
        # 趋势一致性 (直接使用)
        normalized_scores['trend_consistency'] = max(0, moving_avg.get('trend_consistency', 0))
        
        # 高频比例 (越小越平滑)
        normalized_scores['high_freq_ratio'] = max(0, 1 - frequency.get('high_freq_ratio', 0.5) * 2)
        
        # 血糖平滑指数 (直接使用)
        gsi = glucose_specific.get('glucose_smoothness_index', 0)
        normalized_scores['glucose_smoothness_index'] = max(0, min(1, gsi))
        
        # 中位数曲线平滑度 (直接使用)
        normalized_scores['median_curve_smoothness'] = agp_specific.get('median_curve_smoothness', 0)
        
        # 自相关衰减 (适度为好，0.2-0.5最佳)
        autocorr = statistical.get('autocorr_decay', 0)
        if 0.2 <= autocorr <= 0.5:
            normalized_scores['autocorr_decay'] = 1
        else:
            normalized_scores['autocorr_decay'] = max(0, 1 - abs(autocorr - 0.35) / 0.35)
        
        # 加权平均
        total_score = sum(weights[key] * normalized_scores[key] for key in weights.keys())
        
        return {
            'comprehensive_score': total_score,
            'component_scores': normalized_scores,
            'raw_metrics': {
                'first_order': first_order,
                'second_order': second_order,
                'moving_average': moving_avg,
                'frequency_domain': frequency,
                'statistical': statistical,
                'glucose_specific': glucose_specific,
                'agp_specific': agp_specific
            }
        }

# 使用示例
def example_usage():
    """使用示例"""
    # 模拟24小时血糖数据 (每5分钟一个点，共288个点)
    np.random.seed(42)
    time_points = 288
    
    # 生成模拟血糖数据
    # 基础血糖趋势
    base_glucose = 7.0 + 2.0 * np.sin(2 * np.pi * np.arange(time_points) / time_points)
    
    # 添加餐后血糖峰值
    meal_times = [48, 144, 240]  # 早中晚餐时间点
    for meal_time in meal_times:
        peak_range = range(max(0, meal_time), min(time_points, meal_time + 24))
        for i in peak_range:
            base_glucose[i] += 3.0 * np.exp(-(i - meal_time)**2 / 100)
    
    # 添加噪声
    noise = np.random.normal(0, 0.5, time_points)
    glucose_smooth = base_glucose + noise * 0.3  # 平滑血糖
    glucose_noisy = base_glucose + noise * 1.5   # 不平滑血糖
    
    # 计算平滑度
    smooth_analyzer = AGPSmoothness(glucose_smooth)
    noisy_analyzer = AGPSmoothness(glucose_noisy)
    
    smooth_result = smooth_analyzer.comprehensive_smoothness_score()
    noisy_result = noisy_analyzer.comprehensive_smoothness_score()
    
    print("平滑血糖综合评分:", f"{smooth_result['comprehensive_score']:.3f}")
    print("不平滑血糖综合评分:", f"{noisy_result['comprehensive_score']:.3f}")
    
    return smooth_result, noisy_result

if __name__ == "__main__":
    example_usage()