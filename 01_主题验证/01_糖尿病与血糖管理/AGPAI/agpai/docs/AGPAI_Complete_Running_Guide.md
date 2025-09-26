# AGPAI Agent V2.0 完整运行指南

## 🎯 运行方式概览

AGPAI Agent V2.0 提供多种可靠的命令行运行方式：

1. **简单运行** - 单文件分析（推荐）
2. **批量运行** - 多文件批处理
3. **Python脚本** - 集成到其他系统

---

## 📋 环境准备

### 1. Python环境要求
```bash
Python >= 3.8
依赖包: pandas, numpy, datetime
```

### 2. 安装依赖
```bash
# 进入AGPAI目录
cd /Users/williamsun/Documents/gplus/docs/AGPAI

# 安装Python依赖
pip3 install pandas numpy python-dateutil

# 验证安装
python3 -c "import pandas, numpy; print('✅ 依赖安装成功')"
```

### 3. 文件结构检查
```
docs/AGPAI/
├── AGPAI_Agent_V2.py          # 主程序
├── run_agpai.py               # 简易运行脚本
├── batch_analysis.py          # 批量分析脚本
├── requirements.txt           # 依赖文件
├── agpai_patient_data/        # 患者数据存储目录
└── reports/                   # 分析报告输出目录
```

---

## 🚀 运行方法

### 方法1: 最简单运行（强烈推荐）

```bash
# 进入AGPAI目录
cd /Users/williamsun/Documents/gplus/docs/AGPAI

# 使用简化工具分析
python3 simple_run.py "/Users/williamsun/Library/CloudStorage/OneDrive-Personal/AA唐宝图 Pro/AA数据业务/质肽生物/ZT002-揭盲/ZT002-Id_IIa-CGM导出数据_txt_20240730/Placebo-V11/R002 v11.txt"

# 或使用原始工具
python3 run_agpai.py "/Users/williamsun/Library/CloudStorage/OneDrive-Personal/AA唐宝图 Pro/AA数据业务/质肽生物/ZT002-揭盲/ZT002-Id_IIa-CGM导出数据_txt_20240730/Placebo-V11/R002 v11.txt"
```

**输出示例**:
```
🩺 AGPAI Agent V2.0 - 智能血糖分析系统
==================================================
📁 分析文件: R002 v11.txt
👤 患者ID: R002 v11
⏳ 正在分析...
--------------------------------------------------

## 患者R002 v11专业血糖分析报告

### 📊 血糖控制概况
**患者表型**: 稳定性高血糖型
...
💾 报告已保存至: R002 v11_AGPAI_Report.md
```

### 方法2: 标准运行

```bash
# 使用标准run_agpai.py脚本
python3 run_agpai.py "/path/to/cgm_file.txt"
```

### 方法3: 批量运行

```bash
# 批量分析整个文件夹
python3 batch_analysis.py batch "/Users/williamsun/Library/CloudStorage/OneDrive-Personal/AA唐宝图 Pro/AA数据业务/质肽生物/ZT002-揭盲/ZT002-Id_IIa-CGM导出数据_txt_20240730/Placebo-V11/"

# 指定输出目录
python3 batch_analysis.py batch "/path/to/data/folder" "./my_reports"
```

**输出示例**:
```
🔍 发现 3 个数据文件

📊 正在分析 1/3: R002 v11.txt
✅ 完成: R002 v11

📊 正在分析 2/3: R016 v11.txt  
✅ 完成: R016 v11

📊 正在分析 3/3: R022 v11.txt
✅ 完成: R022 v11

📋 批量分析完成:
   ✅ 成功: 3 个
   ❌ 失败: 0 个
   📂 输出目录: ./reports
   📄 汇总文件: ./reports/batch_analysis_summary.json
```

### 方法4: Python脚本集成

```python
from AGPAI_Agent_V2 import AGPAI_Agent_V2

# 初始化Agent
agent = AGPAI_Agent_V2()

# 分析单个患者
report = agent.generate_comprehensive_report(
    patient_id='R002_v11',
    cgm_file_path='/path/to/R002 v11.txt',
    include_historical=True
)

print(report)
```

---

## 📊 数据格式要求

### 支持的文件格式
- **.txt** - 纯文本格式
- **.csv** - 逗号分隔格式

