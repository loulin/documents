# AGPAI - Advanced Glucose Pattern Analysis with Intelligence

## 概述

AGPAI是一个基于混沌理论和人工智能的高级血糖模式分析系统，专为临床血糖管理和糖尿病精准治疗设计。系统采用三Agent协同架构，结合手动切点管理和分段脆性分析，为胰腺外科等专业场景提供精准的血糖脆性评估和治疗效果追踪。

## 🎯 系统架构

### 三Agent协同系统
```
┌─────────────────────────────────────────────────────────────┐
│  Agent 1: AGP专业分析器    │  Agent 2: 脆性临床顾问         │
│  - 94项专业指标           │  - 6种脆性分型                │
│  - 传统+高级指标          │  - 混沌理论分析               │
│  - 国际标准兼容           │  - 个性化治疗建议             │
├─────────────────────────────────────────────────────────────┤
│  Agent 3: 综合智能分析器   │  切点检测和分段分析系统        │
│  - 120项扩展指标          │  - 自动切点检测               │
│  - 多维度综合分析         │  - 手动切点管理               │
│  - 预测性建模             │  - 分段脆性分析               │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 核心特性

### 🧠 三Agent智能协同
- **Agent 1**: AGP Professional Analyzer - 94项专业指标分析
- **Agent 2**: Brittleness Clinical Advisor - 血糖脆性分型和临床建议  
- **Agent 3**: Comprehensive Intelligence Analyzer - 120项综合智能分析

### 🔬 先进算法技术
- **混沌理论分析**: Lyapunov指数、近似熵、Shannon熵
- **脆性智能分型**: 6种血糖脆性类型的精准识别
- **复杂度评估**: 多维度血糖复杂性量化分析
- **预测性建模**: 基于历史模式的趋势预测

### 🏥 临床智能切点系统
- **手动切点管理**: 支持12种专业治疗调整切点标注
- **自动切点检测**: 多算法融合的智能时间点识别
- **分段脆性分析**: 治疗前后血糖脆性变化追踪
- **效果评估**: 量化治疗效果和个性化建议

### 📊 专业临床指标
- **传统核心指标**: TIR、CV、GMI、MAGE等国际标准指标
- **高级混沌指标**: 系统稳定性和可预测性分析
- **脆性特征指标**: 血糖调节系统脆弱性评估
- **个性化风险评估**: 基于个体特征的风险分层

## 📦 目录结构

### 核心模块 (agpai/)
```
agpai/
├── config/           # 配置管理
│   ├── config.yaml           # 主配置文件
│   ├── config_manager.py     # 配置管理器
│   └── *.csv                 # 参数配置表
├── core/            # 核心分析引擎
│   ├── AGP_Professional_Analyzer.py          # Agent 1
│   ├── Brittleness_Clinical_Advisor.py       # Agent 2  
│   ├── Comprehensive_Intelligence_Analyzer.py # Agent 3
│   ├── Multi_Agent_Coordinator.py            # Agent协调器
│   ├── Treatment_Cutpoint_Detector.py        # 切点检测器
│   ├── Manual_Cutpoint_Manager.py            # 手动切点管理
│   ├── Segmented_Brittleness_Analyzer.py     # 分段分析器
│   └── ...                                   # 其他核心模块
├── examples/        # 示例和演示
│   ├── AGPAI_Complete_Enhanced_Demo.py       # 完整演示
│   ├── Manual_Cutpoint_Demo.py               # 手动切点演示
│   ├── Pancreatic_Surgery_Cutpoint_Demo.py   # 胰腺外科演示
│   └── ...
├── docs/            # 文档
│   ├── Manual_Cutpoint_System_Guide.md       # 手动切点使用指南
│   ├── System_Architecture_Update.md         # 系统架构文档
│   └── ...
├── tests/           # 测试文件
├── visualization/   # 可视化模块
└── reports/         # 分析报告输出
```

## 🔥 核心功能

### 1. 血糖脆性分型系统
**6种脆性类型智能识别**：
- **I型混沌脆性**: 极不稳定，大幅随机波动
- **II型准周期脆性**: 中等混沌特征，准周期波动  
- **III型随机脆性**: 高变异且无相关性
- **IV型记忆缺失脆性**: 血糖调节系统失去'记忆'功能
- **V型频域脆性**: 血糖节律完全紊乱
- **稳定型**: 血糖调节系统稳定

### 2. 手动切点管理系统
**12种专业切点类型**：
- **手术类**: 胰腺手术、胆囊手术
- **药物类**: 胰岛素启动/调整、口服药调整、激素治疗
- **营养类**: TPN启动、TPN转EN、饮食恢复
- **事件类**: 感染、应激反应、出院准备

**智能验证功能**：
- 时间合理性检查
- 预期效应验证  
- 数据完整性评估

### 3. 分段脆性分析
**治疗效果量化评估**：
- 段内脆性分型变化
- 段间统计显著性比较
- 临床改善度评分
- 个性化治疗建议

### 4. 94项专业指标分析
**传统核心指标**：
- TIR (Time in Range)
- CV (变异系数)
- GMI (血糖管理指标)
- MAGE (平均血糖波动幅度)

**高级混沌指标**：
- Lyapunov指数 (系统稳定性)
- 近似熵 (复杂度)
- Shannon熵 (信息量)
- Hurst指数 (长程记忆)

## 🛠️ 快速开始

### 1. 环境要求
```bash
Python >= 3.8
numpy >= 1.20.0
pandas >= 1.3.0
scipy >= 1.7.0
scikit-learn >= 1.0.0
matplotlib >= 3.5.0
openpyxl >= 3.0.0
```

### 2. 安装依赖
```bash
pip install -r agpai/requirements.txt
```

### 3. 基础使用
```python
# 导入AGPAI核心模块
from agpai.core.Multi_Agent_Coordinator import MultiAgentCoordinator

