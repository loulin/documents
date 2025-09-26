# 糖尿病知识图谱前端界面设计

## 整体架构设计

### 技术栈选择
- **前端框架**: React 18 + TypeScript
- **UI组件库**: Ant Design Pro
- **状态管理**: Redux Toolkit + RTK Query
- **图表可视化**: ECharts + G6 (知识图谱可视化)
- **移动端**: React Native + Expo
- **构建工具**: Vite

### 应用结构
```
diabetes-kg-frontend/
├── src/
│   ├── components/          # 通用组件
│   │   ├── KnowledgeGraph/  # 知识图谱可视化
│   │   ├── QuestionInput/   # 问题输入组件
│   │   ├── AnswerDisplay/   # 答案展示组件
│   │   └── EntityCard/      # 实体卡片组件
│   ├── pages/              # 页面组件
│   │   ├── QAInterface/    # 问答界面
│   │   ├── KnowledgeBase/  # 知识库浏览
│   │   ├── Statistics/     # 统计分析
│   │   └── Admin/          # 管理后台
│   ├── services/           # API服务
│   ├── hooks/              # 自定义Hooks
│   ├── utils/              # 工具函数
│   └── types/              # TypeScript类型定义
```

## 用户界面设计

### 1. 主要问答界面

#### 1.1 问答聊天界面
```typescript
interface QAInterfaceProps {
  user_id?: string;
  context?: PatientContext;
}

interface ChatMessage {
  id: string;
  type: 'question' | 'answer';
  content: string;
  timestamp: Date;
  entities?: EntityInfo[];
  confidence?: number;
  sources?: string[];
}
```

**界面特性**：
- 📱 响应式设计，支持手机/平板/桌面
- 💬 微信聊天风格的对话界面
- 🎯 智能问题建议和联想
- 📊 答案可信度可视化展示
- 🔗 相关实体链接和跳转

#### 1.2 智能问题输入组件
```typescript
interface QuestionInputProps {
  onSubmit: (question: string, context?: any) => void;
  suggestions?: string[];
  loading?: boolean;
}
```

**功能特性**：
- 🎤 语音输入支持 (Web Speech API)
- 💡 实时问题联想和建议
- 🏷️ 自动实体标注和高亮
- ⌨️ 快捷键支持 (Ctrl+Enter提交)
- 📝 问题历史和收藏

### 2. 知识图谱可视化

#### 2.1 交互式知识图谱
```typescript
interface KnowledgeGraphProps {
  entities: EntityNode[];
  relationships: RelationshipEdge[];
  focusEntity?: string;
  layout?: 'force' | 'circular' | 'hierarchical';
}

interface EntityNode {
  id: string;
  name: string;
  type: EntityType;
  size: number;      // 节点大小(重要性)
  color: string;     // 节点颜色(类型)
  properties: any;
}
```

**可视化特性**：
- 🕸️ 基于G6的交互式图谱展示
- 🎨 实体类型颜色编码
- 🔍 节点搜索和定位
- 📏 关系强度可视化
- 🎯 点击节点查看详情
- 📱 移动端友好的手势操作

#### 2.2 实体详情面板
```typescript
interface EntityDetailProps {
  entity: EntityInfo;
  relationships: Relationship[];
  relatedQuestions?: string[];
}
```

### 3. 知识库浏览界面

#### 3.1 实体分类浏览
```typescript
interface EntityCategoryProps {
  categories: EntityCategory[];
  selectedCategory?: string;
  onCategorySelect: (category: string) => void;
}
```

**浏览特性**：
- 📚 按医学领域分类展示
- 🔍 全文搜索和过滤
- 📊 实体统计和分析
- 🏷️ 标签云展示
- 📱 卡片式布局

#### 3.2 搜索结果页面
```typescript
interface SearchResultProps {
  query: string;
  results: SearchResult[];
  facets: SearchFacet[];      // 搜索分面
  pagination: PaginationInfo;
}
```

## 移动端应用设计

### 移动端特色功能

#### 1. 语音问答
```typescript
interface VoiceQAProps {
  onVoiceInput: (text: string) => void;
  onVoiceOutput: (answer: string) => void;
}
```

#### 2. 离线缓存
```typescript
interface OfflineCache {
  commonQuestions: CachedQA[];
  entities: CachedEntity[];
  lastSync: Date;
}
```

#### 3. 推送通知
```typescript
interface NotificationService {
  scheduleHealthReminder: (reminder: HealthReminder) => void;
  sendEducationTip: (tip: EducationTip) => void;
}
```

### 移动端界面结构
```
TabNavigator:
├── 问答 (QA)           # 主要问答功能
├── 知识库 (Knowledge)   # 浏览医学知识
├── 我的 (Profile)       # 个人设置和历史
└── 更多 (More)         # 工具和设置
```

## 管理后台设计

### 1. 知识图谱管理

