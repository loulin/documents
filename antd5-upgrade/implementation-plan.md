# Ant Design v5 & Pro Components 升级实施计划

## 总体策略

### 升级原则
1. **渐进式升级**: 分阶段逐步迁移，确保每个阶段可回滚
2. **兼容性优先**: 保持现有功能完整性
3. **性能导向**: 关注升级后的性能表现
4. **测试驱动**: 每个阶段完成后进行完整测试

### 技术路线
- **基础分支**: develop分支
- **工作分支**: upgrade/antd5-pro-components
- **包管理策略**: 使用@ant-design/pro-components总包
- **样式迁移**: Less → CSS-in-JS + Token系统

## 详细实施计划

### 阶段一：环境准备与研究 (2-3天)

#### 1.1 环境搭建
```bash
# 创建工作环境
git worktree add ../gplus-antd5-upgrade upgrade/antd5-pro-components
cd ../gplus-antd5-upgrade
git checkout -b upgrade/antd5-pro-components develop

# 安装依赖进行基础测试
npm install
npm run start
```

#### 1.2 依赖分析
- [ ] 分析当前package.json中的所有antd相关依赖
- [ ] 确认Pro Components各包的使用模式
- [ ] 检查第三方依赖的antd版本兼容性
- [ ] 评估UmiJS Max对antd v5的支持程度

#### 1.3 代码扫描
- [ ] 扫描所有文件中的antd组件使用情况
- [ ] 统计需要升级的API调用（visible→open等）
- [ ] 分析自定义样式和Less变量的使用
- [ ] 检查第三方组件库的兼容性

#### 1.4 测试基线建立
- [ ] 运行现有测试套件，记录基线结果
- [ ] 截取关键页面样式截图作为对比基准
- [ ] 测量关键页面的性能指标
- [ ] 记录打包体积等技术指标

### 阶段二：核心升级实施 (3-4天)

#### 2.1 依赖包升级
```bash
# 移除旧的Pro Components包
npm uninstall @ant-design/pro-card @ant-design/pro-descriptions @ant-design/pro-field @ant-design/pro-form @ant-design/pro-layout @ant-design/pro-list @ant-design/pro-table

# 安装新版本
npm install @ant-design/pro-components@^2.8.9
npm install antd@^5.25.4

# 移除不需要的工具
npm uninstall babel-plugin-import
```

#### 2.2 UmiJS配置更新
```typescript
// config/config.ts
export default defineConfig({
  antd: {
    // 移除import配置
    configProvider: {
      theme: {
        token: {
          // 迁移主题配置
          colorPrimary: '#1677ff',
          borderRadius: 6,
        }
      }
    }
  },
  // 添加moment到dayjs转换
  moment2dayjs: {
    preset: 'antd',
    plugins: ['duration']
  }
});
```

#### 2.3 导入语句重构
- [ ] 批量替换所有Pro Components的导入语句
- [ ] 更新相关的TypeScript类型导入
- [ ] 检查并修复可能的循环依赖

#### 2.4 初步构建测试
- [ ] 尝试构建项目，解决基础编译错误
- [ ] 修复TypeScript类型错误
- [ ] 确保项目能够成功启动

### 阶段三：代码迁移重点 (5-7天)

#### 3.1 Ant Design v5 API迁移
**高优先级API变更**:
- [ ] Modal: `visible` → `open`
- [ ] Drawer: `visible` → `open`
- [ ] Tooltip: `visible` → `open`
- [ ] Dropdown: `visible` → `open`
- [ ] Select: `dropdownClassName` → `popupClassName`
- [ ] Cascader: `dropdownClassName` → `popupClassName`
- [ ] TimePicker: `dropdownClassName` → `popupClassName`
- [ ] DatePicker: `dropdownClassName` → `popupClassName`

**表格组件特殊处理**:
- [ ] Table: `filterDropdownVisible` → `filterDropdownOpen`
- [ ] 检查所有ProTable的自定义配置

#### 3.2 Pro Layout配置升级
```typescript
// src/app.tsx
import { ProLayout } from '@ant-design/pro-components';

// 更新RunTimeLayoutConfig
export const layout: RunTimeLayoutConfig = ({
  initialState,
  setInitialState,
}) => {
  return {
    // 检查v7版本API变更
    // 更新菜单配置方式
    // 适配新的设置抽屉配置
  };
};
```

#### 3.3 样式系统迁移
- [ ] 移除所有antd的Less文件引用
- [ ] 替换自定义Less变量为CSS-in-JS token
- [ ] 引入antd/dist/reset.css（如需要）
- [ ] 更新自定义主题配置

