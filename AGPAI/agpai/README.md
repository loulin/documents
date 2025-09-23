# 🎯 AGPAI - 三Agent血糖分析系统

## 📋 系统概述

AGPAI是基于94+120项专业指标的糖尿病血糖分析系统，采用三个专业化Agent协同工作的架构设计。

### 🏥 三个核心Agent

#### Agent 1: AGP专业分析器
- **职责**: 基于94项指标的标准AGP分析和解读
- **特点**: 零AI依赖，纯算法实现，成本$0
- **输出**: 专业AGP报告、血糖模式识别、临床建议

#### Agent 2: 血糖脆性临床顾问  
- **职责**: 6种血糖脆性分型和个性化治疗建议
- **特点**: 基于混沌理论的脆性分析
- **输出**: 脆性档案、治疗策略、风险预警

#### Agent 3: 综合智能分析器
- **职责**: 基于120项扩展指标的AI驱动深度分析
- **特点**: 智能预测、个性化优化
- **输出**: 预测分析、智能建议、综合评估

## 📊 指标体系

### 94项核心指标 (Agent 1 & 2)
- 基础统计指标 (15项)
- TIR分析指标 (10项)
- 变异性指标 (12项)
- 时序模式指标 (7项)
- 餐时模式指标 (10项)
- 事件分析指标 (10项)
- 临床质量指标 (5项)
- 高级数学指标 (17项)
- 病理生理指标 (8项)

### 120项扩展指标 (Agent 3)
- 94项核心指标 + 26项智能指标
  - 智能预测指标 (10项)
  - 精准治疗指标 (8项)
  - 生活质量指标 (6项)
  - 经济效益指标 (2项)

## 🏗️ 系统架构

```
📁 agpai/
├── 📁 core/                    # 核心Agent实现
│   ├── AGP_Professional_Analyzer.py           # Agent 1
│   ├── Brittleness_Clinical_Advisor.py        # Agent 2  
│   ├── Comprehensive_Intelligence_Analyzer.py # Agent 3
│   └── Multi_Agent_Coordinator.py             # 协调器
├── 📁 config/                  # 配置和参数
│   ├── Comprehensive_120_Indicators_Reference.csv
│   └── config.yaml
├── 📁 docs/                    # 技术文档
│   ├── THREE_AGENT_SYSTEM_OVERVIEW.md
│   ├── 6Hour_Glucose_Prediction_Analysis.md
│   └── Stress_Response_Pattern_Analysis.md
├── 📁 examples/                # 使用示例
│   ├── AGPAI_Complete_Enhanced_Demo.py
│   ├── Full_AGP_Demo.py
│   ├── Quick_Demo.py
│   └── Shenyuemei_Three_Agent_Analysis.py
├── 📁 reports/                 # 分析报告
└── 📁 tests/                   # 测试用例
```

## 🚀 快速开始

### 1. 基础使用
```python
# Agent 1: AGP专业分析
from core.AGP_Professional_Analyzer import AGPProfessionalAnalyzer

analyzer = AGPProfessionalAnalyzer()
result = analyzer.generate_professional_agp_report("data.csv", "PATIENT_001")
```

### 2. 协同分析
```python
# 三Agent协同分析
from core.Multi_Agent_Coordinator import MultiAgentCoordinator

coordinator = MultiAgentCoordinator()
request = create_analysis_request(
    data_path="patient_data.xlsx",
    patient_id="PATIENT_001",
    analysis_mode="integrated"
)
result = coordinator.analyze_patient(request)
```

### 3. 运行示例
```bash
cd examples/
python Quick_Demo.py                          # 快速演示
python Shenyuemei_Three_Agent_Analysis.py    # 三Agent协同分析
python AGPAI_Complete_Enhanced_Demo.py       # 完整功能演示
```

## 📈 核心功能

### 🔍 血糖分析能力
- **标准AGP分析**: TIR、CV、GMI等94项专业指标
- **脆性分型**: 6种脆性类型识别和治疗建议
- **智能预测**: 6小时血糖预测，置信度评估
- **个性化建议**: 基于个体特征的精准治疗建议

### 🎯 临床应用
- **日常诊疗**: Agent 1标准分析
- **复杂病例**: Agent 1 + Agent 2协同
- **科研项目**: 全部三Agent深度分析
- **预防性干预**: Agent 3预测性管理

## 📊 数据要求

### 基础数据 (必需)
- ✅ CGM连续血糖数据 (Excel/CSV格式)
- ✅ 患者基础信息 (姓名、年龄等)

### 扩展数据 (可选，提升分析深度)
- 🏥 用药记录 (HIS/EMR系统)
- 🍽️ 饮食日志 (移动APP)
- 🏃‍♂️ 运动数据 (可穿戴设备)
- 💊 治疗依从性记录

## 🎊 成功案例

### 申月梅患者案例
- **数据量**: 1336个血糖读数，14天监测
- **三Agent发现**: 
  - AGP: TIR 26.5%, CV 18.1%, 控制较差但稳定
  - 脆性: II型准周期脆性，严重度37.9
  - 智能: 适合时间治疗学+预测管理
- **协同建议**: 时间优化给药 + TIR提升 + 预测性管理

## 📞 技术支持

### 文档资源
- 📖 完整技术文档: `/docs/`
- 🔧 使用示例: `/examples/`
- 🧪 测试用例: `/tests/`

### 关键特性
- **零AI成本**: 纯算法实现，无API调用费用
- **专业分工**: 每个Agent专注特定领域
- **灵活组合**: 根据需求选择Agent组合
- **本地化**: 完全本地处理，数据安全

---

**AGPAI: 专业分工，智能协作，精准分析** 🎯