#### 1.1 实体管理界面
```typescript
interface EntityManagementProps {
  entities: EntityInfo[];
  onEntityCreate: (entity: EntityCreateRequest) => void;
  onEntityUpdate: (id: string, updates: EntityUpdateRequest) => void;
  onEntityDelete: (id: string) => void;
}
```

#### 1.2 关系管理界面
```typescript
interface RelationshipManagementProps {
  relationships: Relationship[];
  entities: EntityInfo[];
  onRelationshipCreate: (rel: RelationshipCreateRequest) => void;
  onRelationshipUpdate: (id: string, updates: RelationshipUpdateRequest) => void;
}
```

### 2. 问答质量分析

#### 2.1 问答统计面板
```typescript
interface QAStatisticsProps {
  totalQuestions: number;
  averageConfidence: number;
  responseTime: TimeSeriesData[];
  popularQuestions: PopularQuestion[];
  satisfactionScore: number;
}
```

#### 2.2 问题分析界面
```typescript
interface QuestionAnalysisProps {
  questions: AnalyzedQuestion[];
  filters: AnalysisFilter[];
  charts: ChartData[];
}

interface AnalyzedQuestion {
  id: string;
  question: string;
  query_type: QueryType;
  confidence: number;
  user_satisfaction?: number;
  entities_involved: string[];
  response_time: number;
  timestamp: Date;
}
```

### 3. 系统监控

#### 3.1 性能监控
```typescript
interface SystemMonitoringProps {
  apiMetrics: APIMetrics;
  dbMetrics: DatabaseMetrics;
  userMetrics: UserMetrics;
  errorLogs: ErrorLog[];
}
```

## 用户体验设计

### 1. 响应式设计
- **桌面端 (≥1200px)**: 三栏布局，左侧导航，中间内容，右侧相关信息
- **平板端 (768px-1199px)**: 两栏布局，可折叠侧栏
- **手机端 (<768px)**: 单栏布局，底部导航

### 2. 无障碍设计
- 🔤 语义化HTML结构
- ⌨️ 完整键盘导航支持
- 🔊 屏幕阅读器支持
- 🎨 高对比度主题选项
- 📝 ARIA标签完善

### 3. 性能优化
- ⚡ 代码分割和懒加载
- 💾 智能缓存策略
- 🔄 请求去重和防抖
- 📱 PWA支持
- 🚀 CDN资源分发

## 组件库设计

### 1. 核心组件

#### QuestionInput 组件
```tsx
interface QuestionInputProps {
  placeholder?: string;
  maxLength?: number;
  suggestions?: string[];
  onSubmit: (question: string) => void;
  onVoiceInput?: (text: string) => void;
  loading?: boolean;
}

const QuestionInput: React.FC<QuestionInputProps> = ({
  placeholder = "请输入您的问题...",
  maxLength = 500,
  suggestions = [],
  onSubmit,
  onVoiceInput,
  loading = false
}) => {
  // 组件实现
};
```

#### AnswerDisplay 组件
```tsx
interface AnswerDisplayProps {
  answer: string;
  confidence: number;
  entities: EntityInfo[];
  sources: string[];
  onEntityClick?: (entity: EntityInfo) => void;
}

const AnswerDisplay: React.FC<AnswerDisplayProps> = ({
  answer,
  confidence,
  entities,
  sources,
  onEntityClick
}) => {
  // 组件实现
};
```

#### EntityCard 组件
```tsx
interface EntityCardProps {
  entity: EntityInfo;
  showRelationships?: boolean;
  onClick?: (entity: EntityInfo) => void;
}

const EntityCard: React.FC<EntityCardProps> = ({
  entity,
  showRelationships = false,
  onClick
}) => {
  // 组件实现
};
```

### 2. Hook设计

#### useQASystem Hook
```tsx
interface useQASystemReturn {
  askQuestion: (question: string) => Promise<QuestionResponse>;
  loading: boolean;
  error: string | null;
  history: ChatMessage[];
  clearHistory: () => void;
}

const useQASystem = (): useQASystemReturn => {
  // Hook实现
};
```

#### useKnowledgeGraph Hook
```tsx
interface useKnowledgeGraphReturn {
  entities: EntityInfo[];
  relationships: Relationship[];
  searchEntities: (query: string) => Promise<EntityInfo[]>;
  getEntityById: (id: string) => Promise<EntityInfo>;
  loading: boolean;
  error: string | null;
}

const useKnowledgeGraph = (): useKnowledgeGraphReturn => {
  // Hook实现
};
```

## 部署和发布

### 1. 构建配置
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          antd: ['antd'],
          charts: ['echarts', '@antv/g6']
        }
      }
    }
  }
});
```

### 2. Docker部署
```dockerfile
FROM node:16-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3. CI/CD流程
```yaml
# .github/workflows/deploy.yml
name: Deploy Frontend
on:
  push:
    branches: [main]
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm ci
      - run: npm run test
      - run: npm run build
      - run: npm run deploy
```

这个前端设计涵盖了完整的用户界面，从简单的问答界面到复杂的知识图谱可视化，以及管理后台功能，确保系统的易用性和可维护性。