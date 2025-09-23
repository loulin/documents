# Ant Design v5 升级技术规范

## 升级技术要点

### 1. 依赖管理策略

#### 1.1 使用@ant-design/pro-components总包
```json
{
  "dependencies": {
    "@ant-design/pro-components": "^2.8.9",
    "antd": "^5.25.4",
    "@ant-design/icons": "^5.6.1"
  }
}
```

#### 1.2 移除的依赖
```json
{
  "dependencies": {
    // 移除这些单独的包
    // "@ant-design/pro-card": "^2.8.8",
    // "@ant-design/pro-descriptions": "^2.5.53", 
    // "@ant-design/pro-field": "^2.16.2",
    // "@ant-design/pro-form": "^2.30.2",
    // "@ant-design/pro-layout": "^6.38.22",
    // "@ant-design/pro-list": "^2.5.69",
    // "@ant-design/pro-table": "^3.17.2"
  }
}
```

#### 1.3 工具依赖清理
```json
{
  "devDependencies": {
    // 移除babel-plugin-import，v5不再需要
    // "babel-plugin-import": "^1.13.8"
  }
}
```

### 2. 导入语句规范

#### 2.1 Pro Components导入
```typescript
// 旧方式 (需要替换)
import { ProTable } from '@ant-design/pro-table';
import { ProForm } from '@ant-design/pro-form';
import { ProLayout } from '@ant-design/pro-layout';
import { ProCard } from '@ant-design/pro-card';

// 新方式 (统一从总包导入)
import { 
  ProTable, 
  ProForm, 
  ProLayout, 
  ProCard 
} from '@ant-design/pro-components';
```

#### 2.2 Ant Design组件导入
```typescript
// 保持不变
import { Button, Modal, Form, Table } from 'antd';
```

#### 2.3 类型定义导入
```typescript
// 旧方式
import type { ProTableProps } from '@ant-design/pro-table';
import type { ProFormProps } from '@ant-design/pro-form';

// 新方式
import type { ProTableProps, ProFormProps } from '@ant-design/pro-components';
```

### 3. API变更映射表

#### 3.1 组件显示控制API
| 组件 | 旧API | 新API |
|------|-------|-------|
| Modal | visible | open |
| Drawer | visible | open |
| Tooltip | visible | open |
| Dropdown | visible | open |
| Popconfirm | visible | open |
| Popover | visible | open |

#### 3.2 弹出框样式API
| 组件 | 旧API | 新API |
|------|-------|-------|
| Select | dropdownClassName | popupClassName |
| Cascader | dropdownClassName | popupClassName |
| TreeSelect | dropdownClassName | popupClassName |
| AutoComplete | dropdownClassName | popupClassName |
| DatePicker | dropdownClassName | popupClassName |
| TimePicker | dropdownClassName | popupClassName |
| Mentions | dropdownClassName | popupClassName |

#### 3.3 表格组件特殊API
| 组件 | 旧API | 新API |
|------|-------|-------|
| Table | filterDropdownVisible | filterDropdownOpen |
| ProTable | filterDropdownVisible | filterDropdownOpen |

#### 3.4 其他组件API变更
| 组件 | 旧API | 新API | 说明 |
|------|-------|-------|------|
| Tag | visible | 条件渲染 | 使用{visible && <Tag>}模式 |
| Slider | tooltipVisible | tooltip.open | 嵌套在tooltip对象中 |
| Notification | message.warn | message.warning | 方法名变更 |

### 4. 样式系统迁移

#### 4.1 Less变量移除
```less
// 移除所有antd less变量引用
// @import '~antd/es/style/themes/index';
// @import '~antd/es/style/mixins/index';
```

#### 4.2 CSS-in-JS Token系统
```typescript
// config/config.ts
export default defineConfig({
  antd: {
    configProvider: {
      theme: {
        token: {
          // 基础色彩
          colorPrimary: '#1677ff', // 主色调
          colorSuccess: '#52c41a',
          colorWarning: '#faad14',
          colorError: '#ff4d4f',
          
          // 尺寸
          borderRadius: 6,
          
          // 字体
          fontFamily: 'AlibabaSans, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
          
          // 间距
          padding: 16,
          margin: 16,
        },
        algorithm: theme.defaultAlgorithm, // 或 theme.darkAlgorithm
      }
    }
  }
});
```

#### 4.3 样式重置
```typescript
// 如果需要重置样式，在index.tsx中引入
import 'antd/dist/reset.css';
```

### 5. UmiJS配置更新

#### 5.1 完整配置示例
```typescript
// config/config.ts
import { defineConfig } from '@umijs/max';
import { theme } from 'antd';

export default defineConfig({
  antd: {
    // 移除import: true配置
    configProvider: {
      theme: {
        cssVar: true, // 启用CSS变量
        token: {
          colorPrimary: '#1677ff',
          borderRadius: 6,
        },
        algorithm: theme.defaultAlgorithm,
      }
    }
  },
  
  // 添加moment到dayjs转换
  moment2dayjs: {
    preset: 'antd',
    plugins: ['duration', 'isSame', 'isBetween']
  },
  
  // 其他配置保持不变
  hash: true,
  locale: {
    default: 'zh-CN',
    antd: true,
    baseNavigator: true,
  }
});
```

