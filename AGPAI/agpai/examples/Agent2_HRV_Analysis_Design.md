# Agent2_HRV_Analysis 心率变异性脆性分析系统设计

## 🎯 系统概述
基于Agent2 v5.0血糖脆性分析架构，开发专门的心率变异性(HRV)脆性分析和智能分段系统。

## 📊 数据特征对比

| 特征 | 血糖监测(CGM) | 心率变异性(HRV) | 迁移适配 |
|------|---------------|-----------------|----------|
| **采样频率** | 1-15分钟 | 1秒-5分钟 | ✅ 直接适用 |
| **监测周期** | 7-14天 | 24小时-7天 | ✅ 算法通用 |
| **昼夜节律** | 明显 | 极明显 | ✅ 完全吻合 |
| **生理意义** | 代谢稳定性 | 自主神经稳定性 | ✅ 概念相似 |
| **脆性表现** | 血糖波动大 | 自主神经调节失衡 | ✅ 脆性本质相同 |

## 🧠 核心算法迁移

### 1. 混沌动力学指标 (直接迁移)
```python
# 血糖脆性 → HRV脆性
lyapunov_exponent = calculate_lyapunov_exponent(rr_intervals)  # RR间期序列
approximate_entropy = calculate_approximate_entropy(rr_intervals)
hurst_exponent = calculate_hurst_exponent(rr_intervals)

# 临床意义重新定义
if hurst_exponent < 0.5:
    interpretation = "自主神经系统反持续性，应激恢复能力强"
elif hurst_exponent > 0.5:
    interpretation = "自主神经系统持续性，可能存在调节刚性"
```

### 2. HRV特异性脆性分型
```python
class HRV_Brittleness_Types:
    TYPE_I = "I型正常调节型"      # RMSSD>50ms, pNN50>20%
    TYPE_II = "II型轻度失调型"    # RMSSD 30-50ms
    TYPE_III = "III型中度失调型"  # RMSSD 15-30ms  
    TYPE_IV = "IV型重度失调型"    # RMSSD <15ms
    TYPE_V = "V型极度刚性型"      # 几乎无变异性

def classify_hrv_brittleness(rr_data):
    """HRV脆性分型 - 基于Agent2脆性分析架构"""
    # 计算时域指标
    rmssd = calculate_rmssd(rr_data)
    pnn50 = calculate_pnn50(rr_data)
    
    # 计算频域指标  
    lf_power, hf_power = calculate_frequency_domain(rr_data)
    lf_hf_ratio = lf_power / hf_power
    
    # 混沌动力学指标
    chaos_metrics = calculate_chaos_metrics(rr_data)
    
    # 综合脆性评分 (0-100)
    brittleness_score = calculate_hrv_brittleness_score(
        rmssd, pnn50, lf_hf_ratio, chaos_metrics
    )
    
    return {
        "脆性分型": determine_hrv_type(brittleness_score),
        "脆性评分": brittleness_score,
        "风险等级": determine_risk_level(brittleness_score)
    }
```

## 📈 智能分段策略

### 1. HRV变化点检测
```python
def detect_hrv_change_points(rr_data, timestamps):
    """HRV智能变化点检测 - 基于Agent2分段架构"""
    
    # 计算滑动窗口HRV指标
    window_size = 60  # 1小时窗口
    hrv_trends = []
    
    for i in range(0, len(rr_data) - window_size, window_size//4):
        segment = rr_data[i:i+window_size]
        hrv_metrics = {
            'rmssd': calculate_rmssd(segment),
            'lf_hf_ratio': calculate_lf_hf_ratio(segment),
            'complexity': calculate_sample_entropy(segment)
        }
        hrv_trends.append(hrv_metrics)
    
    # 多维度变化点检测
    change_points = detect_multi_dimensional_changes(
        hrv_trends, 
        dimensions=['rmssd', 'lf_hf_ratio', 'complexity'],
        significance_level=0.05
    )
    
    return change_points
```

