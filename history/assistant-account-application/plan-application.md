# 助手账号申请功能实施方案

## 概述

本方案旨在实现一个功能，让助手（Assistant）能够提交开通账号申请。申请的信息包括医院、科室和人员列表，人员信息包括姓名、手机号和角色。助手提交的申请将被暂存在MongoDB中，而不是直接创建账号。账号创建将在后续的审核流程中进行。每个申请都有状态标识，例如等待处理、处理完成和取消等。登录的助手可以查看历史申请列表，并可以取消申请。前端页面将使用Ant Design Mobile组件库，以便于在手机上操作。

## 技术架构

### 后端架构

1. MongoDB Schema：定义`AssistantAccountApplication`模式，用于存储账号申请信息
2. Service层：提供申请的创建、查询、取消等功能
3. Controller层：提供API接口，供前端调用
4. DTO：定义数据传输对象，用于前后端数据交互

### 前端架构

1. 助手页面：使用Ant Design Mobile组件库构建移动友好的界面，包括新的AssistantMobileLayout
2. 管理员页面：使用ProComponents组件库构建管理界面
3. 服务层：与后端API交互的服务函数

## 详细设计

### 1. MongoDB Schema

文件路径：`server/src/modules/assistant/schemas/account-application.schema.ts`

需要定义的字段：
- `id`：MongoDB自动生成的ID
- `hospitalName`：医院名称（字符串）
- `departmentName`：科室名称（字符串）
- `ward`：病区名称（字符串，可选）
- `status`：申请状态（枚举：PENDING, COMPLETED, CANCELED）
- `members`：人员列表（数组），每个成员包含：
  - `name`：姓名（字符串）
  - `mobile`：手机号（字符串）
  - `username`：用户名（字符串，可选）
  - `role`：角色（枚举）
- `assistantId`：提交申请的助手ID（数字）
- `createdAt`：创建时间（日期）
- `updatedAt`：更新时间（日期）
- `processedAt`：处理时间（日期，可选）
- `processedBy`：处理人ID（数字，可选）
- `reason`：处理原因（字符串，可选）

### 2. DTO定义

文件路径：`server/src/modules/assistant/dto/account-application.dto.ts`

需要定义的DTO：
- `AccountApplicationDto`：创建申请的数据传输对象
  - `hospitalName`：医院名称
  - `departmentName`：科室名称
  - `ward`：病区名称（可选）
  - `members`：人员列表
- `AccountApplicationRo`：返回给前端的申请对象
  - 包含申请的完整信息
- `AccountApplicationQueryDto`：查询申请的参数
  - `status`：申请状态（可选）
  - `startAt`：开始时间（可选）
  - `endAt`：结束时间（可选）

### 3. 枚举定义

文件路径：`server/src/modules/assistant/constants/enum.ts`

需要定义的枚举：
- `AccountApplicationStatus`：申请状态
  - `PENDING`：等待处理
  - `COMPLETED`：处理完成
  - `CANCELED`：已取消

### 4. Service层

文件路径：`server/src/modules/assistant/account-application.service.ts`

需要实现的方法：
- `create`：创建新申请
- `findAll`：查询申请列表
- `findOne`：查询单个申请
- `update`：更新申请状态

### 5. Controller层

文件路径：`server/src/modules/assistant/account-application.controller.ts`

需要实现的API：
- `POST /api/assistants/account-applications`：创建申请
- `GET /api/assistants/account-applications`：查询申请列表
- `GET /api/assistants/account-applications/:id`：查询单个申请
- `PUT /api/assistants/account-applications/:id/cancel`：取消申请

### 6. 模块配置

文件路径：`server/src/modules/assistant/assistant.module.ts`

需要更新：
- 添加新的Schema到MongooseModule.forFeature中
- 添加新的Service到providers和exports中
- 更新AssistantController

### 7. 前端页面 (助手端)

文件路径：`client/src/layouts/AssistantMobileLayout.tsx`

组件设计：
- 参考Ant Design Mobile最新文档，创建专为移动设备设计的布局组件
- 不参考现有的MobileLayout.tsx
- 包含底部TabBar用于导航
- 适配移动设备的头部NavBar

文件路径：`client/src/pages/Assistants/AccountApplications/index.tsx`

组件设计：
- 申请表单：用于提交新申请
  - 医院名称输入框
  - 科室名称输入框
  - 病区名称输入框（可选）
  - 人员列表，支持添加/删除人员
  - 提交按钮
- 申请列表：显示历史申请
  - 使用Ant Design Mobile的组件如List和Card
  - 取消按钮（针对待处理的申请）
  - 详情按钮，点击可查看详情

### 8. 前端页面 (管理员端)

文件路径：`client/src/pages/Admin/Assistant/AccountApplications.tsx`

