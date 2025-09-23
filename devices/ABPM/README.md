# ABPM - 动态血压监测系统

## 🩺 系统概述

ABPM (Ambulatory Blood Pressure Monitoring) 动态血压监测系统是G+平台的重要组成部分，提供24小时连续血压监测、分析和临床指导功能。

## 📊 核心功能

### 实时监测 📈
- **24小时连续监测**: 自动记录白天和夜间血压变化
- **智能测量策略**: 根据患者活动状态调整测量频率
- **多参数采集**: 收集收缩压、舒张压、心率、脉压差等指标
- **环境因素记录**: 结合患者活动日志进行综合分析

### 智能分析 🤖
- **昼夜节律分析**: 识别血压的生理性昼夜变化模式
- **异常模式识别**: 自动检测白大衣高血压、隐匿性高血压等
- **血压负荷评估**: 计算超出正常范围的血压测量百分比
- **变异性分析**: 评估血压波动的稳定性和规律性

### 临床指导 🩺
- **风险分层**: 基于多维度指标进行心血管风险评估
- **用药建议**: 结合血压模式提供个性化治疗方案
- **生活方式指导**: 针对性的非药物干预建议
- **随访计划**: 基于血压控制情况制定复查时间表

## 🚀 技术特点

### 数据采集
```python
# ABPM数据结构示例
abpm_measurement = {
    "timestamp": "2025-08-15T10:30:00Z",
    "systolic_bp": 135,
    "diastolic_bp": 85,
    "heart_rate": 72,
    "pulse_pressure": 50,
    "mean_arterial_pressure": 102,
    "activity_level": "light",
    "patient_position": "standing",
    "measurement_quality": "excellent"
}
```

### 分析算法
- **昼夜比值计算**: (白天平均血压 - 夜间平均血压) / 白天平均血压
- **血压负荷**: 超出正常范围测量数 / 总测量数 × 100%
- **平滑指数**: 评估24小时血压变化的平稳程度
- **晨峰现象**: 检测清晨血压急剧上升的现象

### 诊断标准
| 时段 | 正常血压 | 高血压 | 单位 |
|------|----------|--------|------|
| **24小时平均** | <130/80 | ≥130/80 | mmHg |
| **白天平均** | <135/85 | ≥135/85 | mmHg |
| **夜间平均** | <120/70 | ≥120/70 | mmHg |

## 📋 监测流程

### 1. 设备佩戴阶段
- 患者教育和设备使用培训
- 基线血压测量和设备校准
- 活动日志记录指导
- 24小时连续监测

### 2. 数据分析阶段
- 数据质量评估和清洗
- 昼夜节律模式分析
- 异常血压事件识别
- 综合风险评估

### 3. 报告生成阶段
- 标准化ABPM报告生成
- 临床指导建议制定
- 患者教育材料准备
- 随访计划安排

## 📊 报告内容

### 基础数据摘要
- 有效测量次数和成功率
- 24小时、白天、夜间平均血压
- 最高和最低血压值
- 心率变化范围

### 专业分析指标
- **昼夜节律类型**:
  - Dipper (正常下降型): 夜间下降10-20%
  - Non-dipper (非下降型): 夜间下降<10%
  - Extreme dipper (过度下降型): 夜间下降>20%
  - Reverse dipper (反型): 夜间血压高于白天

- **血压变异性**:
  - 标准差 (SD)
  - 变异系数 (CV)
  - 平均真实变异性 (ARV)

### 临床建议
- 血压控制目标设定
- 药物治疗调整方案
- 生活方式干预措施
- 并发症预防策略

## 🔧 系统配置

### 监测参数设置
```yaml
# ABPM配置示例
monitoring_schedule:
  daytime:
    start_time: "06:00"
    end_time: "22:00"
    interval_minutes: 15
  nighttime:
    start_time: "22:00"
    end_time: "06:00"
    interval_minutes: 30

quality_control:
  min_valid_readings: 14  # 最少有效读数
  max_failed_ratio: 0.2   # 最大失败率
  outlier_threshold: 3    # 异常值检测阈值
```

### 报警设置
- 极高血压值报警 (>180/110 mmHg)
- 极低血压值报警 (<90/60 mmHg)
- 设备故障检测
- 测量成功率过低警告

## 🔗 系统集成

### 与其他模块协同
- **[血糖监测 (AGPAI)](../AGPAI/)**: 糖尿病患者血压-血糖关联分析
- **[设备集成](../devices/)**: 支持多品牌ABPM设备对接
- **[CRF研究](../crf_design/)**: 临床研究数据标准化采集

### 设备兼容性
- Spacelabs OnTrak 90217/90227
- Oscar 2 ABPM System
- BPro ABPM Device
- SunTech Oscar 2
- 国产品牌: 康泰、脉搏波等

## 📁 文件结构

```
/ABPM/
├── 📋 README.md                    # 本文档 ⭐
├── 📖 ABPM.md                      # 完整系统设计文档 ⭐
├── 🔧 abpm_analyzer.py             # 核心分析引擎
├── 📊 report_generator.py          # 报告生成器
├── 🗄️ data_models.py               # 数据模型定义
├── ⚙️ config/
│   ├── monitoring_settings.yaml   # 监测配置
│   ├── reference_values.yaml      # 参考值标准
│   └── device_profiles.yaml       # 设备配置文件
├── 📈 templates/
│   ├── standard_report.html       # 标准报告模板
│   ├── summary_report.pdf         # 摘要报告模板
│   └── patient_education.md       # 患者教育材料
└── 🧪 test_data/
    ├── sample_24h_data.csv        # 示例24小时数据
    └── validation_cases.json      # 验证案例数据
```

## 📞 技术支持

**开发团队**: G+ Platform  
**文档更新**: 2025年8月  
**临床顾问**: 心血管专科团队

---

*专业的24小时血压监测解决方案，助力精准血压管理*