### 2. HRV分段模式
```python
# 宏观趋势分段 (适合临床评估)
macro_segments = analyze_hrv_macro_segments(rr_data)
# 示例结果: 
# - 第1段(0-6h): 睡眠恢复期, RMSSD=45ms, 副交感主导
# - 第2段(6-12h): 日间活动期, RMSSD=25ms, 交感激活  
# - 第3段(12-18h): 下午应激期, RMSSD=20ms, 调节降低
# - 第4段(18-24h): 晚间放松期, RMSSD=35ms, 逐步恢复

# 精细监测分段 (适合训练调整)  
fine_segments = analyze_hrv_fine_segments(rr_data)
# 示例结果: 8-12个精细分段，识别具体的应激-恢复转换点
```

## 🏥 临床应用场景

### 1. 运动医学应用
```python
def analyze_athlete_hrv(rr_data, training_log):
    """运动员HRV训练适应性分析"""
    
    # 智能分段检测训练阶段
    training_phases = detect_training_phases(rr_data, training_log)
    
    # 脆性评估
    adaptation_quality = assess_training_adaptation(training_phases)
    
    # 训练建议
    recommendations = generate_training_recommendations(
        brittleness_type, adaptation_quality
    )
    
    return {
        "训练适应性": adaptation_quality,
        "恢复能力评估": recovery_assessment,
        "训练建议": recommendations,
        "过训练风险": overtraining_risk
    }
```

### 2. 心脏康复应用
```python
def analyze_cardiac_rehabilitation(rr_data, patient_id):
    """心脏康复HRV监测分析"""
    
    # 康复阶段智能分段
    rehab_phases = detect_rehabilitation_phases(rr_data)
    
    # 每阶段自主神经恢复评估
    recovery_progress = assess_autonomic_recovery(rehab_phases)
    
    # 康复效果预测
    prognosis = predict_rehabilitation_outcome(recovery_progress)
    
    return {
        "康复进展": recovery_progress,
        "自主神经恢复": autonomic_recovery,
        "预后评估": prognosis,
        "调整建议": adjustment_recommendations
    }
```

## 🔧 技术实现要点

### 1. 数据预处理差异
```python
# 血糖: 直接使用数值
glucose_values = df['glucose'].values

# HRV: 需要从心率计算RR间期
def preprocess_hrv_data(heart_rate_data):
    """心率数据预处理为RR间期"""
    # 心率(bpm) → RR间期(ms)
    rr_intervals = 60000 / heart_rate_data  
    
    # 异常值检测和校正
    rr_intervals = correct_rr_artifacts(rr_intervals)
    
    # 插值处理缺失数据
    rr_intervals = interpolate_missing_rr(rr_intervals)
    
    return rr_intervals
```

### 2. 参考范围调整
```python
# HRV正常参考范围 (需要年龄、性别分层)
HRV_REFERENCE_RANGES = {
    "RMSSD": {
        "young_male": {"normal": ">50ms", "warning": "30-50ms", "risk": "<30ms"},
        "young_female": {"normal": ">40ms", "warning": "25-40ms", "risk": "<25ms"},
        "elderly": {"normal": ">30ms", "warning": "20-30ms", "risk": "<20ms"}
    },
    "pNN50": {
        "normal": ">15%", "warning": "5-15%", "risk": "<5%"
    },
    "LF_HF_ratio": {
        "balanced": "1.0-2.5", "sympathetic_dominant": ">2.5", "parasympathetic_dominant": "<1.0"
    }
}
```

## 🎯 迁移优势

1. **架构完全复用**: Agent2的混沌动力学+智能分段架构100%适用
2. **临床意义明确**: HRV脆性分析在运动医学、心脏康复有明确需求
3. **数据获取便利**: 可穿戴设备广泛支持HRV监测
4. **商业价值高**: 运动员监测、健康管理市场需求强烈

这个HRV分析系统可以成为Agent2技术栈的第一个成功迁移案例。您觉得这个设计方案如何？需要我继续详细设计连续血压监测的迁移方案吗？