组件设计：
- 使用ProComponents组件库构建管理界面
- 申请列表：
  - 使用ProTable组件
  - 状态筛选器
  - 时间范围筛选器
  - 显示申请状态、医院、科室、人数、创建时间等信息
  - 处理按钮，点击可进行审核
  - 详情按钮，点击可查看详情

### 9. 前端路由

文件路径：`client/config/routes.ts`

需要更新：
- 添加新的路由：/assistants和/assistants/*，使用AssistantMobileLayout
- 保留现有的/assistant路由用于兼容性

文件路径：`client/src/pages/Admin/Assistant/index.tsx`

需要更新：
- 添加AccountApplications页面到tabList中

### 10. 前端API服务

文件路径：`client/src/services/api.ts`

需要添加的API：
- `createAccountApplication`：创建申请
- `getAccountApplications`：获取申请列表
- `getAccountApplication`：获取单个申请
- `cancelAccountApplication`：取消申请

## 实施计划 (检查表)

1. 创建MongoDB Schema文件 `server/src/modules/assistant/schemas/account-application.schema.ts`
2. 创建枚举定义文件 `server/src/modules/assistant/constants/enum.ts`
3. 创建DTO定义文件 `server/src/modules/assistant/dto/account-application.dto.ts`
4. 创建Service文件 `server/src/modules/assistant/account-application.service.ts`
5. 创建Controller文件 `server/src/modules/assistant/account-application.controller.ts`
6. 更新 `server/src/modules/assistant/assistant.module.ts` 添加新Schema、Service和Controller
7. 创建移动端布局 `client/src/layouts/AssistantMobileLayout.tsx`
8. 创建助手端申请页面 `client/src/pages/Assistants/AccountApplications/index.tsx`
9. 创建管理员端申请页面 `client/src/pages/Admin/Assistant/AccountApplications.tsx`
10. 更新路由配置 `client/config/routes.ts`
11. 更新管理员端路由 `client/src/pages/Admin/Assistant/index.tsx`
12. 更新前端API服务 `client/src/services/api.ts`
13. 编写单元测试
14. 执行集成测试
15. 部署上线

## 检查清单

1. 创建 `server/src/modules/assistant/schemas` 目录
2. 创建 `server/src/modules/assistant/schemas/account-application.schema.ts` 文件，定义MongoDB Schema
3. 创建 `server/src/modules/assistant/constants` 目录
4. 创建 `server/src/modules/assistant/constants/enum.ts` 文件，定义申请状态枚举
5. 创建 `server/src/modules/assistant/dto/account-application.dto.ts` 文件，定义所有DTO
6. 创建 `server/src/modules/assistant/account-application.service.ts` 文件，实现Service层方法
7. 在Service层实现 `create` 方法，创建新申请
8. 在Service层实现 `findAll` 方法，查询申请列表
9. 在Service层实现 `findOne` 方法，查询单个申请
10. 在Service层实现 `update` 方法，可用于助手取消申请或管理员审批
11. 创建 `server/src/modules/assistant/account-application.controller.ts` 文件，实现Controller层
12. 在Controller层实现 `POST /api/assistants/account-applications` API，创建申请
13. 在Controller层实现 `GET /api/assistants/account-applications` API，查询申请列表
14. 在Controller层实现 `GET /api/assistants/account-applications/:id` API，查询单个申请
15. 在Controller层实现 `PUT /api/assistants/account-applications/:id/cancel` API，取消申请
16. 更新 `server/src/modules/assistant/assistant.module.ts`，添加新Schema到MongooseModule.forFeature中
17. 更新 `server/src/modules/assistant/assistant.module.ts`，添加新Service到providers和exports中
18. 创建 `client/src/layouts/AssistantMobileLayout.tsx` 文件，实现移动端布局
19. 创建 `client/src/pages/Assistants/AccountApplications/index.tsx` 文件，实现助手端申请页面
20. 创建 `client/src/pages/Admin/Assistant/AccountApplications.tsx` 文件，实现管理员端申请页面
21. 在助手端页面实现申请表单组件，用于提交新申请
22. 在助手端页面实现申请列表组件，显示历史申请
23. 在管理员端页面实现申请列表组件，显示申请列表和处理功能
24. 更新 `client/config/routes.ts`，添加新的/assistants路由
25. 更新 `client/src/pages/Admin/Assistant/index.tsx`，添加AccountApplications页面到tabList中
26. 更新 `client/src/services/api.ts`，添加新的API方法
27. 添加 `createAccountApplication` API方法到 `client/src/services/api.ts`
28. 添加 `getAccountApplications` API方法到 `client/src/services/api.ts`
29. 添加 `getAccountApplication` API方法到 `client/src/services/api.ts`
30. 添加 `cancelAccountApplication` API方法到 `client/src/services/api.ts`
31. 添加 `updateAccountApplication` API方法到 `client/src/services/api.ts`
32. 编写单元测试
33. 执行集成测试
34. 部署上线 