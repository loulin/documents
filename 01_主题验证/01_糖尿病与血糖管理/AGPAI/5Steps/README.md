# 五步法Plus - 智能学习CGM分析系统

> AI生成建议 + 医生智慧修改 = 持续优化的临床决策支持

## 📋 系统概述

五步法Plus是基于原五步法CGM分析算法的智能升级版本，在保持原有医学逻辑和计算精度的基础上，新增了智能学习、富文本编辑和个性化适配功能。

### 🏗️ 系统架构

```
五步法Plus 系统架构
├── 📊 核心分析引擎 (复用原有)
│   └── run_report_layered_assessment.py  # 原五步法算法
├── 🧠 智能学习层 (新增)
│   ├── learning_analyzer.py              # 基础学习分析
│   └── enhanced_learning_engine.py       # 增强学习引擎
├── 🌐 Web服务层 (新增)
│   ├── five_steps_plus_server.py         # Flask API服务
│   └── five_steps_plus_interactive.html  # 富文本编辑界面
└── 🛠️ 工具和测试 (新增)
    ├── start_five_steps_plus.py          # 一键启动脚本
    ├── test_five_steps_plus.py           # 完整测试套件
    └── demo_learning_test.py             # 学习机制演示
```

## 🚀 快速开始

### 方法一：一键启动（推荐）
```bash
# 1. 进入项目目录
cd /path/to/AGPAI/5Steps

# 2. 一键启动（自动检查依赖、启动服务、打开浏览器）
python start_five_steps_plus.py

# 3. 浏览器会自动打开 http://localhost:5001
```

### 方法二：手动启动
```bash
# 1. 安装依赖
pip install flask flask-cors pandas numpy openpyxl requests

# 2. 启动服务器
python five_steps_plus_server.py

# 3. 手动打开浏览器
# 访问：http://localhost:5001
```

### 方法三：仅使用原五步法（命令行）
```bash
# 分析单个文件
python run_report_layered_assessment.py path/to/cgm_data.xlsx

# 输出：控制台显示完整的五步法分析报告
```

## 📖 使用指南

### 🌐 Web界面使用

1. **启动系统**：运行 `python start_five_steps_plus.py`
2. **访问界面**：浏览器打开 http://localhost:5001
3. **上传数据**：点击"选择文件"上传CGM数据（支持.xlsx/.csv）
4. **快速体验**：或点击"使用示例数据"立即体验
5. **AI分析**：点击"开始AI分析"生成初始报告
6. **编辑报告**：在右侧富文本编辑器中修改AI建议
7. **保存学习**：点击"保存最终报告"，系统记录修改用于学习

### 💡 界面功能说明

#### 左侧面板 - 数据分析区
- **📊 文件上传**：支持Excel(.xlsx)和CSV(.csv)格式的CGM数据
- **👤 患者信息**：显示患者ID、文件名、分析时间等基本信息
- **⏳ 分析状态**：实时显示当前分析进度和系统状态
- **📝 修改记录**：追踪和显示所有编辑历史和学习记录

#### 右侧面板 - 报告编辑区
- **✏️ 富文本编辑器**：专业的报告编辑界面，支持格式化
- **📋 格式工具**：粗体、斜体、列表、标题等格式工具
- **👀 实时预览**：点击"预览报告"查看最终效果
- **💾 保存功能**：保存最终报告并记录修改用于系统学习

## 🧠 智能学习功能

### 双层学习架构

#### 🔧 基础学习引擎（立即可用）
- **修改记录分析**：完整记录所有医生修改行为
- **用词替换统计**：识别医生偏好的专业术语
- **修改模式识别**：分析内容结构和临床判断变化
- **医生画像构建**：学习不同医生的编辑习惯

#### 🚀 增强学习引擎（生产级）
- **高级文本分析**：使用difflib进行精确差异检测
- **语义相似度分析**：基于医学术语的智能匹配
- **自适应报告生成**：根据学习模式生成个性化建议
- **学习效果评估**：量化分析系统优化效果

### 学习机制类型

#### 1. 🌐 全局学习（各医生知识综合）
- 提取所有医生的共同修改模式
- 识别医学界普遍认可的表述方式
- 当3个以上医生做相同修改时纳入全局知识库

#### 2. 👨‍⚕️ 个性化学习（每个医生专属）
- **用词偏好**：如张医生喜欢"管理"而非"控制"
- **修改风格**：如李医生倾向于详细建议
- **临床习惯**：根据历史修改建立个人档案

### 学习效果示例
```
原始AI建议：血糖控制需要调整，建议强化治疗
张医生个性化：血糖管理需要优化，建议强化治疗
✅ 成功应用：控制→管理，调整→优化
```

## 🔧 高级功能

### API接口

```bash
# 获取学习统计
curl http://localhost:5001/api/stats

# 生成个性化报告
curl -X POST http://localhost:5001/api/generate_adaptive_report \
  -H "Content-Type: application/json" \
  -d '{"base_report":"血糖控制需要调整","doctor_id":"张医生"}'

# 保存反馈数据
curl -X POST http://localhost:5001/api/save_feedback \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"demo","doctor_id":"test","original_report":"...","modified_report":"..."}'

# 导出学习模型
curl http://localhost:5001/api/export_learning_model
```

