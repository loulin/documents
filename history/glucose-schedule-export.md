# 血糖数据标签与统计导出功能需求文档

## 需求概述

为传感器血糖数据实现统一的CSV和Excel导出功能。这包括：
1.  **标签分列导出 (CSV)**: 将每个标签的数据分别显示在不同的列中，帮助用户清晰地查看每个血糖数据点属于哪些标签。
2.  **统计数据导出 (Excel)**: 导出与计划相关的详细统计指标。

此功能将由统一的 `ScheduleExportService` 处理。

## 功能需求 - 标签分列导出 (CSV)

### 1. 导出内容
- **血糖数据**：包含时间和血糖值
- **天数标识**：显示相对于传感器开始时间的天数（如D1、D2、D3等）
- **标签覆盖**：显示每个血糖数据点被哪些标签覆盖，每个标签占一列，列名为 "标签-N"，值为实际标签名。

### 2. 文件格式

#### 文件命名
```
{患者ID}-{探头序列号}.csv
```
示例：`12345-ABC123456.csv`

#### CSV结构
| 时间 | 血糖值(mmol/L) | 天数 | 标签-1 | 标签-2 | 标签-3 | ... |
|------|----------------|------|--------|--------|--------|-----|
| 2024-01-15 08:00 | 5.60 | D1 | 早餐名 |        |        |     |
| 2024-01-15 08:15 | 6.20 | D1 | 早餐名 |        |        |     |
| 2024-01-15 09:00 | 7.80 | D1 | 早餐名 | 运动名 |        |     |
| 2024-01-15 10:00 | 6.50 | D1 |        |        |        |     |

#### 列定义
1. **固定列**：
   - `时间`：血糖数据的采集时间（格式：yyyy-MM-dd HH:mm）
   - `血糖值(mmol/L)`：血糖值，保留两位小数
   - `天数`：相对于sensor.startAt所在日期的天数标识（D1, D2, D3...）

2. **动态列**：
   - `标签-N`：根据该传感器实际关联的标签动态生成，列头为 "标签-1", "标签-2", ... "标签-N"。
   - 值内容：如果血糖点在对应顺序的标签时间范围内，显示**实际标签名称**；否则为空。

### 3. 数据处理规则

#### 时间范围匹配
- **一次性标签**：使用具体的开始和结束时间
- **重复标签**：每天应用相同的时间段
- **默认结束时间**：如果标签没有指定结束时间，默认为开始时间+4小时

#### 标签分列处理
- 一个血糖点可能同时属于多个标签，其名称会显示在各自对应的 "标签-N" 列中。
- 标签列的顺序由 `ScheduleService.findAll()` 返回的顺序决定，并映射到 "标签-1", "标签-2" 等。

#### 天数计算
- 以sensor.startAt所在的日期为D1
- 按自然日计算，跨过0点即进入下一天

## 功能需求 - 统计数据导出 (Excel)

(这部分需求保持不变，由 `ScheduleExportService` 的 `exportStats`, `batchExportStats` 等方法处理，参考 `createStatsWorkbook` 的表头结构)

## 技术方案

### 1. 架构设计

#### 统一导出服务
创建/整合为 `ScheduleExportService`，负责所有与计划相关的导出任务。

```typescript
// In ScheduleExportService
async exportGlucoseScheduleColumns(
  patient: Pick<PatientRo, 'id' | 'name'>,
  sensor: Pick<Sensor, 'id' | 'serialNumber' | 'startAt'>,
  organizationId: number, // Added organizationId
  stream: Writable
): Promise<void>

async exportStats(
  patient: Pick<PatientRo, 'id' | 'name' | 'goals'>,
  sensor: Pick<Sensor, 'id' | 'type' | 'endAt' | 'serialNumber'>,
  stream: Writable,
): Promise<void>

async batchExportStats(organizationId: number, startAt: Interval, stream: Writable): Promise<void>
```

#### 复用现有逻辑
- 复用`schedule.stats.ts`中的时间匹配和统计计算逻辑 (`getRefInterval`, `getStats`, `getCountRate`)
- 复用`ScheduleService.findAll()`进行标签查询和优先级处理。

### 2. 实现步骤 (标签分列导出)

#### 第一步：数据获取
1. 获取传感器的所有血糖数据 (`GlucoseService`)
2. 获取适用于该传感器的所有标签 (`ScheduleService.findAll()`)
3. 按时间顺序排列血糖数据

#### 第二步：标签匹配与数据准备
1. 为每个血糖数据点计算所属的天数。
2. 对每个血糖点，遍历通过 `ScheduleService.findAll()` 获取的有序标签列表。
3. 如果血糖点被第 N 个标签覆盖，则在 "标签-N" 列记录该标签的名称。

#### 第三步：CSV生成
1. 动态确定标签列数量 ("标签-1"..."标签-N")。
2. 生成CSV头部（时间、血糖值、天数、标签-1、标签-2...）。
3. 逐行写入血糖数据和对应的标签名称。

### 3. 数据结构 (标签分列导出)

```typescript
interface GlucoseWithSchedules {
  date: Date;
  value: number;
  dayNumber: string; // "D1", "D2", etc.
  // Key: "标签-N", Value: Actual Schedule Name if covered, otherwise undefined/empty
  scheduleColumns: Record<string, string>; 
}

interface ColumnExportData {
  glucoses: GlucoseWithSchedules[];
  scheduleColumnNames: string[]; // ["标签-1", "标签-2", ...]
}
```

### 4. API接口 (保持不变)

Controller 继续使用 `/api/schedules/column-export` 和 `/api/schedules/stats/export` 路径，但内部调用新的 `ScheduleExportService`。

### 5. 文件组织

```
server/src/modules/schedule/
├── schedule-export.service.ts   # 新增/整合：统一的导出服务
├── schedule.controller.ts       # 修改：依赖新的导出服务
├── schedule.service.ts          # 修改：移除导出相关方法
└── schedule.stats.ts            # 复用：时间匹配和统计逻辑
```

## 技术规格确认 (标签分列导出)

### 1. 标签列排序与命名
- 列头为 "标签-1", "标签-2", ... "标签-N"。
- N 是 `ScheduleService.findAll()` 返回的标签总数。
- 每一列 "标签-X" 对应 `findAll` 结果中第 X 个标签。如果血糖点被该标签覆盖，则显示该标签的 `name` 属性。

### 2. 格式规范
- **时间格式**：`yyyy-MM-dd HH:mm`
- **血糖值**：保留两位小数，单位mmol/L
- **空值处理**：如果血糖点未被某 "标签-N" 列对应的标签覆盖，该单元格为空。

### 3. 天数计算
- 以sensor.startAt所在日期为D1
- 按自然日计算，跨过0点进入下一天

### 4. 数据范围
- 导出传感器的所有血糖数据
- 不设置数量限制

## 实施准备

技术规格已确认，可以开始实施开发工作。 