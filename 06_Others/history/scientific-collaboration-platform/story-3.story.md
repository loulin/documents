# Epic-1 - Story-3

后台项目管理前端实现

**As a** 超级管理员
**I want** 一个后台管理界面来管理科研项目
**so that** 我可以高效地监督所有与项目相关的活动

## Status

Completed

## Context

本Story的目标是为后台项目管理功能开发前端用户界面。这将利用在Story 2中创建的API，为超级管理员提供一个直观的方式来管理项目、机构和成员。PRD中的Story 3（后台项目管理前端实现）和Arch.md中的前端结构为此Story提供了指导。

参考PRD Story 3: 后台项目管理前端实现
参考Arch.md: Project Structure - Client-side

## Estimation

Story Points: 8

## Tasks

1.  - [x] **项目列表页面** (`/client/src/pages/Admin/Project/ProjectList.tsx`)
    1.  - [x] 使用 `@ant-design/pro-table` 的 `ProTable` 组件显示项目列表，包含项目名称、发起机构、状态、创建时间等。
    2.  - [x] 通过 `ProTable` 的 `request` prop 直接调用 `api.adminProject.queryProjects` (假设方法名) 获取分页数据，并处理排序和筛选。
    3.  - [x] 实现 `actionRef` 以便刷新表格，以及 `columnsState` 实现列状态持久化 (参照 `@ts-rules/protable-conventions-agent.mdc`)。
    4.  - [x] 提供"创建项目"按钮，触发 `ModalForm` (见任务2)。
    5.  - [x] 在操作列 (`valueType: 'option'`) 提供"编辑"、"详情"和"删除"项目的按钮/链接。
2.  - [x] **项目创建/编辑页面/表单** (使用 `@ant-design/pro-form` 的 `ModalForm`，在 `ProjectList.tsx` 或 `ProjectEditor.tsx` 中实现)
    1.  - [x] 实现 `ModalForm` 用于创建和编辑项目信息（名称、描述、起止日期、发起机构等），优先使用此组件 (参照 `@ts-rules/modalform-preference-agent.mdc`)。
    2.  - [x] 通过 `open` 和 `onOpenChange` 控制 `ModalForm` 可见性。设置 `modalProps={{ destroyOnClose: true }}`。
    3.  - [x] 使用 `initialValues` 填充编辑表单。
    4.  - [x] 在 `onFinish` 中调用 `api.adminProject.createProject` 或 `api.adminProject.updateProject` (假设方法名)。
    5.  - [x] 实现表单校验逻辑。
3.  - [x] **项目详情页面** (`/client/src/pages/Admin/Project/ProjectDetail.tsx`)
    1.  - [x] 显示项目的详细信息 (可使用 `@ant-design/pro-descriptions`)。
    2.  - [x] 包含一个用于管理该项目参与机构的组件 (见任务4)。可考虑使用 `ahooks` `useRequest` 获取项目详情数据。
4.  - [x] **项目机构管理组件** (例如，在 `/client/src/pages/Admin/Project/OrganizationManagement.tsx` 或作为 `ProjectDetail.tsx` 的一部分)
    1.  - [x] 使用 `ProTable` 显示项目已关联的参与机构列表，通过 `request` 调用 `api.adminProject.queryProjectOrganizations` (假设方法名)。
    2.  - [x] 提供添加参与机构的功能 (例如，通过一个 `SelectOrganizations.tsx` 组件选择机构，然后调用 `api.adminProject.addProjectOrganization`)。
    3.  - [x] 提供移除参与机构的功能 (调用 `api.adminProject.removeProjectOrganization`)。
5.  - [x] **API集成与类型** (参照 `@ts-rules/api-services-structure-agent.mdc` 和 `@ts-rules/typescript-best-practices-agent.mdc`)
    1.  - [x] 确保 `adminProject` 相关的服务方法 (如 `queryProjects`, `createProject`, `getProjectDetails`, `updateProject`, `deleteProject`, `queryProjectOrganizations`, `addProjectOrganization`, `removeProjectOrganization`) 在 `client/src/services/ant-design-pro/adminProject.ts` (或类似自动生成文件) 中定义，并正确集成到 `client/src/services/api.ts` 中。
    2.  - [x] 所有API调用通过集中的 `api` 对象进行 (e.g., `api.adminProject.queryProjects(...)`)。
    3.  - [x] 对于非ProComponent直接处理的API调用 (如获取单个项目详情用于表单预填)，使用 `ahooks` 的 `useRequest` Hook。
    4.  - [x] 定义清晰的TypeScript接口/类型 (例如 `API.AdminProject`, `API.AdminProjectParams`) 用于API请求参数和响应数据，避免使用 `any`。
