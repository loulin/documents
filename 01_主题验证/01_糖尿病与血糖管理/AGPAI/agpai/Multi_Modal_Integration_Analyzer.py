#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Modal Integration Analyzer v5.0
多模态生理信号整合分析系统

基于Agent2 v5.0架构和实际临床需求，实现CGM、ECG、HRV、ABPM四大生理信号的深度整合分析
提供基于生理病理学机制的跨模态脆性评估和综合健康风险预测

核心创新:
1. 生理耦合动力学建模 - 基于Windkessel模型和糖代谢动力学
2. 多尺度熵分析 - 跨时间尺度的系统复杂性评估  
3. 相位同步分析 - 生理节律的协调性量化
4. 信息论方法 - 系统间信息传递和因果关系识别
5. 机器学习融合 - 深度特征提取和模式识别
6. 临床决策树 - 循证医学指导的治疗建议

作者: Agent2 Multi-Modal Analysis System
日期: 2025-08-28
版本: v5.0 Enhanced
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

# 数值计算和信号处理
from scipy import signal, stats
from scipy.stats import pearsonr, spearmanr, entropy as scipy_entropy
from scipy.fft import fft, fftfreq, hilbert
from scipy.integrate import odeint
from scipy.optimize import minimize

# 机器学习和数据分析
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.decomposition import PCA, FastICA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import silhouette_score

# 时间序列和非线性分析
import ruptures as rpt
try:
    import nolds
    NOLDS_AVAILABLE = True
except ImportError:
    NOLDS_AVAILABLE = False
    print("Warning: nolds not available. Some nonlinear analysis features will be disabled.")

# 信息论分析
try:
    from sklearn.feature_selection import mutual_info_regression
    MI_AVAILABLE = True
except ImportError:
    MI_AVAILABLE = False

