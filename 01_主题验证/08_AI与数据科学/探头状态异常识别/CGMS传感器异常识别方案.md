# CGMS传感器异常识别方案

## 项目概述

本项目旨在开发一套完整的CGMS（连续血糖监测）传感器异常识别系统，能够区分传感器技术故障和真实血糖波动，提高数据质量和临床可靠性。

## 问题定义

### 核心挑战
- **区分传感器异常 vs 真实血糖异常**
- 传感器故障可能产生：假高值、假低值、信号丢失、噪声干扰
- 真实血糖波动可能包括：快速升降、极值、病理性波动

### 异常类型分类

#### 1. 技术性异常（传感器问题）
```
A. 硬件故障
   - 电极老化/污染
   - 机械损坏
   - 电路故障

B. 信号处理异常
   - 校准漂移
   - 温度干扰
   - 电磁干扰

C. 算法处理异常
   - 滤波器异常
   - 转换算法错误
```

#### 2. 生理性异常（真实血糖）
```
A. 正常生理波动
   - 餐后血糖升高
   - 运动后下降
   - 夜间血糖变化

B. 病理性波动
   - 严重低血糖
   - 糖尿病酮症酸中毒
   - 药物反应
```

## 识别指标体系

### 1. 信号质量指标

#### 信噪比分析
```python
def calculate_snr(signal, noise_window=30):
    """计算信噪比"""
    # 信号功率
    signal_power = np.mean(signal ** 2)

    # 噪声功率（高频成分）
    noise = signal - savgol_filter(signal, noise_window, 3)
    noise_power = np.mean(noise ** 2)

    snr_db = 10 * np.log10(signal_power / noise_power)
    return snr_db

# 正常范围：SNR > 20dB
# 异常警告：SNR < 15dB
# 严重异常：SNR < 10dB
```

#### 信号稳定性
```python
def signal_stability(data, window_size=15):
    """信号稳定性评估"""
    # 变异系数
    cv = np.std(data) / np.mean(data) * 100

    # 滑动窗口稳定性
    rolling_cv = data.rolling(window_size).apply(
        lambda x: np.std(x) / np.mean(x) * 100
    )

    return {
        'overall_cv': cv,
        'rolling_cv_mean': np.mean(rolling_cv),
        'rolling_cv_max': np.max(rolling_cv)
    }

# 正常范围：CV < 15%
# 轻度异常：15% < CV < 25%
# 严重异常：CV > 25%
```

### 2. 时间序列特征分析

#### 异常跳跃检测
```python
def detect_abnormal_jumps(glucose_data, time_data, threshold=4.0):
    """检测异常血糖跳跃"""
    # 计算变化率 (mg/dL/min)
    dt = np.diff(time_data)  # 时间间隔（分钟）
    dg = np.diff(glucose_data)  # 血糖变化
    rate = np.abs(dg / dt)

    # 生理学限制：正常血糖变化率 < 4-6 mg/dL/min
    abnormal_jumps = rate > threshold

    return {
        'jump_indices': np.where(abnormal_jumps)[0],
        'max_rate': np.max(rate),
        'jump_count': np.sum(abnormal_jumps),
        'jump_percentage': np.mean(abnormal_jumps) * 100
    }
```

#### 平坦信号检测
```python
def detect_flat_signals(data, min_duration=30, tolerance=1.0):
    """检测异常平坦信号"""
    # 检测连续相同或近似相同的数值
    diff = np.abs(np.diff(data))
    flat_points = diff < tolerance

    # 找出连续平坦区间
    flat_segments = []
    start_idx = None

    for i, is_flat in enumerate(flat_points):
        if is_flat and start_idx is None:
            start_idx = i
        elif not is_flat and start_idx is not None:
            duration = i - start_idx
            if duration >= min_duration:
                flat_segments.append((start_idx, i, duration))
            start_idx = None

    return flat_segments

# 正常：偶发短时间平坦（<10分钟）
# 异常：连续平坦 >30分钟
# 严重异常：连续平坦 >60分钟
```

### 3. 生理合理性检查

