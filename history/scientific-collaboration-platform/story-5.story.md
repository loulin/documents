# Epic-2 - Story-5

项目患者管理功能实现

**As a** 项目成员，我希望能在项目中添加和管理患者数据。
**As a** 项目发起方成员，我希望能查看所有参与机构提交的患者数据。
**As a** 项目参与方成员，我希望能只查看我机构提交的患者数据。
**So that** 项目协作中的患者数据管理和隐私控制能够高效进行。

## Status

Completed

## Context

本Story旨在根据PRD (Epic 2, Story 5), 架构文档 (`arch.md`), 以及前端开发规则 (`ui-rules/frontend-development-guidelines-agent`), 为科研项目协作平台实现项目患者管理功能。该功能允许项目成员添加或移除本机构患者到项目中，并根据机构角色（发起方或参与方）控制数据可见性。发起方机构成员可以查看所有患者数据，而参与方机构成员只能查看自己机构提交的患者数据。

- 参考PRD Story 5: 项目患者管理功能实现
- 参考Arch.md: 主要API端点定义 - 机构项目API (注意患者列表需要分页)
- 参考已实现的Story 4及其组件 (ProjectList.tsx, ProjectDetail.tsx)
- 参考Rule: `ui-rules/frontend-development-guidelines-agent`

## Estimation

Story Points: 8

## Tasks

1.  - [x] **项目患者列表页面实现** (`/client/src/pages/Project/PatientManagement.tsx`)
    1.  - [x] 使用 `@ant-design/pro-table` 的 `ProTable` 组件显示项目患者列表。
    2.  - [x] **数据列展示**: 
        * 对所有用户显示: 患者ID、患者姓名、添加时间等基本信息
        * 对发起方机构(isInitiator)用户额外显示: 所属机构、添加者等字段
        * 对参与方机构用户: 隐藏其他机构的数据(后端API已处理)和相关字段
    3.  - [x] **数据获取与分页**: 直接使用 `ProTable` 的 `request` 属性调用 `api.projectPatient.findAll`，将自动处理分页参数 (current, pageSize)。
    4.  - [x] **ProTable配置**: 设置适当的分页配置，如 `pagination={{ pageSize: 10 }}`。
    5.  - [x] **数据访问控制**: 
        * 获取当前用户机构信息 (通过 `useModel('@@initialState')`)
        * 获取项目信息判断机构角色 (isInitiator)
        * 根据机构角色调整表格列显示
    6.  - [x] 提供适当的患者操作功能，如移除患者等。
2.  - [x] **患者列表页面访问入口实现**
    1.  - [x] 在项目列表页面 (`ProjectList.tsx`) 的操作列中添加"患者管理"入口。
    2.  - [x] 点击后导航到项目患者列表页面 (`/project/:id/patients`)。
3.  - [x] **从患者列表页添加患者到项目功能实现**
    1.  - [x] 在患者列表页 (`/client/src/pages/Patient/List.tsx`) 的操作菜单中添加"添加到项目"选项。
    2.  - [x] 点击后弹出项目选择模态框，展示用户有权限的项目列表。
    3.  - [x] 项目选择后调用 `api.projectPatient.create({ projectId }, { patientId: patient.id })` 或类似API。
    4.  - [x] 添加成功后显示成功消息提示，无需导航至项目患者列表。
4.  - [x] **从项目移除患者功能实现**
    1.  - [x] 在项目患者列表页的操作列提供移除患者功能。
    2.  - [x] 使用 `Popconfirm` 添加确认对话框防止误操作。
    3.  - [x] 确认后调用 `api.projectPatient.remove({ projectId, patientId })` 或类似API。
    4.  - [x] 移除成功后刷新患者列表并显示成功消息。
5.  - [x] **API集成与类型定义** (遵循 `ui-rules/frontend-development-guidelines-agent`)
    1.  - [x] 使用已提供的 `ProjectPatient.ts` 中的API方法。
    2.  - [x] 所有API调用通过集中的 `api` 对象进行，如 `api.projectPatient.findAll`, `api.projectPatient.create`, `api.projectPatient.remove`。
    3.  - [x] 使用 `API.` 命名空间为API请求参数和响应数据定义清晰的TypeScript类型。
