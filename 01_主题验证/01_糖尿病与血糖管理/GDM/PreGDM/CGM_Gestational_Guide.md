# 孕周期特异性CGM评估工具 - 使用指南

## 快速开始

### 安装依赖
```bash
pip install numpy pandas datetime dataclasses
```

### 基本使用
```python
from CGM_GDM_Final import GestationalCGMRiskAssessmentTool, PatientFactors

# 创建工具实例
tool = GestationalCGMRiskAssessmentTool()

# 设置患者信息
patient_factors = PatientFactors(
    gestational_weeks=28,     # 孕28周
    obesity=True,             # 肥胖
    advanced_age=True,        # 高龄
    previous_gdm=False        # 无既往GDM史
)

# 执行评估
result = tool.assess_patient(glucose_values, timestamps, patient_factors)

# 查看结果
if result['success']:
    print(f"孕期阶段: {result['gestational_period_cn']}")
    print(f"综合分型: {result['classification']['comprehensive_type']}")
    print(f"风险等级: {result['risk_scores']['risk_level']}")
    print(result['report'])
```

## 核心特性详解

### 1. 孕期自动识别

工具会根据孕周自动识别孕期阶段：

| 孕期 | 孕周范围 | 生理特点 | 评估重点 |
|------|----------|----------|----------|
| 孕早期 | <20周 | 器官发生期 | 预防胎儿畸形 |
| 孕中期 | 20-32周 | 胰岛素抵抗开始 | 预防妊娠并发症 |
| 孕晚期 | >32周 | 胰岛素抵抗高峰 | 确保分娩安全 |

### 2. 孕期特异性目标范围

```python
# 不同孕期的TIR目标范围
孕早期: 3.5-7.5 mmol/L    # 更严格，预防畸形
孕中期: 3.5-7.8 mmol/L    # 国际标准
孕晚期: 3.9-7.8 mmol/L    # 防止低血糖
```

### 3. 动态权重系统

```python
# 权重配置随孕期变化
孕早期: 控制40% | 变异性35% | 急性15% | 长期10%
孕中期: 控制35% | 变异性30% | 急性25% | 长期10%
孕晚期: 控制30% | 变异性25% | 急性35% | 长期10%
```

## 详细功能说明

### PatientFactors 参数说明

```python
@dataclass
class PatientFactors:
    gestational_weeks: float        # 孕周数（必需）
    previous_gdm: bool = False      # 既往GDM史
    obesity: bool = False           # 肥胖(BMI≥28)
    advanced_age: bool = False      # 高龄(≥35岁)
    family_history: bool = False    # 家族史
    pcos: bool = False             # 多囊卵巢综合征
    hypertension: bool = False     # 高血压史
```

### 评估结果结构

```python
{
    'success': True,                              # 评估是否成功
    'assessment_id': 'GA28W_202501091430',        # 评估ID
    'gestational_period': 'mid',                 # 孕期阶段
    'gestational_period_cn': '孕中期',           # 孕期中文名称
    'gestational_weeks': 28.0,                   # 孕周数
    'target_glucose_range': (3.5, 7.8),          # 目标血糖范围
    'risk_weights_used': {...},                  # 使用的权重配置
    'metrics': {...},                            # CGM指标
    'classification': {...},                     # 血糖分型
    'risk_scores': {...},                        # 风险评分
    'management_recommendations': {...},         # 管理建议
    'adverse_outcome_predictions': {...},        # 不良事件预测
    'clinical_summary': {...},                   # 临床摘要
    'report': '...',                            # 详细报告
    'assessment_timestamp': '2025-01-09T14:30:00' # 评估时间
}
```

## 高级功能

### 批量评估

```python
# 准备批量数据
patients_data = [
    {
        'patient_id': 'P001',
        'glucose_values': [...],
        'timestamps': [...],
        'patient_factors': PatientFactors(gestational_weeks=16, obesity=True)
    },
    {
        'patient_id': 'P002', 
        'glucose_values': [...],
        'timestamps': [...],
        'patient_factors': PatientFactors(gestational_weeks=30, previous_gdm=True)
    }
]

# 执行批量评估
results = tool.batch_assess(patients_data)

# 处理结果
for result in results:
    if result['success']:
        print(f"患者{result['patient_id']}: {result['risk_scores']['risk_level']}")
```

### 结果导出

```python
# 导出JSON格式
json_file = tool.export_results(result, 'json', 'patient_assessment')

# 导出文本报告
txt_file = tool.export_results(result, 'txt', 'patient_report')

# 导出Excel格式（需要pandas）
excel_file = tool.export_results(result, 'excel', 'patient_data')

# 批量结果导出
batch_file = tool.export_results(batch_results, 'json', 'batch_assessment')
```

## 临床应用场景

### 场景1：孕早期初次评估

```python
# 孕16周，既往GDM史，高龄
patient = PatientFactors(
    gestational_weeks=16,
    previous_gdm=True,
    advanced_age=True
)

result = tool.assess_patient(glucose_values, timestamps, patient)

# 重点关注：
# - 胎儿畸形风险
# - 血糖控制稳定性
# - 早期干预必要性
```

