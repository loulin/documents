# 营养管理系统 v3.0 - 完整版

## 🌟 最新功能亮点

### 🖥️ Web可视化界面 (NEW!)
- **Streamlit交互界面** - `nutrition_interface.py`
- 一键启动Web应用，支持表单填写和实时分析
- 完整的患者数据录入和营养报告生成
- 访问地址: http://localhost:8501

### 📅 一周菜谱智能轮换 (NEW!)
- **7天不重复营养菜谱** - 55道高质量菜品
- 智能表格化展示，横轴为餐次，纵轴为星期
- 根据患者偏好自动选择菜系(川菜/粤菜/清淡)
- 每日自动轮换，确保饮食多样性

### 🧬 CGM血糖监测集成 (NEW!)
- 动态血糖监测数据分析
- 个性化血糖反应模式识别
- CGM驱动的菜谱智能优化推荐

## 📁 目录结构

### 🎯 Core_Systems/ - 核心系统（当前版本）
**推荐使用的最新版本系统**

- `integrated_nutrition_system_v2.py` - **主系统** ⭐
  - 整合版营养管理系统v2.0
  - 集成患者分层、疾病支持、菜谱推荐、GI数据库、营养雷达图
  - 支持95种食物，111道菜谱，35种疾病
  - **这是推荐使用的主要系统**

- `weekly_menu_manager.py` - **一周菜谱管理器** 🗓️
  - 7天不重复菜谱轮换系统
  - 55道高质量营养菜品
  - 支持3种菜系风格
  - 智能日期对应推荐

- `cgm_nutrition_integration.py` - **CGM集成系统** 🩺
  - 动态血糖监测数据处理
  - 餐后血糖反应分析
  - 个性化血糖敏感性评估
  - CGM驱动的菜谱优化

- `gi_database_integration_v2.py` - **专用GI系统** 🩺
  - 血糖指数数据库专用系统
  - 95种食物完整GI/GL数据
  - 糖尿病患者餐食规划功能
  - 专业的血糖管理工具

### 🖥️ Web界面系统
**可视化交互界面**

- `nutrition_interface.py` - **主界面** 🌐
  - Streamlit Web应用
  - 完整的患者信息录入表单
  - 实时营养分析和报告生成
  - 一周菜谱表格化展示
  - CGM数据管理和分析

- `run_interface.sh` / `run_interface.bat` - **启动脚本** 🚀
  - 一键启动Web界面
  - 自动环境检测和依赖安装
  - 跨平台支持(Mac/Windows)

### 📚 Documentation/ - 系统文档
**完整的使用指南和技术文档**

- `README.md` - 系统使用说明
- `GI数据库报告.md` - GI数据库详细报告（95种食物）
- `GI数据库更新摘要.md` - 数据库更新对比分析
- `系统使用指南_机构分类建议.md` - 不同机构的使用指南
- `系统优化建议_全面分析.md` - 系统优化建议和发展规划
- `系统集成验证报告.md` - 系统集成测试报告
- `脚本更新完成报告.md` - 最新更新完成报告
- `hybrid_system_design.md` - 混合系统设计文档
- `system_update_summary.md` - 系统更新摘要

### 📊 Reports/ - 示例报告
**真实患者案例的营养分析报告**

- `整合系统示例报告_王先生.md` - 整合系统示例
- `详细营养建议报告_王先生.md` - 详细营养报告（markdown）
- `详细营养建议报告_王先生.pdf` - 详细营养报告（PDF）
- `膳食营养分析报告.md` - 膳食营养分析示例

### 📈 Charts/ - 营养图表
**系统生成的营养可视化图表**

- `健康午餐营养雷达图.png` - 餐食营养雷达图
- `蛋白质食物对比雷达图.png` - 食物对比分析图
- `鸡胸肉营养雷达图.png` - 单食物营养分析图

### 🗂️ Legacy_Versions/ - 历史版本
**开发过程中的历史版本，仅供参考**

包含系统开发过程中的各个版本和组件：
- 增强版中式食物推荐系统
- 患者分层系统各版本
- 疾病支持系统
- 菜谱数据库各版本
- PDF生成工具
- 营养雷达图组件

## 🚀 快速开始

### 1. Web界面使用 (推荐方式)

**最简单的使用方式 - 一键启动Web界面**

```bash
# macOS/Linux
./run_interface.sh

# Windows
run_interface.bat

# 或手动启动
streamlit run nutrition_interface.py
```

访问 http://localhost:8501 即可使用完整的Web界面：
- ✅ 患者信息表单填写
- ✅ 实时营养分析报告
- ✅ 一周菜谱表格展示
- ✅ CGM血糖数据管理
- ✅ 营养雷达图可视化

### 2. 编程接口使用