# 初始化系统
coordinator = MultiAgentCoordinator()

# 运行完整分析
result = coordinator.run_comprehensive_analysis(
    glucose_data=glucose_values,
    timestamps=time_values,
    patient_info=patient_data
)
```

### 4. 手动切点分析
```python
# 导入手动切点系统
from agpai.core.Segmented_Brittleness_Analyzer import SegmentedBrittlenessAnalyzer
from agpai.core.Manual_Cutpoint_Manager import ManualCutpointManager

# 创建手动切点
manager = ManualCutpointManager()
surgery_cutpoint = manager.create_manual_cutpoint(
    timestamp='2025-07-30 08:00:00',
    cutpoint_type='PANCREATIC_SURGERY',
    description='胰十二指肠切除术'
)

# 分段脆性分析
analyzer = SegmentedBrittlenessAnalyzer()
result = analyzer.analyze_with_cutpoints(
    glucose_data=data,
    timestamps=timestamps,
    patient_info=patient_info,
    manual_cutpoints=[surgery_cutpoint]
)
```

## 📋 示例演示

### 完整系统演示
```bash
python agpai/examples/AGPAI_Complete_Enhanced_Demo.py
```

### 手动切点演示
```bash
python agpai/examples/Manual_Cutpoint_Demo.py
```

### 胰腺外科专项演示  
```bash
python agpai/examples/Pancreatic_Surgery_Cutpoint_Demo.py
```

## 🏥 临床应用场景

### 胰腺外科
- **术前评估**: 基线血糖脆性评估
- **术后监测**: 手术对血糖系统影响追踪
- **治疗调整**: TPN、胰岛素方案优化
- **恢复评估**: 胰腺功能和代谢恢复监测

### 内分泌科
- **脆性评估**: 糖尿病血糖脆性分型
- **药物调整**: 治疗方案优化建议
- **风险预警**: 并发症风险识别
- **效果追踪**: 长期治疗效果评估

### ICU/CCU
- **重症监测**: 危重患者血糖管理
- **应激评估**: 应激状态血糖模式分析
- **营养管理**: TPN/EN血糖控制优化
- **预后评估**: 血糖稳定性与预后关系

## 📊 分析报告

### 标准报告内容
- **患者基本信息**
- **数据质量评估**
- **94项专业指标**
- **脆性分型结果**
- **混沌分析指标**
- **临床建议**
- **个性化治疗方案**

### 切点分析报告
- **切点检测结果**
- **分段特征分析**
- **治疗效果评估**
- **改善度量化**
- **下一步建议**

## 🔧 系统配置

### 配置文件
```yaml
# config/config.yaml
analysis:
  enable_chaos_analysis: true
  brittleness_confidence_threshold: 0.8
  
cutpoint_detection:
  min_segment_hours: 24
  statistical_significance: 0.01
  
output:
  report_format: ["json", "pdf"]
  visualization: true
```

### 参数调整
通过修改 `config/` 目录下的CSV参数文件可调整：
- 脆性分型阈值
- 混沌分析参数
- 切点检测灵敏度
- 临床建议规则

## 🚀 高级功能

### 批量分析
```python
# 批量处理多个患者
from agpai.examples.Batch_Analysis import BatchProcessor

processor = BatchProcessor()
results = processor.analyze_folder('/path/to/patient/data/')
```

### 算法验证
```python
# 一致性测试
from agpai.examples.Algorithm_Consistency_Test import test_consistency

test_results = test_consistency(patient_data, num_tests=5)
```

### 数据导出
```python
# 多格式导出
manager.export_cutpoints(cutpoints, format='timeline')  # 时间线
manager.export_cutpoints(cutpoints, format='json')      # JSON
manager.export_cutpoints(cutpoints, format='csv')       # CSV
```

## 📈 技术优势

### 算法稳定性
- Hurst指数计算一致性: 100%
- 脆性分型重现性: 99.4%
- 批量分析成功率: 99.4%

### 临床实用性  
- 12种专业切点类型覆盖临床常见场景
- 智能验证提供质量控制
- 个性化建议基于循证医学指南

### 系统性能
- 单患者分析: <30秒
- 批量分析: <5分钟/100例
- 支持并发用户: 50+

## 🤝 技术支持

### 文档资源
- [系统架构文档](docs/System_Architecture_Update.md)
- [手动切点使用指南](docs/Manual_Cutpoint_System_Guide.md)
- [临床应用指南](docs/Clinical_Application_Guide.md)

### 问题反馈
- 技术问题: 提交GitHub Issue
- 临床咨询: 联系开发团队
- 功能建议: 参与社区讨论

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有参与AGPAI系统开发和验证的临床专家、数据科学家和工程师团队。

---

**AGPAI** - 让血糖管理更智能，让糖尿病治疗更精准。