### 场景2：孕中期血糖恶化

```python
# 孕26周，肥胖，PCOS
patient = PatientFactors(
    gestational_weeks=26,
    obesity=True,
    pcos=True
)

result = tool.assess_patient(glucose_values, timestamps, patient)

# 重点关注：
# - 胎儿生长发育
# - 妊娠并发症预防
# - 治疗方案调整
```

### 场景3：孕晚期分娩准备

```python
# 孕36周，多重风险因素
patient = PatientFactors(
    gestational_weeks=36,
    previous_gdm=True,
    obesity=True,
    hypertension=True
)

result = tool.assess_patient(glucose_values, timestamps, patient)

# 重点关注：
# - 分娩时机选择
# - 新生儿并发症预防
# - 产后管理计划
```

## 分型解读指南

### A型-理想稳定
- **特征**：TIR≥80%, CV<25%
- **风险**：极低到低风险
- **管理**：标准产检，维持现状

### B型-良好控制
- **特征**：TIR 70-79%, CV稳定
- **风险**：低到中风险
- **管理**：定期监测，适当调整

### C型-餐后失控
- **特征**：餐后血糖升高明显
- **风险**：中等风险
- **管理**：餐后血糖管理，营养指导

### D型-持续高血糖
- **特征**：TIR<50%, 持续高血糖
- **风险**：高风险
- **管理**：强化治疗，密切监测

### F型-极不稳定
- **特征**：CV>50%, 血糖波动极大
- **风险**：极高风险
- **管理**：紧急干预，可能需要住院

## 风险预测解读

### 不良事件风险分级

| 风险水平 | 概率范围 | 临床意义 | 管理策略 |
|----------|----------|----------|----------|
| **低风险** | <10% | 常规管理 | 标准产检 |
| **中风险** | 10-20% | 需要关注 | 加强监测 |
| **高风险** | 20-40% | 积极干预 | 专科管理 |
| **极高风险** | >40% | 紧急处理 | 多学科协作 |

### 孕期特异性高风险事件

**孕早期重点：**
- 胎儿畸形风险
- 流产风险

**孕中期重点：**
- 巨大儿风险
- 妊娠高血压风险

**孕晚期重点：**
- 胎儿窘迫风险
- 新生儿低血糖风险

## 管理建议解读

### 产检频率调整

| 风险等级 | 孕早期 | 孕中期 | 孕晚期 |
|----------|--------|--------|--------|
| **绿级** | 标准 | 标准 | 标准 |
| **黄级** | 每3周 | 每2周 | 每2周 |
| **橙级** | 每2周 | 每周 | 每周 |
| **红级** | 每周 | 住院评估 | 住院管理 |

### CGM监测策略

- **间歇性CGM**：每周2-3天，适用于低风险
- **连续CGM**：持续监测，适用于中等风险
- **实时CGM**：实时预警，适用于高风险

### 专科会诊建议

- **内分泌科**：血糖控制不佳时
- **产科专家**：高风险孕妇管理
- **营养科**：个体化营养方案
- **新生儿科**：孕晚期高风险准备

## 常见问题解答

### Q1: 孕周数不准确怎么办？
A: 建议使用末次月经期结合早期超声核实孕周，确保评估准确性。

### Q2: CGM数据不完整如何处理？
A: 工具要求至少70%有效数据点，数据质量过低会给出警告提示。

### Q3: 不同孕期的目标范围依据是什么？
A: 基于NICE 2015, ADA 2023, IADPSG 2010等国际指南的孕期特异性建议。

### Q4: 权重调整的科学依据？
A: 基于Murphy HR (2018), Feig DS (2017), Kristensen K (2019)等循证医学文献。

### Q5: 如何处理评估结果的临床应用？
A: 结果仅供临床参考，需要结合患者具体情况和临床经验进行综合判断。

## 技术支持

### 系统要求
- Python 3.7+
- numpy >= 1.19.0
- pandas >= 1.3.0 (导出Excel功能)

### 性能优化
- 单次评估：<1秒
- 批量评估：支持并发处理
- 内存占用：每1000个数据点约2MB

### 错误处理
工具提供详细的错误信息和处理建议：

```python
if not result['success']:
    print(f"评估失败: {result['error']}")
    print(f"错误类型: {result['error_type']}")
    print(f"建议: {result['message']}")
```

## 版本更新日志

### v2.0.0 (当前版本)
- ✅ 新增孕周期特异性评估功能
- ✅ 动态权重调整机制
- ✅ 时间窗口风险预测
- ✅ 个体化管理建议
- ✅ 批量处理和结果导出
- ✅ 完整的演示和文档

### 未来计划
- 🔄 结合人工智能优化算法
- 🔄 增加更多生物标志物整合
- 🔄 开发Web界面和移动应用
- 🔄 多中心临床验证研究

---

**免责声明**: 本工具仅供临床辅助决策使用，不能替代医生的专业判断。所有治疗决策应基于完整的临床评估和患者个体情况。