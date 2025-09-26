# CRF模块实施 - 行动计划

## 1. 概述

本行动计划旨在将新的"融合档案"科研项目模型付诸实施。计划涵盖数据库迁移、后端代码重构和文档同步等关键步骤，以确保平稳、有序地过渡到新架构。

---

## 2. 数据库层 (Database Layer)

**负责人**: `DBA / Backend Lead`

| 任务 | 目标实体/表 | 具体操作 | 备注 |
| :--- | :--- | :--- | :--- |
| **2.1. 改造项目表** | `project` | 1. 将表名重命名为 `research_project`。 <br> 2. **修改列**: 将 `status` 字段类型从 `integer` 改为 `string`，并定义相应的 `enum` 值（如 'DRAFT', 'ACTIVE'）。<br> 3. 确认 `start_date`, `end_date`, `metadata` 等字段存在且类型正确。 | 这是对现有表的改造，保留主键为`integer`。迁移脚本需处理数据转换。 |
| **2.2. 升级患者关联表** | `project_patient` | 1. 将表名重命名为 `project_enrollment`。 <br> 2. **添加列**: `enrollment_date` (date), `status` (string)。 <br> 3. **修改列**: 确认主键为`uuid`（如果原表不是，则需要替换）。 <br> 4. **保留列**: `project_id`, `patient_id`, `organization_id`, `added_by_user_id`。 | 这是对现有表的升级，使其成为"档案表"。 |
| **2.3. 创建访视模板表** | `visit_templates` (新) | 1. 根据 `database_schema.md` 定义创建 `visit_templates` 表。 | 用于定义标准化的访视计划。 |
| **2.4. 修改访视表** | `clinical_visit` | 1. **移除列**: `visit_name`。 <br> 2. **新增列**: `visit_template_id` (uuid)。<br> 3. **新增列**: `medical_record_number` (string, nullable)。 | 使访视事件与预定义模板关联，并记录病案号。 |
| **2.5. 创建核心数据表** | `observations`, `observation_definitions` 等 | 1. 根据 `database_schema.md` 中的定义创建新表。 <br> 2. **特别注意**: `observations`表的`value_numeric`字段使用`NUMERIC(15, 5)`类型。 | 这些是新科研模块的核心数据表。 |
| **2.6. 创建单位管理表** | `unit_definitions`, `project_unit_preferences` | 1. 根据 `database_schema.md` 定义创建这两张新表。 | 用于支持灵活的单位换算与显示。 |
| **2.7. 编写迁移脚本** | - | 1. 使用 `TypeORM migration` 生成上述所有变更的迁移脚本。 <br> 2. 在执行前仔细审查脚本，确保无误。 | **关键步骤**: 所有数据库变更必须通过迁移脚本管理。 |

---

## 3. 后端服务层 (Backend Service Layer)

**负责人**: `Backend Team`

| 任务 | 目标文件/模块 | 具体操作 | 备注 |
| :--- | :--- | :--- | :--- |
| **3.1. 实体类重构** | `project.entity.ts`, `project-patient.entity.ts` | 1. 将 `Project` 类重命名为 `ResearchProject`，并更新 `@Entity` 装饰器指向 `research_project` 表。 <br> 2. 在 `ResearchProject` 实体中，将 `status` 属性的类型从 `number` 修改为 `string` 类型，并最好定义一个TS `enum`。 <br> 3. 将 `ProjectPatient` 类重命名为 `ProjectEnrollment`，更新指向 `project_enrollment` 表，并添加 `enrollmentDate`, `status` 等新属性。 | 这是与数据库变更对应的代码调整。 |
| **3.2. 实现档案自动维护** | `clinical_visit.service.ts` 或新建 `subscriber` | 1. 实现核心逻辑：在创建**首个** `ClinicalVisit` 时，自动在 `project_enrollment` 表中插入一条记录。 <br> 2. 建议使用 **TypeORM Subscriber** 或**领域事件 (Domain Event)** 模式，以实现逻辑解耦。 | 这是新架构的核心自动化机制。 |
| **3.3. 实现单位换算服务** | 新建 `unit-conversion.service.ts` | 1. 创建 `UnitConversionService`，提供 `convertToCanonical` 和 `convertFromCanonical` 方法。<br> 2. 实现服务启动时将 `unit_definitions` 表加载到缓存的逻辑。 | 这是单位换算的核心引擎。 |
| **3.4. 新增访视模板模块** | 新建 `visit-template` 模块 | 1. 创建 `VisitTemplate` 实体类。 <br> 2. 创建 `VisitTemplateService` 和 `VisitTemplateController`，提供对访视模板的CRUD管理接口 (项目管理员权限)。 | 需提供API来管理项目的访视计划。 |
| **3.5. 改造观测值模块** | `observation` 模块 | 1. **改造实体**: 更新 `ObservationDefinition` 实体，添加 `shortName`, `canonicalUnitCode` 等字段。 <br> 2. **改造录入逻辑**: 在创建`Observation`的service中，**必须**调用`UnitConversionService`将输入值转换为标准单位再存储。 | 这是确保数据库数据纯净的关键。 |
| **3.6. 改造访视模块** | `clinical_visit` 模块 | 1. 更新 `ClinicalVisit` 实体，使用 `visitTemplateId` 替换 `visitName`。 <br> 2. 修改"创建访视"的 service 和 DTO，使其接受 `visit_template_id` 作为参数。 | 对齐 `clinical_visit` 表的变更。 |
| **3.7. 更新服务逻辑** | 所有依赖旧实体的 `service` 和 `controller` | 1. 全局搜索并替换 `Project` 为 `ResearchProject`，`ProjectPatient` 为 `ProjectEnrollment`。 <br> 2. **重构查询**: 获取项目参与者的逻辑，必须从查询 `clinical_visit` 改为直接查询 `ProjectEnrollment`。 | 确保所有业务逻辑都与新的实体和表对齐。 |