### 数据格式示例（质肽生物格式）
```
LYPI
# R002
ID	时间	记录类型	葡萄糖历史记录（mmol/L）
122701	2024/06/10 08:35	0	7.4
122702	2024/06/10 08:50	0	7.7
122703	2024/06/10 09:05	0	8.3
...
```

### 数据质量要求
- 最少24小时数据
- 建议48-72小时数据
- 数据间隔: 5-15分钟
- 血糖单位: mmol/L

---

## 📄 输出文件说明

### 1. Markdown报告文件
```
患者ID_AGPAI_Report.md
包含完整的分析报告，可以用任何文本编辑器打开
```

### 2. JSON数据文件（批量模式）
```json
{
  "patient_id": "R002 v11",
  "status": "success", 
  "report_file": "./reports/R002 v11_report.md",
  "timestamp": "2025-08-14T12:30:45"
}
```

### 3. 汇总文件（批量模式）
```
batch_analysis_summary.json
包含所有患者的分析结果汇总
```

---

## 🔧 常见问题解决

### 问题1: ModuleNotFoundError
```bash
# 错误信息
ModuleNotFoundError: No module named 'AGPAI_Agent_V2'

# 解决方法
cd /Users/williamsun/Documents/gplus/docs/AGPAI
python3 run_agpai.py "your_file.txt"
```

### 问题2: 文件路径错误
```bash
# 错误信息
❌ 文件不存在: R002 v11.txt

# 解决方法：使用完整路径
python3 run_agpai.py "/完整/文件/路径/R002 v11.txt"
```

### 问题3: 数据格式错误
```bash
# 检查数据格式
head -5 "your_file.txt"

# 确保包含：
# - 时间戳列
# - 血糖值列  
# - 正确的分隔符
```

### 问题4: 权限错误
```bash
# 如果遇到权限问题
chmod +x run_agpai.py batch_analysis.py
```

---

## 🎯 快速测试

### 测试单文件分析
```bash
cd /Users/williamsun/Documents/gplus/docs/AGPAI

# 使用提供的测试文件
python3 run_agpai.py "/Users/williamsun/Library/CloudStorage/OneDrive-Personal/AA唐宝图 Pro/AA数据业务/质肽生物/ZT002-揭盲/ZT002-Id_IIa-CGM导出数据_txt_20240730/Placebo-V11/R002 v11.txt"

# 检查输出文件
ls -la *_AGPAI_Report.md
```

### 测试批量分析
```bash
# 创建测试目录并复制几个文件
mkdir test_data
cp "/Users/williamsun/Library/CloudStorage/OneDrive-Personal/AA唐宝图 Pro/AA数据业务/质肽生物/ZT002-揭盲/ZT002-Id_IIa-CGM导出数据_txt_20240730/Placebo-V11/R"*.txt test_data/

# 批量分析
python3 batch_analysis.py batch test_data

# 检查结果
ls -la reports/
```

---

## 🔄 集成到其他系统

### 作为Python模块使用
```python
# 导入AGPAI
sys.path.append('/Users/williamsun/Documents/gplus/docs/AGPAI')
from AGPAI_Agent_V2 import AGPAI_Agent_V2

# 在你的代码中使用
agent = AGPAI_Agent_V2()
result = agent.generate_comprehensive_report(...)
```

### API服务集成
```python
# 可以封装为Flask API
from flask import Flask, request, jsonify
from AGPAI_Agent_V2 import AGPAI_Agent_V2

app = Flask(__name__)
agent = AGPAI_Agent_V2()

@app.route('/analyze', methods=['POST'])
def analyze_cgm():
    # 接收CGM数据并分析
    # 返回分析结果
    pass
```

---

## 🎯 性能优化建议

### 大文件处理
- 单个文件 > 10MB：分段处理
- 批量文件 > 100个：并行处理
- 内存不足：调整分析参数

### 加速分析
```python
# 跳过历史比较（加速分析）
report = agent.generate_comprehensive_report(
    patient_id='patient_id',
    cgm_file_path='file_path',
    include_historical=False  # 设为False加速
)
```

---

**🎯 总结**: AGPAI Agent V2.0 提供了可靠的命令行运行方式，满足不同用户的需求。强烈推荐使用 `simple_run.py` 开始，它是最简单可靠的选择。熟悉后可以使用批量处理和系统集成功能。