# G+ 医疗平台技术文档

## 概述

G+ 是一个综合性的医疗平台，专注于血糖监测和糖尿病管理。本文档库包含了平台的核心技术方案、临床研究工具和设备集成方案。

## 核心系统

### 🩺 AGPAI - 动态血糖图谱AI分析系统
- **路径**: `/AGPAI/`
- **功能**: 基于AI的动态血糖图谱分析，提供双重变异性分析和循证医学建议
- **核心文件**:
  - `AGPAI_Agent_V2.py` - 主要分析引擎
  - `AGPAI_Complete_System.md` - 完整系统文档
  - `AGPAI_Running_Guide.md` - 运行指南

### 📊 CRF设计系统 - 临床研究数据挖掘
- **路径**: `/crf_design/`
- **功能**: 临床研究表单设计和数据挖掘分析
- **核心文件**:
  - `CRF_Research_Mining_Agent.py` - 智能数据挖掘代理
  - `CRF-AI.md` - CRF设计AI助手说明
  - `CRF_Test_Analysis_Report.md` - 测试分析报告

### 🩸 ABPM - 动态血压监测系统
- **路径**: `/ABPM/`
- **功能**: 24小时动态血压监测分析
- **核心文件**:
  - `ABPM.md` - 完整系统设计文档

## 设备集成方案

### 📱 医疗设备对接
- **路径**: `/devices/`
- **功能**: 主流医疗设备的技术对接方案

#### 血糖仪对接 (BGM)
- **文件**: `BGM.md`
- **支持设备**: 
  - 国际品牌: Abbott, Roche, OneTouch, AgaMatrix, Dexcom
  - 国产品牌: 三诺, 鱼跃, 欧姆龙, 怡成, 爱科来
- **技术方案**: Bluetooth GATT协议, 厂商API集成

#### 综合医疗设备集成
- **文件**: `Medical_Devices_Integration.md`
- **设备类型**:
  - 血压计 (欧姆龙, 九安, 乐心等)
  - 心电图/心率设备 (华为, 小米, Polar等)
  - 体成分分析仪 (InBody, 欧姆龙, 华为等)
  - 血氧仪和脉搏设备
  - 其他慢病管理设备

## 临床研究工具

### 📋 标准化量表
- **PHQ-9**: 抑郁症筛查量表 (`PHQ9.md`, `PHQ9.csv`)
- **GAD-7**: 焦虑症筛查量表 (`GAD7.md`, `GAD7.csv`)
- **MMAS-8**: 药物依从性评估 (`MMAS8.md`, `MMAS8.csv`)
- **PSQI**: 睡眠质量评估 (`PSQI.md`, `PSQI.csv`)
- **MMSE**: 认知功能评估 (`MMSE.md`)
- **IPAQ**: 体力活动评估 (`ipaq_LF_cn.csv`, `ipaq_LF_cn.md`)

### 🔬 专科应用

#### 妊娠糖尿病 (GDM)
- **路径**: `/GDM/`
- **功能**: 妊娠糖尿病筛查和管理
- **核心文件**: `GDM_AI.md`, `GDMCRF.csv`

#### 胰腺癌糖代谢 (PPGM)
- **路径**: `/HuaShan/`
- **功能**: 胰腺癌患者血糖脆性分析
- **核心文件**: `PPGM.md`, `PPGM_methods.md`

#### 体重管理 (Fit)
- **路径**: `/Fit/`
- **功能**: 综合性体重管理系统
- **核心文件**: `Fit.md`, `IntegratedWeightManagementSystem.md`

## 技术架构

### 前端技术栈
- React 18 + TypeScript
- Ant Design Pro (UmiJS)
- ECharts (数据可视化)

### 后端技术栈
- NestJS + TypeScript
- PostgreSQL (主数据库)
- MongoDB (缓存/分析)
- Redis (会话/队列)

### 数据分析
- Python 数据科学栈
- 机器学习和AI分析
- 统计分析和报告生成

## 开发指南

### 环境设置
```bash
# 安装Python依赖
pip install -r requirements.txt

# 运行AGPAI分析
python AGPAI/AGPAI_Agent_V2.py

# 运行CRF数据挖掘
python crf_design/CRF_Research_Mining_Agent.py
```

### 文档更新
- 遵循Markdown格式
- 包含代码示例和使用说明
- 提供完整的技术规范

## 联系信息

**技术负责人**: 开发团队  
**文档更新**: 2025年8月  
**项目地址**: `/Users/williamsun/Documents/gplus/`

---

*本文档库持续更新中，如有问题请联系开发团队*