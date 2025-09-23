# Agent2 智能脆性分析技术栈

🩸 **血糖脆性分析系统** + 🫀 **ECG脆性分析系统**

## 📋 目录结构

```
Agent2_Scripts/
├── README.md                                    # 本文档
├── Agent2_Intelligent_Analysis.py              # 核心血糖脆性分析脚本
├── Agent2_Optimized_Segmentation.py            # 血糖优化分段算法
├── Agent2_Intelligent_Analysis_Deployment.py   # 血糖分析部署版本
├── ../ECG_Agent2_Intelligent_Analyzer.py       # 🔥 ECG智能脆性分析器
├── specialized_analyzers/                      # 专用分析器
│   ├── Agent2_ECG_Brittleness_Analyzer.py     # ECG脆性分析(基础版)
│   ├── Agent2_HRV_Brittleness_Analyzer.py     # HRV脆性分析
│   └── Agent2_ABPM_Brittleness_Analyzer.py    # ABPM脆性分析
├── documentation/                              # 设计文档
│   ├── Agent2_HRV_Analysis_Design.md          # HRV分析设计
│   ├── Agent2_ECG_Analysis_Design.md          # ECG分析设计
│   └── Agent2_ABPM_Analysis_Design.md         # ABPM分析设计
└── sample_reports/                             # 示例报告
    ├── Agent2_Intelligent_Analysis_上官李军-253124_20250828_161331.json
    └── Agent2_Intelligent_Analysis_吴四毛-103782_20250828_175707.json
```

## 🔧 核心脚本说明

### 1. Agent2_Intelligent_Analysis.py
**主要功能**: 智能血糖脆性分析和时间分段
**核心特性**:
- 混沌动力学分析（Lyapunov指数、近似熵、Hurst指数）
- 多维评分决策系统
- 24小时时段脆性分析
- 智能时间分段纵向分析
- 标准脆性分型体系

**参数体系**:
```python
# 混沌动力学指标
lyapunov_exponent       # Lyapunov指数 (混沌程度)
approximate_entropy     # 近似熵 (复杂性)  
shannon_entropy        # Shannon熵 (随机性)
hurst_exponent         # Hurst指数 (记忆特性)
fractal_dimension      # 分形维度 (几何复杂性)
correlation_dimension  # 关联维数 (动力学复杂度)

# 智能分段参数
window_size = max(48, len*0.08)     # 滑动窗口大小
step_size = max(12, window_size//4) # 窗口移动步长
significance_level = 0.01           # 统计显著性水平
merge_threshold = 24.0              # 变化点合并阈值(小时)
```

### 2. Agent2_Optimized_Segmentation.py
**主要功能**: 最优分段约束，确保临床实用性
**核心改进**:
- 最优分段数量控制（2-4段）
- 智能变化点重要性排序
- 分段质量优先策略
- 临床意义阈值控制

**关键参数**:
```python
max_segments = 4                    # 最大分段数（临床友好）
min_segments = 2                    # 最小分段数
clinical_mode = True                # 临床模式开关
importance_weights = {
    'boundary_bonus': 50,           # 边界分段权重
    'duration_weight': 20,          # 持续时间权重
    'feature_weight': 30,           # 控制特征权重
    'gmi_weight': 25,              # GMI差异权重
}
```

### 3. ECG_Agent2_Intelligent_Analyzer.py 🔥 **全新ECG智能分析器**
**主要功能**: ECG脆性分析和智能分段（完全基于Agent2架构）
**核心特性**:
- 心律混沌动力学分析（RR间期Lyapunov指数、近似熵）
- ECG脆性5类分型系统（I-V型风险分级）
- 智能时间分段（4种变化点检测算法）
- 心血管风险评估和个性化治疗建议

**ECG专用参数体系**:
```python
# ECG混沌动力学指标
lyapunov_rr          # RR间期Lyapunov指数 (心律混沌程度)
rr_entropy           # RR间期近似熵 (心率变异复杂性)
hr_cv                # 心率变异系数 (>40%为极高变异)
qt_variability       # QT间期变异性 (>50ms为异常)
st_instability       # ST段不稳定性 (>20%为高风险)

# ECG智能分段参数
window_duration = 600      # 10分钟窗口 (vs 血糖48个点)
step_size = window_size//4 # 2.5分钟步长
significance_level = 0.01  # 统计显著性水平
merge_threshold = 30       # 变化点合并阈值(分钟)
```

**ECG脆性5类分型**:
- **V型极度危险型** (85-100分): 心脏猝死高危
- **IV型重度脆弱型** (70-85分): 恶性心律失常高危
- **III型中度易损型** (50-70分): 心血管事件中危
- **II型轻度不稳定型** (30-50分): 需要监测关注
- **I型正常稳定型** (0-30分): 心电活动稳定

### 4. 专用分析器系列（基础版）

#### ECG脆性分析器
- 心电图节律变异性分析
- QT间期变异与血糖脆性关联
- 心率变异性与血糖波动相关性

#### HRV脆性分析器  
- 心率变异性时域分析
- 频域分析与血糖脆性
- 非线性动力学指标

#### ABPM脆性分析器
- 24小时动态血压监测
- 血压变异性与血糖脆性
- 昼夜血压节律分析

## 🚀 使用方法

### 血糖脆性分析
```bash
# 基本血糖分析
python Agent2_Intelligent_Analysis.py patient_data.xlsx 患者ID

# 优化分段分析
python Agent2_Optimized_Segmentation.py data.csv 患者ID 4
```

### ECG脆性分析 🔥 **新功能**
```bash
# ECG智能分析
python ECG_Agent2_Intelligent_Analyzer.py ecg_data.csv 患者ID
```

