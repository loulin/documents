# AGPAI Agent V2.0 - 简化使用指南

## 🎯 最简单的使用方式

### 快速开始

```bash
# 进入AGPAI目录
cd /Users/williamsun/Documents/gplus/docs/AGPAI

# 分析单个文件
python3 simple_run.py "/path/to/your/cgm_file.txt"
```

### 示例

```bash
# 使用完整路径
python3 simple_run.py "/Users/williamsun/Library/CloudStorage/OneDrive-Personal/AA唐宝图 Pro/AA数据业务/质肽生物/ZT002-揭盲/ZT002-Id_IIa-CGM导出数据_txt_20240730/Placebo-V11/R002 v11.txt"

# 使用相对路径（如果文件在当前目录）
python3 simple_run.py "R002 v11.txt"
```

## 📊 输出内容

分析完成后会生成：
- **控制台输出**：完整的分析报告
- **Markdown文件**：`患者ID_分析报告.md`

## 📋 支持的数据格式

- `.txt` 文本文件
- `.csv` 表格文件
- 血糖单位：mmol/L
- 时间间隔：5-15分钟
- 最少数据：24小时（建议48-72小时）

## ❓ 常见问题

### 文件不存在
```bash
❌ 错误: 文件不存在
```
**解决**：检查文件路径是否正确，使用引号包围包含空格的路径

### 数据格式错误
```bash
❌ 分析失败: [具体错误信息]
```
**解决**：检查文件格式，确保包含时间戳和血糖值列

## 🚀 其他运行方式

### 1. 批量分析
```bash
python3 batch_analysis.py batch "/path/to/data/folder"
```

### 2. 原始AGPAI脚本
```bash
python3 run_agpai.py "/path/to/file.txt"
```

### 3. 直接使用核心模块
```python
from AGPAI_Agent_V2 import AGPAI_Agent_V2
agent = AGPAI_Agent_V2()
report = agent.generate_comprehensive_report(
    patient_id='your_patient_id',
    cgm_file_path='/path/to/file.txt',
    include_historical=True
)
```

## 💡 建议

- **新手使用**: `simple_run.py` - 最简单可靠
- **批量处理**: `batch_analysis.py` - 处理多个文件
- **开发集成**: 直接调用 `AGPAI_Agent_V2` 类

---

**注意**: GUI版本存在兼容性问题，推荐使用命令行版本以获得最佳体验。