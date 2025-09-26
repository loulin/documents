"""
血糖模式复杂度计算算法集合
包含多种复杂度计算方法的Python实现
"""

import numpy as np
import pandas as pd
from scipy import signal, stats
from scipy.fft import fft, fftfreq
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
import warnings
warnings.filterwarnings('ignore')

class GlucoseComplexity:
    """血糖模式复杂度计算类"""
    
    def __init__(self, glucose_data, timestamps=None):
        """
        初始化
        glucose_data: 血糖数据数组
        timestamps: 时间戳数组（可选）
        """
        self.glucose = np.array(glucose_data)
        self.timestamps = timestamps
        self.n = len(self.glucose)
        
    def fractal_dimension_box_counting(self):
        """
        盒子计数法计算分形维数
        衡量血糖曲线填充空间的能力
        """
        if self.n < 10:
            return 1.0
            
        # 标准化数据到[0,1]区间
        normalized = (self.glucose - np.min(self.glucose)) / (np.max(self.glucose) - np.min(self.glucose))
        
        # 创建不同尺寸的盒子
        scales = np.logspace(0.01, 0.5, num=20)
        box_counts = []
        
        for scale in scales:
            # 计算每个尺寸下需要的盒子数量
            grid_size = int(1/scale) + 1
            boxes = set()
            
            for i in range(len(normalized)-1):
                x1, y1 = i/len(normalized), normalized[i]
                x2, y2 = (i+1)/len(normalized), normalized[i+1]
                
                # 计算线段经过的盒子
                x_boxes = range(int(x1*grid_size), int(x2*grid_size)+1)
                y_boxes = range(int(y1*grid_size), int(y2*grid_size)+1)
                
                for x_box in x_boxes:
                    for y_box in y_boxes:
                        boxes.add((x_box, y_box))
            
            box_counts.append(len(boxes))
        
        # 线性拟合 log(N) vs log(1/scale)
        if len(box_counts) > 1:
            log_scales = np.log(1/scales)
            log_counts = np.log(box_counts)
            
            # 过滤无效值
            valid_idx = np.isfinite(log_scales) & np.isfinite(log_counts)
            if np.sum(valid_idx) > 1:
                slope, _ = np.polyfit(log_scales[valid_idx], log_counts[valid_idx], 1)
                return max(1.0, min(3.0, slope))  # 限制在合理范围
        
        return 1.5  # 默认值
    
    def approximate_entropy(self, m=2, r=None):
        """
        计算近似熵 (ApEn)
        衡量血糖时间序列的复杂度和可预测性
        """
        if r is None:
            r = 0.2 * np.std(self.glucose)
        
        N = len(self.glucose)
        if N < m + 1:
            return 0
        
        def _maxdist(xi, xj, m):
            """计算两个模板的最大距离"""
            return max([abs(ua - va) for ua, va in zip(xi, xj)])
        
        def _phi(m):
            """计算φ(m)"""
            patterns = []
            for i in range(N - m + 1):
                patterns.append(self.glucose[i:i + m])
            
            phi_list = []
            for i in range(len(patterns)):
                template = patterns[i]
                matches = 0
                for j in range(len(patterns)):
                    if _maxdist(template, patterns[j], m) <= r:
                        matches += 1
                
                if matches > 0:
                    phi_list.append(np.log(matches / len(patterns)))
            
            return np.mean(phi_list) if phi_list else 0
        
        phi_m = _phi(m)
        phi_m_plus_1 = _phi(m + 1)
        
        return max(0, phi_m - phi_m_plus_1)
    
    def sample_entropy(self, m=2, r=None):
        """
        计算样本熵 (SampEn)
        排除自匹配，比近似熵更稳健
        """
        if r is None:
            r = 0.2 * np.std(self.glucose)
        
        N = len(self.glucose)
        if N < m + 1:
            return 0
        
        def _maxdist(xi, xj, m):
            return max([abs(ua - va) for ua, va in zip(xi, xj)])
        
        def _phi(m):
            patterns = []
            for i in range(N - m + 1):
                patterns.append(self.glucose[i:i + m])
            
            matches = 0
            total_comparisons = 0
            
            for i in range(len(patterns)):
                for j in range(len(patterns)):
                    if i != j:  # 排除自匹配
                        total_comparisons += 1
                        if _maxdist(patterns[i], patterns[j], m) <= r:
                            matches += 1
            
            return matches / total_comparisons if total_comparisons > 0 else 0
        
        phi_m = _phi(m)
        phi_m_plus_1 = _phi(m + 1)
        
        if phi_m > 0 and phi_m_plus_1 > 0:
            return -np.log(phi_m_plus_1 / phi_m)
        
        return 0
    
    def permutation_entropy(self, order=3, delay=1):
        """
        计算排列熵 (PE)
        基于序列的排列模式
        """
        if self.n < order:
            return 0
        
        # 创建排列模式
        permutations = []
        for i in range(self.n - (order - 1) * delay):
            pattern = []
            for j in range(order):
                pattern.append(self.glucose[i + j * delay])
            
            # 转换为排列
            sorted_indices = np.argsort(pattern)
            permutation = tuple(sorted_indices)
            permutations.append(permutation)
        
        # 计算排列频率
        unique_perms, counts = np.unique(permutations, return_counts=True, axis=0)
        probabilities = counts / len(permutations)
        
        # 计算熵
        pe = -np.sum(probabilities * np.log(probabilities + 1e-10))
        
        # 标准化到[0,1]
        max_entropy = np.log(np.math.factorial(order))
        return pe / max_entropy if max_entropy > 0 else 0
    
    def spectral_entropy(self):
        """
        计算频谱熵
        基于功率谱密度的熵值
        """
        if self.n < 8:
            return 0
        
        # 计算功率谱密度
        freqs, psd = signal.welch(self.glucose, nperseg=min(256, self.n//4))
        
        # 过滤正频率和非零功率
        positive_idx = (freqs > 0) & (psd > 0)
        if np.sum(positive_idx) < 2:
            return 0
        
        psd_positive = psd[positive_idx]
        
        # 归一化概率
        psd_norm = psd_positive / np.sum(psd_positive)
        
        # 计算频谱熵
        spectral_entropy = -np.sum(psd_norm * np.log(psd_norm + 1e-10))
        
        # 标准化
        max_entropy = np.log(len(psd_norm))
        return spectral_entropy / max_entropy if max_entropy > 0 else 0
    
    def lempel_ziv_complexity(self):
        """
        计算Lempel-Ziv复杂度
        基于序列压缩的复杂度
        """
        # 将血糖数据二值化
        median_glucose = np.median(self.glucose)
        binary_string = ''.join(['1' if g >= median_glucose else '0' for g in self.glucose])
        
        # LZ77压缩算法
        def lz77_compress(data):
            compressed = []
            i = 0
            
            while i < len(data):
                match_length = 0
                match_distance = 0
                
                # 查找最长匹配
                for j in range(max(0, i - 255), i):
                    length = 0
                    while (i + length < len(data) and 
                           j + length < i and 
                           data[j + length] == data[i + length] and
                           length < 255):
                        length += 1
                    
                    if length > match_length:
                        match_length = length
                        match_distance = i - j
                
                if match_length >= 3:  # 最小匹配长度
                    compressed.append((match_distance, match_length))
                    i += match_length
                else:
                    compressed.append(data[i])
                    i += 1
            
            return compressed
        
        compressed = lz77_compress(binary_string)
        
        # 计算压缩率
        original_length = len(binary_string)
        compressed_length = len(compressed)
        
        # LZ复杂度 = 压缩后长度 / 原始长度
        return compressed_length / original_length if original_length > 0 else 0
    
    def hjorth_complexity(self):
        """
        计算Hjorth复杂度
        基于导数方差的复杂度
        """
        if self.n < 3:
            return 1.0
        
        # 计算一阶和二阶导数
        first_deriv = np.diff(self.glucose)
        second_deriv = np.diff(first_deriv)
        
        # 计算方差
        var_glucose = np.var(self.glucose)
        var_first = np.var(first_deriv)
        var_second = np.var(second_deriv)
        
        if var_glucose == 0 or var_first == 0:
            return 1.0
        
        # Hjorth活动度和机动度
        activity = var_first / var_glucose
        mobility = np.sqrt(activity)
        
        if mobility == 0:
            return 1.0
        
        # Hjorth复杂度
        complexity = np.sqrt(var_second / var_first) / mobility
        
        return max(1.0, complexity)
    
    def hurst_exponent(self):
        """
        计算Hurst指数
        衡量时间序列的长程相关性
        """
        if self.n < 20:
            return 0.5
        
        # 去除趋势
        detrended = signal.detrend(self.glucose)
        
        # 不同时间窗口
        max_window = min(self.n // 4, 100)
        window_sizes = np.unique(np.logspace(1, np.log10(max_window), 15).astype(int))
        
        rs_values = []
        
        for window_size in window_sizes:
            if window_size >= self.n:
                continue
                
            # 分段计算R/S
            rs_list = []
            for i in range(0, self.n - window_size + 1, window_size // 2):
                segment = detrended[i:i + window_size]
                
                if len(segment) < window_size:
                    continue
                
                # 累积偏差
                mean_segment = np.mean(segment)
                cumulative_deviate = np.cumsum(segment - mean_segment)
                
                # 范围
                R = np.max(cumulative_deviate) - np.min(cumulative_deviate)
                
                # 标准差
                S = np.std(segment)
                
                if S > 0:
                    rs_list.append(R / S)
            
            if rs_list:
                rs_values.append(np.mean(rs_list))
        
        if len(rs_values) < 2:
            return 0.5
        
        # 线性拟合 log(R/S) vs log(n)
        log_windows = np.log(window_sizes[:len(rs_values)])
        log_rs = np.log(rs_values)
        
        # 过滤有效值
        valid_idx = np.isfinite(log_windows) & np.isfinite(log_rs)
        if np.sum(valid_idx) > 1:
            hurst, _ = np.polyfit(log_windows[valid_idx], log_rs[valid_idx], 1)
            return max(0.0, min(2.0, hurst))
        
        return 0.5
    
    def multiscale_entropy(self, scales=20, m=2, r=None):
        """
        计算多尺度熵
        在多个时间尺度上计算样本熵
        """
        if r is None:
            r = 0.15 * np.std(self.glucose)
        
        mse_values = []
        
        for scale in range(1, min(scales + 1, self.n // 10)):
            # 粗粒化
            coarse_grained = []
            for i in range(0, self.n - scale + 1, scale):
                coarse_grained.append(np.mean(self.glucose[i:i + scale]))
            
            if len(coarse_grained) < m + 1:
                break
            
            # 计算样本熵
            temp_complexity = GlucoseComplexity(coarse_grained)
            se = temp_complexity.sample_entropy(m=m, r=r * scale)
            mse_values.append(se)
        
        return mse_values
    
    def lyapunov_exponent(self, emb_dim=3, lag=1):
        """
        计算最大李雅普诺夫指数
        衡量系统的混沌特征
        """
        if self.n < emb_dim * lag + 10:
            return 0
        
        # 相空间重构
        embedded = []
        for i in range(self.n - (emb_dim - 1) * lag):
            vector = []
            for j in range(emb_dim):
                vector.append(self.glucose[i + j * lag])
            embedded.append(vector)
        
        embedded = np.array(embedded)
        
        # 寻找最近邻
        divergences = []
        
        for i in range(len(embedded) - 10):  # 留出足够的演化时间
            distances = []
            for j in range(len(embedded)):
                if abs(i - j) > 10:  # 避免时间上太近的点
                    dist = np.linalg.norm(embedded[i] - embedded[j])
                    distances.append((dist, j))
            
            if len(distances) == 0:
                continue
            
            # 找最近邻
            distances.sort()
            nearest_idx = distances[0][1]
            initial_distance = distances[0][0]
            
            if initial_distance == 0:
                continue
            
            # 跟踪轨道发散
            evolution_length = min(10, len(embedded) - max(i, nearest_idx))
            for t in range(1, evolution_length):
                if i + t >= len(embedded) or nearest_idx + t >= len(embedded):
                    break
                
                current_distance = np.linalg.norm(embedded[i + t] - embedded[nearest_idx + t])
                
                if current_distance > 0 and initial_distance > 0:
                    divergence = np.log(current_distance / initial_distance) / t
                    divergences.append(divergence)
        
        return np.mean(divergences) if divergences else 0
    
    def comprehensive_complexity_score(self):
        """
        综合复杂度评分
        整合多种复杂度指标
        """
        # 计算各种复杂度
        fractal_dim = self.fractal_dimension_box_counting()
        approx_entropy = self.approximate_entropy()
        perm_entropy = self.permutation_entropy()
        spec_entropy = self.spectral_entropy()
        lz_complexity = self.lempel_ziv_complexity()
        hjorth_comp = self.hjorth_complexity()
        hurst_exp = self.hurst_exponent()
        lyap_exp = self.lyapunov_exponent()
        
        # 权重设置 (可根据临床需要调整)
        weights = {
            'fractal_dimension': 0.15,      # 几何复杂性
            'approximate_entropy': 0.20,    # 可预测性
            'permutation_entropy': 0.15,    # 模式复杂性
            'spectral_entropy': 0.10,       # 频域复杂性
            'lempel_ziv': 0.10,            # 压缩复杂性
            'hjorth_complexity': 0.10,      # 导数复杂性
            'hurst_exponent': 0.10,         # 长程相关性
            'lyapunov_exponent': 0.10       # 混沌特征
        }
        
        # 标准化处理
        normalized_scores = {}
        
        # 分形维数 (1.0-2.0为正常)
        normalized_scores['fractal_dimension'] = min(1.0, max(0, (fractal_dim - 1.0) / 1.0))
        
        # 近似熵 (0.1-0.4为正常)
        normalized_scores['approximate_entropy'] = min(1.0, max(0, approx_entropy / 0.8))
        
        # 排列熵 (0.3-0.7为正常)
        normalized_scores['permutation_entropy'] = min(1.0, max(0, perm_entropy / 1.0))
        
        # 频谱熵
        normalized_scores['spectral_entropy'] = min(1.0, max(0, spec_entropy))
        
        # LZ复杂度
        normalized_scores['lempel_ziv'] = min(1.0, max(0, lz_complexity))
        
        # Hjorth复杂度 (1.0-2.0为正常)
        normalized_scores['hjorth_complexity'] = min(1.0, max(0, (hjorth_comp - 1.0) / 2.0))
        
        # Hurst指数 (0.5为随机，偏离0.5越远越复杂)
        normalized_scores['hurst_exponent'] = min(1.0, max(0, 2 * abs(hurst_exp - 0.5)))
        
        # 李雅普诺夫指数 (>0为混沌)
        normalized_scores['lyapunov_exponent'] = min(1.0, max(0, lyap_exp / 0.1)) if lyap_exp > 0 else 0
        
        # 加权平均
        total_score = sum(weights[key] * normalized_scores[key] for key in weights.keys())
        
        return {
            'comprehensive_complexity': total_score,
            'component_scores': normalized_scores,
            'raw_metrics': {
                'fractal_dimension': fractal_dim,
                'approximate_entropy': approx_entropy,
                'permutation_entropy': perm_entropy,
                'spectral_entropy': spec_entropy,
                'lempel_ziv_complexity': lz_complexity,
                'hjorth_complexity': hjorth_comp,
                'hurst_exponent': hurst_exp,
                'lyapunov_exponent': lyap_exp
            }
        }

# 使用示例
def example_usage():
    """使用示例"""
    # 模拟血糖数据
    np.random.seed(42)
    time_points = 288  # 24小时，每5分钟一个点
    
    # 简单血糖模式
    t = np.linspace(0, 24, time_points)
    simple_glucose = 7.0 + 2.0 * np.sin(2 * np.pi * t / 24) + np.random.normal(0, 0.3, time_points)
    
    # 复杂血糖模式
    complex_glucose = (7.0 + 
                      2.0 * np.sin(2 * np.pi * t / 24) +      # 昼夜节律
                      1.5 * np.sin(2 * np.pi * t / 4) +       # 餐后波动
                      0.5 * np.sin(2 * np.pi * t / 1.5) +     # 高频波动
                      np.random.normal(0, 0.8, time_points))   # 随机噪声
    
    # 计算复杂度
    simple_analyzer = GlucoseComplexity(simple_glucose)
    complex_analyzer = GlucoseComplexity(complex_glucose)
    
    simple_result = simple_analyzer.comprehensive_complexity_score()
    complex_result = complex_analyzer.comprehensive_complexity_score()
    
    print("简单血糖模式复杂度:", f"{simple_result['comprehensive_complexity']:.3f}")
    print("复杂血糖模式复杂度:", f"{complex_result['comprehensive_complexity']:.3f}")
    
    # 详细分析
    print("\n复杂血糖模式详细分析:")
    for metric, value in complex_result['raw_metrics'].items():
        print(f"{metric}: {value:.3f}")
    
    return simple_result, complex_result

if __name__ == "__main__":
    example_usage()