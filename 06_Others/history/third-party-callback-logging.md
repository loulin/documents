# 第三方回调日志与监控方案

## 1. 目标

为第三方服务（如：Sibionics）的回调接口提供一套可靠、高效的日志与监控机制。该机制旨在解决以下痛点：

- **问题排查困难**：当第三方数据推送出现问题（如验签失败、数据格式错误）时，缺乏完整的请求上下文信息，导致定位问题耗时耗力。
- **被动响应**：只能在用户反馈或业务大规模异常后才发现问题，缺乏主动发现和预警的能力。
- **缺乏通用性**：针对不同厂商的回调，日志记录逻辑重复开发，增加维护成本。

## 2. 方案选型

我们对比了两种方案：

1.  **自建日志服务**：通过 MongoDB 存储回调日志。
2.  **利用现有APM工具**：通过 Sentry 记录回调事件。

**最终选择：利用 Sentry**。

理由如下：

| 对比维度 | 自建日志 (MongoDB) | 利用 Sentry (推荐) |
| :--- | :--- | :--- |
| **开发成本** | 高：需设计 Schema、开发服务、管理数据库和TTL。 | **低**：仅需编写一个 NestJS 拦截器，复用现有 Sentry 设施。 |
| **功能强度** | 弱：仅支持基本查询。 | **强**：提供高级搜索、聚合分析、仪表盘、Trace关联等强大功能。 |
| **性能影响** | 中：数据库同步写入可能阻塞请求，增加接口延迟。 | **低**：SDK 异步上报，对主流程性能影响极小。 |
| **告警能力** | 无：需额外集成 Grafana 等工具。 | **强**：内置强大的告警引擎，可根据频率、数量等灵活配置规则。 |
| **架构耦合** | 高：业务代码中需显式调用日志服务。 | **低**：通过拦截器/装饰器与业务代码解耦，实现"无侵入式"监控。 |
| **维护成本** | 高：需要维护日志数据库的稳定性、备份和扩容。 | **低**：Sentry 作为SaaS服务，由服务商保障。 |

## 3. 实现方案

我们将通过创建一个可重用的 `CallbackLoggingInterceptor` 和一个 `@LogCallback()` 装饰器来实现。

### 3.1. 创建 `CallbackLoggingInterceptor`

这个拦截器将是实现日志功能的核心。它会：

1.  在请求进入时，从 `request` 对象中提取 `ip`, `headers`, `rawBody`。
2.  **智能提取关键字段**：检查解析后的 `body`，提取 `type` 和 `content` 中的通用业务ID（如 `outpatientId`, `deviceId`, `bizId` 等）作为 Sentry 的 `tags`，用于索引和筛选。
3.  使用 `tap` 操作符来响应流，无论成功或失败，都能执行日志记录逻辑。
4.  在响应成功时，使用 `Sentry.captureMessage` 发送一个 `info` 级别的事件，并附加上下文（包括完整的 `content` 作为 `extra data`）。
5.  在发生错误时，Sentry 的默认异常拦截器会捕获异常，我们只需确保在 `Scope` 中加入了请求上下文，这些信息就会自动附加到异常报告中。

### 3.2. 创建 `@LogCallback()` 装饰器

为了方便地将拦截器应用到需要监控的 Controller 方法上，我们创建一个装饰器。

```typescript
// src/decorators/log-callback.decorator.ts

import { applyDecorators, UseInterceptors } from '@nestjs/common';
import { CallbackLoggingInterceptor } from '../interceptors/callback-logging.interceptor';

export function LogCallback() {
  return applyDecorators(
    UseInterceptors(CallbackLoggingInterceptor),
  );
}
```

### 3.3. 应用到 Controller

在需要记录日志的 Controller 方法上，只需添加 `@LogCallback()` 装饰器即可。

```typescript
// src/modules/sibionics/sibionics-open.controller.ts

import { LogCallback } from 'src/decorators/log-callback.decorator';

// ...

export class SibionicsOpenController {
  
  // ...

  @Post('callback')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'callback for sibionics push service' })
  @LogCallback() // <-- 应用装饰器
  async callback(
    @Body() body: SiCustomerCallbackDto,
    @Headers() headers: CallbackHeaders,
    @Req() req: RawBodyRequest<Request>,
  ) {
    // ... 业务逻辑不变
  }

  @Post('outpatient/callback')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'callback for sibionics outpatient push service' })
  @LogCallback() // <-- 应用装饰器
  async outpatientCallback(
    @Body() body: OutpatientCallbackDto,
    @Headers() headers: CallbackHeaders,
    @Req() req: RawBodyRequest<Request>,
  ) {
    // ... 业务逻辑不变
  }
}
```

### 3.4. Sentry 事件示例

在 Sentry 中，一个成功的回调日志看起来会是这样：

- **Message**: `Sibionics Callback Received - Type: 201`
- **Level**: `info`
- **Tags**:
  - `callback.type`: `201`
  - `callback.source`: `sibionics`
  - `callback.bizId`: `123456789012345678`  // <-- 从 content 中提取的业务ID
- **Extra Data**:
  - `request.ip`: `"123.123.123.123"`
  - `request.headers`: `{ "x-si-signature": "...", ... }`
  - `request.rawBody`: `"{ \"type\": 201, ... }"`
  - `request.parsedBody`: `{ "type": 201, "content": { "outpatientId": "123456789012345678", ... } }`

## 4. 监控与告警

我们建议在 Sentry 中配置以下告警规则，以实现主动监控：

1.  **未知回调类型告警**
    - **规则**: 当日志中出现 "Unhandled ... callback type" 的 `warning` 消息时。
    - **动作**: 立即发送通知到开发团队。
    - **目的**: 第三方可能新增了接口类型，需要我们适配。

2.  **验签失败频率告警**
    - **规则**: 当包含 "verify failed" 的 `error` 事件在 10 分钟内超过 5 次时。
    - **动作**: 发送高优先级告警。
    - **目的**: 可能对方的 `secret` 或签名算法变更，或遭到了恶意攻击。

3.  **接口异常率告警**
    - **规则**: 某一个回调接口（如 `POST /api/open/sibionics/callback`）的错误率超过 5% 时。
    - **动作**: 发送中优先级告警。
    - **目的**: 捕捉普遍性的代码BUG或服务依赖问题。 