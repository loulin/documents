# Ant Design v5 升级项目总览

## 项目概述

本项目旨在将GPlus医疗平台的客户端从Ant Design v4升级到v5，同时将Pro Components从多个独立包迁移到统一的总包管理。

## 升级环境

### 工作分支
- **基础分支**: `develop`
- **升级分支**: `upgrade/antd5-pro-components`  
- **工作目录**: `../gplus-antd5-upgrade`

### 版本目标
- **Ant Design**: 4.24.16 → 5.25.4
- **Pro Components**: 独立包 → @ant-design/pro-components v2.8.9
- **构建工具**: 移除babel-plugin-import，使用原生CSS-in-JS

## 文档结构

### 1. 需求文档 (`requirements.md`)
- 详细的升级需求和目标
- 业务功能兼容性要求
- 性能和质量标准
- 风险评估和成功指标

### 2. 实施计划 (`implementation-plan.md`)
- 5个阶段的详细实施计划
- 关键里程碑和时间节点
- 风险控制措施
- 质量保证流程

### 3. 技术规范 (`technical-specification.md`)
- 详细的技术迁移指南
- API变更映射表
- 配置更新规范
- 代码检查清单

## 关键升级点

### 架构变更
1. **样式系统**: Less → CSS-in-JS + Token系统
2. **包管理**: 多包 → @ant-design/pro-components 总包
3. **日期库**: Moment.js → Day.js
4. **构建优化**: 移除babel-plugin-import

### API变更
1. **显示控制**: `visible` → `open`
2. **弹出框样式**: `dropdownClassName` → `popupClassName`
3. **表格组件**: `filterDropdownVisible` → `filterDropdownOpen`

### 配置更新
1. **UmiJS配置**: 适配antd v5的ConfigProvider
2. **主题配置**: 使用新的token系统
3. **国际化**: 保持现有多语言支持

## 开发环境

### 环境要求
- Node.js >= 16.0.0
- npm >= 7.0.0
- Git >= 2.25.0

### 开发流程
1. 在 `../gplus-antd5-upgrade` 目录下进行开发
2. 每个阶段完成后进行完整测试
3. 关键变更需要进行代码审查
4. 保持与原分支的同步

## 质量保证

### 测试策略
- **单元测试**: 确保代码逻辑正确
- **集成测试**: 验证组件协作
- **E2E测试**: 保证用户流程完整
- **性能测试**: 监控关键指标

### 验收标准
- 所有现有功能正常工作
- 性能指标在可接受范围内
- 所有自动化测试通过
- 代码质量检查通过

## 风险控制

### 主要风险
1. **Pro Layout v7**: 重大API变更
2. **CSS-in-JS**: 样式系统重构
3. **第三方兼容**: 依赖包兼容性

### 应对措施
- 分阶段渐进升级
- 详细的回滚方案
- 完整的测试覆盖
- 持续的进度监控

## 项目里程碑

### 第一阶段 (3天)
- [x] 文档准备完成
- [x] 升级环境创建
- [ ] 依赖分析完成
- [ ] 测试基线建立

### 第二阶段 (7天)
- [ ] 依赖包升级
- [ ] 基础配置更新
- [ ] 项目构建成功

### 第三阶段 (14天)
- [ ] API迁移完成
- [ ] 样式系统迁移
- [ ] 核心功能测试通过

### 第四阶段 (21天)
- [ ] 完整功能测试
- [ ] 性能优化
- [ ] 兼容性验证

### 第五阶段 (23天)
- [ ] 最终测试完成
- [ ] 文档更新
- [ ] 部署准备就绪

## 后续计划

### 部署策略
1. 在测试环境充分验证
2. 灰度发布到生产环境
3. 监控系统稳定性
4. 收集用户反馈

### 技术债务处理
1. 清理不需要的依赖
2. 优化代码结构
3. 完善测试覆盖
4. 更新开发文档

## 联系方式

如有任何问题或建议，请通过以下方式联系：
- 项目仓库: `/data/workspace/gplus`
- 升级分支: `upgrade/antd5-pro-components`
- 工作目录: `../gplus-antd5-upgrade`

## 快速开始

```bash
# 切换到升级工作目录
cd ../gplus-antd5-upgrade

# 安装依赖
npm install

# 开始开发
npm start

# 运行测试
npm test

# 构建项目
npm run build
```

---

*本文档将随着升级进度持续更新，确保信息的准确性和完整性。*