### 编程接口
```python
# 血糖脆性分析
from Agent2_Intelligent_Analysis import analyze_intelligent_brittleness
result = analyze_intelligent_brittleness('glucose_data.xlsx', '患者001')

# ECG脆性分析
import sys
sys.path.append('../')
from ECG_Agent2_Intelligent_Analyzer import ECGAgent2Analyzer

# 创建ECG分析器
ecg_analyzer = ECGAgent2Analyzer(sampling_rate=500)
# 执行ECG智能分析
ecg_result = ecg_analyzer.analyze_ecg_intelligence(
    ecg_data, timestamps, patient_id="Patient001"
)
```

## 📊 输出报告结构

### 血糖智能分析报告包含：
1. **混沌动力学指标** - 6大混沌参数详细分析
2. **智能脆性分型** - 基于多维评分的5类分型
3. **时段脆性风险** - 24小时时段风险分析
4. **智能时间分段** - 变化点检测和分段分析
5. **治疗反应评估** - 动态治疗效果评估
6. **个性化建议** - 基于分型的精准治疗建议

### 血糖关键指标解读：
- **I型混沌脆性**: Lyapunov>0.01, 系统极难预测
- **II型准周期脆性**: 存在准周期振荡模式
- **III型随机脆性**: 高随机性，缺乏规律
- **IV型记忆缺失脆性**: Hurst<0.4, 记忆功能受损
- **V型频域脆性**: 特定频率范围异常
- **稳定型**: 各指标在正常范围

### ECG智能分析报告包含：🔥 **新增**
1. **心律混沌动力学指标** - RR间期Lyapunov指数、近似熵等
2. **ECG脆性分型评估** - I-V型心电脆性分型系统
3. **ECG智能分段分析** - 4种心电变化点检测算法
4. **心血管风险评估** - 综合风险评分和分级预警
5. **个性化医疗建议** - 从急救到长期治疗的完整方案

### ECG关键指标解读：
- **V型极度危险型**: 心脏猝死高危，需要ICD植入评估
- **IV型重度脆弱型**: 恶性心律失常高危，需要住院治疗
- **III型中度易损型**: 心血管事件中危，加强监测治疗
- **II型轻度不稳定型**: 需要关注，生活方式调整为主
- **I型正常稳定型**: 心电活动稳定，维持健康状态

## ⚙️ 环境要求

```bash
# Python依赖
pip install pandas numpy scipy scikit-learn

# 核心库
pandas >= 1.3.0
numpy >= 1.21.0  
scipy >= 1.7.0
scikit-learn >= 1.0.0
```

## 🔍 技术特点

### 混沌动力学理论（血糖+ECG通用）
- 基于非线性动力学系统分析
- Lyapunov指数量化系统混沌程度
- 多维熵分析评估系统复杂性
- Hurst指数评估长程记忆特性

### 智能分段算法（双系统适配）
- **血糖分段**: 统计学、聚类、梯度、脆性四维检测
- **ECG分段**: 心率统计、心律聚类、缺血梯度、脆性阶段检测
- 自适应参数调整（血糖小时级，ECG分钟级）
- 严格质量控制体系

### 临床导向设计
- **血糖**: 2-4段最优分段保证临床友好性
- **ECG**: 2-4段心电分析便于医患沟通
- 多维度脆性分型对应治疗策略
- 个性化治疗建议生成
- 分级预警系统（血糖+心血管双重风险）

### ECG分析的独特优势 🔥
- **数据丰富度**: ECG采样频率500Hz vs 血糖15分钟
- **实时监测**: 24小时连续心电监测，即时预警
- **临床价值**: 心血管疾病全球第一死因，ECG为核心诊断工具
- **混沌理论天然适配**: 心脏本身就是混沌系统
- **技术迁移成功**: Agent2架构完美适配ECG分析

## 📝 版本信息

### 血糖分析系统
- **Agent2 v5.0**: 完整混沌动力学分析
- **优化分段 v1.0**: 临床最优分段约束
- **部署版本**: 生产环境优化版本

### ECG分析系统 🔥 **新增**
- **ECG-Agent2 v1.0**: 基于Agent2架构的心电脆性分析
- **发布日期**: 2025年09月03日
- **核心创新**: 混沌动力学理论从血糖成功迁移至ECG领域
- **技术突破**: 5类ECG脆性分型 + 4种变化点检测算法
- **临床价值**: 心血管疾病智能诊断和精准治疗

## 📞 技术支持

如有技术问题，请参考：
1. 示例报告文件了解输出格式
2. 设计文档了解算法原理  
3. 代码注释了解参数含义

## 🏆 项目成就

### 技术迁移成功
✅ **Agent2血糖分析架构** → **ECG脆性分析系统**  
✅ **混沌动力学理论** → **心律失常预测模型**  
✅ **智能分段算法** → **心电变化点检测**  
✅ **脆性分型体系** → **心血管风险分级**  

### 临床应用价值
🩸 **血糖管理**: 糖尿病个性化治疗，脆性血糖精准识别  
🫀 **心血管预警**: 心脏猝死预测，恶性心律失常早期发现  
📊 **数据驱动**: 从单一指标到多维智能分析  
🎯 **精准医疗**: 个性化治疗方案，风险分层管理

---
**最新更新**: 2025年09月03日 - 新增ECG-Agent2智能分析器  
**来源**: AGPAI项目 Agent2智能分析技术栈  
**适用**: 血糖脆性分析、ECG脆性分析、智能分段、混沌动力学研究、心血管风险评估