#### 3.4 日期库迁移
- [ ] 将moment.js替换为dayjs
- [ ] 更新日期格式化相关代码
- [ ] 测试日期选择器功能

### 阶段四：功能测试与修复 (4-6天)

#### 4.1 核心功能测试
**患者管理模块**:
- [ ] 患者列表页面 (ProTable功能)
- [ ] 患者详情页面 (ProDescriptions功能)
- [ ] 患者编辑表单 (ProForm功能)
- [ ] 患者搜索功能

**血糖数据模块**:
- [ ] 血糖数据展示
- [ ] 图表渲染功能
- [ ] 数据导出功能
- [ ] 报告生成功能

**系统管理模块**:
- [ ] 用户管理页面
- [ ] 权限设置功能
- [ ] 组织架构管理
- [ ] 系统设置页面

#### 4.2 样式检查与修复
- [ ] 对比升级前后的页面截图
- [ ] 修复样式不一致的问题
- [ ] 检查响应式布局
- [ ] 验证暗色主题（如有）

#### 4.3 交互功能验证
- [ ] 表单提交功能
- [ ] 模态框和抽屉组件
- [ ] 下拉菜单和弹出框
- [ ] 文件上传功能

#### 4.4 性能测试
- [ ] 首屏加载时间测试
- [ ] 页面渲染性能测试
- [ ] 内存使用情况监控
- [ ] 打包体积对比

### 阶段五：完整测试与优化 (2-3天)

#### 5.1 自动化测试
- [ ] 运行所有单元测试
- [ ] 执行E2E测试套件
- [ ] 进行回归测试
- [ ] 性能基准测试

#### 5.2 兼容性测试
- [ ] 不同浏览器测试
- [ ] 不同屏幕分辨率测试
- [ ] 移动端兼容性测试
- [ ] 第三方组件集成测试

#### 5.3 代码质量检查
- [ ] ESLint检查通过
- [ ] TypeScript类型检查
- [ ] Prettier格式化
- [ ] 依赖安全检查

#### 5.4 文档更新
- [ ] 更新README.md
- [ ] 记录升级过程中的问题和解决方案
- [ ] 准备部署文档
- [ ] 编写回滚指南

## 关键里程碑

### 里程碑1：环境就绪 (第3天)
- 升级环境搭建完成
- 依赖分析完成
- 基线测试完成

### 里程碑2：核心升级 (第7天)
- 依赖包升级完成
- 项目能够正常构建和启动
- 基础功能可访问

### 里程碑3：迁移完成 (第14天)
- 所有API迁移完成
- 样式系统迁移完成
- 核心功能测试通过

### 里程碑4：测试通过 (第21天)
- 所有测试通过
- 性能指标达标
- 代码质量检查通过

## 风险控制措施

### 技术风险
1. **API不兼容**: 准备详细的API映射表，逐一验证
2. **样式问题**: 使用视觉对比工具，确保样式一致性
3. **性能下降**: 建立性能监控，及时优化性能问题

### 项目风险
1. **时间延期**: 设置缓冲时间，准备应急方案
2. **质量问题**: 严格按照测试流程，不跳过任何测试步骤
3. **回滚需求**: 准备完整的回滚方案和回滚测试

### 沟通风险
1. **进度同步**: 每日更新进度，及时沟通问题
2. **需求变更**: 确认升级范围，避免中途增加需求
3. **验收标准**: 明确验收标准，避免标准分歧

## 质量保证

### 测试策略
1. **单元测试**: 保证代码逻辑正确性
2. **集成测试**: 验证组件间协作
3. **E2E测试**: 确保用户流程完整
4. **性能测试**: 监控性能指标

### 代码审查
1. **PR审查**: 所有代码变更都要经过审查
2. **架构审查**: 重要架构变更需要架构师审查
3. **安全审查**: 确保升级不引入安全问题

## 成功标准

### 功能标准
- [ ] 所有现有功能正常工作
- [ ] 用户界面保持一致
- [ ] 性能指标在可接受范围内

### 技术标准
- [ ] 所有测试通过
- [ ] 代码质量达标
- [ ] 构建和部署流程正常

### 业务标准
- [ ] 产品团队验收通过
- [ ] 用户体验无明显下降
- [ ] 系统稳定性良好

## 后续计划

### 监控计划
- 升级后两周内密切监控系统稳定性
- 收集用户反馈，及时处理问题
- 性能指标持续监控

### 优化计划
- 根据实际使用情况优化性能
- 清理不需要的代码和依赖
- 利用新版本特性进一步优化体验

### 技术债务
- 完善测试覆盖率
- 优化代码结构
- 更新开发文档和最佳实践