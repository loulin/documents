# Agent_ZS HMC CGM报告生成器 v2.0 增强版

## 📋 概述

基于GPlus CGM报告样式的增强版报告生成器，提供专业的可视化血糖分析报告。

## 🎨 新增功能（基于GPlus PDF模板）

### 1. **AGP (Ambulatory Glucose Profile) 可视化**
- 百分位数带状图 (5-95%, 25-75%)
- 中位数曲线展示
- 目标范围标注 (3.9-10.0 mmol/L)
- 24小时完整血糖模式展示

### 2. **14天每日血糖曲线**
- 小图布局 (Small Multiples)
- 每日TIR、平均值、CV统计
- 快速识别血糖模式变化

### 3. **TIR/TAR/TBR可视化条**
- 直观的堆叠柱状图
- 颜色编码（绿色=TIR，橙色=TAR，红色=TBR）
- 百分比精确标注

### 4. **专业HTML报告**
- 响应式设计
- 可打印为PDF（浏览器打印功能）
- Chart.js交互式图表
- 符合医疗报告规范

## 🚀 快速开始

### 安装依赖

```bash
pip install pandas numpy
```

### 基础用法

```python
from Agent_ZS_HMC_Report_Generator_Enhanced import generate_enhanced_report

# 患者信息
patient_info = {
    "name": "张三",
    "age": 45,
    "gender": "男"
}

# 生成报告
html_path = generate_enhanced_report(
    filepath="cgm_data.csv",           # CGM数据文件
    patient_id="P001",                  # 患者ID
    patient_info=patient_info,          # 患者信息
    output_path="CGM_Report.html"       # 输出路径
)

print(f"✅ 报告已生成: {html_path}")
```

### 数据格式要求

CSV文件应包含以下列：

```csv
timestamp,glucose_value
2025-10-01 08:00:00,5.5
2025-10-01 08:05:00,5.8
2025-10-01 08:10:00,6.2
...
```

支持的列名变体：
- `timestamp` / `Timestamp` / `time`
- `glucose_value` / `glucose` / `Glucose` / `value`

## 📊 报告内容

### 1. 报告头部
- 患者基本信息
- 监测周期
- 数据质量评估

### 2. 核心指标摘要卡片
- **平均血糖 (MG)**
- **血糖管理指标 (GMI)** - 目标 < 7.0%
- **目标范围内时间 (TIR)** - 目标 > 70%

### 3. 血糖分布总览
- 可视化TIR/TAR/TBR分布条
- 三区域百分比统计

### 4. AGP动态血糖图谱
- 5-95%百分位数范围（浅蓝色）
- 25-75%百分位数范围（深蓝色）
- 中位数曲线（深蓝线）
- 目标范围带（绿色背景）

### 5. 14天每日血糖曲线
- 7x2网格布局
- 每日小图包含：
  - 全天血糖曲线
  - TIR百分比
  - 平均血糖值
  - CV变异系数

## 🎯 对比原版改进

| 功能 | 原版 (v1.0) | 增强版 (v2.0) |
|------|------------|--------------|
| 输出格式 | JSON | HTML (可打印PDF) |
| AGP可视化 | ❌ | ✅ 百分位数带状图 |
| 每日曲线 | ❌ | ✅ 14天小图网格 |
| TIR可视化 | 仅数值 | ✅ 堆叠柱状图 |
| 交互性 | 无 | ✅ Chart.js图表 |
| 样式设计 | 基础 | ✅ GPlus专业样式 |

## 📖 GPlus样式特性

基于真实GPlus CGM报告分析，实现了以下设计元素：

