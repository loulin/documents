# Agent2 ABPM Analysis System v5.0

连续血压监测(ABPM)脆性分析系统

基于Agent2 v5.0血糖脆性分析架构，专为24小时动态血压监测数据设计的智能分析系统。

## 系统概述

Agent2 ABPM Analysis System 是专门为连续血压监测数据设计的脆性分析系统，继承了Agent2 v5.0在血糖脆性分析方面的核心算法和架构优势，并针对血压数据的特点进行了深度优化。

### 核心特色

- **血压脆性五型分类**: I-V型血压脆性智能分类
- **昼夜节律分析**: 杓型血压模式评估与紊乱检测
- **治疗反应分段**: 药物治疗效果的时间段识别
- **血压负荷评估**: 日间/夜间高血压负荷量化
- **变异性分析**: 血压变异性模式识别
- **智能分段算法**: 多模式分段策略自适应选择

## 文件结构

```
ABPM_Analysis/
├── Agent2_ABPM_Brittleness_Analyzer.py    # ABPM脆性分析主程序
├── ABPM_Segmentation_Analyzer.py          # ABPM智能分段分析器
└── README.md                               # 系统文档（本文件）
```

## 主要功能模块

### 1. Agent2_ABPM_Brittleness_Analyzer.py

**连续血压监测脆性分析核心引擎**

#### 核心功能:
- ABPM数据预处理与质量控制
- 血压脆性五型分类 (I-V型)
- 昼夜节律分析与杓型血压评估
- 血压负荷与变异性量化
- 心血管风险评估
- 临床治疗建议生成

#### 脆性分型标准:
- **I型_稳定**: 0-20分 - 血压控制良好，变异性低
- **II型_轻度不稳定**: 20-40分 - 轻度血压波动
- **III型_中度不稳定**: 40-60分 - 中度变异性增加
- **IV型_重度脆性**: 60-80分 - 严重血压不稳定
- **V型_极度脆性**: 80-100分 - 极度血压脆性

#### 评分组成:
- 血压变异性评分 (40分)
- 昼夜节律紊乱评分 (30分)
- 血压负荷评分 (20分)
- 血压峰值波动评分 (10分)

### 2. ABPM_Segmentation_Analyzer.py

**ABPM智能分段分析系统**

#### 分段模式:
- **精细监测模式**: 6-15个分段，1.5小时最小分段时长
- **宏观趋势模式**: 2-4个分段，6小时最小分段时长
- **昼夜节律模式**: 3-8个分段，基于生理节律
- **治疗反应模式**: 4-10个分段，针对药物效果评估

#### 核心算法:
- 治疗反应变化点检测
- 昼夜节律转换点识别
- 血压变异性突变检测
- 多维度特征融合分析

## 使用指南

### 基础使用

```python
from Agent2_ABPM_Brittleness_Analyzer import Agent2ABPMBrittlenessAnalyzer
from ABPM_Segmentation_Analyzer import ABPMSegmentationAnalyzer

# 1. 创建ABPM脆性分析器
analyzer = Agent2ABPMBrittlenessAnalyzer(
    patient_id="Patient_001",
    analysis_config={
        'day_period': (6, 22),
        'night_period': (22, 6)
    }
)

# 2. 加载ABPM数据（支持Excel、CSV格式）
analyzer.load_abpm_data("patient_abpm_data.xlsx")

# 3. 预处理数据
preprocessing_result = analyzer.preprocess_abpm_data()

# 4. 执行脆性分类
brittleness_result = analyzer.classify_abpm_brittleness()

print(f"脆性类型: {brittleness_result['brittleness_classification']['brittleness_type']}")
print(f"脆性评分: {brittleness_result['brittleness_classification']['brittleness_score']}")
```

### 分段分析使用

