# AGPAI增强版智能标注系统使用指南

## 系统概述

AGPAI增强版智能标注系统在原有的57种视觉指标分析基础上，新增了AGP图表和每日血糖曲线的智能标注功能。系统能够自动识别临床显著的血糖模式，并在图表上进行直观的标注和解读。

## 系统特性

### 🎯 核心功能
- **57种视觉指标分析**：完整的AGP模式识别
- **智能AGP标注**：自动标注黎明现象、餐后峰值、目标范围等
- **每日曲线标注**：标注低血糖、高血糖、急剧变化等事件
- **临床解读**：基于循证医学的专业解读
- **多格式输出**：PNG图表、JSON报告、详细分析

### 🔍 标注类型
- **黎明现象检测**：凌晨4-8点血糖变化模式
- **餐后血糖分析**：三餐后血糖反应评估  
- **目标范围评估**：TIR、TAR、TBR分析
- **血糖变异性**：CV、分位数带宽等指标
- **夜间稳定性**：睡眠期间血糖平稳度
- **异常事件**：低血糖、高血糖、急剧变化

## 快速开始

### 1. 环境准备

```bash
# 确保安装所需依赖
pip install pandas numpy matplotlib seaborn scipy
```

### 2. 基本使用

```python
from AGP_Intelligent_Annotation_System import EnhancedAGPAISystem

# 创建系统实例
enhanced_agpai = EnhancedAGPAISystem()

# 患者信息
patient_info = {
    'name': '张三',
    'age': 45,
    'gender': '男',
    'diabetes_type': 'T2DM',
    'diabetes_duration': '8年',
    'cgm_device': 'Dexcom G6'
}

# 执行分析
results = enhanced_agpai.comprehensive_analysis_with_annotations(
    cgm_file_path="path/to/your/cgm_data.csv",
    patient_info=patient_info,
    output_dir="./output"
)
```

### 3. 输出文件

分析完成后会生成以下文件：
- `AGP_智能标注图表_YYYYMMDD_HHMMSS.png`
- `每日血糖曲线_智能标注_YYYYMMDD_HHMMSS.png`
- `AGPAI_完整智能分析报告_YYYYMMDD_HHMMSS.json`

## 详细功能说明

### AGP图表智能标注

#### 标注内容
1. **黎明现象标注**
   - 位置：凌晨4-8点血糖峰值处
   - 内容：上升速率（mmol/L/h）
   - 颜色：红色（严重）、橙色（中等）

2. **餐后峰值标注**
   - 位置：早餐后血糖最高点
   - 内容：升高幅度（mmol/L）
   - 颜色：根据严重程度分级

3. **目标范围标注**
   - 位置：TIR偏低的时段
   - 内容：TIR百分比和偏离程度
   - 颜色：红色或橙色警示

4. **夜间稳定性标注**
   - 位置：夜间不稳定时段
   - 内容：平坦度指数
   - 颜色：橙色提醒

5. **血糖变异性标注**
   - 位置：变异最大的时段
   - 内容：变异系数（CV%）
   - 颜色：根据严重程度

#### 图表特性
- **分位数带显示**：5%-95%和25%-75%分位数
- **目标范围背景**：3.9-10.0 mmol/L绿色区域
- **危险区域**：<3.0和>13.9 mmol/L红色背景
- **关键指标框**：TIR、CV、平滑度等指标
- **时间轴标签**：24小时格式，2小时间隔

### 每日血糖曲线标注

#### 标注事件
1. **餐后峰值**
   - 检测：餐后2小时内血糖升高>3.0 mmol/L
   - 标注："+X.X mmol/L"，颜色分级
   - 位置：峰值点上方

2. **低血糖事件**
   - 检测：血糖<3.9 mmol/L
   - 标注："低血糖 X.X"
   - 颜色：红色警示

3. **高血糖事件**
   - 检测：血糖>13.9 mmol/L
   - 标注："高血糖 X.X"
   - 颜色：深红色警示