6.  - [x] **UI/UX与React最佳实践** (遵循 `ui-rules/frontend-development-guidelines-agent`)
    1.  - [x] 组件使用 `function` 声明。
    2.  - [x] 确保界面遵循Ant Design Pro的设计规范。
    3.  - [x] 使用 `useMemo`, `useCallback` 等Hooks进行性能优化。
    4.  - [x] 确保界面的响应式设计和用户友好性。
    5.  - [x] 提供适当的用户反馈 (加载状态、操作结果提示如 `message.success`)。

## Constraints

- 前端框架/库: React, UmiJS, Ant Design, Ant Design Pro Components (ProTable, ProForm, ModalForm).
- 状态管理: 优先使用 `@umijs/max` 的 `useRequest` Hook进行数据获取和状态管理。
- API调用: 通过 `client/src/services/api.ts` 封装的服务进行。
- 代码风格: 遵循项目现有的前端编码规范和 `ui-rules/frontend-development-guidelines-agent`。
- 权限与数据访问: 
  - 发起方机构成员可以看到所有患者数据
  - 参与方机构成员只能看到自己机构的患者数据
  - 只有项目成员可以添加/移除患者

## Structure

相关前端文件结构:

```
/client/src/
├── pages/
│   ├── Project/
│   │   ├── ProjectList.tsx                # (已完成) 用户项目列表页面 (需添加患者管理入口)
│   │   ├── ProjectDetail.tsx              # (已完成) 用户项目详情页面
│   │   ├── MemberManagement.tsx           # (已完成) 机构管理员管理其机构成员的界面
│   │   └── PatientManagement.tsx          # (新增) 项目患者管理界面 (独立页面)
│   └── Patient/
│       └── List.tsx                      # (已提供) 患者列表页面 (需添加"添加到项目"功能)
├── services/
│   ├── api.ts                           # 中心 API 导出对象
│   └── ant-design-pro/                  
│       ├── Project.ts                   # (已提供) Project 相关的API方法定义
│       ├── ProjectMember.ts             # (已提供) ProjectMember 相关的API方法定义
│       └── ProjectPatient.ts            # (已提供) ProjectPatient 相关的API方法定义
```



## Relevant API Endpoints

此前端Story依赖以下API端点:

| HTTP Verb & Path                        | Service & Method                     | 描述                                   | 分页 | 
|-----------------------------------------|-------------------------------------------|----------------------------------------|--------------------|
| GET /api/projects/:id/patients          | `api.projectPatient.findAll` | 获取项目患者列表 (ProTable的request属性会自动处理分页参数) | 需要分页 |
| POST /api/projects/:id/patients         | `api.projectPatient.create({ projectId }, { patientId })` | 添加患者到项目 | N/A |
| DELETE /api/projects/:id/patients/:patientId | `api.projectPatient.remove({ projectId, patientId })` | 从项目移除患者 | N/A |
| GET /api/projects                       | `api.project.query({})` | 获取用户可访问的项目列表(用于选择项目时) | 无需分页 |



## Dev Notes

- ProjectPatient.ts API接口已提供，可直接使用 `api.projectPatient.findAll` 等方法。
- 患者添加功能应参考 Patient/List.tsx 文件中的列表操作区实现方式，如 TableDropdown 组件。
- 项目列表页面需要添加"患者管理"入口，参考现有操作区的实现方式。
- ProTable的request属性会自动处理分页相关参数，无需手动构建查询参数。
- 使用 isInitiator 标志判断当前用户所属机构是否为项目发起方，据此显示或隐藏特定列。
- 确保添加患者到项目时，给用户清晰的成功反馈，但不需要强制跳转到项目患者列表。
- 患者管理功能入口应仅对项目成员可见。

## Chat Command Log

(This section will be updated as development progresses) 