# CRF设计系统 - 临床研究表单与数据挖掘

## 🎯 系统概述

CRF (Clinical Research Form) 设计系统是G+平台的核心临床研究模块，提供标准化的临床研究表单设计、数据收集和智能分析功能。

## 📊 核心功能

### 1. 智能数据挖掘 🤖
- **文件**: `CRF_Research_Mining_Agent.py` ⭐
- **功能**: 
  - 实时处理数百患者的临床数据
  - 自动发现研究机会和发表切入点
  - 配置驱动的数据质量评估
  - 多维度统计分析与关联发现

### 2. 标准化量表系统 📋
支持多种国际标准化评估量表：

| 量表名称 | 文件 | 用途 | 评分范围 |
|----------|------|------|----------|
| **PHQ-9** | `PHQ9.md`, `PHQ9.csv` | 抑郁症筛查 | 0-27分 |
| **GAD-7** | `GAD7.md`, `GAD7.csv` | 焦虑症筛查 | 0-21分 |
| **MMAS-8** | `MMAS8.md`, `MMAS8.csv` | 药物依从性 | 0-8分 |
| **PSQI** | `PSQI.md`, `PSQI.csv` | 睡眠质量 | 0-21分 |
| **MMSE** | `MMSE.md` | 认知功能 | 0-30分 |
| **IPAQ** | `ipaq_LF_cn.md` | 体力活动 | 分级评估 |

### 3. 专项工作流程 🔄
- `medication_details_workflow.md` - 药物详情采集
- `family_history_workflow.md` - 家族史采集
- `cancer_history_workflow.md` - 肿瘤病史工作流
- `personal_cancer_history_workflow.md` - 个人癌症史

## 🚀 快速开始

### 环境要求
```bash
# Python 依赖
pip install pandas numpy scipy scikit-learn matplotlib seaborn

# 可选依赖 (增强功能)
pip install pyyaml networkx
```

### 运行数据挖掘分析
```bash
# 基本分析
python CRF_Research_Mining_Agent.py

# 完整测试
python test_agent.py
```

### 数据结构示例
```python
# 患者基本信息
patient_demographics = {
    'patient_id': 'P001',
    'age': 58,
    'gender': 'female',
    'diabetes_type': 'type2',
    'duration': 12,
    'bmi': 28.5
}

# 临床数据
clinical_data = {
    'hba1c': 8.5,
    'fbg': 10.2,
    'creatinine': 90,
    'systolic_bp': 142
}
```

## 📈 分析功能

### 数据质量评估
- 缺失值检测和分析
- 异常值识别 (IQR方法)
- 数据分布分析
- 重复记录检测
- 数据完整性评估

### 研究机会发现
- 横断面关联分析
- 纵向趋势分析
- 多因素交互作用
- 亚组分析
- 发表价值评估

### 统计分析方法
- 卡方检验 (χ²)
- 相关性分析
- 回归建模
- 聚类分析
- 机器学习预测

## 📊 输出报告

### 分析报告示例
**文件**: `CRF_Test_Analysis_Report.md`

包含内容:
- 📊 数据质量评估
- 🎯 研究机会发现  
- 🏆 优先级推荐
- 📅 发表路线图
- 💡 总体建议

### 研究价值等级
- **极高价值**: 统计显著且临床意义重大
- **高价值**: 具有发表潜力的发现
- **中等价值**: 需要进一步验证的趋势
- **低价值**: 探索性发现

## 🔧 配置系统

### 配置文件结构
```yaml
# config.yaml 示例
data_sources:
  patient_demographics:
    path: "./test_data/patient_demographics.csv"
  clinical_data:  
    path: "./test_data/clinical_data.csv"

analysis:
  - title: "糖尿病患者抑郁症状分析"
    type: "chi2_contingency"
    trigger:
      metric: "p_value"
      operator: "lt" 
      value: 0.05
```

## 🗂️ 文件组织

```
/crf_design/
├── 📋 README.md                          # 本文档 ⭐
├── 🤖 CRF_Research_Mining_Agent.py       # 智能分析引擎 ⭐
├── 🧪 test_agent.py                      # 测试脚本
├── 📊 CRF_Test_Analysis_Report.md        # 示例分析报告
│
├── 📋 标准化量表/
│   ├── PHQ9.md + PHQ9.csv               # 抑郁症筛查
│   ├── GAD7.md + GAD7.csv               # 焦虑症筛查  
│   ├── MMAS8.md + MMAS8.csv             # 药物依从性
│   ├── PSQI.md + PSQI.csv               # 睡眠质量
│   └── MMSE.md                          # 认知功能
│
├── 🔄 工作流程/
│   ├── medication_details_workflow.md   # 药物详情
│   ├── family_history_workflow.md       # 家族史
│   └── cancer_history_workflow.md       # 肿瘤史
│
├── 📊 数据文件/
│   ├── crfmain2.csv                     # 主要CRF表单
│   ├── test_data/                       # 测试数据集
│   └── sample_data/                     # 示例数据
│
└── 📝 技术文档/
    ├── database_schema.md               # 数据库设计
    ├── technical_spec.md                # 技术规范
    └── Research_Mining_Guide.md         # 挖掘指南
```

## 🔗 关联系统

- **[AGPAI血糖分析](../AGPAI/)** - AGP动态血糖分析
- **[设备集成方案](../devices/)** - 医疗设备对接
- **[ABPM血压监测](../ABPM/)** - 动态血压分析

## 📞 技术支持

**开发团队**: G+ Platform  
**文档更新**: 2025年8月  
**问题反馈**: 通过GitHub Issues

---

*完整的临床研究数据管理解决方案，助力医学研究和循证实践*