#### 数值范围验证
```python
def physiological_range_check(glucose_values):
    """生理合理性范围检查"""
    # 定义生理范围
    NORMAL_RANGE = (70, 180)      # mg/dL
    EXTENDED_RANGE = (40, 400)    # mg/dL
    ABSOLUTE_RANGE = (20, 600)    # mg/dL

    results = {
        'in_normal_range': np.sum((glucose_values >= NORMAL_RANGE[0]) &
                                 (glucose_values <= NORMAL_RANGE[1])) / len(glucose_values),
        'in_extended_range': np.sum((glucose_values >= EXTENDED_RANGE[0]) &
                                   (glucose_values <= EXTENDED_RANGE[1])) / len(glucose_values),
        'out_of_absolute_range': np.sum((glucose_values < ABSOLUTE_RANGE[0]) |
                                       (glucose_values > ABSOLUTE_RANGE[1])),
        'extreme_values': glucose_values[(glucose_values < 30) | (glucose_values > 500)]
    }

    return results
```

#### 梯度一致性分析
```python
def gradient_consistency_analysis(data):
    """血糖梯度一致性分析"""
    # 一阶导数（变化率）
    first_derivative = np.gradient(data)

    # 二阶导数（加速度）
    second_derivative = np.gradient(first_derivative)

    # 异常梯度检测
    abnormal_first = np.abs(first_derivative) > 5.0  # mg/dL/min
    abnormal_second = np.abs(second_derivative) > 2.0  # mg/dL/min²

    return {
        'first_derivative_anomalies': np.sum(abnormal_first),
        'second_derivative_anomalies': np.sum(abnormal_second),
        'gradient_consistency_score': 1 - (np.sum(abnormal_first | abnormal_second) / len(data))
    }
```

### 4. 校准一致性评估

#### 与参考血糖对比
```python
def calibration_accuracy_assessment(cgms_values, reference_bg_values, timestamps):
    """校准准确性评估"""
    # 配对数据（时间匹配）
    paired_data = match_timestamps(cgms_values, reference_bg_values, timestamps)

    # MARD (Mean Absolute Relative Difference)
    mard = np.mean(np.abs(paired_data['cgms'] - paired_data['reference']) /
                   paired_data['reference']) * 100

    # Clarke错误网格分析
    clarke_zones = clarke_error_grid_analysis(paired_data['cgms'], paired_data['reference'])

    # 偏差分析
    bias = np.mean(paired_data['cgms'] - paired_data['reference'])
    precision = np.std(paired_data['cgms'] - paired_data['reference'])

    return {
        'mard': mard,
        'clarke_zones': clarke_zones,
        'bias': bias,
        'precision': precision,
        'accuracy_grade': classify_accuracy(mard, clarke_zones)
    }

def classify_accuracy(mard, clarke_zones):
    """准确性分级"""
    zone_a_b_percentage = (clarke_zones['A'] + clarke_zones['B']) / sum(clarke_zones.values()) * 100

    if mard <= 10 and zone_a_b_percentage >= 95:
        return "优秀"
    elif mard <= 15 and zone_a_b_percentage >= 90:
        return "良好"
    elif mard <= 20 and zone_a_b_percentage >= 85:
        return "可接受"
    else:
        return "需要重新校准"
```

## 综合异常检测算法

### 多维度异常评分
```python
class CGMSAnomalyDetector:
    """CGMS异常检测器"""

    def __init__(self):
        self.weights = {
            'signal_quality': 0.25,
            'temporal_features': 0.25,
            'physiological_plausibility': 0.25,
            'calibration_consistency': 0.25
        }

    def comprehensive_anomaly_detection(self, cgms_data, reference_data=None):
        """综合异常检测"""
        scores = {}

        # 1. 信号质量评分
        snr = self.calculate_snr(cgms_data)
        stability = self.signal_stability(cgms_data)
        scores['signal_quality'] = self.normalize_signal_quality_score(snr, stability)

        # 2. 时间序列特征评分
        jumps = self.detect_abnormal_jumps(cgms_data)
        flat_signals = self.detect_flat_signals(cgms_data)
        scores['temporal_features'] = self.normalize_temporal_score(jumps, flat_signals)

        # 3. 生理合理性评分
        range_check = self.physiological_range_check(cgms_data)
        gradient_check = self.gradient_consistency_analysis(cgms_data)
        scores['physiological_plausibility'] = self.normalize_physiological_score(
            range_check, gradient_check
        )

        # 4. 校准一致性评分（如果有参考数据）
        if reference_data is not None:
            calibration = self.calibration_accuracy_assessment(cgms_data, reference_data)
            scores['calibration_consistency'] = self.normalize_calibration_score(calibration)
        else:
            scores['calibration_consistency'] = 0.5  # 中性分数

        # 计算综合异常分数
        overall_score = sum(scores[key] * self.weights[key] for key in scores.keys())

        # 异常程度分类
        anomaly_level = self.classify_anomaly_level(overall_score)

        return {
            'overall_anomaly_score': overall_score,
            'anomaly_level': anomaly_level,
            'component_scores': scores,
            'recommendations': self.generate_recommendations(scores, anomaly_level)
        }

    def classify_anomaly_level(self, score):
        """异常程度分类"""
        if score >= 0.8:
            return "正常"
        elif score >= 0.6:
            return "轻度异常"
        elif score >= 0.4:
            return "中度异常"
        else:
            return "严重异常"

    def generate_recommendations(self, scores, level):
        """生成处理建议"""
        recommendations = []

        if level == "严重异常":
            recommendations.append("立即停止使用该传感器")
            recommendations.append("更换新的传感器")
            recommendations.append("检查传感器安装是否正确")

        elif level == "中度异常":
            recommendations.append("增加指血校准频率")
            recommendations.append("密切监控数据质量")
            recommendations.append("考虑传感器更换")

        elif level == "轻度异常":
            recommendations.append("进行校准验证")
            recommendations.append("检查环境干扰因素")

        # 针对具体问题的建议
        if scores['signal_quality'] < 0.5:
            recommendations.append("检查传感器连接和电极状态")

        if scores['calibration_consistency'] < 0.5:
            recommendations.append("使用多点校准提高准确性")

        return recommendations
```