### 视觉设计
- 蓝色主题色系 (#2196F3)
- 渐变色卡片设计
- 专业医疗报告布局

### 图表设计
- AGP百分位数带状图（参考GPlus Page 1）
- 每日血糖小图布局（参考GPlus Page 1下半部分）
- TIR分布条（参考GPlus统计表格）

### 数据展示
- 核心指标优先级排序
- 目标范围清晰标注
- 百分位数精确计算

## 💡 使用场景

### 1. 医疗机构
- 门诊随访报告
- 住院患者监测
- 手术围术期血糖管理

### 2. 健康管理中心
- 体检后续跟踪
- 慢病管理项目
- 个性化健康指导

### 3. 科研项目
- 临床试验数据分析
- 血糖模式研究
- 干预效果评估

## 🔧 高级功能

### 自定义用药信息

```python
medication_data = {
    "medications": [
        {
            "name": "二甲双胍",
            "dosage": "500mg",
            "frequency": "bid",
            "start_date": "2025-09-01"
        }
    ]
}

generate_enhanced_report(
    filepath="data.csv",
    patient_id="P001",
    medication_data=medication_data
)
```

### 导出为PDF

1. **浏览器打印法**（推荐）
   - 在浏览器中打开生成的HTML
   - 按 `Cmd+P` (Mac) 或 `Ctrl+P` (Windows)
   - 选择"另存为PDF"
   - 调整边距和缩放

2. **命令行转换法**
   ```bash
   # 使用wkhtmltopdf
   wkhtmltopdf CGM_Report.html CGM_Report.pdf

   # 或使用Chrome headless
   chrome --headless --print-to-pdf=CGM_Report.pdf CGM_Report.html
   ```

## 📐 技术架构

### 核心技术栈
- **Python**: pandas, numpy (数据处理)
- **JavaScript**: Chart.js 4.4.0 (图表渲染)
- **CSS3**: Grid Layout, Flexbox (响应式布局)
- **HTML5**: 语义化标签

### 关键算法

#### AGP百分位数计算
```python
# 每15分钟时间段，计算各百分位数
for t in np.arange(0, 24, 0.25):
    values = get_values_around_time(t)
    p5 = np.percentile(values, 5)
    p25 = np.percentile(values, 25)
    p50 = np.percentile(values, 50)  # 中位数
    p75 = np.percentile(values, 75)
    p95 = np.percentile(values, 95)
```

#### 每日指标计算
- **TIR**: `count(3.9 ≤ glucose ≤ 10.0) / total * 100`
- **CV**: `(std / mean) * 100`
- **GMI**: `3.31 + (0.02392 * mean_glucose_mg/dL)`

## 🐛 故障排除

### 问题1: Chart.js加载失败
**现象**: 图表不显示
**解决**: 检查网络连接，CDN可访问性

### 问题2: 中文字体显示异常
**现象**: 中文显示为方块
**解决**: 确保系统安装"PingFang SC"或"Microsoft YaHei"字体

### 问题3: PDF打印布局异常
**现象**: 图表被截断
**解决**:
- 调整浏览器缩放至100%
- 使用"适应页面"选项
- 调整页边距为"最小"

## 📝 版本历史

### v2.0 (2025-10-09)
- ✅ 新增AGP百分位数可视化
- ✅ 新增14天每日血糖曲线小图
- ✅ 新增TIR/TAR/TBR堆叠条形图
- ✅ 采用GPlus专业报告样式
- ✅ HTML报告可打印为PDF

### v1.0 (2025-09-14)
- ✅ JSON格式报告输出
- ✅ 基础血糖指标计算
- ✅ 分时段血糖分析

## 🔗 相关文件

- `Agent_ZS_HMC_Report_Generator.py` - 原版报告生成器
- `Agent_ZS_HMC_Report_Generator_Enhanced.py` - 增强版（本文档）
- `郁君君-20250805.pdf` - GPlus参考报告样本

## 📧 技术支持

遇到问题或有改进建议，请查看项目文档或联系开发团队。

---

**报告生成器版本**: v2.0 Enhanced
**最后更新**: 2025-10-09
**基于**: GPlus CGM Report Template Analysis
