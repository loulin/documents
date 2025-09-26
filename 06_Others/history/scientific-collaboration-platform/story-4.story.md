# Epic-2 - Story-4

机构用户项目访问与成员管理前端实现

**As a** 认证用户，我希望能通过界面查看我有权访问的项目列表和项目详情。
**As a** 机构管理员，我希望能通过界面管理我机构内部的项目成员。
**So that** 项目协作相关的查看和管理操作能够直观便捷地在前端完成。

## Status

Completed

## Context

本Story旨在根据PRD (Epic 2, Story 4 - 前端部分), 架构文档 (`arch.md`), 以及前端开发规则 (`ui-rules/frontend-development-guidelines-agent`), 为科研项目协作平台实现面向普通用户和机构管理员的前端界面。这些界面将利用已有的API（通过 `client/src/services/api.ts` 访问，具体方法参考 `client/src/services/ant-design-pro/Project.ts` 和 `client/src/services/ant-design-pro/ProjectMember.ts`），允许普通用户查看他们参与的项目，并允许机构管理员管理其机构内特定项目的成员。

参考PRD Story 4: 机构用户项目访问与成员管理API及前端 (前端部分)
参考Arch.md: 主要API端点定义 - 机构项目API (注意分页要求)
参考Generated API Clients: `Project.ts`, `ProjectMember.ts`
参考Rule: `ui-rules/frontend-development-guidelines-agent`

## Estimation

Story Points: 5

## Tasks

1.  - [x] **用户项目列表页面实现** (`/client/src/pages/Project/ProjectList.tsx`)
    1.  - [x] 使用 `@ant-design/pro-table` 的 `ProTable` 组件显示用户可访问的项目列表。
    2.  - [x] Columns 包括项目名称、项目角色 (发起方/参与方)、状态等。
    3.  - [x] **数据获取**: 使用 `useRequest` (来自 `ahooks`) 调用 `api.project.query({})` 获取项目列表，并将获取的数组直接传递给 `ProTable` 的 `dataSource` prop。
    4.  - [x] **ProTable配置**: 设置 `search={false}` 和 `pagination={false}`。
    5.  - [x] 提供操作，包括点击项目名称或详情按钮，导航到项目详情页面 (`/project/detail/:id`)。
2.  - [x] **用户项目详情页面实现** (`/client/src/pages/Project/ProjectDetail.tsx`)
    1.  - [x] 使用 `useRequest` (来自 `ahooks`) 调用 `api.project.findOne({ projectId })` 获取项目详细信息。
    2.  - [x] 使用 `@ant-design/pro-descriptions` 显示项目详情。
    3.  - [x] 根据用户机构是否为项目发起方 (使用 isInitiator 判断)，条件性显示参与机构列表和成员管理组件。
3.  - [x] **机构项目成员管理界面实现** (已作为 `ProjectDetail.tsx` 的一部分实现)
    1.  - [x] 供机构管理员查看和管理其机构在特定项目中的成员。
    2.  - [x] **数据获取**: 使用 `useRequest` (来自 `ahooks`) 调用 `api.projectMember.findAll({ projectId })` 获取成员列表。
    3.  - [x] **ProTable配置**: 设置 `search={false}` 和 `pagination={false}`。
    4.  - [x] 提供添加机构成员到项目的功能: 使用 `ModalForm` 并包含用户选择组件。
    5.  - [x] 在 `ProTable` 的操作列提供从项目中移除机构成员的功能，使用 `Popconfirm` 确认。
4.  - [x] **API集成与类型定义** (遵循 `ui-rules/frontend-development-guidelines-agent`)
    1.  - [x] 使用 `api.project.query`, `api.project.findOne`, `api.projectMember.findAll`, `api.projectMember.create`, `api.projectMember.remove` 等API方法。
    2.  - [x] 所有API调用通过集中的 `api` 对象进行。
    3.  - [x] 使用 `API.` 命名空间为API参数和响应数据定义TypeScript类型。
5.  - [x] **路由配置**
    1.  - [x] 实现 `/project`, `/project/detail/:id` 等路由配置。
