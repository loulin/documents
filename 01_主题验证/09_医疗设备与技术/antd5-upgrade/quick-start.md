# 快速开始指南

## 环境准备

### 1. 升级工作环境
升级工作环境已经创建完成：
- **工作目录**: `/data/workspace/gplus-antd5-upgrade`
- **分支**: `upgrade/antd5-pro-components`
- **基于**: `develop` 分支

### 2. 验证环境
```bash
# 查看worktree状态
git worktree list

# 查看当前分支
git branch -v
```

## 下一步工作

### 阶段一任务清单

#### 1.1 依赖分析 (1天)
- [ ] 分析 `client/package.json` 中的antd相关依赖
- [ ] 扫描代码中的Pro Components使用情况
- [ ] 检查第三方依赖的兼容性
- [ ] 记录当前的依赖版本清单

#### 1.2 代码扫描 (1天)  
- [ ] 扫描所有文件中的 `visible` 属性使用
- [ ] 找出所有 `dropdownClassName` 的使用
- [ ] 统计Pro Components的导入语句
- [ ] 分析自定义样式和Less变量

#### 1.3 基线测试 (1天)
- [ ] 运行现有测试套件并记录结果
- [ ] 截取关键页面的样式截图
- [ ] 测量首屏加载性能
- [ ] 记录打包体积

### 具体执行步骤

#### 步骤1: 切换到升级环境
由于安全限制，需要手动切换到升级工作目录：
```bash
# 在新的终端窗口中
cd /data/workspace/gplus-antd5-upgrade
```

#### 步骤2: 安装依赖并测试
```bash
cd client
npm install
npm start
```

#### 步骤3: 运行基线测试
```bash
npm test
npm run build
npm run lint
```

#### 步骤4: 依赖分析
```bash
# 查看当前依赖
npm list | grep -E "(antd|@ant-design)"

# 检查过时的依赖
npm outdated
```

### 重要提醒

1. **工作目录隔离**: 升级工作在独立的worktree中进行，不影响主开发环境
2. **分支管理**: 所有升级相关的提交都在 `upgrade/antd5-pro-components` 分支中
3. **测试优先**: 每个阶段都要先运行测试，确保功能正常
4. **文档更新**: 及时更新升级过程中遇到的问题和解决方案

### 常用命令

```bash
# 查看升级相关文档
ls docs/antd5-upgrade/

# 检查代码中的antd使用
grep -r "from 'antd'" client/src/
grep -r "@ant-design/pro-" client/src/

# 查看构建配置
cat client/config/config.ts

# 运行测试
cd client && npm test
```

### 问题反馈

如果在升级过程中遇到问题，请：
1. 查看相关技术文档
2. 记录具体的错误信息
3. 更新文档中的问题解决方案
4. 保持工作进度的记录

## 预期成果

完成阶段一后，应该获得：
- [ ] 完整的依赖分析报告
- [ ] 代码变更范围评估
- [ ] 测试基线数据
- [ ] 详细的升级计划调整

这些信息将为后续的实际升级工作提供重要依据。