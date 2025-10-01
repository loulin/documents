"""
统一配置中心
集中管理所有算法参数、阈值和绘图设置
"""

class Config:
    # --- 绘图和通用设置 ---
    class General:
        # 优先使用这些字体, 如果找不到则使用系统默认
        FONT_LIST = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
        # 机器学习和随机过程的种子, 确保结果可复现
        RANDOM_STATE = 42

    # --- 1. 统计学异常检测参数 ---
    class Statistical:
        Z_SCORE_THRESHOLD = 2.5  # Z-score阈值
        IQR_MULTIPLIER = 1.5     # IQR乘数
        MAD_THRESHOLD = 3.5      # 修正Z-score的MAD阈值

    # --- 2. 模式识别异常检测参数 ---
    class Pattern:
        FLAT_TOLERANCE = 0.5      # 平台模式的血糖波动容忍度 (mg/dL)
        FLAT_MIN_LENGTH = 6       # 平台模式的最短持续点数
        OSCILLATION_STD_MULTIPLIER = 2.0 # 锯齿波(振荡)检测的二阶差分标准差倍数
        TREND_CHANGE_THRESHOLD = 2.0   # 趋势突变阈值 (mg/dL/min)
        AUTOCORR_PEAK_HEIGHT_RATIO = 0.3 # 周期性检测的自相关峰值高度比例
        AUTOCORR_MAX_PEAKS = 3         # 周期性检测中, 短周期内的最大峰值数

    # --- 3. 频域分析异常检测参数 ---
    class Frequency:
        HIGH_FREQ_ENERGY_RATIO = 0.15  # 高频能量占比阈值
        WINDOW_HIGH_FREQ_RATIO = 0.2   # 滑动窗口内的高频能量占比阈值
        PEAK_HEIGHT_RATIO = 0.1        # 异常周期信号的峰值高度比例
        PERIODIC_ANOMALY_MIN_MINUTES = 5 # 异常周期的最短时间 (分钟)
        PERIODIC_ANOMALY_MAX_MINUTES = 20# 异常周期的最长时间 (分钟)

    # --- 4. 机器学习异常检测参数 ---
    class MachineLearning:
        # Isolation Forest中异常数据比例的估计值
        CONTAMINATION = 0.1

    # --- 5. 生理学约束检验参数 ---
    class Physiological:
        ABSOLUTE_MIN_GLUCOSE = 20    # 绝对生理下限 (mg/dL)
        ABSOLUTE_MAX_GLUCOSE = 600   # 绝对生理上限 (mg/dL)
        EXTREME_MIN_GLUCOSE = 40     # 极端低血糖阈值 (mg/dL)
        EXTREME_MAX_GLUCOSE = 400    # 极端高血糖阈值 (mg/dL)
        EXTREME_RATE_OF_CHANGE = 15.0 # 极速变化率 (mg/dL/min)
        SUSTAINED_HIGH_GLUCOSE = 300 # 持续高血糖阈值
        SUSTAINED_HIGH_MIN_LENGTH = 6  # 持续高血糖的最短点数
        SUSTAINED_LOW_GLUCOSE = 60   # 持续低血糖阈值
        SUSTAINED_LOW_MIN_LENGTH = 4   # 持续低血糖的最短点数
        REPEATED_VALUE_RATIO = 0.1   # 单一数值点位占比超过该比例则认为异常

    # --- 6. 综合检测投票阈值 ---
    class Ensemble:
        HIGH_CONFIDENCE_VOTES = 3 # 高置信度所需的最少方法投票数
        MEDIUM_CONFIDENCE_VOTES = 2 # 中置信度所需的最少方法投票数

    # --- 7. 时间序列分析参数 ---
    class Temporal:
        MIN_INTERVAL_MINUTES = 2      # 合理的最小时间间隔(分钟)
        MAX_INTERVAL_MINUTES = 60     # 合理的最大时间间隔(分钟)
        PREDICTION_ERROR_THRESHOLD = 50 # 简单时序预测的误差阈值 (mg/dL)
        LOCAL_Z_SCORE_THRESHOLD = 3   # 局部窗口Z-score异常阈值

    # --- 7. 约束优化分析参数 ---
    class Optimization:
        # 各方法在优化阶段的基础权重
        METHOD_WEIGHTS = {
            'statistical': 0.15,
            'pattern_based': 0.20,
            'frequency': 0.08,
            'ml_based': 0.15,
            'physiological': 0.30,
            'temporal': 0.12
        }
        # 最终确认异常的综合评分阈值
        FINAL_SCORE_THRESHOLD = 0.15

        # 上下文评分调整因子
        class ContextScores:
            LUNCH_HIGH_GLUCOSE = 0.6      # 午餐后生理性高血糖
            DINNER_HIGH_GLUCOSE = 0.7     # 晚餐后生理性高血糖
            NIGHT_STABLE_GLUCOSE = 0.5    # 夜间稳定期
            NIGHT_LOW_GLUCOSE = 1.4       # 夜间低血糖, 提高关注度
            NEIGHBORHOOD_STABLE = 1.2     # 邻域稳定, 异常更可信
            NEIGHBORHOOD_UNSTABLE = 0.8   # 邻域不稳定, 可能是噪声

        # 约束规则评分调整因子
        class ConstraintScores:
            STAT_IN_PHYSIO_RANGE = 0.5 # 统计异常但在生理范围内
            NIGHT_PATTERN_ANOMALY = 0.3  # 夜间模式异常, 可能是正常稳定
            PHYSIO_METHOD_BOOST = 1.5    # 提高生理学检测的权威性
            ML_NEEDS_SUPPORT = 0.8       # ML方法需要其他方法支持