4. **急剧变化**
   - 检测：变化速率>5或<-3 mmol/L/h
   - 标注："急升"或"急降"
   - 颜色：橙色或蓝色

#### 图表特性
- **餐时标记**：早餐、午餐、晚餐时段背景
- **目标范围**：3.9-10.0 mmol/L参考线
- **连续显示**：7天曲线垂直排列
- **时间轴**：24小时，4小时间隔标记

## 高级使用

### 自定义标注规则

```python
# 创建自定义标注引擎
from AGP_Intelligent_Annotation_System import AGPAnnotationEngine

annotator = AGPAnnotationEngine()

# 修改标注阈值
custom_thresholds = {
    'dawn_slope_threshold': 0.3,  # 降低黎明现象检测阈值
    'postprandial_threshold': 2.5,  # 调整餐后峰值阈值
    'tir_target': 75  # 提高TIR目标
}

# 应用自定义规则（需要修改源码）
```

### 批量处理

```python
import os
from pathlib import Path

# 批量处理多个CGM文件
cgm_files = Path("./cgm_data").glob("*.csv")

for cgm_file in cgm_files:
    patient_name = cgm_file.stem
    patient_info = {'name': patient_name}
    
    results = enhanced_agpai.comprehensive_analysis_with_annotations(
        cgm_file_path=str(cgm_file),
        patient_info=patient_info,
        output_dir=f"./output/{patient_name}"
    )
    print(f"完成 {patient_name} 的分析")
```

### 结果数据提取

```python
# 提取分析结果
analysis_data = results['analysis_results']
report_data = results['intelligent_report']

# 关键指标
tir = analysis_data.get('target_range_coverage', 0)
cv = analysis_data.get('glucose_coefficient_of_variation', 0)
smoothness = analysis_data.get('median_curve_smoothness', 0)

print(f"TIR: {tir:.1f}%")
print(f"CV: {cv:.1f}%")
print(f"平滑度: {smoothness:.3f}")

# 临床发现
findings = report_data['key_findings']
for finding in findings:
    print(f"发现: {finding['description']}")
    print(f"意义: {finding['clinical_significance']}")
```

## CGM数据格式要求

### 支持的格式

1. **Dexcom格式**
   ```csv
   Timestamp (YYYY-MM-DDTHH:MM:SS),Glucose Value (mg/dL)
   2024-01-01T00:00:00,120
   2024-01-01T00:15:00,115
   ```

2. **FreeStyle格式**
   ```csv
   时间,血糖值
   2024/01/01 00:00,6.7
   2024/01/01 00:15,6.4
   ```

3. **通用CSV格式**
   ```csv
   timestamp,glucose
   2024-01-01 00:00:00,6.7
   2024-01-01 00:15:00,6.4
   ```

4. **Tab分隔格式（R002 V5.txt样式）**
   ```
   ID	时间	记录类型	葡萄糖历史记录（mmol/L）
   001	2024/01/01 00:00	历史记录	6.7
   001	2024/01/01 00:15	历史记录	6.4
   ```

### 数据质量要求

- **最少数据量**：14天，每天≥20个数据点
- **数据完整性**：≥70%数据可用
- **时间范围**：连续的时间序列
- **血糖单位**：mmol/L（自动转换mg/dL）

## 输出解读

### AGP图表解读

1. **查看标注优先级**
   - 🔴 红色：需要立即关注
   - 🟡 橙色：建议优化
   - 🔵 蓝色：一般性建议
   - ✅ 绿色：表现良好

2. **重点关注区域**
   - 凌晨4-8点：黎明现象
   - 餐后2小时：血糖峰值
   - 夜间：血糖稳定性
   - 整体：目标范围覆盖

3. **曲线形态分析**
   - 平滑度：血糖控制稳定性
   - 对称性：生活规律性
   - 分位数带：血糖变异程度

### 每日曲线解读

