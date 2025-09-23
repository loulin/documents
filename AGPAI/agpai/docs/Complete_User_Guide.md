# AGPAI 完整使用指南

## 🎯 项目概述

AGPAI（Advanced Glucose Pattern Analysis with Intelligence）是基于混沌理论和人工智能的高级血糖模式分析系统，专为临床血糖管理和糖尿病精准治疗设计。

### 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AGPAI 三Agent协同系统                      │
├─────────────────────────────────────────────────────────────┤
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

## 🚀 快速开始

### 环境要求

- Python >= 3.8
- 必需依赖包：numpy, pandas, scipy, matplotlib, openpyxl
- 可选依赖包：scikit-learn (Agent 3)

### 安装依赖

```bash
cd /path/to/agpai
pip install -r requirements.txt
```

### 基本使用示例

#### 单独使用Agent 1 (AGP专业分析器)

```python
# 导入Agent 1
from agpai.core.AGP_Professional_Analyzer import AGPProfessionalAnalyzer

# 初始化
agent1 = AGPProfessionalAnalyzer()

# 分析血糖数据
report = agent1.generate_professional_agp_report(
    data_path="patient_data.xlsx",
    patient_id="P001"
)

# 查看结果
print(f"TIR: {report['94_indicators']['target_standard_range']:.1f}%")
print(f"CV: {report['94_indicators']['cv']:.1f}%")
```

#### 单独使用Agent 2 (脆性临床顾问)

```python
# 导入Agent 2
from agpai.core.Brittleness_Clinical_Advisor import BrittlenessClinicalAdvisor

# 初始化
agent2 = BrittlenessClinicalAdvisor()

# 脆性分析
brittleness_profile = agent2.analyze_brittleness_profile(
    glucose_data=glucose_values,
    patient_info={"patient_id": "P001"}
)

# 查看脆性类型
print(f"脆性类型: {brittleness_profile.type.value}")
print(f"风险等级: {brittleness_profile.risk_level.value}")
```

#### 手动切点分析

```python
# 导入切点管理器
from agpai.core.Manual_Cutpoint_Manager import ManualCutpointManager
from agpai.core.Segmented_Brittleness_Analyzer import SegmentedBrittlenessAnalyzer

# 创建手动切点
manager = ManualCutpointManager()
surgery_cutpoint = manager.create_manual_cutpoint(
    timestamp='2025-07-30 08:00:00',
    cutpoint_type='PANCREATIC_SURGERY',
    description='胰十二指肠切除术'
)

# 分段分析
analyzer = SegmentedBrittlenessAnalyzer()
result = analyzer.analyze_with_cutpoints(
    glucose_data=data,
    timestamps=timestamps,
    patient_info=patient_info,
    manual_cutpoints=[surgery_cutpoint]
)
```

## 📊 Agent功能详解

### Agent 1: AGP专业分析器

**功能**: 94项专业AGP指标分析
**适用场景**: 标准临床AGP报告生成

#### 核心指标分类

1. **基础统计** (15项)
   - 平均血糖、中位数、标准差、变异系数
   - 最值、分位数、偏度、峰度等

2. **TIR分析** (10项)
   - 目标范围时间、严重低血糖时间
   - 不同血糖范围的时间分布

3. **变异性指标** (12项)
   - CV、MAGE、风险指数(LBGI/HBGI)
   - 血糖变化率相关指标

4. **时序模式** (7项)
   - Dawn现象、夜间稳定性
   - 昼夜节律、峰值/低谷时间

5. **餐时模式** (10项)
   - 三餐血糖平均值、峰值
   - 餐后血糖升高幅度

#### 使用示例

```python
# 完整的AGP分析
analyzer = AGPProfessionalAnalyzer()
report = analyzer.generate_professional_agp_report(
    data_path="cgm_data.xlsx",
    patient_id="P001"
)

# 获取关键指标
indicators = report['94_indicators']
interpretation = report['agp_interpretation']

print(f"整体控制评级: {interpretation['overall_control']}")
print(f"TIR: {indicators['target_standard_range']:.1f}%")
print(f"平均血糖: {indicators['mean_glucose']:.1f} mmol/L")
```

### Agent 2: 脆性临床顾问

**功能**: 基于混沌理论的血糖脆性分型
**适用场景**: 个性化治疗策略制定

#### 6种脆性类型

1. **I型混沌脆性**
   - 特征: 极不稳定，大幅随机波动
   - 治疗: 混沌稳定化治疗，保守减量
   - 目标HbA1c: 8.0-8.5%

2. **II型准周期脆性**
   - 特征: 中等混沌特征，准周期波动
   - 治疗: 节律重建治疗，时间优化给药
   - 目标HbA1c: 7.5-8.0%

3. **III型随机脆性**
   - 特征: 高变异且无相关性
   - 治疗: 智能化精准治疗，考虑胰岛素泵
   - 目标HbA1c: 7.0-7.5%