### 6. 日期库迁移

#### 6.1 替换moment.js
```typescript
// 旧方式
import moment from 'moment';
import 'moment/locale/zh-cn';
moment.locale('zh-cn');

// 新方式
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
dayjs.locale('zh-cn');

// 添加需要的插件
import duration from 'dayjs/plugin/duration';
import isSameOrBefore from 'dayjs/plugin/isSameOrBefore';
dayjs.extend(duration);
dayjs.extend(isSameOrBefore);
```

#### 6.2 日期格式化
```typescript
// 旧方式
moment(date).format('YYYY-MM-DD');

// 新方式
dayjs(date).format('YYYY-MM-DD');
```

### 7. Pro Layout配置迁移

#### 7.1 app.tsx配置更新
```typescript
// src/app.tsx
import type { RunTimeLayoutConfig } from '@umijs/max';
import { ProLayout } from '@ant-design/pro-components';

export const layout: RunTimeLayoutConfig = ({ initialState, setInitialState }) => {
  return {
    // 检查v7版本的API变更
    actionsRender: () => [
      // 顶部操作按钮
    ],
    avatarProps: {
      // 头像配置
    },
    waterMarkProps: {
      // 水印配置
    },
    footerRender: () => <Footer />,
    onPageChange: () => {
      // 页面切换回调
    },
    menuHeaderRender: undefined,
    childrenRender: (children) => {
      return (
        <>
          {children}
          {isDev && (
            <SettingDrawer
              disableUrlParams
              enableDarkTheme
              settings={initialState?.settings}
              onSettingChange={(settings) => {
                setInitialState((preInitialState) => ({
                  ...preInitialState,
                  settings,
                }));
              }}
            />
          )}
        </>
      );
    },
    ...initialState?.settings,
  };
};
```

### 8. 兼容性处理

#### 8.1 使用V4兼容主题
```typescript
// 如果需要保持V4样式
import { ConfigProvider } from 'antd';
import { defaultTheme } from '@ant-design/compatible';

function App() {
  return (
    <ConfigProvider theme={defaultTheme}>
      <YourApp />
    </ConfigProvider>
  );
}
```

#### 8.2 浏览器兼容性
```typescript
// 对于不支持:where选择器的浏览器
import { StyleProvider } from '@ant-design/cssinjs';

function App() {
  return (
    <StyleProvider hashPriority="high">
      <YourApp />
    </StyleProvider>
  );
}
```

### 9. 性能优化

#### 9.1 按需加载
```typescript
// v5自动支持按需加载，无需配置
import { Button, Modal } from 'antd';
```

#### 9.2 主题缓存
```typescript
// 使用CSS变量提高主题切换性能
const theme = {
  cssVar: true,
  token: {
    colorPrimary: '#1677ff',
  }
};
```

### 10. 测试配置

#### 10.1 Jest配置更新
```javascript
// jest.config.js
module.exports = {
  // 处理CSS-in-JS
  moduleNameMapping: {
    '^antd/es/(.*)$': 'antd/lib/$1',
  },
  
  // 处理样式文件
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx'],
  
  // 设置测试环境
  testEnvironment: 'jsdom',
};
```

#### 10.2 测试工具配置
```typescript
// 测试中使用ConfigProvider
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';

function TestWrapper({ children }) {
  return (
    <ConfigProvider locale={zhCN}>
      {children}
    </ConfigProvider>
  );
}
```

### 11. 代码检查规则

#### 11.1 ESLint规则更新
```json
{
  "rules": {
    // 禁止使用已废弃的API
    "no-restricted-imports": [
      "error",
      {
        "patterns": [
          {
            "group": ["@ant-design/pro-*"],
            "message": "请使用 @ant-design/pro-components 替代单独的包"
          }
        ]
      }
    ]
  }
}
```

#### 11.2 TypeScript配置
```json
{
  "compilerOptions": {
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true
  }
}
```

### 12. 迁移检查清单

#### 12.1 自动化检查
- [ ] 运行codemod工具: `npx @ant-design/codemod-v5 src`
- [ ] 检查所有导入语句是否正确
- [ ] 验证TypeScript类型是否正确

#### 12.2 手动检查
- [ ] 检查所有Modal、Drawer等组件的visible属性
- [ ] 检查所有Select、Cascader等组件的dropdownClassName属性
- [ ] 验证自定义样式是否正常
- [ ] 测试所有表单功能
- [ ] 检查图标显示是否正常

#### 12.3 性能检查
- [ ] 对比打包体积变化
- [ ] 测试首屏加载时间
- [ ] 检查内存使用情况
- [ ] 验证热更新是否正常