## 实时监控系统

### 滑动窗口检测
```python
class RealTimeAnomalyMonitor:
    """实时异常监控"""

    def __init__(self, window_size=60, update_interval=5):
        self.window_size = window_size  # 监控窗口大小（分钟）
        self.update_interval = update_interval  # 更新间隔（分钟）
        self.data_buffer = []
        self.anomaly_history = []

    def add_data_point(self, glucose_value, timestamp):
        """添加新数据点"""
        self.data_buffer.append({
            'value': glucose_value,
            'timestamp': timestamp
        })

        # 维护滑动窗口
        cutoff_time = timestamp - timedelta(minutes=self.window_size)
        self.data_buffer = [d for d in self.data_buffer if d['timestamp'] > cutoff_time]

        # 检查是否需要更新异常检测
        if len(self.data_buffer) >= 10:  # 至少需要10个数据点
            self.update_anomaly_detection()

    def update_anomaly_detection(self):
        """更新异常检测"""
        current_data = [d['value'] for d in self.data_buffer]
        timestamps = [d['timestamp'] for d in self.data_buffer]

        detector = CGMSAnomalyDetector()
        result = detector.comprehensive_anomaly_detection(current_data)

        # 记录异常历史
        self.anomaly_history.append({
            'timestamp': timestamps[-1],
            'result': result
        })

        # 触发警报
        if result['anomaly_level'] in ['中度异常', '严重异常']:
            self.trigger_alert(result)

    def trigger_alert(self, result):
        """触发异常警报"""
        alert_message = f"CGMS传感器异常检测: {result['anomaly_level']}"
        print(f"🚨 {alert_message}")
        for rec in result['recommendations']:
            print(f"📋 建议: {rec}")
```

## 使用示例

```python
# 初始化异常检测器
detector = CGMSAnomalyDetector()

# 模拟CGMS数据
glucose_data = np.array([120, 125, 130, 400, 135, 140, 145, 150])  # 包含异常值
reference_bg = np.array([118, 124, 132, 138, 142, 148])

# 执行异常检测
result = detector.comprehensive_anomaly_detection(glucose_data, reference_bg)

print(f"异常程度: {result['anomaly_level']}")
print(f"综合评分: {result['overall_anomaly_score']:.2f}")
print("处理建议:")
for rec in result['recommendations']:
    print(f"- {rec}")
```

## 临床应用建议

### 1. 分级处理策略
- **轻度异常**: 增加校准频率，继续监控
- **中度异常**: 结合指血验证，考虑传感器更换
- **严重异常**: 立即停用，更换传感器

### 2. 医护人员培训要点
- 识别常见传感器故障模式
- 掌握异常数据的临床判断
- 了解校准和维护最佳实践

### 3. 质量保证流程
- 建立数据质量监控SOP
- 定期校准和验证程序
- 异常事件记录和分析

## 技术发展方向

### 短期目标
- 完善算法参数优化
- 建立更大的验证数据集
- 开发用户友好的监控界面

### 长期规划
- 机器学习模型集成
- 个性化异常检测阈值
- 多传感器融合技术

---

*创建时间: 2025年9月26日*
*项目状态: 方案设计阶段*