4. **IV型记忆缺失脆性**
   - 特征: 血糖调节系统失去'记忆'功能
   - 治疗: 外源性记忆重建
   - 目标HbA1c: 7.5-8.0%

5. **V型频域脆性**
   - 特征: 血糖节律完全紊乱
   - 治疗: 频域稳定化治疗
   - 目标HbA1c: 7.0-7.5%

6. **稳定型**
   - 特征: 血糖调节系统稳定
   - 治疗: 维持优化治疗
   - 目标HbA1c: 6.5-7.0%

#### 混沌分析指标

- **Lyapunov指数**: 衡量系统敏感性和混沌程度
- **Shannon熵**: 评估血糖分布的不确定性
- **Hurst指数**: 反映长程记忆和持续性
- **近似熵**: 测量时间序列的规律性

#### 使用示例

```python
# 脆性分析
advisor = BrittlenessClinicalAdvisor()
profile = advisor.analyze_brittleness_profile(
    glucose_data=glucose_values
)

# 获取治疗策略
strategy = advisor.treatment_strategies[profile.type]
print(f"脆性类型: {profile.type.value}")
print(f"主要治疗策略: {strategy['primary_strategy']}")
print(f"胰岛素方案: {strategy['insulin_approach']}")
```

### Agent 3: 综合智能分析器

**功能**: 120项扩展指标和预测性分析
**适用场景**: 深度研究分析和预测建模

#### 扩展指标分类

1. **基础统计扩展** (20项)
2. **高级变异性分析** (15项)
3. **深度时序分析** (18项)
4. **多维度模式识别** (12项)
5. **机器学习特征** (15项)
6. **预测性建模** (10项)
7. **个性化评估** (12项)
8. **风险层次化** (8项)
9. **治疗优化** (10项)

#### 使用示例

```python
# 综合分析
analyzer = ComprehensiveIntelligenceAnalyzer()
indicators = analyzer.calculate_extended_120_indicators(
    glucose_data=glucose_values,
    timestamps=timestamps
)

# 预测分析
predictions = analyzer.generate_predictive_analysis(
    glucose_data=glucose_values,
    timestamps=timestamps
)
```

## 🏥 临床应用场景

### 胰腺外科应用

#### 完整工作流程

1. **术前评估**
   ```python
   # 基线脆性评估
   baseline_profile = agent2.analyze_brittleness_profile(pre_surgery_data)
   print(f"术前脆性类型: {baseline_profile.type.value}")
   ```

2. **手术切点标记**
   ```python
   # 标记手术时间点
   surgery_cutpoint = manager.create_manual_cutpoint(
       timestamp='2025-07-30 08:00:00',
       cutpoint_type='PANCREATIC_SURGERY',
       clinical_details={
           'surgeon': 'XXX主任',
           'duration_hours': 6,
           'complications': '无'
       }
   )
   ```

3. **术后监测**
   ```python
   # 分段脆性分析
   result = analyzer.analyze_with_cutpoints(
       glucose_data=post_surgery_data,
       timestamps=timestamps,
       manual_cutpoints=[surgery_cutpoint]
   )
   ```

### 内分泌科应用

#### 复杂糖尿病管理

```python
# 多Agent协同分析
agent1_report = agent1.generate_professional_agp_report(data_path)
agent2_profile = agent2.analyze_brittleness_profile(glucose_data)

# 综合治疗建议
if agent2_profile.type == BrittlenessType.CHAOTIC:
    print("建议采用混沌稳定化治疗策略")
    target_tir = 60  # 降低TIR目标
elif agent1_report['94_indicators']['cv'] > 50:
    print("建议优先改善血糖变异性")
```

### ICU/CCU应用

#### 重症血糖管理

```python
# 实时风险评估
risk_assessment = agent2.analyze_brittleness_profile(icu_glucose_data)

if risk_assessment.risk_level == RiskLevel.CRITICAL:
    print("⚠️ 极高风险，需要24小时严密监控")
    # 触发紧急协议
```

## 🛠️ 手动切点管理系统

### 支持的切点类型

#### 手术相关
- `PANCREATIC_SURGERY`: 胰腺手术
- `GALLBLADDER_SURGERY`: 胆囊手术

#### 药物调整
- `INSULIN_INITIATION`: 胰岛素启动
- `INSULIN_ADJUSTMENT`: 胰岛素调整
- `ORAL_MEDICATION_CHANGE`: 口服药物调整
- `STEROID_TREATMENT`: 激素治疗

#### 营养管理
- `TPN_INITIATION`: TPN启动
- `TPN_TO_EN_TRANSITION`: TPN转EN
- `DIET_RESUMPTION`: 饮食恢复

#### 临床事件
- `INFECTION`: 感染
- `STRESS_RESPONSE`: 应激反应
- `DISCHARGE_PREPARATION`: 出院准备