6.  - [x] **UI/UX与React最佳实践** (遵循 `ui-rules/frontend-development-guidelines-agent`)
    1.  - [x] 组件使用 `function` 声明。
    2.  - [x] 确保界面遵循Ant Design Pro的设计规范。
    3.  - [x] 使用 `useMemo` 等Hooks进行性能优化。
    4.  - [x] 确保界面的响应式设计和用户友好性。
    5.  - [x] 提供适当的用户反馈 (加载状态、操作结果提示等)。

## Constraints

- 前端框架/库: React, UmiJS, Ant Design, Ant Design Pro Components (ProTable, ProForm, ModalForm, ProDescriptions).
- 状态管理: 优先使用 `@umijs/max` 的 `useRequest` Hook进行数据获取和状态管理。若有更复杂的跨组件状态，可考虑UmiJS的model。
- API调用: 通过 `client/src/services/api.ts` 封装的服务进行。
- 代码风格: 遵循项目现有的前端编码规范和 `ui-rules/frontend-development-guidelines-agent`。
- 权限: 界面的可见性和操作权限需与后端API权限匹配 (普通用户 vs 机构管理员)。机构管理员只能管理自己机构的成员。

## Relevant API Endpoints

此前端Story依赖以下API端点 (路径和方法名参考 `Project.ts` 和 `ProjectMember.ts`):

| HTTP Verb & Path                        | Service & Method (example)                     | 描述                                   | arch.md Pagination | 
|-----------------------------------------|------------------------------------------------|----------------------------------------|--------------------|
| GET /api/projects                       | `api.project.query({})`                        | 获取用户可访问的项目列表               | 无需分页           |
| GET /api/projects/:id                   | `api.project.findOne({ id })`                  | 获取项目详情                           | N/A                |
| GET /projects/:projectId/members        | `api.projectMember.findAll({ projectId })`     | 获取项目下某机构的成员列表             | 无需分页           |
| POST /projects/:projectId/members       | `api.projectMember.create({ projectId }, body)`| 添加机构成员到项目                     | N/A                |
| DELETE /projects/:projectId/members/:memberId | `api.projectMember.remove({ projectId, memberId })` | 从项目移除机构成员                   | N/A                |

*Note: API paths for ProjectMember in the generated client (`/projects/...`) differ slightly from `arch.md` (`/api/projects/...`). The client paths are used here. Also note that in arch.md the parameter for removing members is specified as `:userId` but the actual implementation uses `:memberId`.*

## Structure

相关前端文件结构（基于 `arch.md` 和项目约定）：

```
/client/src/
├── pages/
│   └── Project/
│       ├── ProjectList.tsx                # 用户项目列表页面 (ProTable with dataSource)
│       ├── ProjectDetail.tsx              # 用户项目详情页面 (ProDescriptions, conditional MemberManagement)
│       └── MemberManagement.tsx           # (或内嵌于Detail) 机构管理员管理其机构成员的界面 (ProTable with dataSource, ModalForm)
├── services/
│   ├── api.ts                           # 中心 API 导出对象 (确保 Project 和 ProjectMember 服务已集成)
│   └── ant-design-pro/                  
│       ├── Project.ts                   # (已提供) Project 相关的API方法定义
│       └── ProjectMember.ts             # (已提供) ProjectMember 相关的API方法定义
├── models/                              # (可选) 若 useRequest 不足以满足状态管理需求
└── locales/                             # 国际化文件更新 (若需)
    ├── zh-CN/
    │   └── menu.ts                      
    │   └── pages.ts                     
    └── en-US/
        └── menu.ts                      
        └── pages.ts                     
```

## Dev Notes

- 明确 `Project.ts` 的 `query` 方法在不分页情况下如何调用 (e.g. `api.project.query({})` or if specific params are needed to disable pagination if the API client defaults to it).
- 对于 `ModalForm` 中选择用户的组件，需确认具体实现方式或是否有现有通用组件。
- 严格使用TypeScript，定义明确的类型 (`API.something`)。
- 确保与后端API的权限逻辑一致。机构管理员只能管理自己机构的成员。
- 充分的联调测试。

## Chat Command Log

Story 4 has been successfully implemented with all components working as specified:
- ProjectList.tsx displays the list of projects a user has access to
- ProjectDetail.tsx shows project details and includes ProjectMemberManagement component
- MemberManagement.tsx implements the project member management functionality 