**临床营养管理**：使用 `Core_Systems/integrated_nutrition_system_v2.py`
```python
from Core_Systems.integrated_nutrition_system_v2 import *

# 初始化系统
system = IntegratedNutritionSystemV2(SystemVersion.CLINICAL)

# 创建患者档案
patient = PatientProfile(
    name="患者姓名",
    age=45,
    gender="女",
    height=160,
    weight=65,
    diagnosed_diseases=["糖尿病", "高血压"]
)

# 生成综合营养报告
report = system.generate_comprehensive_report_v2(patient)
```

**一周菜谱管理**：使用 `Core_Systems/weekly_menu_manager.py`
```python
from Core_Systems.weekly_menu_manager import WeeklyMenuManager

# 初始化一周菜谱管理器
weekly_manager = WeeklyMenuManager()

# 获取今日推荐
today_menu = weekly_manager.get_today_menu("清淡")
print(f"今日推荐: {today_menu}")

# 获取完整一周菜谱
weekly_menu = weekly_manager.get_weekly_menu("川菜")
```

**糖尿病血糖管理**：使用 `Core_Systems/gi_database_integration_v2.py`
```python
from Core_Systems.gi_database_integration_v2 import *

# 初始化GI系统
gi_system = GIDatabaseSystemV2()

# 查询低GI食物
low_gi_foods = gi_system.get_low_gi_foods()
print(f"可选择的低GI食物: {len(low_gi_foods)}种")
```

### 2. 系统版本选择

| 机构类型 | 推荐版本 | 特点 |
|----------|----------|------|
| **三甲医院** | 临床版 | 完整功能，支持科研 |
| **综合医院** | 专业版 | 核心功能，适合临床 |
| **社区医院** | 基础版 | 简化操作，易于使用 |

### 3. 主要功能概览

- ✅ **Web可视化界面**: Streamlit交互式应用
- ✅ **一周菜谱智能轮换**: 55道菜品7天不重复
- ✅ **CGM血糖监测集成**: 动态血糖数据分析
- ✅ **患者风险分层**: 35层多维度评估
- ✅ **疾病营养支持**: 35种疾病个性化方案
- ✅ **中式菜谱推荐**: 111道传统菜肴
- ✅ **血糖指数管理**: 95种食物GI/GL数据
- ✅ **营养可视化**: 多维度雷达图分析
- ✅ **专业报告生成**: PDF/Markdown格式

## 📖 详细文档

### 核心文档（必读）
1. `Documentation/GI数据库报告.md` - 完整的GI食物数据库
2. `Documentation/系统使用指南_机构分类建议.md` - 机构使用指南
3. `Documentation/脚本更新完成报告.md` - 最新功能更新

### 技术文档
1. `Documentation/系统集成验证报告.md` - 系统技术验证
2. `Documentation/系统优化建议_全面分析.md` - 未来发展规划

## 🔧 技术支持

### 依赖环境
- Python 3.8+
- streamlit (Web界面)
- pandas (数据处理)
- plotly (交互式图表)
- matplotlib (营养图表)
- numpy (数值计算)

### 安装方式
```bash
# 安装所有依赖
pip install -r requirements.txt

# 或单独安装核心组件
pip install streamlit pandas plotly matplotlib numpy
```

### 常见问题
1. **中文字体问题**: 系统会自动尝试多种中文字体
2. **数据兼容性**: 所有版本向下兼容
3. **性能优化**: 推荐使用最新的v2.0版本

## 📊 系统统计

### 数据规模
- **一周菜谱**: 55道高质量菜品（7天不重复）
- **总食物数**: 95种（GI数据库）
- **低GI食物**: 84种（88.4%）
- **菜谱数量**: 111道中式菜肴
- **疾病支持**: 35种常见疾病
- **文档数量**: 17个完整文档

### 功能模块
- **Web可视化界面**: Streamlit交互式界面
- **一周菜谱轮换**: 智能日期对应推荐
- **CGM血糖集成**: 动态血糖监测分析
- **患者管理**: 完整的患者档案系统
- **营养分析**: 多维度营养成分分析
- **血糖管理**: 专业的GI/GL计算
- **报告生成**: 自动化专业报告
- **可视化**: 营养雷达图表系统

---

## 🎯 使用建议

1. **💡 推荐方式**: 使用Web界面 `./run_interface.sh` 或 `streamlit run nutrition_interface.py`
2. **👩‍⚕️ 首次使用**: 从 `Core_Systems/integrated_nutrition_system_v2.py` 开始
3. **🩺 糖尿病专用**: 使用 `Core_Systems/gi_database_integration_v2.py`
4. **📅 一周菜谱**: 查看 `Core_Systems/weekly_menu_manager.py`
5. **📊 学习参考**: 查看 `Reports/` 中的示例报告
6. **📖 深入了解**: 阅读 `Documentation/` 中的详细文档

**🎉 欢迎使用营养管理系统v3.0！**

---
*最后更新: 2025年09月22日*
*版本: v3.0 完整版 - 增加Web界面和一周菜谱功能*