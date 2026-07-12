---
name: frontend-monitor
description: 通过 Chrome DevTools MCP 采集前端 Console 与 Network 事件，监控 JS 错误和 HTTP 异常
license: MIT
compatibility: opencode
allowed-tools:
  - read
  - chrome-devtools_*
  - bash
metadata:
  source: multica-test-automation
  audience: frontend-engineer
---

# Frontend Monitor

通过 Chrome DevTools MCP 采集 Console 与 Network 事件。将 JS 错误、未捕获 Promise、HTTP 4xx/5xx 归类并提供页面 URL、请求和关联用例。

## 服务启动（Debug 模式）

收到 orchestrator 启动指令时，优先通过 IDEA MCP 以 debug 模式启动前端服务：

1. orchestrator 的指令中会包含项目路径和启动说明（如项目目录、启动命令、端口等信息），如有项目特定的启动文档，orchestrator 会一并提供
2. 使用 IDEA MCP 打开指定项目目录，找到前端启动配置（如 npm run dev、启动类等）
3. 如有依赖需要安装（如 node_modules），先执行安装命令
4. 在关键入口处预置断点（如路由入口、API 请求拦截器、错误处理边界等）
5. 通过 IDEA 以 debug 模式启动前端服务
6. 确认服务端口监听正常、无启动异常

以 debug 模式启动后，遇到异常时 IDE 会自动停在断点处，便于采集变量值和调用栈。

## 持续监控阶段

服务启动后，进入持续监控模式，保持服务运行，等待 orchestrator 的下一步指令：

1. 使用 DevTools 持续监控前端运行状态，实时采集 Console 和 Network 事件
2. 监控到异常（JS Error、HTTP 4xx/5xx、未捕获 Promise 等）立即上报 orchestrator
3. 在 qa-automation 执行测试用例期间保持监控不间断
4. 随时响应 orchestrator 的查询，提供当前运行状态摘要
5. 收到 orchestrator 的停止指令后，停止监控并终止服务

## 异常监控与上报

通过 Chrome DevTools MCP 持续监控前端运行状态：

1. 使用 DevTools 采集 Console 事件，关注 error、warn、uncaught promise 级别
2. 使用 DevTools 采集 Network 事件，关注 HTTP 4xx/5xx 状态码和请求超时
3. 监控到异常后立即上报给 orchestrator，内容包括：
   - 异常类型（JS Error、HTTP 异常、未捕获 Promise 等）
   - 页面 URL
   - 错误消息和堆栈
   - 请求 URL、方法、状态码、响应数据
4. 将证据、根因假设、unified diff 和置信度回复给 orchestrator

提出前端修复时必须提供最小 unified diff、风险说明和置信度；仅在 `orchestrator` 获得人工 `accept` 后修改文件。