1. **事件识别**
   - 低血糖：红色标注，关注原因
   - 高血糖：深红标注，调整治疗
   - 餐后峰值：评估餐时管理
   - 急剧变化：查找诱因

2. **模式识别**
   - 餐后反应一致性
   - 夜间血糖稳定性
   - 运动等生活事件影响

### 报告数据解读

```json
{
  "overall_assessment": {
    "level": "良好",
    "overall_score": 75.2,
    "description": "血糖控制基本稳定，存在改善空间"
  },
  "key_findings": [
    {
      "type": "dawn_phenomenon",
      "severity": "moderate",
      "description": "检测到明显黎明现象，血糖上升速率1.2mmol/L/h",
      "clinical_significance": "提示基础胰岛素剂量或时机需要调整"
    }
  ],
  "clinical_recommendations": [
    {
      "category": "insulin_adjustment",
      "priority": "medium",
      "recommendation": "建议调整基础胰岛素剂量或注射时间",
      "rationale": "黎明现象检测，可能需要优化基础胰岛素治疗",
      "follow_up": "1-2周后复查AGP评估效果"
    }
  ]
}
```

## 故障排除

### 常见问题

1. **文件读取失败**
   ```
   错误：无法读取CGM文件
   解决：检查文件格式和编码（建议UTF-8）
   ```

2. **数据质量不足**
   ```
   错误：数据质量不合格，无法进行可靠的AGP分析
   解决：确保至少14天数据，数据完整性>70%
   ```

3. **图表显示异常**
   ```
   错误：中文字体显示方框
   解决：安装中文字体或修改字体设置
   ```

4. **内存不足**
   ```
   错误：处理大文件时内存溢出
   解决：分批处理数据或增加系统内存
   ```

### 性能优化

```python
# 大数据集处理优化
enhanced_agpai = EnhancedAGPAISystem()

# 设置较短的分析周期
results = enhanced_agpai.comprehensive_analysis_with_annotations(
    cgm_file_path="large_dataset.csv",
    patient_info=patient_info,
    analysis_days=7,  # 减少分析天数
    output_dir="./output"
)
```

## 扩展开发

### 自定义标注类型

```python
class CustomAnnotationEngine(AGPAnnotationEngine):
    def identify_annotation_points(self, analysis_results, agp_curve):
        annotations = super().identify_annotation_points(analysis_results, agp_curve)
        
        # 添加自定义标注逻辑
        custom_annotation = {
            'type': 'custom_pattern',
            'x': 12,  # 小时
            'y': 8.0,  # 血糖值
            'text': '自定义标注',
            'priority': 'medium_priority',
            'arrow_direction': 'up'
        }
        annotations.append(custom_annotation)
        
        return annotations
```

### 集成第三方系统

```python
# 与HIS系统集成示例
def integrate_with_his(patient_id, results):
    his_data = {
        'patient_id': patient_id,
        'analysis_date': datetime.now(),
        'tir': results['analysis_results']['target_range_coverage'],
        'cv': results['analysis_results']['glucose_coefficient_of_variation'],
        'recommendations': results['intelligent_report']['clinical_recommendations']
    }
    
    # 发送到HIS系统
    # his_api.upload_agp_analysis(his_data)
```

## 版本更新

### v1.0 特性
- ✅ 基础AGP标注功能
- ✅ 每日曲线标注
- ✅ 57种视觉指标分析
- ✅ 临床解读报告
- ✅ 多格式输出

### 计划更新
- 📅 v1.1：增加运动、用药事件标注
- 📅 v1.2：支持多周期趋势分析
- 📅 v1.3：AI驱动的个性化建议
- 📅 v2.0：实时标注和预警系统

## 技术支持

### 联系方式
- 邮箱：support@agpai.com
- 文档：https://docs.agpai.com
- 问题报告：https://github.com/agpai/issues

### 培训资源
- [AGPAI标注系统培训视频](link)
- [临床应用案例集](link)
- [最佳实践指南](link)

---

*本使用指南持续更新，请关注最新版本。*