### 切点创建示例

```python
# 详细切点信息
cutpoint = manager.create_manual_cutpoint(
    timestamp='2025-07-30 08:00:00',
    cutpoint_type='PANCREATIC_SURGERY',
    description='胰十二指肠切除术（Whipple手术）',
    clinical_details={
        'surgeon': 'XXX主任',
        'duration_hours': 6,
        'complications': '无',
        'blood_loss_ml': 800,
        'anesthesia_type': '全麻'
    },
    expected_duration_hours=72
)
```

### 验证系统

系统会自动验证切点的合理性：

```python
validation = manager.validate_cutpoint_timing(cutpoint, data, timestamps)
print(f"时间合理性: {validation['timing_reasonable']}")
print(f"数据完整性: {validation['data_completeness']}")
print(f"预期效应: {validation['expected_effect_match']}")
```

## 📈 结果解读指南

### AGP解读

#### TIR (Time in Range)
- **优秀**: >70%
- **良好**: 50-70%
- **一般**: 30-50%
- **较差**: <30%

#### CV (变异系数)
- **稳定**: <25%
- **可接受**: 25-36%
- **不稳定**: 36-50%
- **严重不稳定**: >50%

### 脆性分型解读

#### 临床意义
- **混沌脆性**: 需要保守治疗，避免过度干预
- **准周期脆性**: 关注时间节律，优化给药时机
- **随机脆性**: 适合智能化治疗，考虑胰岛素泵
- **稳定型**: 可以实施精细化管理

#### 治疗调整原则
- 根据脆性类型调整目标HbA1c
- 选择合适的胰岛素方案
- 制定个性化监测频率

## 🔧 高级配置

### 参数调整

在 `config/config.yaml` 中可以调整：

```yaml
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

### 自定义阈值

通过修改 `config/` 目录下的CSV文件可以调整：
- 脆性分型阈值
- 混沌分析参数
- 切点检测灵敏度
- 临床建议规则

## 🚨 常见问题与解决

### Q1: Agent导入失败
**问题**: `ModuleNotFoundError: No module named 'xxx'`
**解决**: 检查Python路径设置，确保正确导入模块

```python
import sys
import os
sys.path.append('/path/to/agpai')
```

### Q2: 数据格式不正确
**问题**: 血糖数据无法读取
**解决**: 确保数据格式正确

```python
# 标准格式
df = pd.DataFrame({
    'timestamp': timestamps,  # datetime类型
    'glucose': glucose_values  # float类型，mmol/L
})
```

### Q3: 脆性分型不稳定
**问题**: 多次分析结果不一致
**解决**: 使用最新的Hurst指数算法

```python
# 检查算法版本
print(f"Agent 2版本: {agent2.version}")
# 应该使用稳定的多窗口R/S分析
```

### Q4: 切点验证失败
**问题**: 手动切点验证不通过
**解决**: 检查切点时间和数据匹配

```python
# 验证切点
validation = manager.validate_cutpoint_timing(cutpoint, data, timestamps)
if not validation['timing_reasonable']:
    print("切点时间需要调整")
```

## 📝 最佳实践

### 数据准备
1. **数据质量**: 确保CGM数据完整性>70%
2. **时间格式**: 使用标准datetime格式
3. **血糖单位**: 统一使用mmol/L

### 分析流程
1. **先运行Agent 1**: 获得标准AGP指标
2. **再运行Agent 2**: 进行脆性分型
3. **结合临床信息**: 制定个性化方案

### 切点管理
1. **及时标注**: 治疗调整后立即添加切点
2. **详细记录**: 填写完整的临床细节
3. **质量控制**: 重视系统验证警告

## 📊 性能基准

### 算法性能
- **分析速度**: 单患者<30秒，批量<5分钟/100例
- **算法一致性**: Hurst指数100%稳定
- **成功率**: 99.4% (345/347患者验证)

### 系统要求
- **内存**: <500MB
- **CPU**: 支持多核并行
- **存储**: 每例患者报告约1-2MB

## 🔮 未来规划

### 短期目标 (6个月)
- 实时分析支持
- 可视化增强
- EMR/HIS集成接口

### 中期目标 (1-2年)
- AI增强预测
- 多模态数据融合
- 云端SaaS服务

### 长期愿景 (3-5年)
- 国际标准建立
- 产业化部署
- 全球推广应用

## 📞 技术支持

### 获取帮助
- **文档**: 查看 `docs/` 目录下的详细文档
- **示例**: 运行 `examples/` 目录下的演示脚本
- **问题**: 提交GitHub Issue或联系开发团队

### 联系信息
- **项目地址**: `/Users/williamsun/Documents/gplus/docs/AGPAI/agpai/`
- **文档路径**: `docs/` 目录
- **示例路径**: `examples/` 目录

---

**AGPAI v1.0** - 让血糖管理更智能，让糖尿病治疗更精准 🎯