# Epic-2 - Story-6

患者数据统计与导出功能

**As a** 项目研究员或管理员
**I want** 能够查看科研项目的关键患者数据统计指标, 并且对于项目发起机构，能够查看其项目中各参与机构的这些统计数据。
**So that** 我可以快速了解项目进展、患者群体特征、各机构对项目的贡献情况，并为研究分析和报告提供数据支持。

## Status

In Progress

## Context

本Story旨在根据PRD (Epic 2, Story 6) 为科研项目协作平台实现患者数据统计功能。这将涉及后端API的开发，用于计算和提供指定项目的多维度统计数据。
此Story已更新，以包含按项目中每个参与机构细分的统计数据，此视图对项目发起机构可见。后端将提供一个单一的API端点，以检索项目的所有参与机构的统计信息。

- 参考PRD Story 6: 患者数据统计与导出功能
- 参考已确定的统计维度和SQL实现方案

## Estimation

Story Points: 5 (后端API和服务逻辑)

## Tasks

1.  - [ ] **后端统计服务实现** (`server/src/modules/project/services/project.service.ts`)
    1.  - [ ] 定义 `ProjectOrganizationStatisticsRo` DTO (例如在 `server/src/modules/project/dto/project-organization-statistics.ro.ts`). 此RO将包含一个数组，其中每个元素包括 `organizationId`, `organizationName`, 以及其特定的 `ProjectStatisticsRo` (项目整体统计RO结构)。
    2.  - [ ] 在 `ProjectService` 中实现新的方法 `getProjectOrganizationStatistics(projectId: number): Promise<ProjectOrganizationStatisticsRo[]>`。
    3.  - [ ] 在新的服务方法中, 首先获取指定 `projectId` 的所有参与机构。
    4.  - [ ] 对于每个参与机构, 实现或复用逻辑来计算以下指标:
        - [ ] 案例总数 (Total Cases)
        - [ ] 传感器数 (Total Sensor Count)
        - [ ] 平均佩戴数 (Average Sensors per Patient)
        - [ ] 男女比例 (Gender Ratio)
        - [ ] 平均年龄 (Average Age)
        - [ ] 平均病程 (Average Disease Duration)
        - [ ] 平均佩戴时长（天）(Average Sensor Wearing Duration)
    5.  - [ ] 确保用于这些计算的所有SQL查询都已修改，以便除了 `projectId` 之外，还按特定的 `organizationId` 进行筛选。
    6.  - [ ] 确保所有SQL查询都能高效并正确处理边界条件 (例如，某个机构没有数据，或发生除零错误)。
    7.  - [ ] 为新的服务方法和按机构计算的逻辑添加适当的日志记录。
2.  - [ ] **项目统计API端点实现** (`server/src/modules/project/project.controller.ts`)
    1.  - [ ] 创建新的GET API端点: `/api/projects/:projectId/organization-statistics`。
    2.  - [ ] 此端点调用 `ProjectService.getProjectOrganizationStatistics` 方法。
    3.  - [ ] 确保此API端点有适当的权限控制 (例如，只有项目发起机构的成员才能访问此特定端点，可参考 `ProjectAccessService.canViewOrganizations` 或类似逻辑)。
    4.  - [ ] 返回 `ProjectOrganizationStatisticsRo[]` (数组) 格式的响应。
3.  - [ ] **(现有任务调整/确认) 后端整体项目统计服务** (`server/src/modules/project/services/project.service.ts`)
    1.  - [ ] 确认 `getProjectStatistics(projectId: number): Promise<ProjectStatisticsRo>` 方法 (用于项目整体统计) 保持功能正常或根据需要进行调整。
    2.  - [ ] 对应的 API `GET /api/projects/:projectId/statistics` 用于提供项目整体统计数据。
4.  - [ ] **(后续任务) 数据导出功能**
    1.  - [ ] 设计导出数据的格式 (例如 CSV, Excel)。
    2.  - [ ] 实现按机构筛选的数据导出API。
5.  - [x] **数据统计可视化界面**
    1.  - [x] 在前端项目详情页或专门的统计页面展示这些数据，包括按机构展示的统计列表。

## Constraints

- 后端框架/库: NestJS, TypeORM, PostgreSQL.
- API设计: 遵循项目的RESTful API设计规范。
- 代码风格: 遵循项目现有的后端编码规范。

## Relevant API Endpoints

此Story将创建/确认以下API端点:

| HTTP Verb & Path                                  | Service & Method                                | 描述                                                                 |
|---------------------------------------------------|-------------------------------------------------|----------------------------------------------------------------------|
| GET /api/projects/:projectId/statistics           | `ProjectService.getProjectStatistics`           | 获取指定项目的**整体**患者数据统计                                       |
| GET /api/projects/:projectId/organization-statistics | `ProjectService.getProjectOrganizationStatistics` | 获取指定项目中**各参与机构**的患者数据统计 (新, 供项目发起方使用)           |

## Dev Notes

- 仔细核对 `SuperPatientEntity` (`Patients` 表), `Sensor` 表, 和 `ProjectPatient` 表的实际列名和数据类型, 特别是用于筛选的 `ProjectPatient.organizationId`。
- SQL查询应尽可能高效，利用数据库索引。核心统计计算逻辑将需要调整，以根据项目内每个参与组织的 `organizationId` 来筛选数据。
- 考虑统计计算的性能，特别是对于大型项目。后端将获取给定项目的所有参与组织，然后为每个组织计算统计数据，并在单个响应中返回它们。
- `ProjectOrganizationStatisticsRo` DTO 的创建是此Story的一部分。

## Chat Command Log

(This section will be updated as development progresses)