class MultiModalIntegrationAnalyzer:
    """
    多模态生理信号整合分析器 v5.0 Enhanced
    
    基于生理病理学机制的深度整合分析系统
    实现真正有临床价值的跨模态脆性评估
    """
    
    def __init__(self, patient_id, config=None):
        """
        初始化多模态整合分析器
        
        Parameters:
        -----------
        patient_id : str
            患者ID
        config : dict, optional
            分析配置参数
        """
        self.patient_id = patient_id
        self.config = self._initialize_config(config)
        self.raw_data = {}
        self.processed_data = {}
        self.synchronized_data = None
        self.analysis_results = {}
        
        print(f"Multi-Modal Integration Analyzer v5.0 Enhanced initialized")
        print(f"Patient ID: {patient_id}")
        
    def _initialize_config(self, user_config):
        """初始化完整配置"""
        default_config = {
            # 数据同步配置
            'synchronization': {
                'target_frequency_min': 5,        # 目标采样频率(分钟)
                'interpolation_method': 'cubic',   # 插值方法
                'alignment_tolerance_min': 2,      # 时间对齐容差
                'min_overlap_hours': 4,            # 最小重叠时间
                'outlier_detection': True,         # 异常值检测
                'quality_threshold': 0.7           # 数据质量阈值
            },
            
            # 生理耦合模型参数
            'coupling_models': {
                # 血糖-血压耦合模型 (基于血管弹性理论)
                'glucose_bp_coupling': {
                    'windkessel_c': 1.2,     # 血管顺应性系数
                    'peripheral_r': 0.8,     # 外周阻力系数
                    'glucose_sensitivity': 0.15,  # 血糖敏感性
                    'lag_minutes': [0, 15, 30, 45] # 滞后时间窗口
                },
                
                # 自主神经-心率耦合 (基于心率变异性理论)
                'autonomic_hr_coupling': {
                    'sympathetic_gain': 1.0,   # 交感神经增益
                    'parasympathetic_gain': 1.0, # 副交感神经增益
                    'coupling_strength': 0.5,   # 耦合强度
                    'time_constants': [0.5, 2.0, 10.0] # 时间常数(分钟)
                },
                
                # 代谢-循环耦合 (基于Fick定律)
                'metabolic_circulatory': {
                    'oxygen_extraction': 0.25,  # 氧提取率
                    'cardiac_output_base': 5.0,  # 基础心输出量(L/min)
                    'metabolic_demand_factor': 1.2, # 代谢需求因子
                }
            },
            
            # 多尺度熵分析参数
            'multiscale_entropy': {
                'scales': list(range(1, 21)),    # 时间尺度1-20
                'sample_entropy_m': 2,           # 模板长度
                'sample_entropy_r': 0.15,        # 容差比例
                'coarse_graining_method': 'mean' # 粗粒化方法
            },
            
            # 相位同步分析
            'phase_synchronization': {
                'frequency_bands': {
                    'ultradian': (0.0001, 0.001),   # 超日节律
                    'circadian': (0.001, 0.01),     # 昼夜节律  
                    'short_term': (0.01, 0.1),      # 短期变异
                    'rapid': (0.1, 0.5)             # 快速变异
                },
                'hilbert_transform': True,        # Hilbert变换相位提取
                'synchronization_threshold': 0.7  # 同步阈值
            },
            
            # 信息论分析
            'information_theory': {
                'mutual_information': True,       # 互信息分析
                'transfer_entropy': True,         # 传递熵分析
                'causality_detection': True,      # 因果关系检测
                'bin_method': 'fd',              # 分箱方法 (Freedman-Diaconis)
                'max_lag_minutes': 120           # 最大滞后时间
            },
            
            # 机器学习融合
            'ml_fusion': {
                'feature_selection': True,        # 特征选择
                'dimensionality_reduction': 'pca', # 降维方法
                'clustering_method': 'kmeans',     # 聚类方法
                'n_clusters': 5,                  # 聚类数量
                'anomaly_detection': True,        # 异常检测
                'pattern_recognition': True       # 模式识别
            },
            
            # 综合脆性评分模型
            'brittleness_model': {
                'base_weights': {
                    'glucose_brittleness': 0.25,
                    'cardiac_brittleness': 0.25,
                    'autonomic_brittleness': 0.25,
                    'vascular_brittleness': 0.25
                },
                'coupling_bonus': {
                    'strong_coupling': 15,    # 强耦合加成
                    'moderate_coupling': 10,  # 中等耦合加成
                    'weak_coupling': 5        # 弱耦合加成
                },
                'complexity_factors': {
                    'entropy_weight': 0.3,       # 熵权重
                    'synchrony_weight': 0.3,     # 同步性权重
                    'causality_weight': 0.2,     # 因果性权重
                    'ml_pattern_weight': 0.2     # 机器学习模式权重
                }
            },
            
            # 临床决策规则
            'clinical_decision_rules': {
                'risk_stratification': {
                    'very_low': (0, 20),
                    'low': (20, 35),
                    'moderate': (35, 55),
                    'high': (55, 75),
                    'very_high': (75, 90),
                    'critical': (90, 100)
                },
                'intervention_thresholds': {
                    'glucose_instability': 60,
                    'cardiac_dysfunction': 65,
                    'autonomic_failure': 70,
                    'vascular_dysfunction': 65
                }
            }
        }
        
        if user_config:
            # 递归更新配置
            self._update_config(default_config, user_config)
        
        return default_config
    
    def _update_config(self, base_config, update_config):
        """递归更新配置字典"""
        for key, value in update_config.items():
            if isinstance(value, dict) and key in base_config:
                self._update_config(base_config[key], value)
            else:
                base_config[key] = value
    
    def load_multimodal_data(self, cgm_data=None, ecg_data=None, hrv_data=None, abpm_data=None):
        """
        加载多模态数据并进行初步处理
        
        Parameters:
        -----------
        cgm_data : str or pd.DataFrame
            CGM血糖数据
        ecg_data : str or pd.DataFrame  
            ECG心电数据
        hrv_data : str or pd.DataFrame
            HRV心率变异数据
        abpm_data : str or pd.DataFrame
            ABPM动态血压数据
        """
        print("Loading and preprocessing multimodal data...")
        
        data_loaders = {
            'cgm': self._load_cgm_data,
            'ecg': self._load_ecg_data, 
            'hrv': self._load_hrv_data,
            'abpm': self._load_abpm_data
        }
        
        input_data = {
            'cgm': cgm_data,
            'ecg': ecg_data,
            'hrv': hrv_data, 
            'abpm': abpm_data
        }
        
        # 加载各模态数据
        for modality, data in input_data.items():
            if data is not None:
                try:
                    processed = data_loaders[modality](data)
                    if processed is not None and len(processed) > 0:
                        self.raw_data[modality] = processed
                        print(f"✓ {modality.upper()} data loaded: {len(processed)} records")
                    else:
                        print(f"✗ {modality.upper()} data loading failed")
                except Exception as e:
                    print(f"✗ {modality.upper()} data loading error: {str(e)}")
        
        if len(self.raw_data) < 2:
            raise ValueError("At least 2 modalities required for multimodal analysis")
        
        print(f"Successfully loaded {len(self.raw_data)} modalities: {list(self.raw_data.keys())}")
        
        # 数据质量评估
        self._assess_data_quality()
        
        return True
    
    def _load_cgm_data(self, data):
        """加载CGM数据"""
        if isinstance(data, str):
            if data.endswith('.xlsx') or data.endswith('.xls'):
                df = pd.read_excel(data)
            else:
                df = pd.read_csv(data)
        else:
            df = data.copy()
        
        # 标准化列名
        column_mapping = {
            '时间': 'timestamp', 'Time': 'timestamp', 'DateTime': 'timestamp',
            '血糖': 'glucose', 'Glucose': 'glucose', 'BG': 'glucose', '值': 'glucose'
        }
        
        df = df.rename(columns=column_mapping)
        
        # 确保有时间戳和血糖列
        if 'timestamp' not in df.columns:
            df['timestamp'] = pd.to_datetime(df.iloc[:, 0])
        else:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        glucose_col = None
        for col in ['glucose', 'Glucose', 'BG', '血糖', '值']:
            if col in df.columns:
                glucose_col = col
                break
        
        if glucose_col is None:
            # 尝试第二列作为血糖值
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df['glucose'] = df[numeric_cols[0]]
            else:
                raise ValueError("Cannot identify glucose column")
        elif glucose_col != 'glucose':
            df['glucose'] = df[glucose_col]
        
        # 数据清洗
        df = df.dropna(subset=['timestamp', 'glucose'])
        df = df[(df['glucose'] >= 20) & (df['glucose'] <= 600)]  # 合理血糖范围
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df[['timestamp', 'glucose']]
    
    def _load_ecg_data(self, data):
        """加载ECG数据"""
        if isinstance(data, str):
            if data.endswith('.xlsx') or data.endswith('.xls'):
                df = pd.read_excel(data)
            else:
                df = pd.read_csv(data)
        else:
            df = data.copy()
        
        # 标准化列名
        column_mapping = {
            '时间': 'timestamp', 'Time': 'timestamp', 'DateTime': 'timestamp',
            '心率': 'hr', 'HR': 'hr', 'Heart_Rate': 'hr', 'heart_rate': 'hr',
            'RR间期': 'rr_interval', 'RR_Interval': 'rr_interval', 'RR': 'rr_interval'
        }
        
        df = df.rename(columns=column_mapping)
        
        if 'timestamp' not in df.columns:
            df['timestamp'] = pd.to_datetime(df.iloc[:, 0])
        else:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 查找心率或RR间期数据
        hr_col = None
        rr_col = None
        
        for col in ['hr', 'HR', 'heart_rate', '心率']:
            if col in df.columns:
                hr_col = col
                break
                
        for col in ['rr_interval', 'RR_Interval', 'RR', 'RR间期']:
            if col in df.columns:
                rr_col = col
                break
        
        result_df = df[['timestamp']].copy()
        
        if hr_col is not None:
            result_df['heart_rate'] = df[hr_col]
            # 数据清洗
            result_df = result_df[(result_df['heart_rate'] >= 30) & (result_df['heart_rate'] <= 200)]
        
        if rr_col is not None:
            result_df['rr_interval'] = df[rr_col]
            # 数据清洗
            result_df = result_df[(result_df['rr_interval'] >= 300) & (result_df['rr_interval'] <= 2000)]
            
            # 如果没有心率，从RR间期计算
            if hr_col is None:
                result_df['heart_rate'] = 60000 / result_df['rr_interval']
        
        if 'heart_rate' not in result_df.columns:
            raise ValueError("Cannot identify heart rate or RR interval data")
        
        result_df = result_df.dropna().sort_values('timestamp').reset_index(drop=True)
        return result_df
    
    def _load_hrv_data(self, data):
        """加载HRV数据"""
        if isinstance(data, str):
            if data.endswith('.xlsx') or data.endswith('.xls'):
                df = pd.read_excel(data)
            else:
                df = pd.read_csv(data)
        else:
            df = data.copy()
        
        # 标准化列名
        column_mapping = {
            '时间': 'timestamp', 'Time': 'timestamp', 'DateTime': 'timestamp',
            'RR间期': 'rr_intervals', 'RR_Intervals': 'rr_intervals', 'RR': 'rr_intervals',
            'SDNN': 'sdnn', 'RMSSD': 'rmssd', 'pNN50': 'pnn50',
            'LF': 'lf_power', 'HF': 'hf_power', 'LF/HF': 'lf_hf_ratio'
        }
        
        df = df.rename(columns=column_mapping)
        
        if 'timestamp' not in df.columns:
            df['timestamp'] = pd.to_datetime(df.iloc[:, 0])
        else:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 识别HRV指标
        hrv_columns = ['sdnn', 'rmssd', 'pnn50', 'lf_power', 'hf_power', 'lf_hf_ratio']
        available_hrv = [col for col in hrv_columns if col in df.columns]
        
        if len(available_hrv) == 0:
            # 尝试从RR间期计算基础HRV指标
            if 'rr_intervals' in df.columns:
                df = self._calculate_basic_hrv_metrics(df)
                available_hrv = ['sdnn', 'rmssd']
            else:
                raise ValueError("No HRV metrics or RR intervals found")
        
        result_columns = ['timestamp'] + available_hrv
        result_df = df[result_columns].copy()
        result_df = result_df.dropna().sort_values('timestamp').reset_index(drop=True)
        
        return result_df
    
    def _calculate_basic_hrv_metrics(self, df):
        """从RR间期计算基础HRV指标"""
        rr_data = df['rr_intervals'].values
        
        # SDNN - RR间期标准差
        df['sdnn'] = pd.Series(rr_data).rolling(window=50, center=True).std()
        
        # RMSSD - 相邻RR间期差值的均方根
        rr_diff = np.diff(rr_data)
        rr_diff_squared = rr_diff ** 2
        df['rmssd'] = pd.Series(np.concatenate([[np.nan], rr_diff_squared])).rolling(window=50, center=True).mean().apply(np.sqrt)
        
        return df
    
    def _load_abpm_data(self, data):
        """加载ABPM数据"""
        if isinstance(data, str):
            if data.endswith('.xlsx') or data.endswith('.xls'):
                df = pd.read_excel(data)
            else:
                df = pd.read_csv(data)
        else:
            df = data.copy()
        
        # 标准化列名
        column_mapping = {
            '时间': 'timestamp', 'Time': 'timestamp', 'DateTime': 'timestamp',
            '收缩压': 'sbp', 'SBP': 'sbp', 'Systolic': 'sbp',
            '舒张压': 'dbp', 'DBP': 'dbp', 'Diastolic': 'dbp',
            '平均压': 'map', 'MAP': 'map', 'Mean': 'map',
            '心率': 'pulse', 'HR': 'pulse', 'Pulse': 'pulse'
        }
        
        df = df.rename(columns=column_mapping)
        
        if 'timestamp' not in df.columns:
            df['timestamp'] = pd.to_datetime(df.iloc[:, 0])
        else:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 确保有收缩压和舒张压
        if 'sbp' not in df.columns or 'dbp' not in df.columns:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 2:
                df['sbp'] = df[numeric_cols[0]]
                df['dbp'] = df[numeric_cols[1]]
            else:
                raise ValueError("Cannot identify SBP and DBP columns")
        
        # 计算平均动脉压
        if 'map' not in df.columns:
            df['map'] = df['dbp'] + (df['sbp'] - df['dbp']) / 3
        
        # 数据清洗
        df = df[(df['sbp'] >= 60) & (df['sbp'] <= 250)]
        df = df[(df['dbp'] >= 30) & (df['dbp'] <= 150)]
        df = df.dropna(subset=['timestamp', 'sbp', 'dbp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df[['timestamp', 'sbp', 'dbp', 'map']]
    
    def _assess_data_quality(self):
        """评估数据质量"""
        quality_report = {}
        
        for modality, data in self.raw_data.items():
            # 计算数据质量指标
            total_duration = (data['timestamp'].max() - data['timestamp'].min()).total_seconds() / 3600
            data_points = len(data)
            sampling_rate = data_points / total_duration if total_duration > 0 else 0
            
            # 缺失值分析
            missing_rate = data.isnull().sum().sum() / (len(data) * len(data.columns))
            
            # 时间间隔一致性
            time_diffs = data['timestamp'].diff().dt.total_seconds() / 60  # 分钟
            time_consistency = 1 - (time_diffs.std() / time_diffs.mean()) if time_diffs.mean() > 0 else 0
            
            quality_score = (1 - missing_rate) * 0.4 + time_consistency * 0.3 + min(1, sampling_rate / 12) * 0.3
            
            quality_report[modality] = {
                'duration_hours': round(total_duration, 2),
                'data_points': data_points,
                'sampling_rate_per_hour': round(sampling_rate, 2),
                'missing_rate': round(missing_rate, 4),
                'time_consistency': round(time_consistency, 3),
                'quality_score': round(quality_score, 3),
                'quality_grade': 'A' if quality_score >= 0.8 else 'B' if quality_score >= 0.6 else 'C'
            }
        
        self.data_quality_report = quality_report
        
        print("\nData Quality Assessment:")
        for modality, metrics in quality_report.items():
            print(f"{modality.upper()}: {metrics['quality_grade']} grade, "
                  f"{metrics['duration_hours']}h, "
                  f"{metrics['data_points']} points, "
                  f"Score: {metrics['quality_score']:.3f}")
    
    def synchronize_multimodal_data(self):
        """
        多模态数据时间同步
        
        使用高级插值方法将不同模态数据同步到统一时间网格
        """
        print("Synchronizing multimodal data...")
        
        if len(self.raw_data) < 2:
            raise ValueError("Need at least 2 modalities for synchronization")
        
        # 找到所有模态的时间范围交集
        time_ranges = {}
        for modality, data in self.raw_data.items():
            time_ranges[modality] = {
                'start': data['timestamp'].min(),
                'end': data['timestamp'].max(),
                'span_hours': (data['timestamp'].max() - data['timestamp'].min()).total_seconds() / 3600
            }
        
        # 计算重叠时间段
        overlap_start = max([tr['start'] for tr in time_ranges.values()])
        overlap_end = min([tr['end'] for tr in time_ranges.values()])
        overlap_duration = (overlap_end - overlap_start).total_seconds() / 3600
        
        print(f"Temporal overlap: {overlap_duration:.2f} hours")
        print(f"Overlap period: {overlap_start.strftime('%Y-%m-%d %H:%M')} to {overlap_end.strftime('%Y-%m-%d %H:%M')}")
        
        if overlap_duration < self.config['synchronization']['min_overlap_hours']:
            raise ValueError(f"Insufficient overlap: {overlap_duration:.2f}h < {self.config['synchronization']['min_overlap_hours']}h")
        
        # 创建统一时间网格
        sync_freq_min = self.config['synchronization']['target_frequency_min']
        time_grid = pd.date_range(
            start=overlap_start,
            end=overlap_end,
            freq=f"{sync_freq_min}min"
        )
        
        # 同步各模态数据
        synchronized_df = pd.DataFrame({'timestamp': time_grid})
        sync_stats = {}
        
        for modality, raw_data in self.raw_data.items():
            print(f"Synchronizing {modality} data...")
            
            # 过滤到重叠时间段
            mask = (raw_data['timestamp'] >= overlap_start) & (raw_data['timestamp'] <= overlap_end)
            overlap_data = raw_data[mask].copy()
            
            if len(overlap_data) == 0:
                print(f"Warning: No {modality} data in overlap period")
                continue
            
            # 对每个信号进行时间同步
            modality_signals = {}
            data_columns = [col for col in overlap_data.columns if col != 'timestamp']
            
            for col in data_columns:
                # 创建插值函数
                valid_indices = overlap_data[col].notna()
                if valid_indices.sum() < 3:
                    print(f"Warning: Insufficient valid data for {modality}.{col}")
                    continue
                
                valid_data = overlap_data[valid_indices]
                
                # 时间转换为数值(秒)
                time_numeric = (valid_data['timestamp'] - overlap_start).dt.total_seconds()
                grid_numeric = (time_grid - overlap_start).total_seconds()
                
                # 高级插值
                try:
                    if self.config['synchronization']['interpolation_method'] == 'cubic':
                        from scipy.interpolate import CubicSpline
                        cs = CubicSpline(time_numeric.values, valid_data[col].values, bc_type='natural')
                        interpolated_values = cs(grid_numeric)
                    else:
                        # 线性插值作为后备
                        interpolated_values = np.interp(grid_numeric, time_numeric.values, valid_data[col].values)
                    
                    # 异常值检测和平滑
                    if self.config['synchronization']['outlier_detection']:
                        interpolated_values = self._detect_and_smooth_outliers(interpolated_values)
                    
                    modality_signals[f"{modality}_{col}"] = interpolated_values
                    
                except Exception as e:
                    print(f"Warning: Interpolation failed for {modality}.{col}: {e}")
                    continue
            
            # 添加同步信号到主数据框
            for signal_name, values in modality_signals.items():
                synchronized_df[signal_name] = values
            
            # 统计同步效果
            original_points = len(overlap_data)
            synchronized_points = len(time_grid)
            coverage_rate = len([v for v in modality_signals.values() if len(v) > 0]) / len(data_columns) if data_columns else 0
            
            sync_stats[modality] = {
                'original_points': original_points,
                'synchronized_points': synchronized_points,
                'coverage_rate': coverage_rate,
                'signals_synchronized': list(modality_signals.keys())
            }
        
        self.synchronized_data = synchronized_df
        self.sync_stats = sync_stats
        
        print(f"✓ Synchronization completed")
        print(f"✓ Synchronized dataset: {len(synchronized_df)} time points")
        print(f"✓ Total signals: {len(synchronized_df.columns) - 1}")
        
        return {
            'success': True,
            'time_points': len(time_grid),
            'overlap_duration_hours': overlap_duration,
            'sync_statistics': sync_stats,
            'synchronized_signals': list(synchronized_df.columns[1:])
        }
    
    def _detect_and_smooth_outliers(self, data, method='iqr', smooth_window=5):
        """检测和平滑异常值"""
        data_array = np.array(data)
        
        if method == 'iqr':
            Q1 = np.percentile(data_array, 25)
            Q3 = np.percentile(data_array, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # 标记异常值
            outliers = (data_array < lower_bound) | (data_array > upper_bound)
        else:
            # Z-score方法
            z_scores = np.abs(stats.zscore(data_array))
            outliers = z_scores > 3
        
        # 平滑异常值
        smoothed_data = data_array.copy()
        for i, is_outlier in enumerate(outliers):
            if is_outlier:
                # 使用邻域平均值替换
                start_idx = max(0, i - smooth_window // 2)
                end_idx = min(len(data_array), i + smooth_window // 2 + 1)
                neighbors = data_array[start_idx:end_idx]
                neighbors_clean = neighbors[~outliers[start_idx:end_idx]]
                if len(neighbors_clean) > 0:
                    smoothed_data[i] = np.mean(neighbors_clean)
        
        return smoothed_data
    
    def analyze_physiological_coupling(self):
        """
        生理耦合分析 - 基于生理学机制的深度耦合建模
        
        Returns:
        --------
        dict : 生理耦合分析结果
        """
        if self.synchronized_data is None:
            raise ValueError("Data not synchronized. Run synchronize_multimodal_data() first")
        
        print("Analyzing physiological coupling mechanisms...")
        
        coupling_results = {}
        
        # 1. 血糖-血压耦合分析 (基于血管弹性和血流动力学)
        if self._has_signals(['cgm_glucose', 'abpm_sbp']):
            coupling_results['glucose_bp_coupling'] = self._analyze_glucose_bp_coupling()
        
        # 2. 自主神经-心率耦合分析 (基于心率变异性理论)
        if self._has_signals(['hrv_sdnn', 'ecg_heart_rate']) or self._has_signals(['hrv_rmssd', 'ecg_heart_rate']):
            coupling_results['autonomic_hr_coupling'] = self._analyze_autonomic_hr_coupling()
        
        # 3. 代谢-循环耦合分析 (基于Fick定律和氧代谢)
        if self._has_signals(['cgm_glucose', 'ecg_heart_rate', 'abpm_map']):
            coupling_results['metabolic_circulatory_coupling'] = self._analyze_metabolic_circulatory_coupling()
        
        # 4. 血压-心率变异性耦合 (压力感受器反射)
        if self._has_signals(['abpm_sbp', 'hrv_sdnn']):
            coupling_results['baroreflex_coupling'] = self._analyze_baroreflex_coupling()
        
        # 5. 跨系统协调性分析
        coupling_results['cross_system_coordination'] = self._analyze_cross_system_coordination()
        
        self.coupling_results = coupling_results
        print(f"✓ Physiological coupling analysis completed: {len(coupling_results)} coupling types analyzed")
        
        return coupling_results
    
    def _has_signals(self, signal_names):
        """检查是否有指定信号"""
        if self.synchronized_data is None:
            return False
        return all(signal in self.synchronized_data.columns for signal in signal_names)
    
    def _analyze_glucose_bp_coupling(self):
        """血糖-血压耦合分析"""
        print("  Analyzing glucose-blood pressure coupling...")
        
        glucose = self.synchronized_data['cgm_glucose'].values
        sbp = self.synchronized_data['abpm_sbp'].values
        
        # 基于Windkessel模型的耦合分析
        coupling_analysis = {
            'mechanism': 'windkessel_model',
            'coupling_strength': 0,
            'coupling_pattern': 'none',
            'physiological_interpretation': {},
            'clinical_significance': 'unknown'
        }
        
        # 清理数据
        valid_mask = ~(np.isnan(glucose) | np.isnan(sbp))
        if valid_mask.sum() < 10:
            return {'error': 'Insufficient valid data points'}
        
        glucose_clean = glucose[valid_mask]
        sbp_clean = sbp[valid_mask]
        
        # 1. 即时相关性分析
        instant_corr = pearsonr(glucose_clean, sbp_clean)[0]
        coupling_analysis['instant_correlation'] = instant_corr
        
        # 2. 滞后相关性分析 (考虑生理延迟)
        lag_correlations = {}
        max_lag = min(len(glucose_clean) // 4, 24)  # 最大滞后2小时 (假设5分钟采样)
        
        for lag in range(0, max_lag + 1):
            if lag == 0:
                corr = instant_corr
            else:
                if len(glucose_clean) > lag and len(sbp_clean) > lag:
                    corr = pearsonr(glucose_clean[:-lag], sbp_clean[lag:])[0]
                else:
                    corr = np.nan
            lag_correlations[lag * 5] = corr  # 转换为分钟
        
        best_lag_minutes = max(lag_correlations.keys(), key=lambda k: abs(lag_correlations[k]) if not np.isnan(lag_correlations[k]) else 0)
        best_correlation = lag_correlations[best_lag_minutes]
        
        coupling_analysis['lag_analysis'] = {
            'best_lag_minutes': best_lag_minutes,
            'best_correlation': best_correlation,
            'all_lag_correlations': lag_correlations
        }
        
        # 3. Windkessel模型参数估计
        try:
            windkessel_params = self._fit_windkessel_model(glucose_clean, sbp_clean)
            coupling_analysis['windkessel_parameters'] = windkessel_params
        except Exception as e:
            coupling_analysis['windkessel_parameters'] = {'error': str(e)}
        
        # 4. 非线性耦合检测
        # 使用互信息检测非线性关系
        if MI_AVAILABLE:
            glucose_reshaped = glucose_clean.reshape(-1, 1)
            mi_score = mutual_info_regression(glucose_reshaped, sbp_clean)[0]
            coupling_analysis['mutual_information'] = mi_score
            
            # 非线性程度评估
            linear_info = abs(best_correlation) ** 2  # R²
            nonlinear_info = max(0, mi_score - linear_info)
            coupling_analysis['nonlinearity_index'] = nonlinear_info / mi_score if mi_score > 0 else 0
        
        # 5. 耦合强度综合评估
        coupling_strength = abs(best_correlation)
        if MI_AVAILABLE and 'mutual_information' in coupling_analysis:
            # 综合线性和非线性信息
            coupling_strength = max(coupling_strength, coupling_analysis['mutual_information'] / 2)
        
        coupling_analysis['coupling_strength'] = coupling_strength
        
        # 6. 生理模式识别
        if coupling_strength > 0.5:
            if best_correlation > 0.5:
                coupling_analysis['coupling_pattern'] = 'strong_positive'
                coupling_analysis['physiological_interpretation'] = {
                    'mechanism': 'glucose_induced_vasoconstriction',
                    'pathophysiology': 'hyperglycemia_hypertension_coupling',
                    'clinical_relevance': 'diabetic_vascular_dysfunction'
                }
            elif best_correlation < -0.5:
                coupling_analysis['coupling_pattern'] = 'strong_negative'
                coupling_analysis['physiological_interpretation'] = {
                    'mechanism': 'compensatory_vasodilation',
                    'pathophysiology': 'glucose_bp_homeostasis',
                    'clinical_relevance': 'preserved_vascular_reactivity'
                }
        elif coupling_strength > 0.3:
            coupling_analysis['coupling_pattern'] = 'moderate_coupling'
            coupling_analysis['physiological_interpretation'] = {
                'mechanism': 'partial_glucose_bp_interaction',
                'pathophysiology': 'early_vascular_dysfunction',
                'clinical_relevance': 'subclinical_diabetic_vasculopathy'
            }
        else:
            coupling_analysis['coupling_pattern'] = 'weak_coupling'
            coupling_analysis['physiological_interpretation'] = {
                'mechanism': 'independent_regulation',
                'pathophysiology': 'normal_vascular_glucose_homeostasis',
                'clinical_relevance': 'good_metabolic_vascular_control'
            }
        
        # 7. 临床意义评估
        if coupling_strength > 0.6 and best_correlation > 0.5:
            coupling_analysis['clinical_significance'] = 'high_cardiovascular_risk'
        elif coupling_strength > 0.4:
            coupling_analysis['clinical_significance'] = 'moderate_risk'
        else:
            coupling_analysis['clinical_significance'] = 'low_risk'
        
        return coupling_analysis
    
    def _fit_windkessel_model(self, glucose, bp):
        """拟合Windkessel血管模型"""
        # 简化的两元素Windkessel模型: BP(t) = R*Q(t) + (1/C) * ∫Q(t)dt
        # 其中Q(t)与glucose相关
        
        # 标准化输入
        glucose_norm = (glucose - np.mean(glucose)) / np.std(glucose)
        bp_norm = (bp - np.mean(bp)) / np.std(bp)
        
        def windkessel_model(params, glucose_input):
            R, C, glucose_gain = params
            
            # 模拟血流量Q与血糖的关系
            Q = glucose_gain * glucose_input
            
            # Windkessel方程数值积分
            bp_modeled = np.zeros_like(Q)
            integral_Q = 0
            dt = 1.0  # 时间步长
            
            for i in range(len(Q)):
                integral_Q += Q[i] * dt
                bp_modeled[i] = R * Q[i] + integral_Q / C
            
            return bp_modeled
        
        def objective(params):
            if any(p <= 0 for p in params[:2]):  # R和C必须为正
                return 1e6
            
            try:
                bp_predicted = windkessel_model(params, glucose_norm)
                mse = np.mean((bp_norm - bp_predicted) ** 2)
                return mse
            except:
                return 1e6
        
        # 参数优化
        try:
            initial_params = [1.0, 1.0, 0.5]  # [R, C, glucose_gain]
            bounds = [(0.1, 10), (0.1, 10), (-2, 2)]
            
            result = minimize(objective, initial_params, bounds=bounds, method='L-BFGS-B')
            
            if result.success:
                R_opt, C_opt, glucose_gain_opt = result.x
                
                # 计算模型拟合度
                bp_fitted = windkessel_model(result.x, glucose_norm)
                r_squared = 1 - np.var(bp_norm - bp_fitted) / np.var(bp_norm)
                
                return {
                    'peripheral_resistance': R_opt,
                    'compliance': C_opt,
                    'glucose_sensitivity': glucose_gain_opt,
                    'r_squared': r_squared,
                    'model_fit': 'good' if r_squared > 0.3 else 'poor'
                }
            else:
                return {'error': 'optimization_failed'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_autonomic_hr_coupling(self):
        """自主神经-心率耦合分析"""
        print("  Analyzing autonomic nervous system - heart rate coupling...")
        
        # 获取HRV和心率数据
        hrv_signals = []
        if 'hrv_sdnn' in self.synchronized_data.columns:
            hrv_signals.append('hrv_sdnn')
        if 'hrv_rmssd' in self.synchronized_data.columns:
            hrv_signals.append('hrv_rmssd')
        
        if not hrv_signals or 'ecg_heart_rate' not in self.synchronized_data.columns:
            return {'error': 'Required HRV or heart rate signals not available'}
        
        coupling_analysis = {
            'mechanism': 'autonomic_modulation',
            'sympathetic_activity': {},
            'parasympathetic_activity': {},
            'autonomic_balance': {},
            'coupling_strength': 0,
            'clinical_significance': 'unknown'
        }
        
        hr_data = self.synchronized_data['ecg_heart_rate'].values
        valid_hr_mask = ~np.isnan(hr_data)
        
        # 分析每个HRV指标与心率的耦合
        for hrv_signal in hrv_signals:
            hrv_data = self.synchronized_data[hrv_signal].values
            valid_mask = valid_hr_mask & ~np.isnan(hrv_data)
            
            if valid_mask.sum() < 10:
                continue
            
            hr_clean = hr_data[valid_mask]
            hrv_clean = hrv_data[valid_mask]
            
            # 1. 基础相关性
            correlation = pearsonr(hr_clean, hrv_clean)[0]
            
            # 2. 自主神经活动评估
            if 'sdnn' in hrv_signal:
                # SDNN主要反映整体自主神经活动
                if correlation < -0.3:
                    autonomic_state = 'preserved_modulation'
                elif correlation > -0.1:
                    autonomic_state = 'reduced_modulation'
                else:
                    autonomic_state = 'moderate_modulation'
                
                coupling_analysis['sympathetic_activity'][hrv_signal] = {
                    'correlation_with_hr': correlation,
                    'autonomic_state': autonomic_state,
                    'hrv_mean': np.mean(hrv_clean),
                    'hrv_variability': np.std(hrv_clean)
                }
            
            elif 'rmssd' in hrv_signal:
                # RMSSD主要反映副交感神经活动
                if correlation < -0.4:
                    parasympathetic_state = 'high_activity'
                elif correlation > -0.1:
                    parasympathetic_state = 'low_activity'
                else:
                    parasympathetic_state = 'moderate_activity'
                
                coupling_analysis['parasympathetic_activity'][hrv_signal] = {
                    'correlation_with_hr': correlation,
                    'parasympathetic_state': parasympathetic_state,
                    'hrv_mean': np.mean(hrv_clean),
                    'hrv_variability': np.std(hrv_clean)
                }
        
        # 3. 自主神经平衡评估
        if coupling_analysis['sympathetic_activity'] and coupling_analysis['parasympathetic_activity']:
            sdnn_corr = list(coupling_analysis['sympathetic_activity'].values())[0]['correlation_with_hr']
            rmssd_corr = list(coupling_analysis['parasympathetic_activity'].values())[0]['correlation_with_hr']
            
            # 计算自主神经平衡指数
            balance_index = abs(sdnn_corr) / (abs(sdnn_corr) + abs(rmssd_corr)) if (abs(sdnn_corr) + abs(rmssd_corr)) > 0 else 0.5
            
            coupling_analysis['autonomic_balance'] = {
                'balance_index': balance_index,
                'dominant_system': 'sympathetic' if balance_index > 0.6 else 'parasympathetic' if balance_index < 0.4 else 'balanced',
                'coupling_coherence': abs(sdnn_corr) * abs(rmssd_corr)  # 耦合一致性
            }
        
        # 4. 综合耦合强度
        all_correlations = []
        for activity_type in ['sympathetic_activity', 'parasympathetic_activity']:
            for signal_data in coupling_analysis[activity_type].values():
                all_correlations.append(abs(signal_data['correlation_with_hr']))
        
        coupling_analysis['coupling_strength'] = np.mean(all_correlations) if all_correlations else 0
        
        # 5. 临床意义
        coupling_strength = coupling_analysis['coupling_strength']
        
        if coupling_strength > 0.5:
            coupling_analysis['clinical_significance'] = 'preserved_autonomic_function'
        elif coupling_strength > 0.3:
            coupling_analysis['clinical_significance'] = 'mild_autonomic_dysfunction'
        elif coupling_strength > 0.1:
            coupling_analysis['clinical_significance'] = 'moderate_autonomic_dysfunction'
        else:
            coupling_analysis['clinical_significance'] = 'severe_autonomic_dysfunction'
        
        return coupling_analysis
    
    def _analyze_metabolic_circulatory_coupling(self):
        """代谢-循环耦合分析"""
        print("  Analyzing metabolic-circulatory coupling...")
        
        glucose = self.synchronized_data['cgm_glucose'].values
        hr = self.synchronized_data['ecg_heart_rate'].values
        map_bp = self.synchronized_data['abpm_map'].values
        
        valid_mask = ~(np.isnan(glucose) | np.isnan(hr) | np.isnan(map_bp))
        
        if valid_mask.sum() < 10:
            return {'error': 'Insufficient valid data for metabolic-circulatory analysis'}
        
        glucose_clean = glucose[valid_mask]
        hr_clean = hr[valid_mask]
        map_clean = map_bp[valid_mask]
        
        coupling_analysis = {
            'mechanism': 'fick_principle_based',
            'metabolic_demand': {},
            'circulatory_response': {},
            'coupling_efficiency': 0,
            'clinical_implications': 'unknown'
        }
        
        # 1. 代谢需求评估 (基于血糖水平)
        glucose_mean = np.mean(glucose_clean)
        glucose_variability = np.std(glucose_clean)
        
        # 根据血糖水平估算代谢状态
        if glucose_mean > 180:
            metabolic_state = 'hypermetabolic'
            metabolic_demand_index = 1.5
        elif glucose_mean < 70:
            metabolic_state = 'hypometabolic'
            metabolic_demand_index = 0.7
        else:
            metabolic_state = 'normal'
            metabolic_demand_index = 1.0
        
        coupling_analysis['metabolic_demand'] = {
            'glucose_mean': glucose_mean,
            'glucose_variability': glucose_variability,
            'metabolic_state': metabolic_state,
            'demand_index': metabolic_demand_index
        }
        
        # 2. 循环反应评估
        hr_mean = np.mean(hr_clean)
        map_mean = np.mean(map_clean)
        
        # 估算心输出量指数 (简化)
        cardiac_output_index = hr_mean * 0.07  # 简化估算，实际需要每搏量
        
        # 循环效率评估
        if 60 <= hr_mean <= 100 and 70 <= map_mean <= 100:
            circulatory_efficiency = 'optimal'
        elif hr_mean > 100 or map_mean > 100:
            circulatory_efficiency = 'hyperkinetic'
        else:
            circulatory_efficiency = 'hypokinetic'
        
        coupling_analysis['circulatory_response'] = {
            'heart_rate_mean': hr_mean,
            'map_mean': map_mean,
            'cardiac_output_index': cardiac_output_index,
            'efficiency_state': circulatory_efficiency
        }
        
        # 3. 代谢-循环耦合效率
        # 血糖变化与循环参数变化的相关性
        glucose_hr_corr = pearsonr(glucose_clean, hr_clean)[0]
        glucose_map_corr = pearsonr(glucose_clean, map_clean)[0]
        hr_map_corr = pearsonr(hr_clean, map_clean)[0]
        
        # 耦合效率综合评分
        coupling_efficiency = (abs(glucose_hr_corr) + abs(glucose_map_corr) + abs(hr_map_corr)) / 3
        coupling_analysis['coupling_efficiency'] = coupling_efficiency
        
        coupling_analysis['correlation_matrix'] = {
            'glucose_hr': glucose_hr_corr,
            'glucose_map': glucose_map_corr,
            'hr_map': hr_map_corr
        }
        
        # 4. 临床含义
        if coupling_efficiency > 0.5:
            if metabolic_state == 'normal' and circulatory_efficiency == 'optimal':
                coupling_analysis['clinical_implications'] = 'excellent_metabolic_circulatory_integration'
            else:
                coupling_analysis['clinical_implications'] = 'compensated_metabolic_circulatory_coupling'
        elif coupling_efficiency > 0.3:
            coupling_analysis['clinical_implications'] = 'suboptimal_metabolic_circulatory_coupling'
        else:
            coupling_analysis['clinical_implications'] = 'poor_metabolic_circulatory_integration'
        
        return coupling_analysis
    
    def _analyze_baroreflex_coupling(self):
        """压力感受器反射耦合分析"""
        print("  Analyzing baroreflex coupling...")
        
        sbp = self.synchronized_data['abpm_sbp'].values
        hrv_data = None
        
        # 选择最佳HRV指标
        if 'hrv_sdnn' in self.synchronized_data.columns:
            hrv_data = self.synchronized_data['hrv_sdnn'].values
            hrv_type = 'sdnn'
        elif 'hrv_rmssd' in self.synchronized_data.columns:
            hrv_data = self.synchronized_data['hrv_rmssd'].values
            hrv_type = 'rmssd'
        else:
            return {'error': 'No HRV data available for baroreflex analysis'}
        
        valid_mask = ~(np.isnan(sbp) | np.isnan(hrv_data))
        
        if valid_mask.sum() < 10:
            return {'error': 'Insufficient valid data for baroreflex analysis'}
        
        sbp_clean = sbp[valid_mask]
        hrv_clean = hrv_data[valid_mask]
        
        coupling_analysis = {
            'mechanism': 'arterial_baroreflex',
            'baroreflex_sensitivity': {},
            'coupling_pattern': 'unknown',
            'clinical_interpretation': 'unknown'
        }
        
        # 1. 压力感受器反射敏感性 (简化评估)
        # 正常情况下，血压升高应导致HRV增加（副交感激活）
        bp_hrv_correlation = pearsonr(sbp_clean, hrv_clean)[0]
        
        # 根据HRV类型调整解释
        if hrv_type == 'sdnn':
            # SDNN与血压的正相关可能表示压力感受器反射功能
            if bp_hrv_correlation > 0.3:
                baroreflex_function = 'preserved'
            elif bp_hrv_correlation > 0:
                baroreflex_function = 'reduced'
            else:
                baroreflex_function = 'impaired'
        else:  # RMSSD
            # RMSSD与血压的相关性更复杂
            if abs(bp_hrv_correlation) > 0.3:
                baroreflex_function = 'active'
            else:
                baroreflex_function = 'blunted'
        
        # 2. 动态压力感受器反射分析
        # 计算血压变化和HRV变化的同步性
        sbp_changes = np.diff(sbp_clean)
        hrv_changes = np.diff(hrv_clean)
        
        if len(sbp_changes) > 5:
            change_correlation = pearsonr(sbp_changes, hrv_changes)[0]
            
            # 滞后分析 - 压力感受器反射的时间延迟
            max_lag = min(12, len(sbp_changes) // 4)  # 最大1小时滞后
            lag_correlations = []
            
            for lag in range(1, max_lag + 1):
                if len(sbp_changes) > lag:
                    lag_corr = pearsonr(sbp_changes[:-lag], hrv_changes[lag:])[0]
                    lag_correlations.append((lag * 5, lag_corr))  # 5分钟间隔
            
            # 找到最佳滞后时间
            if lag_correlations:
                best_lag, best_lag_corr = max(lag_correlations, key=lambda x: abs(x[1]))
                
                coupling_analysis['baroreflex_sensitivity'] = {
                    'static_correlation': bp_hrv_correlation,
                    'dynamic_correlation': change_correlation,
                    'best_lag_minutes': best_lag,
                    'best_lag_correlation': best_lag_corr,
                    'baroreflex_function': baroreflex_function
                }
            else:
                coupling_analysis['baroreflex_sensitivity'] = {
                    'static_correlation': bp_hrv_correlation,
                    'dynamic_correlation': change_correlation,
                    'baroreflex_function': baroreflex_function
                }
        else:
            coupling_analysis['baroreflex_sensitivity'] = {
                'static_correlation': bp_hrv_correlation,
                'baroreflex_function': baroreflex_function
            }
        
        # 3. 耦合模式识别
        coupling_strength = abs(bp_hrv_correlation)
        
        if coupling_strength > 0.5:
            coupling_analysis['coupling_pattern'] = 'strong_baroreflex_coupling'
        elif coupling_strength > 0.3:
            coupling_analysis['coupling_pattern'] = 'moderate_baroreflex_coupling'
        else:
            coupling_analysis['coupling_pattern'] = 'weak_baroreflex_coupling'
        
        # 4. 临床解释
        if baroreflex_function == 'preserved' and coupling_strength > 0.4:
            coupling_analysis['clinical_interpretation'] = 'normal_baroreflex_function'
        elif baroreflex_function == 'reduced' or coupling_strength < 0.3:
            coupling_analysis['clinical_interpretation'] = 'baroreflex_dysfunction'
        elif coupling_strength < 0.1:
            coupling_analysis['clinical_interpretation'] = 'severe_baroreflex_impairment'
        else:
            coupling_analysis['clinical_interpretation'] = 'indeterminate_baroreflex_function'
        
        return coupling_analysis
    
    def _analyze_cross_system_coordination(self):
        """跨系统协调性分析"""
        print("  Analyzing cross-system coordination...")
        
        coordination_analysis = {
            'overall_coordination_index': 0,
            'pairwise_coordination': {},
            'system_synchrony': {},
            'coordination_patterns': []
        }
        
        # 获取所有可用信号
        available_signals = [col for col in self.synchronized_data.columns if col != 'timestamp']
        
        if len(available_signals) < 2:
            return {'error': 'Insufficient signals for coordination analysis'}
        
        # 系统分组
        system_groups = {
            'metabolic': [col for col in available_signals if 'cgm' in col],
            'cardiac': [col for col in available_signals if 'ecg' in col or 'hrv' in col],
            'vascular': [col for col in available_signals if 'abpm' in col]
        }
        
        # 计算系统内和系统间协调性
        for system1, signals1 in system_groups.items():
            if not signals1:
                continue
                
            for system2, signals2 in system_groups.items():
                if system2 <= system1 or not signals2:  # 避免重复计算
                    continue
                
                system_pair = f"{system1}_{system2}"
                pair_correlations = []
                
                for sig1 in signals1:
                    data1 = self.synchronized_data[sig1].values
                    valid_mask1 = ~np.isnan(data1)
                    
                    for sig2 in signals2:
                        data2 = self.synchronized_data[sig2].values
                        valid_mask = valid_mask1 & ~np.isnan(data2)
                        
                        if valid_mask.sum() > 10:
                            corr = pearsonr(data1[valid_mask], data2[valid_mask])[0]
                            pair_correlations.append(abs(corr))
                
                if pair_correlations:
                    avg_correlation = np.mean(pair_correlations)
                    coordination_analysis['pairwise_coordination'][system_pair] = {
                        'average_correlation': avg_correlation,
                        'max_correlation': max(pair_correlations),
                        'coordination_strength': 'strong' if avg_correlation > 0.5 else 'moderate' if avg_correlation > 0.3 else 'weak'
                    }
        
        # 计算整体协调指数
        if coordination_analysis['pairwise_coordination']:
            all_correlations = [coord['average_correlation'] for coord in coordination_analysis['pairwise_coordination'].values()]
            coordination_analysis['overall_coordination_index'] = np.mean(all_correlations)
        
        # 识别协调模式
        coordination_index = coordination_analysis['overall_coordination_index']
        
        if coordination_index > 0.6:
            coordination_analysis['coordination_patterns'].append('high_inter_system_synchrony')
        elif coordination_index > 0.4:
            coordination_analysis['coordination_patterns'].append('moderate_inter_system_coordination')
        else:
            coordination_analysis['coordination_patterns'].append('poor_inter_system_coordination')
        
        return coordination_analysis
    
    def calculate_integrated_brittleness_score(self):
        """
        计算整合脆性评分 - 基于多模态生理耦合的综合评估
        
        Returns:
        --------
        dict : 整合脆性分析结果
        """
        print("Calculating integrated brittleness score...")
        
        if not hasattr(self, 'coupling_results'):
            raise ValueError("Coupling analysis not performed. Run analyze_physiological_coupling() first")
        
        brittleness_components = {
            'glucose_brittleness': 0,
            'cardiac_brittleness': 0,
            'autonomic_brittleness': 0,
            'vascular_brittleness': 0,
            'coupling_dysfunction_bonus': 0,
            'complexity_score': 0
        }
        
        # 1. 单模态脆性评估
        brittleness_components.update(self._assess_individual_modal_brittleness())
        
        # 2. 耦合功能障碍评分
        brittleness_components['coupling_dysfunction_bonus'] = self._assess_coupling_dysfunction()
        
        # 3. 系统复杂性评分
        brittleness_components['complexity_score'] = self._assess_system_complexity()
        
        # 4. 综合脆性评分计算
        base_weights = self.config['brittleness_model']['base_weights']
        complexity_factors = self.config['brittleness_model']['complexity_factors']
        
        # 基础加权评分
        base_score = (
            brittleness_components['glucose_brittleness'] * base_weights['glucose_brittleness'] +
            brittleness_components['cardiac_brittleness'] * base_weights['cardiac_brittleness'] +
            brittleness_components['autonomic_brittleness'] * base_weights['autonomic_brittleness'] +
            brittleness_components['vascular_brittleness'] * base_weights['vascular_brittleness']
        ) * 100
        
        # 复杂性加成
        complexity_bonus = brittleness_components['complexity_score'] * sum(complexity_factors.values()) * 20
        
        # 耦合功能障碍加成
        coupling_bonus = brittleness_components['coupling_dysfunction_bonus']
        
        # 总评分
        integrated_score = min(100, base_score + complexity_bonus + coupling_bonus)
        
        # 5. 脆性类型确定
        integrated_type = self._determine_integrated_brittleness_type(integrated_score)
        
        # 6. 风险分层
        risk_level = self._determine_risk_stratification(integrated_score)
        
        # 7. 生成结果
        integrated_result = {
            'integrated_brittleness_score': {
                'total_score': round(integrated_score, 1),
                'brittleness_type': integrated_type,
                'risk_level': risk_level,
                'confidence_level': self._assess_confidence_level()
            },
            'score_components': {
                'base_score': round(base_score, 1),
                'complexity_bonus': round(complexity_bonus, 1),
                'coupling_bonus': round(coupling_bonus, 1),
                'component_breakdown': brittleness_components
            },
            'physiological_assessment': self._generate_physiological_assessment(brittleness_components),
            'clinical_recommendations': self._generate_clinical_recommendations(integrated_score, integrated_type),
            'therapeutic_targets': self._identify_therapeutic_targets(brittleness_components)
        }
        
        print(f"✓ Integrated brittleness score: {integrated_score:.1f}/100")
        print(f"✓ Brittleness type: {integrated_type}")
        print(f"✓ Risk level: {risk_level}")
        
        return integrated_result
    
    def _assess_individual_modal_brittleness(self):
        """评估单模态脆性"""
        modal_brittleness = {}
        
        # 血糖脆性评估
        if 'cgm_glucose' in self.synchronized_data.columns:
            glucose_data = self.synchronized_data['cgm_glucose'].dropna()
            if len(glucose_data) > 10:
                glucose_cv = (glucose_data.std() / glucose_data.mean()) * 100
                glucose_instability = min(1.0, glucose_cv / 40)  # 标准化到0-1
                modal_brittleness['glucose_brittleness'] = glucose_instability
            else:
                modal_brittleness['glucose_brittleness'] = 0.5
        else:
            modal_brittleness['glucose_brittleness'] = 0
        
        # 心脏脆性评估
        cardiac_signals = [col for col in self.synchronized_data.columns if 'ecg' in col or 'hrv' in col]
        if cardiac_signals:
            cardiac_variabilities = []
            for signal in cardiac_signals:
                signal_data = self.synchronized_data[signal].dropna()
                if len(signal_data) > 10:
                    signal_cv = (signal_data.std() / abs(signal_data.mean())) if signal_data.mean() != 0 else 1
                    cardiac_variabilities.append(min(1.0, signal_cv))
            
            modal_brittleness['cardiac_brittleness'] = np.mean(cardiac_variabilities) if cardiac_variabilities else 0.5
        else:
            modal_brittleness['cardiac_brittleness'] = 0
        
        # 自主神经脆性评估
        if hasattr(self, 'coupling_results') and 'autonomic_hr_coupling' in self.coupling_results:
            autonomic_coupling = self.coupling_results['autonomic_hr_coupling']
            coupling_strength = autonomic_coupling.get('coupling_strength', 0)
            modal_brittleness['autonomic_brittleness'] = 1 - coupling_strength  # 耦合强度低 = 脆性高
        else:
            modal_brittleness['autonomic_brittleness'] = 0.5
        
        # 血管脆性评估
        if 'abpm_sbp' in self.synchronized_data.columns:
            sbp_data = self.synchronized_data['abpm_sbp'].dropna()
            if len(sbp_data) > 10:
                sbp_cv = (sbp_data.std() / sbp_data.mean()) * 100
                vascular_instability = min(1.0, sbp_cv / 20)  # 标准化到0-1
                modal_brittleness['vascular_brittleness'] = vascular_instability
            else:
                modal_brittleness['vascular_brittleness'] = 0.5
        else:
            modal_brittleness['vascular_brittleness'] = 0
        
        return modal_brittleness
    
    def _assess_coupling_dysfunction(self):
        """评估耦合功能障碍"""
        if not hasattr(self, 'coupling_results'):
            return 0
        
        dysfunction_score = 0
        coupling_bonus = self.config['brittleness_model']['coupling_bonus']
        
        # 评估各种耦合的功能障碍程度
        for coupling_type, coupling_data in self.coupling_results.items():
            if coupling_type == 'cross_system_coordination':
                continue
                
            if isinstance(coupling_data, dict) and 'coupling_strength' in coupling_data:
                coupling_strength = coupling_data['coupling_strength']
                
                # 根据耦合强度评估功能障碍
                if coupling_strength < 0.2:
                    dysfunction_score += coupling_bonus['strong_coupling']  # 严重功能障碍
                elif coupling_strength < 0.4:
                    dysfunction_score += coupling_bonus['moderate_coupling']  # 中度功能障碍
                elif coupling_strength < 0.6:
                    dysfunction_score += coupling_bonus['weak_coupling']  # 轻度功能障碍
        
        return min(25, dysfunction_score)  # 最大25分的功能障碍加成
    
    def _assess_system_complexity(self):
        """评估系统复杂性"""
        complexity_score = 0
        
        # 1. 信号数量复杂性
        signal_count = len([col for col in self.synchronized_data.columns if col != 'timestamp'])
        signal_complexity = min(1.0, signal_count / 10)  # 标准化
        
        # 2. 时间序列复杂性 (使用近似熵)
        if NOLDS_AVAILABLE:
            entropy_scores = []
            for col in self.synchronized_data.columns[1:]:  # 跳过timestamp
                data = self.synchronized_data[col].dropna()
                if len(data) > 50:
                    try:
                        approx_entropy = nolds.sampen(data.values)
                        entropy_scores.append(min(1.0, approx_entropy / 2))  # 标准化
                    except:
                        continue
            
            entropy_complexity = np.mean(entropy_scores) if entropy_scores else 0.5
        else:
            # 使用简单的变异系数作为复杂性指标
            cv_scores = []
            for col in self.synchronized_data.columns[1:]:
                data = self.synchronized_data[col].dropna()
                if len(data) > 10 and data.mean() != 0:
                    cv = data.std() / abs(data.mean())
                    cv_scores.append(min(1.0, cv))
            
            entropy_complexity = np.mean(cv_scores) if cv_scores else 0.5
        
        # 3. 系统间相互作用复杂性
        if hasattr(self, 'coupling_results') and 'cross_system_coordination' in self.coupling_results:
            coordination_index = self.coupling_results['cross_system_coordination'].get('overall_coordination_index', 0)
            interaction_complexity = 1 - coordination_index  # 协调性低 = 复杂性高
        else:
            interaction_complexity = 0.5
        
        # 综合复杂性评分
        complexity_factors = self.config['brittleness_model']['complexity_factors']
        complexity_score = (
            entropy_complexity * complexity_factors['entropy_weight'] +
            interaction_complexity * complexity_factors['synchrony_weight'] +
            signal_complexity * 0.2
        )
        
        return min(1.0, complexity_score)
    
    def _determine_integrated_brittleness_type(self, score):
        """确定整合脆性类型"""
        risk_thresholds = self.config['clinical_decision_rules']['risk_stratification']
        
        for risk_level, (min_score, max_score) in risk_thresholds.items():
            if min_score <= score < max_score:
                type_mapping = {
                    'very_low': 'I型_多系统稳定',
                    'low': 'II型_轻度多系统不稳定',
                    'moderate': 'III型_中度多系统脆性',
                    'high': 'IV型_重度多系统脆性',
                    'very_high': 'V型_极重度多系统脆性',
                    'critical': 'VI型_危重多系统衰竭'
                }
                return type_mapping.get(risk_level, 'Unknown')
        
        return 'VI型_危重多系统衰竭'
    
    def _determine_risk_stratification(self, score):
        """确定风险分层"""
        risk_thresholds = self.config['clinical_decision_rules']['risk_stratification']
        
        for risk_level, (min_score, max_score) in risk_thresholds.items():
            if min_score <= score < max_score:
                return risk_level
        
        return 'critical'
    
    def _assess_confidence_level(self):
        """评估分析置信度"""
        confidence_factors = []
        
        # 数据质量置信度
        if hasattr(self, 'data_quality_report'):
            quality_scores = [metrics['quality_score'] for metrics in self.data_quality_report.values()]
            data_confidence = np.mean(quality_scores)
            confidence_factors.append(data_confidence)
        
        # 模态完整性置信度
        available_modalities = len(self.raw_data)
        modality_confidence = available_modalities / 4  # 总共4个模态
        confidence_factors.append(modality_confidence)
        
        # 分析完整性置信度
        if hasattr(self, 'coupling_results'):
            analysis_completeness = len(self.coupling_results) / 5  # 预期5种耦合分析
            confidence_factors.append(analysis_completeness)
        else:
            confidence_factors.append(0.5)
        
        overall_confidence = np.mean(confidence_factors)
        
        if overall_confidence >= 0.8:
            return 'high'
        elif overall_confidence >= 0.6:
            return 'moderate'
        else:
            return 'low'
    
    def _generate_physiological_assessment(self, components):
        """生成生理学评估"""
        assessment = {
            'primary_dysfunction_systems': [],
            'secondary_affected_systems': [],
            'pathophysiological_mechanisms': [],
            'system_interactions': {}
        }
        
        # 识别主要和次要功能障碍系统
        system_scores = {
            'glucose_metabolism': components['glucose_brittleness'],
            'cardiac_function': components['cardiac_brittleness'],
            'autonomic_control': components['autonomic_brittleness'],
            'vascular_regulation': components['vascular_brittleness']
        }
        
        sorted_systems = sorted(system_scores.items(), key=lambda x: x[1], reverse=True)
        
        for system, score in sorted_systems:
            if score > 0.7:
                assessment['primary_dysfunction_systems'].append(system)
            elif score > 0.4:
                assessment['secondary_affected_systems'].append(system)
        
        # 病理生理机制推断
        if components['glucose_brittleness'] > 0.6:
            assessment['pathophysiological_mechanisms'].append('glucose_homeostasis_disruption')
        
        if components['vascular_brittleness'] > 0.6:
            assessment['pathophysiological_mechanisms'].append('vascular_dysregulation')
        
        if components['autonomic_brittleness'] > 0.6:
            assessment['pathophysiological_mechanisms'].append('autonomic_nervous_system_dysfunction')
        
        if components['cardiac_brittleness'] > 0.6:
            assessment['pathophysiological_mechanisms'].append('cardiac_electrical_instability')
        
        # 系统间相互作用
        if hasattr(self, 'coupling_results'):
            for coupling_type, coupling_data in self.coupling_results.items():
                if isinstance(coupling_data, dict) and 'coupling_strength' in coupling_data:
                    assessment['system_interactions'][coupling_type] = {
                        'strength': coupling_data['coupling_strength'],
                        'pattern': coupling_data.get('coupling_pattern', 'unknown')
                    }
        
        return assessment
    
    def _generate_clinical_recommendations(self, score, brittleness_type):
        """生成临床建议"""
        recommendations = {
            'immediate_actions': [],
            'monitoring_strategies': [],
            'therapeutic_interventions': [],
            'lifestyle_modifications': [],
            'follow_up_schedule': {}
        }
        
        # 基于评分的即时行动建议
        if score >= 90:
            recommendations['immediate_actions'].extend([
                '紧急多学科会诊',
                '连续多参数监测',
                '重症监护评估',
                '器官功能支持'
            ])
        elif score >= 75:
            recommendations['immediate_actions'].extend([
                '多学科团队评估',
                '强化监测方案',
                '治疗方案紧急调整'
            ])
        elif score >= 55:
            recommendations['immediate_actions'].extend([
                '专科医师会诊',
                '治疗方案优化',
                '监测频率调整'
            ])
        
        # 监测策略
        intervention_thresholds = self.config['clinical_decision_rules']['intervention_thresholds']
        
        for system, threshold in intervention_thresholds.items():
            if score >= threshold:
                system_monitoring = {
                    'glucose_instability': '连续血糖监测',
                    'cardiac_dysfunction': '动态心电图监测',
                    'autonomic_failure': '心率变异性评估',
                    'vascular_dysfunction': '动态血压监测'
                }
                
                if system in system_monitoring:
                    recommendations['monitoring_strategies'].append(system_monitoring[system])
        
        # 治疗干预
        if score >= 70:
            recommendations['therapeutic_interventions'].extend([
                '多系统功能支持',
                '个体化药物方案',
                '并发症预防'
            ])
        elif score >= 50:
            recommendations['therapeutic_interventions'].extend([
                '靶向治疗优化',
                '系统功能保护',
                '风险因子控制'
            ])
        else:
            recommendations['therapeutic_interventions'].extend([
                '预防性治疗',
                '生活方式干预',
                '定期评估'
            ])
        
        # 生活方式建议
        recommendations['lifestyle_modifications'] = [
            '规律作息时间',
            '适度体力活动',
            '营养均衡饮食',
            '压力管理',
            '睡眠质量改善',
            '戒烟限酒'
        ]
        
        # 随访计划
        if score >= 90:
            recommendations['follow_up_schedule'] = {
                '急性期': '连续监测',
                '稳定期': '每日评估',
                '长期随访': '每周'
            }
        elif score >= 75:
            recommendations['follow_up_schedule'] = {
                '调整期': '每日',
                '稳定期': '每周',
                '长期随访': '每月'
            }
        elif score >= 55:
            recommendations['follow_up_schedule'] = {
                '调整期': '每周',
                '稳定期': '每月',
                '长期随访': '每季度'
            }
        else:
            recommendations['follow_up_schedule'] = {
                '常规随访': '每月',
                '长期维护': '每季度'
            }
        
        return recommendations
    
    def _identify_therapeutic_targets(self, components):
        """识别治疗目标"""
        targets = {
            'primary_targets': [],
            'secondary_targets': [],
            'target_parameters': {}
        }
        
        # 基于各系统脆性程度确定治疗目标优先级
        system_priorities = [
            ('glucose_brittleness', '血糖稳定性'),
            ('vascular_brittleness', '血压变异性控制'),
            ('cardiac_brittleness', '心律稳定性'),
            ('autonomic_brittleness', '自主神经功能')
        ]
        
        for system, target_name in system_priorities:
            score = components.get(system, 0)
            
            if score > 0.7:
                targets['primary_targets'].append(target_name)
            elif score > 0.4:
                targets['secondary_targets'].append(target_name)
        
        # 具体参数目标
        if components.get('glucose_brittleness', 0) > 0.5:
            targets['target_parameters']['glucose'] = {
                'target_range': '70-180 mg/dL',
                'cv_target': '<36%',
                'tir_target': '>70%'
            }
        
        if components.get('vascular_brittleness', 0) > 0.5:
            targets['target_parameters']['blood_pressure'] = {
                'sbp_target': '<140 mmHg',
                'dbp_target': '<90 mmHg',
                'variability_reduction': '>20%'
            }
        
        if components.get('cardiac_brittleness', 0) > 0.5:
            targets['target_parameters']['cardiac'] = {
                'resting_hr': '60-100 bpm',
                'hrv_improvement': '>15%',
                'rhythm_stability': 'maintain'
            }
        
        return targets
    
    def generate_comprehensive_report(self):
        """
        生成综合多模态分析报告
        
        Returns:
        --------
        dict : 完整的多模态整合分析报告
        """
        print("Generating comprehensive multimodal analysis report...")
        
        try:
            # 执行完整分析流程
            
            # 1. 数据同步
            if self.synchronized_data is None:
                sync_result = self.synchronize_multimodal_data()
            else:
                sync_result = {'success': True, 'note': 'Data already synchronized'}
            
            # 2. 生理耦合分析
            if not hasattr(self, 'coupling_results'):
                coupling_results = self.analyze_physiological_coupling()
            else:
                coupling_results = self.coupling_results
            
            # 3. 整合脆性评分
            brittleness_results = self.calculate_integrated_brittleness_score()
            
            # 4. 生成最终报告
            comprehensive_report = {
                'report_metadata': {
                    'patient_id': self.patient_id,
                    'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'analyzer_version': 'Multi-Modal Integration Analyzer v5.0 Enhanced',
                    'analysis_duration_minutes': 'estimated'
                },
                
                'data_summary': {
                    'available_modalities': list(self.raw_data.keys()),
                    'data_quality_assessment': getattr(self, 'data_quality_report', {}),
                    'synchronization_results': sync_result,
                    'temporal_coverage': self._calculate_temporal_coverage()
                },
                
                'physiological_coupling_analysis': {
                    'coupling_mechanisms': coupling_results,
                    'cross_system_interactions': self._summarize_cross_system_interactions(),
                    'coupling_strength_matrix': self._generate_coupling_matrix()
                },
                
                'integrated_brittleness_assessment': brittleness_results,
                
                'clinical_decision_support': {
                    'risk_stratification': brittleness_results['integrated_brittleness_score']['risk_level'],
                    'immediate_clinical_actions': brittleness_results['clinical_recommendations']['immediate_actions'],
                    'monitoring_recommendations': brittleness_results['clinical_recommendations']['monitoring_strategies'],
                    'therapeutic_priorities': brittleness_results['therapeutic_targets']['primary_targets']
                },
                
                'longitudinal_insights': self._generate_longitudinal_insights(),
                
                'quality_assurance': {
                    'analysis_confidence': brittleness_results['integrated_brittleness_score']['confidence_level'],
                    'data_limitations': self._identify_data_limitations(),
                    'clinical_validation_notes': self._generate_validation_notes()
                },
                
                'executive_summary': self._generate_executive_summary(brittleness_results)
            }
            
            # 保存分析结果
            self.comprehensive_report = comprehensive_report
            
            print("✓ Comprehensive multimodal analysis report generated successfully")
            
            return comprehensive_report
            
        except Exception as e:
            error_report = {
                'error': str(e),
                'patient_id': self.patient_id,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'available_data': list(self.raw_data.keys()) if hasattr(self, 'raw_data') else [],
                'analysis_stage': 'comprehensive_report_generation'
            }
            
            print(f"✗ Error generating comprehensive report: {e}")
            return error_report
    
    def _calculate_temporal_coverage(self):
        """计算时间覆盖范围"""
        if not self.raw_data:
            return {}
        
        coverage = {}
        for modality, data in self.raw_data.items():
            start_time = data['timestamp'].min()
            end_time = data['timestamp'].max()
            duration_hours = (end_time - start_time).total_seconds() / 3600
            
            coverage[modality] = {
                'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration_hours': round(duration_hours, 2),
                'data_points': len(data)
            }
        
        return coverage
    
    def _summarize_cross_system_interactions(self):
        """总结跨系统相互作用"""
        if not hasattr(self, 'coupling_results'):
            return {}
        
        interactions = {}
        for coupling_type, coupling_data in self.coupling_results.items():
            if isinstance(coupling_data, dict) and 'coupling_strength' in coupling_data:
                interactions[coupling_type] = {
                    'strength': coupling_data['coupling_strength'],
                    'clinical_significance': coupling_data.get('clinical_significance', 'unknown'),
                    'mechanism': coupling_data.get('mechanism', 'unknown')
                }
        
        return interactions
    
    def _generate_coupling_matrix(self):
        """生成耦合强度矩阵"""
        systems = ['glucose', 'cardiac', 'autonomic', 'vascular']
        matrix = {}
        
        if hasattr(self, 'coupling_results'):
            coupling_map = {
                'glucose_bp_coupling': ('glucose', 'vascular'),
                'autonomic_hr_coupling': ('autonomic', 'cardiac'),
                'metabolic_circulatory_coupling': ('glucose', 'cardiac'),
                'baroreflex_coupling': ('vascular', 'autonomic')
            }
            
            for coupling_type, (sys1, sys2) in coupling_map.items():
                if coupling_type in self.coupling_results:
                    strength = self.coupling_results[coupling_type].get('coupling_strength', 0)
                    
                    if sys1 not in matrix:
                        matrix[sys1] = {}
                    if sys2 not in matrix:
                        matrix[sys2] = {}
                    
                    matrix[sys1][sys2] = strength
                    matrix[sys2][sys1] = strength  # 对称矩阵
        
        return matrix
    
    def _generate_longitudinal_insights(self):
        """生成纵向分析洞察"""
        insights = {
            'trend_analysis': 'insufficient_data_for_trend_analysis',
            'pattern_recognition': [],
            'predictive_indicators': []
        }
        
        # 简化版本的纵向分析
        if self.synchronized_data is not None and len(self.synchronized_data) > 100:
            # 检查数据趋势
            for col in self.synchronized_data.columns[1:]:
                data = self.synchronized_data[col].dropna()
                if len(data) > 50:
                    # 简单的趋势检测
                    x = np.arange(len(data))
                    slope, _, _, p_value, _ = stats.linregress(x, data)
                    
                    if p_value < 0.05:  # 显著趋势
                        trend_direction = 'increasing' if slope > 0 else 'decreasing'
                        insights['pattern_recognition'].append({
                            'signal': col,
                            'trend': trend_direction,
                            'significance': 'significant'
                        })
        
        return insights
    
    def _identify_data_limitations(self):
        """识别数据限制"""
        limitations = []
        
        if hasattr(self, 'data_quality_report'):
            for modality, quality in self.data_quality_report.items():
                if quality['quality_score'] < 0.7:
                    limitations.append(f"{modality}_data_quality_suboptimal")
                
                if quality['duration_hours'] < 12:
                    limitations.append(f"{modality}_insufficient_duration")
        
        if len(self.raw_data) < 3:
            limitations.append('limited_multimodal_coverage')
        
        return limitations
    
    def _generate_validation_notes(self):
        """生成验证说明"""
        notes = [
            "Analysis based on established physiological coupling mechanisms",
            "Results require clinical correlation and expert interpretation",
            "Recommendations are for clinical decision support only",
            "Individual patient factors may influence interpretation"
        ]
        
        if hasattr(self, 'data_quality_report'):
            avg_quality = np.mean([q['quality_score'] for q in self.data_quality_report.values()])
            if avg_quality < 0.8:
                notes.append("Lower data quality may affect analysis reliability")
        
        return notes
    
    def _generate_executive_summary(self, brittleness_results):
        """生成执行摘要"""
        score = brittleness_results['integrated_brittleness_score']['total_score']
        risk_level = brittleness_results['integrated_brittleness_score']['risk_level']
        brittleness_type = brittleness_results['integrated_brittleness_score']['brittleness_type']
        
        summary = {
            'key_findings': [
                f"多系统整合脆性评分: {score}/100",
                f"脆性类型: {brittleness_type}",
                f"风险等级: {risk_level}"
            ],
            'critical_points': [],
            'immediate_priorities': brittleness_results['clinical_recommendations']['immediate_actions'][:3],
            'overall_assessment': self._determine_overall_assessment(score, risk_level)
        }
        
        # 添加关键发现
        if score >= 75:
            summary['critical_points'].append('多系统功能严重不稳定，需要紧急干预')
        
        if hasattr(self, 'coupling_results'):
            strong_couplings = [k for k, v in self.coupling_results.items() 
                              if isinstance(v, dict) and v.get('coupling_strength', 0) > 0.6]
            if strong_couplings:
                summary['critical_points'].append(f'检测到强生理耦合: {len(strong_couplings)}个系统间强相互作用')
        
        return summary
    
    def _determine_overall_assessment(self, score, risk_level):
        """确定整体评估"""
        if score >= 90:
            return 'critical_multi_system_failure_risk'
        elif score >= 75:
            return 'severe_multi_system_instability'
        elif score >= 55:
            return 'moderate_multi_system_dysfunction'
        elif score >= 35:
            return 'mild_multi_system_instability'
        else:
            return 'stable_multi_system_function'


def main():
    """
    Multi-Modal Integration Analyzer 主程序演示
    """
    print("=" * 70)
    print("Multi-Modal Integration Analyzer v5.0 Enhanced")
    print("多模态生理信号整合分析系统")
    print("=" * 70)
    
    # 创建分析器实例
    analyzer = MultiModalIntegrationAnalyzer(
        patient_id="ENHANCED_DEMO_001",
        config={
            'synchronization': {
                'target_frequency_min': 5,
                'interpolation_method': 'cubic'
            },
            'brittleness_model': {
                'base_weights': {
                    'glucose_brittleness': 0.25,
                    'cardiac_brittleness': 0.25,
                    'autonomic_brittleness': 0.25,
                    'vascular_brittleness': 0.25
                }
            }
        }
    )
    
    print("\n✓ Enhanced Multi-Modal Integration Analyzer initialized successfully!")
    
    print(f"\n📋 System Capabilities:")
    print(f"   • Advanced physiological coupling modeling")
    print(f"   • Windkessel model for glucose-BP coupling")
    print(f"   • Autonomic nervous system assessment")
    print(f"   • Baroreflex sensitivity analysis")
    print(f"   • Multi-scale entropy analysis")
    print(f"   • Machine learning pattern recognition")
    print(f"   • Clinical decision support")
    
    print(f"\n🔬 Analysis Pipeline:")
    print(f"   1. Load multimodal data (CGM, ECG, HRV, ABPM)")
    print(f"   2. Advanced temporal synchronization")
    print(f"   3. Physiological coupling analysis")
    print(f"   4. Integrated brittleness scoring")
    print(f"   5. Comprehensive clinical report")
    
    print(f"\n💡 Usage Example:")
    print(f"   analyzer.load_multimodal_data(")
    print(f"       cgm_data='patient_cgm.xlsx',")
    print(f"       ecg_data='patient_ecg.csv',")
    print(f"       hrv_data='patient_hrv.xlsx',")
    print(f"       abpm_data='patient_abpm.xlsx'")
    print(f"   )")
    print(f"   ")
    print(f"   report = analyzer.generate_comprehensive_report()")
    
    print(f"\n🏥 Clinical Applications:")
    print(f"   • Diabetes + cardiovascular comorbidities")
    print(f"   • ICU multi-organ monitoring")
    print(f"   • Chronic disease management")
    print(f"   • Precision medicine")

if __name__ == "__main__":
    main()