---

## 4. 文档与验证 (Documentation & Verification)

**负责人**: `All`

| 任务 | 目标 | 具体操作 | 备注 |
| :--- | :--- | :--- | :--- |
| **4.1. 确认文档同步** | `database_schema.md` | 1. 本次已更新完毕。 | |
| **4.2. 审查其他文档** | `technical_spec.md`, 等 | 1. 快速审查其他设计文档，确认没有对 `ProjectPatient` 的硬编码引用。 | `technical_spec.md` 目前看来无需修改，因为它更关注CRF字段映射。 |
| **4.3. 编写单元/集成测试** | `*.spec.ts` | 1. 重点为"档案自动维护"逻辑编写测试用例。 <br> 2. 确保所有被修改的API端点都有测试覆盖。 | **质量保证**: 自动化测试是确保重构成功的关键。 |

---
## 5. 部署计划 (Deployment)

1.  **开发环境**: 执行迁移脚本，部署后端服务，开发人员进行初步功能验证。
2.  **测试环境**: 部署并通过QA团队的完整回归测试。
3.  **生产环境**: 在维护窗口期执行数据库迁移，并采用蓝绿部署或滚动更新策略部署新的后端服务。

---
## 6. 科研项目协作平台 - 架构对齐 (Architecture Alignment for Scientific Collaboration Platform)

**负责人**: `Backend Team`

此部分任务旨在将`科研项目协作平台`模块的核心实体主键从 `integer` 迁移至 `uuid`，以实现与系统整体设计风格的统一。

| 任务 | 目标模块/实体 | 具体操作 | 备注 |
| :--- | :--- | :--- | :--- |
| **6.1. 核心实体主键升级** | `project` 模块: `Project`, `ProjectOrganization`, `ProjectMember`, `ProjectPatient` 实体 | 1. 将所有相关实体的 `id` 主键属性类型从 `number` 改为 `string`，并使用 `@PrimaryGeneratedColumn('uuid')`。 <br> 2. 更新所有关联实体中的外键（如 `projectId`）属性，使其类型与新的 `uuid` 主键匹配。 <br> 3. 相应地更新所有相关的 DTO 和 RO 定义。 | 这是核心代码重构步骤。 |
| **6.2. API控制器与服务调整** | `admin-project.controller.ts`, `project.controller.ts`, `project.service.ts` 等 | 1. 检查并修改所有依赖 `id` 的服务层逻辑，确保它们能正确处理 `uuid` 字符串。 <br> 2. 将控制器中用于验证ID的 `ParseIntPipe` 替换为 `ParseUUIDPipe`。 | 确保API接口能正确接收和处理UUID。 |
| **6.3. 数据库迁移脚本** | - | 1. 使用 `TypeORM migration` 生成将主键和外键从 `int` 修改为 `uuid` 的迁移脚本。 <br> 2. **仔细审查脚本**：这种类型的迁移通常很复杂，可能涉及删除旧约束、转换数据、添加新列、再重建约束等步骤。 | **高风险操作**: 必须在开发和测试环境中充分验证迁移脚本。 |
| **6.4. 设计文档同步** | `arch.md`, `prd.md` | 1. 本次已更新完毕。 | 确保所有文档都反映了 `uuid` 主键的最终设计。 | 