```python
# 1. 创建分段分析器
segmentation_analyzer = ABPMSegmentationAnalyzer(patient_id="Patient_001")

# 2. 加载预处理数据
segmentation_analyzer.load_processed_data(analyzer.processed_data)

# 3. 治疗反应分段分析
treatment_segments = segmentation_analyzer.analyze_treatment_response_segments(mode='auto')

# 4. 昼夜节律分段分析
circadian_segments = segmentation_analyzer.analyze_circadian_rhythm_segments()

# 5. 血压变异性分段分析
variability_segments = segmentation_analyzer.analyze_variability_segments(mode='fine_monitoring')
```

## 数据格式要求

### 输入数据格式
ABPM数据应包含以下列（支持中英文列名）:

| 必需列 | 中文列名 | 英文列名 | 数据类型 | 说明 |
|--------|----------|----------|----------|------|
| 时间戳 | 时间/测量时间 | Time/DateTime | datetime | 血压测量时间 |
| 收缩压 | 收缩压 | SBP/Systolic | numeric | 收缩压值(mmHg) |
| 舒张压 | 舒张压 | DBP/Diastolic | numeric | 舒张压值(mmHg) |
| 心率 | 心率 | HR/Heart_Rate | numeric | 心率值(可选) |

### 数据质量要求
- 24小时监测数据，至少20小时有效数据
- 日间(6:00-22:00)每小时至少2个读数
- 夜间(22:00-6:00)每小时至少1个读数
- 数据缺失率不超过30%
- 血压值在生理范围内(SBP: 60-250mmHg, DBP: 30-150mmHg)

## 临床应用场景

### 1. 高血压管理
- 血压控制效果评估
- 降压药物剂量调整指导
- 心血管风险分层

### 2. 昼夜节律评估
- 杓型血压模式识别
- 夜间高血压检测
- 晨峰血压评估

### 3. 治疗监测
- 药物治疗反应追踪
- 治疗方案优化建议
- 副作用早期预警

### 4. 科研应用
- 血压变异性研究
- 心血管事件预测模型
- 个体化治疗方案研究

## 输出结果解读

### 脆性分析结果
```json
{
  "brittleness_classification": {
    "brittleness_type": "III型_中度不稳定",
    "brittleness_score": 45.2,
    "confidence_level": "high"
  },
  "clinical_interpretation": {
    "risk_level": "moderate",
    "clinical_significance": "needs_optimization",
    "cardiovascular_risk": "moderate_risk"
  },
  "treatment_recommendations": {
    "immediate_actions": ["心血管风险分层", "调整降压方案"],
    "lifestyle_interventions": ["规律作息", "适度运动", "低盐饮食"],
    "monitoring_frequency": "每3个月"
  }
}
```

### 分段分析结果
```json
{
  "segmentation_mode": "treatment_response",
  "total_segments": 4,
  "segment_details": [
    {
      "segment_id": 1,
      "start_time": "2024-01-15 08:00:00",
      "end_time": "2024-01-15 14:30:00",
      "duration_hours": 6.5,
      "treatment_response": "baseline"
    }
  ],
  "clinical_interpretation": {
    "overall_treatment_response": "good_overall_response"
  }
}
```

## 技术特性

### 算法优势
- **多维度融合**: 结合变异性、节律性、负荷性多个维度
- **智能阈值**: 基于临床指南的动态阈值设定
- **稳定性保证**: 确定性算法确保结果一致性
- **临床导向**: 面向临床决策的结果解释

### 性能特点
- 支持大规模ABPM数据处理
- 快速变化点检测算法
- 内存优化的时间序列处理
- 并行计算能力

## 注意事项

1. **数据质量**: 确保ABPM数据质量符合临床标准
2. **时区处理**: 注意时间戳的时区一致性
3. **个体差异**: 考虑患者个体生理特征差异
4. **临床结合**: 分析结果需结合临床实际情况解读

## 版本历史

- **v5.0** (2025-08-28): 基于Agent2 v5.0架构的ABPM分析系统
  - 完整的血压脆性五型分类
  - 智能分段算法集成
  - 昼夜节律深度分析
  - 治疗反应评估系统

## 技术支持

如需技术支持或功能建议，请参考Agent2主系统文档或联系开发团队。

---

*Agent2 ABPM Analysis System - 专业的连续血压监测脆性分析解决方案*