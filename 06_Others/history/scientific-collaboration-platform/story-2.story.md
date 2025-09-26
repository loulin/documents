# Epic-1 - Story-2

后台项目管理API实现

**As a** 开发人员
**I want** 为超级管理员实现项目管理的后端API
**so that** 超级管理员可以创建、读取、更新和删除项目，并管理这些项目的参与机构

## Status

已完成

## Context

本Story旨在根据PRD和架构文档，为科研项目协作平台的后台管理功能实现核心API。这些API将允许超级管理员全面管理科研项目，包括项目的生命周期以及参与项目的机构。这是构建项目管理模块的关键一步。

参考PRD Story 2: 后台项目管理API实现
参考Arch.md: 主要API端点定义 - 项目管理API

## Estimation

Story Points: 5

## Tasks

1.  - [x] **项目CRUD API实现** (`/server/src/modules/admin/project/admin-project.controller.ts`)
    1.  - [x] 实现 `POST /api/admin/projects` API 用于创建新项目 (服务调用 `project.service.ts`)
    2.  - [x] 实现 `GET /api/admin/projects` API 用于获取项目列表 (支持分页) (服务调用 `project.service.ts`)
    3.  - [x] 实现 `GET /api/admin/projects/:id` API 用于获取特定项目详情 (服务调用 `project.service.ts`)
    4.  - [x] 实现 `PUT /api/admin/projects/:id` API 用于更新特定项目信息 (服务调用 `project.service.ts`)
    5.  - [x] 实现 `DELETE /api/admin/projects/:id` API 用于删除特定项目 (服务调用 `project.service.ts`)
2.  - [x] **项目机构管理API实现** (`/server/src/modules/admin/project/admin-project.controller.ts`)
    1.  - [x] 实现 `GET /api/admin/projects/:id/orgs` API 用于获取项目参与机构列表 (服务调用 `project-organization.service.ts`)
    2.  - [x] 实现 `POST /api/admin/projects/:id/orgs` API 用于为项目添加参与机构 (服务调用 `project-organization.service.ts`)
    3.  - [x] 实现 `DELETE /api/admin/projects/:id/orgs/:orgId` API 用于从项目移除参与机构 (服务调用 `project-organization.service.ts`)
3.  - [x] **项目机构成员管理API实现** (`/server/src/modules/admin/admin-project.controller.ts`)
    1.  - [x] 实现 `POST /api/admin/projects/:id/orgs/:orgId/members` API 用于为项目下机构添加成员 (服务调用 `project-member.service.ts`)
    2.  - [x] 实现 `DELETE /api/admin/projects/:id/orgs/:orgId/members/:memberId` API 用于移除项目下机构成员 (服务调用 `project-member.service.ts`)
4.  - [x] **DTO和RO定义**
    1.  - [x] 创建/更新 `admin-project.dto.ts` 用于项目创建和更新的数据传输对象。
    2.  - [x] 创建/更新 `admin-project-organization.dto.ts` 用于项目机构管理的数据传输对象。
    3.  - [x] 创建/更新 `admin-project.ro.ts` 用于项目相关的响应对象。
5.  - [x] **权限控制**
    1.  - [x] 确保所有上述API端点仅限超级管理员访问。
    2.  - [x] 使用适当的Guard进行权限校验。
6.  - [x] **单元测试**
    1.  - [x] 为所有新的API端点编写单元测试。
    2.  - [x] 确保测试覆盖主要业务逻辑和边界情况。
7.  - [x] **API文档**
    1.  - [x] 使用NestJS Swagger (OpenAPI) 装饰器为所有API端点生成文档。

## Constraints

- API必须在 `/server/src/modules/admin/project/` 模块下实现。
- 服务逻辑应主要位于 `/server/src/modules/project/services/` 目录下的 `project.service.ts` 和 `project-organization.service.ts`。
- 所有操作严格限制为超级管理员角色。
- 遵循项目中已有的编码标准和NestJS最佳实践。
- 数据库交互使用TypeORM实体，实体定义在 `/server/src/modules/project/entities/`。

## API Endpoints

根据 `arch.md`，此Story将实现以下管理员API端点：

| 端点                                | 方法   | 描述                            | 权限       |
|------------------------------------|--------|--------------------------------|-----------|
| /api/admin/projects                | GET    | 获取项目列表（需要分页）          | 超级管理员 |
| /api/admin/projects                | POST   | 创建新项目                       | 超级管理员 |
| /api/admin/projects/:id            | GET    | 获取项目详情                     | 超级管理员 |
| /api/admin/projects/:id            | PUT    | 更新项目信息                     | 超级管理员 |
| /api/admin/projects/:id            | DELETE | 删除项目                         | 超级管理员 |
| /api/admin/projects/:id/orgs       | GET    | 获取项目参与机构列表（无需分页）   | 超级管理员 |
| /api/admin/projects/:id/orgs       | POST   | 添加参与机构                     | 超级管理员 |
| /api/admin/projects/:id/orgs/:orgId| DELETE | 移除参与机构                     | 超级管理员 |
| /api/admin/projects/:id/orgs/:orgId/members       | POST   | 添加机构成员                         | 超级管理员        |
| /api/admin/projects/:id/orgs/:orgId/members/:memberId | DELETE | 移除机构成员                         | 超级管理员        |

## Structure

相关文件结构（基于 `story-1.story.md` 和 `arch.md`）：

```
/server/src/modules/admin/
├── project/                                 # 新增或主要修改部分
│   └── admin-project.controller.ts          # 管理员项目控制器
├── dto/
│   ├── admin-project.dto.ts                 # 管理员项目DTOs
│   ├── admin-project-organization.dto.ts    # 管理员项目机构DTOs
│   └── admin-project.ro.ts                  # 管理员项目响应对象
└── ...                                      # 其他 admin 模块文件

/server/src/modules/project/
├── services/
│   ├── project.service.ts                   # 项目核心服务 (被AdminController调用)
│   ├── project-organization.service.ts      # 项目机构核心服务 (被AdminController调用)
│   └── ...
├── entities/
│   ├── project.entity.ts
│   ├── project-organization.entity.ts
│   └── ...
└── ...                                      # 其他 project 模块文件
```

## Dev Notes

- 控制器 (`admin-project.controller.ts`) 应保持轻量，主要负责请求处理和调用服务。
- 复杂的业务逻辑应封装在服务层 (`project.service.ts`, `project-organization.service.ts`)。
- 严格遵循PRD中关于超级管理员权限的规定。
- 参考 `/server/src/modules/admin/`下其他控制器的实现模式。
- 确保参数校验（如使用 `class-validator`）和错误处理机制。

## Chat Command Log

- User: ok，story 2已完成，标记一下所有的task，然后计划下一个story
- Agent: Marked all tasks in story-2 as complete and updated status to 已完成. 