6.  - [x] **路由配置**
    1.  - [x] 在UmiJS路由配置中添加新页面的路由 (`/admin/project/list`, `/admin/project/detail/:id` 等)。
7.  - [x] **UI/UX与React最佳实践** (参照 `@ts-rules/react-best-practices-agent.mdc`)
    1.  - [x] 确保界面遵循Ant Design Pro的设计规范。
    2.  - [x] 使用 `useMemo` 优化 `ProTable` 的 `columns` 定义，使用 `useCallback` 优化传递给子组件的事件处理器。
    3.  - [x] 组件定义为函数，props通过单个对象传递并解构。
    4.  - [x] 确保界面的响应式设计和用户友好性。

## Constraints

- 前端框架/库: React, UmiJS, Ant Design, Ant Design Pro。
- 状态管理: 使用UmiJS的内置model或推荐的状态管理方案。
- API调用: 通过services层进行封装。
- 代码风格: 遵循项目现有的前端编码规范和最佳实践。
- 目标用户: 超级管理员。

## Structure

根据 `arch.md` 和项目约定，相关前端文件结构可能如下:

```
/client/src/
├── pages/
│   └── Admin/
│       └── Project/
│           ├── ProjectList.tsx                # 项目列表页面 (ProTable, ModalForm for create/edit)
│           ├── ProjectDetail.tsx              # 项目详情页面 (ProDescriptions, OrganizationManagement component)
│           ├── OrganizationManagement.tsx     # (可选) 机构管理组件 (ProTable)
│           └── SelectOrganizations.tsx        # (可选) 机构选择辅助组件
├── services/
│   ├── api.ts                               # 中心 API 导出对象 (会包含 adminProject)
│   └── ant-design-pro/                      # OpenAPI 自动生成的服务
│       └── adminProject.ts                  # (示例) adminProject 相关的API方法定义
├── models/
│   └── adminProject.ts                      # (可选) 项目管理相关的UmiJS Model (若 useRequest 不足时)
└── locales/                                 # 国际化文件更新
    ├── zh-CN/
    │   └── menu.ts                          # 菜单中文名
    │   └── pages.ts                         # 页面相关中文
    └── en-US/
        └── menu.ts                          # 菜单英文名
        └── pages.ts                         # 页面相关英文
```

## Dev Notes

- 优先使用 `@ant-design/pro-components` (如 `ProTable`, `ProForm`, `ModalForm`, `ProDescriptions`) 来提高开发效率 (参照 `@ts-rules/antd-procomponents-usage-agent.mdc`)。
- 所有API调用必须通过集中的 `api` 对象 (e.g., `api.adminProject.methodName`)，如 `@ts-rules/api-services-structure-agent.mdc` 所述。
- 如果发现API调用有不合理的地方，包括lint错误等，不要直接修复，请详细说明并列出来该如何修改。
- 对于非 `ProTable` `request` 或 `ProForm` `onFinish` 直接处理的API调用，优先使用 `ahooks` `useRequest`。
- 严格使用TypeScript，为props、state和API数据定义明确的类型 (参照 `@ts-rules/typescript-best-practices-agent.mdc`)。
- 使用 `useMemo` 和 `useCallback` 进行性能优化，特别是在 `ProTable` 列定义和传递给子组件的回调中 (参照 `@ts-rules/react-best-practices-agent.mdc`)。
- 考虑组件的可复用性。
- 确保所有操作都有明确的用户反馈 (如加载提示、成功/失败消息)。
- 与后端API进行充分的联调测试。
- 确保国际化支持，更新必要的 `locales` 文件。

## Chat Command Log

(This section will be updated as development progresses) 