### 命令行工具

```bash
# 基础学习分析
python learning_analyzer.py

# 增强学习分析和模型导出
python enhanced_learning_engine.py

# 学习机制演示
python demo_learning_test.py

# 完整系统测试
python test_five_steps_plus.py
```

## 📊 系统测试

### 快速检查系统状态
```bash
# 检查依赖和文件完整性
python start_five_steps_plus.py --check-only

# 运行完整测试套件
python test_five_steps_plus.py
```

### 测试项目包括
- ✅ 文件完整性检查
- ✅ 依赖包验证
- ✅ 基础学习引擎测试
- ✅ 增强学习引擎测试
- ✅ 五步法算法验证
- ✅ Web服务器启动测试
- ✅ HTML界面加载测试
- ✅ API端点功能测试
- ✅ 反馈系统测试

## 📁 文件说明

### 核心文件
- `run_report_layered_assessment.py` - 原五步法分析核心算法
- `five_steps_plus_server.py` - Flask Web服务器
- `five_steps_plus_interactive.html` - 富文本编辑界面
- `enhanced_learning_engine.py` - 增强学习引擎
- `learning_analyzer.py` - 基础学习分析器

### 配置和数据
- `5Steps.json` - 五步法算法配置文件
- `feedback_database.json` - 学习反馈数据库
- `learned_model.json` - 导出的学习模型

### 工具脚本
- `start_five_steps_plus.py` - 一键启动脚本
- `test_five_steps_plus.py` - 完整测试套件
- `demo_learning_test.py` - 学习机制演示

## 🎯 使用场景

### 场景1：日常CGM分析
1. 启动系统：`python start_five_steps_plus.py`
2. 上传患者CGM数据文件
3. 获得AI生成的五步法分析报告
4. 根据临床经验调整建议内容
5. 保存最终报告，系统自动学习

### 场景2：批量数据处理
```bash
# 使用原五步法命令行批量处理
for file in *.xlsx; do
    python run_report_layered_assessment.py "$file" > "report_${file%.xlsx}.txt"
done
```

### 场景3：学习效果分析
```bash
# 查看学习统计
python learning_analyzer.py

# 生成学习报告
python enhanced_learning_engine.py

# 演示学习机制
python demo_learning_test.py
```

### 场景4：个性化报告生成
- 系统自动识别医生身份
- 应用该医生的历史偏好
- 生成符合个人习惯的报告建议

## 🚨 故障排除

### 常见问题

**Q: 启动时提示端口被占用**
```bash
# A: 检查5000端口（macOS可能被AirPlay占用）
# 解决：系统偏好设置 -> 通用 -> 隔空投送与接力 -> 关闭接收器
# 或者修改端口：编辑five_steps_plus_server.py中的端口号
```

**Q: 缺少依赖包**
```bash
# A: 安装完整依赖
pip install flask flask-cors pandas numpy openpyxl requests
```

**Q: 学习功能不工作**
```bash
# A: 检查学习引擎状态
curl http://localhost:5001/api/stats
# 确保learning_engine_status为"active"
```

**Q: 无法加载CGM数据**
```bash
# A: 确保数据格式正确
# 支持格式：Excel (.xlsx) 或 CSV (.csv)
# 必需列：时间/Time/timestamp, 值/glucose/血糖值
# 单位：mmol/L（系统自动检测mg/dL并转换）
```

## 📈 版本信息

### 当前版本：v1.0
- ✅ 基础五步法分析算法
- ✅ 富文本Web界面
- ✅ 双层智能学习系统
- ✅ 个性化报告生成
- ✅ 完整API服务
- ✅ 学习效果评估

### 计划功能：v1.1
- 🔄 实时协作编辑
- 📊 可视化学习报告
- 🔗 HIS系统集成
- 🌐 多语言支持

## 💡 最佳实践

### 医生使用建议
1. **初期使用**：多修改AI建议，帮助系统快速学习您的偏好
2. **术语一致性**：保持用词习惯一致，系统学习效果更好
3. **定期查看**：关注学习统计，了解系统改进情况
4. **反馈质量**：详细的修改比简单的修改学习效果更好

### 系统管理建议
1. **数据备份**：定期备份feedback_database.json学习数据
2. **性能监控**：关注学习引擎状态和改进率指标
3. **模型导出**：定期导出学习模型用于分析和备份
4. **版本升级**：关注系统更新，及时应用新功能

## 📞 技术支持

### 系统要求
- **Python**: 3.7+ 
- **内存**: 建议4GB+
- **浏览器**: Chrome/Firefox/Edge现代浏览器
- **网络**: 本地运行无需网络连接

### 获取帮助
- 查看详细日志：服务器控制台输出
- 检查系统状态：`python test_five_steps_plus.py`
- 学习数据分析：`python learning_analyzer.py`

---

**五步法Plus** - 让AI更懂临床，让临床更智能！ 🚀

> 基于医生智慧的持续学习，为每位医生提供个性化的CGM分析支持