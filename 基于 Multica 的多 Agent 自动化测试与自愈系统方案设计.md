# 基于 Multica 的多 Agent 自动化测试与自愈系统方案设计

---

## 文档版本

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| v1.0 | 2026-07-09 | AI 辅助设计 | 初始版本 |
| v1.1 | 2026-07-09 | AI 辅助设计 | 整合 Debugger 能力、区分主体/拓展功能、明确交付件 |
| v1.2 | 2026-07-09 | AI 辅助设计 | 补充 Loop 闭环控制与可视化设计 |


## 1. 概述

### 1.1 项目背景

在软件持续交付过程中，自动化测试用例的执行、异常发现、根因定位及修复往往需要大量人工介入。为解决此痛点，本项目设计一套**基于多 Agent 协作的自动化测试与自愈系统**，通过 Agent 技术实现测试执行、实时监控、智能诊断与自动修复的**闭环循环**。

### 1.2 设计目标

| 目标 | 说明 |
|------|------|
| **自动化测试执行** | 无人工干预地运行端到端测试用例 |
| **实时监控** | 同时监控后端服务、前端页面及浏览器运行状态，捕获异常 |
| **智能诊断** | 聚合多源异常信息，快速定位问题根因（前端/后端/环境/测试脚本） |
| **自动修复** | 针对常见问题（空指针、SQL错误、元素定位失效等）自动生成修复方案并验证 |
| **自愈闭环（Loop）** | 修复后自动重启服务并重跑失败用例，循环往复直到全部通过或达到阈值 |
| **可视化** | 实时展示用例执行状态、异常检测、修复过程和最终结果 |
| **轻量化部署** | 最小化外部依赖，适应 Windows 开发环境，零侵入现有代码 |

### 1.3 核心概念：Loop（自愈循环）

本方案的核心是 **Loop（循环）** 机制：

> **触发条件** → **侦查分析** → **修复代码** → **重启服务** → **重跑用例** → **验证结果** → （若失败则继续循环） → **全部通过则退出**

这个 Loop 是系统自动运行的，直到：
- ✅ **成功退出**：所有测试用例全部通过
- ❌ **失败退出**：达到最大循环次数（如 3 次）或修复置信度低于阈值，转人工介入

### 1.4 适用场景

- 微服务架构下的集成测试与回归测试
- 前端 UI 自动化测试（基于 Playwright）
- 开发自测阶段的问题快速响应
- CI/CD 流水线中的质量门禁（可扩展）


## 2. 整体架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Multica 主 Agent（Orchestrator）                   │
│  【主体功能】                                                                   │
│  - 测试用例编排与调度（通过 Issue 分配）                                        │
│  - Loop 控制器（循环检测、重试计数、退出条件判断）                              │
│  - 异常汇总与根因分析（基于 LLM）                                               │
│  - 修复决策与分发                                                               │
│  - 服务重启与用例重跑控制                                                       │
│  - 报告生成                                                                     │
│  【拓展功能】                                                                   │
│  - 修复 PR 自动创建与审核流程管理                                               │
│  - 历史修复案例学习与复用                                                       │
│  - 多测试套件并行调度                                                           │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                       Multica 内置通信（Issue + Comment 机制）
                                      │
       ┌──────────────────────────────┼──────────────────────────────┐
       │                              │                              │
       ▼                              ▼                              ▼
┌───────────────────┐   ┌─────────────────────┐   ┌─────────────────────────┐
│ 后端监控与修复    │   │ 前端监控与修复      │   │ 浏览器自动化与测试      │
│      Agent        │   │      Agent          │   │       Agent             │
│                   │   │                     │   │                         │
│ 【主体功能】      │   │ 【主体功能】        │   │ 【主体功能】            │
│ - 启动/调试后端   │   │ - 启动/调试前端     │   │ - 执行 Playwright 用例  │
│ - 扫描日志文件    │   │ - 监控 Chrome       │   │ - 捕获元素定位异常      │
│ - 分析异常堆栈    │   │   Console/Network   │   │ - 自愈选择器            │
│ - 生成代码修复    │   │ - 分析 JS 错误      │   │ - 上报执行结果          │
│ - 重启 Windows    │   │ - 生成前端修复      │   │                         │
│   服务/进程       │   │ - 重启前端服务      │   │                         │
│                   │   │                     │   │                         │
│ 【拓展功能】      │   │ 【拓展功能】        │   │ 【拓展功能】            │
│ - 条件断点侦查    │   │ - 热更新验证        │   │ - 多浏览器兼容测试      │
│ - 变量值深度检查  │   │ - Source Map 解析   │   │ - 性能指标采集          │
│ - 表达式执行验证  │   │ - 异步错误追踪      │   │ - 截图差异比对          │
│ - 调用栈逐层分析  │   │                     │   │                         │
└───────────────────┘   └─────────────────────┘   └─────────────────────────┘
       │                              │                              │
       │                              │                              │
  ┌────▼────┐                   ┌─────▼─────┐                  ┌─────▼─────┐
  │ JetBrains│                   │ Chrome    │                  │ Playwright │
  │ MCP      │                   │ DevTools  │                  │ MCP        │
  │ Server   │                   │ MCP       │                  │            │
  │(含Debug) │                   │           │                  │            │
  └──────────┘                   └───────────┘                  └────────────┘
```

### 2.2 核心流程：Loop 闭环

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             Loop 自愈循环控制                                    │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │                     主 Loop 控制器 (Orchestrator)                         │  │
│   │                                                                          │  │
│   │  loop_count = 0                                                          │  │
│   │  max_retries = 3                                                         │  │
│   │  failed_tests = 全部测试用例                                              │  │
│   │                                                                          │  │
│   │  while (failed_tests不为空 and loop_count < max_retries):                │  │
│   │      loop_count += 1                                                     │  │
│   │                                                                          │  │
│   │      ┌─────────────────────────────────────────────────────────────┐     │  │
│   │      │ 1. 执行阶段 (Execution Phase)                              │     │  │
│   │      │    - 浏览器 Agent 执行所有 failed_tests                    │     │  │
│   │      │    - 后端/前端 Agent 持续监控日志                          │     │  │
│   │      │    - 实时更新可视化面板                                    │     │  │
│   │      └─────────────────────────────────────────────────────────────┘     │  │
│   │                              │                                            │  │
│   │                              ▼                                            │  │
│   │      ┌─────────────────────────────────────────────────────────────┐     │  │
│   │      │ 2. 检测阶段 (Detection Phase)                              │     │  │
│   │      │    - 汇总所有 Agent 上报的异常                             │     │  │
│   │      │    - 区分：无异常 → passed；有异常 → failed                │     │  │
│   │      └─────────────────────────────────────────────────────────────┘     │  │
│   │                              │                                            │  │
│   │                              ▼                                            │  │
│   │      ┌─────────────────────────────────────────────────────────────┐     │  │
│   │      │ 3. 判断阶段 (Decision Phase)                               │     │  │
│   │      │    - 全部通过？→ ✅ 退出 Loop，生成报告                    │     │  │
│   │      │    - 有异常且 loop_count >= max_retries？→ ❌ 退出，人工介入│     │  │
│   │      │    - 有异常且 loop_count < max_retries？→ 进入修复阶段    │     │  │
│   │      └─────────────────────────────────────────────────────────────┘     │  │
│   │                              │                                            │  │
│   │                              ▼                                            │  │
│   │      ┌─────────────────────────────────────────────────────────────┐     │  │
│   │      │ 4. 修复阶段 (Fix Phase)                                    │     │  │
│   │      │    - 根因分析（LLM 综合多源异常）                          │     │  │
│   │      │    - 选择修复 Agent（后端/前端/选择器）                    │     │  │
│   │      │    - 执行修复（修改代码/配置/选择器）                      │     │  │
│   │      │    - 记录修复内容和置信度                                  │     │  │
│   │      └─────────────────────────────────────────────────────────────┘     │  │
│   │                              │                                            │  │
│   │                              ▼                                            │  │
│   │      ┌─────────────────────────────────────────────────────────────┐     │  │
│   │      │ 5. 重启阶段 (Restart Phase)                                │     │  │
│   │      │    - 后端 Agent 重启服务（sc restart / taskkill + start）  │     │  │
│   │      │    - 前端 Agent 重启前端服务                               │     │  │
│   │      │    - 等待服务健康检查通过                                  │     │  │
│   │      └─────────────────────────────────────────────────────────────┘     │  │
│   │                              │                                            │  │
│   │                              ▼                                            │  │
│   │      （回到执行阶段，继续下一轮循环）                                     │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│   退出条件：                                                                     │
│   ✅ 全部测试用例通过 → 生成成功报告，通知开发者                                 │
│   ❌ 达到最大重试次数仍失败 → 生成失败报告，标记人工介入                         │
│   ⚠️ 修复置信度低于阈值 → 暂停循环，请求人工确认                                │
└──────────────────────────────────────────────────────────────────────────────────┘
```


## 3. Loop 控制器详细设计

### 3.1 状态管理

Loop 控制器需要维护以下状态：

| 状态变量 | 类型 | 说明 |
|----------|------|------|
| `loop_count` | int | 当前循环次数（从 1 开始） |
| `max_retries` | int | 最大循环次数（默认 3） |
| `failed_tests` | List[Test] | 当前本轮需要执行的失败用例列表 |
| `all_tests` | List[Test] | 全部测试用例列表 |
| `passed_tests` | List[Test] | 已通过的测试用例 |
| `anomalies` | List[Anomaly] | 当前轮检测到的所有异常 |
| `fix_records` | List[FixRecord] | 所有修复记录（用于报告） |
| `exit_reason` | str | 退出原因（`ALL_PASSED` / `MAX_RETRIES` / `LOW_CONFIDENCE`） |
| `status` | str | 当前状态（`RUNNING` / `PASSED` / `FAILED` / `WAITING_APPROVAL`） |

### 3.2 Loop 控制器伪代码

```python
# skills/orchestrator/scripts/loop_controller.py

class LoopController:
    def __init__(self, test_suite, max_retries=3, confidence_threshold=0.6):
        self.max_retries = max_retries
        self.confidence_threshold = confidence_threshold
        self.loop_count = 0
        self.failed_tests = test_suite
        self.passed_tests = []
        self.fix_records = []
        self.status = "RUNNING"
        self.exit_reason = None
        
        # Agent 引用
        self.browser_agent = None
        self.backend_agent = None
        self.frontend_agent = None
        
        # 可视化回调
        self.visualization_callback = None
    
    def run(self):
        """主循环入口"""
        while self.failed_tests and self.loop_count < self.max_retries:
            self.loop_count += 1
            self._update_visualization("loop_start", {
                "loop": self.loop_count,
                "failed_count": len(self.failed_tests),
                "passed_count": len(self.passed_tests)
            })
            
            # === Phase 1: 执行 ===
            execution_results = self._execute_tests(self.failed_tests)
            self._update_visualization("execution_done", execution_results)
            
            # === Phase 2: 检测 ===
            anomalies = self._collect_anomalies()
            self._update_visualization("detection_done", anomalies)
            
            # === Phase 3: 判断 ===
            if not anomalies:
                # 本轮所有用例通过
                self.passed_tests.extend(self.failed_tests)
                self.failed_tests = []
                self.status = "PASSED"
                self.exit_reason = "ALL_PASSED"
                self._update_visualization("all_passed", {"loop": self.loop_count})
                break
            
            # 检查是否达到最大重试次数
            if self.loop_count >= self.max_retries:
                self.status = "FAILED"
                self.exit_reason = "MAX_RETRIES"
                self._update_visualization("max_retries_reached", {
                    "remaining_failed": len(self.failed_tests),
                    "anomalies": anomalies
                })
                break
            
            # === Phase 4: 修复 ===
            fix_results = self._fix_anomalies(anomalies)
            self.fix_records.extend(fix_results)
            self._update_visualization("fix_done", fix_results)
            
            # 检查修复置信度
            low_confidence_fixes = [f for f in fix_results if f.confidence < self.confidence_threshold]
            if low_confidence_fixes:
                self.status = "WAITING_APPROVAL"
                self.exit_reason = "LOW_CONFIDENCE"
                self._update_visualization("waiting_approval", low_confidence_fixes)
                # 暂停等待人工确认（可通过 Multica Comment 通知）
                self._wait_for_approval(low_confidence_fixes)
                if not self._is_approved():
                    break
            
            # === Phase 5: 重启 ===
            self._restart_services()
            self._update_visualization("restart_done", {"service": "backend+frontend"})
            
            # 继续下一轮循环（回到 Phase 1）
        
        # 生成最终报告
        self._generate_report()
        self._update_visualization("finished", {
            "status": self.status,
            "exit_reason": self.exit_reason,
            "total_loops": self.loop_count,
            "passed_count": len(self.passed_tests),
            "failed_count": len(self.failed_tests),
            "fix_records": self.fix_records
        })
        
        return self._get_final_result()
    
    def _execute_tests(self, tests):
        """调用浏览器 Agent 执行测试用例"""
        results = []
        for test in tests:
            result = self.browser_agent.execute(test)
            results.append(result)
            self._update_visualization("test_executed", {
                "test_id": test.id,
                "result": result.status,
                "duration": result.duration,
                "loop": self.loop_count
            })
        return results
    
    def _collect_anomalies(self):
        """收集所有子 Agent 上报的异常"""
        anomalies = []
        # 后端 Agent 上报的日志异常
        backend_anomalies = self.backend_agent.get_anomalies()
        anomalies.extend(backend_anomalies)
        
        # 前端 Agent 上报的浏览器异常
        frontend_anomalies = self.frontend_agent.get_anomalies()
        anomalies.extend(frontend_anomalies)
        
        # 浏览器 Agent 上报的测试失败
        browser_anomalies = self.browser_agent.get_failures()
        anomalies.extend(browser_anomalies)
        
        return anomalies
    
    def _fix_anomalies(self, anomalies):
        """根因分析并执行修复"""
        # 1. 根因分析
        root_cause = self._analyze_root_cause(anomalies)
        
        # 2. 选择修复 Agent
        fix_agent = self._select_fix_agent(root_cause)
        
        # 3. 执行修复
        fix_result = fix_agent.fix(root_cause)
        
        # 4. 记录修复
        return [fix_result]
    
    def _restart_services(self):
        """重启后端和前端服务"""
        self.backend_agent.restart_service()
        self.frontend_agent.restart_service()
        # 等待服务健康检查
        self._wait_for_health_check()
```

### 3.3 退出条件详细定义

| 退出原因 | 条件 | 行为 |
|----------|------|------|
| `ALL_PASSED` | 所有测试用例通过 | ✅ 成功退出，生成通过报告 |
| `MAX_RETRIES` | 达到最大重试次数仍有失败用例 | ❌ 失败退出，生成失败报告，标记人工介入 |
| `LOW_CONFIDENCE` | 修复方案置信度低于阈值 | ⚠️ 暂停循环，请求人工确认后继续或退出 |
| `MANUAL_STOP` | 人工主动停止 | ⏹️ 正常停止，生成当前状态报告 |


## 4. 可视化设计

### 4.1 可视化整体布局

采用 **Multica Web UI + 自定义 Dashboard** 的方式实现可视化：

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  🧪 自动化测试自愈系统 - Dashboard                                              │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  测试总览     │  │  循环次数    │  │  通过率      │  │  当前状态    │        │
│  │  ✅ 45 通过   │  │  🔄 3 次    │  │  ████████░░  │  │  🟢 运行中   │        │
│  │  ❌ 5 失败    │  │  📊 第 2 轮  │  │  90%        │  │  🔄 Loop #2  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  实时执行日志 (Live Logs)                                                   │ │
│  │  ┌────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ [10:23:45] 🟢 后端 Agent: 服务启动成功，端口 8080                      │ │ │
│  │  │ [10:23:47] 🔵 浏览器 Agent: 执行用例 #23 - 用户登录                    │ │ │
│  │  │ [10:23:52] 🔵 浏览器 Agent: 用例 #23 执行中...                         │ │ │
│  │  │ [10:23:55] 🔴 后端 Agent: 检测到 NullPointerException                   │ │ │
│  │  │ [10:23:55] 🟡 后端 Agent: 正在使用 Debugger 侦查...                    │ │ │
│  │  │ [10:23:58] 🟢 后端 Agent: 已生成修复方案 (置信度 85%)                  │ │ │
│  │  │ [10:24:00] 🔄 主 Agent: 应用修复，重启服务...                          │ │ │
│  │  │ [10:24:05] 🔵 浏览器 Agent: 重新执行用例 #23...                        │ │ │
│  │  │ [10:24:10] 🟢 浏览器 Agent: 用例 #23 通过！ ✅                         │ │ │
│  │  └────────────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  ┌─────────────────────────────┐  ┌────────────────────────────────────────────┐ │
│  │  测试用例状态 (按执行轮次)   │  │  异常与修复统计                           │ │
│  │                              │  │                                            │ │
│  │  Round 1  ████████░░ 8/10   │  │  🔴 NPE          ████░░ 4 次  ✅ 已修复  │ │
│  │  Round 2  █████████░ 9/10   │  │  🟡 SQLException ██░░░░ 2 次  ✅ 已修复  │ │
│  │  Round 3  ██████████ 10/10  │  │  🔵 选择器失效   ███░░░ 3 次  ✅ 已修复  │ │
│  └─────────────────────────────┘  └────────────────────────────────────────────┘ │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  修复历史                                                                    │ │
│  │  ┌──────┬──────────────┬────────────────────────┬──────────┬───────────────┐│ │
│  │  │ 轮次  │ 异常类型      │ 修复内容               │ 置信度   │ 状态          ││ │
│  │  ├──────┼──────────────┼────────────────────────┼──────────┼───────────────┤│ │
│  │  │ #1    │ NPE          │ UserService.java +23   │ 85%      │ ✅ 验证通过   ││ │
│  │  │ #2    │ 选择器失效   │ login-btn → #loginBtn  │ 92%      │ ✅ 验证通过   ││ │
│  │  │ #3    │ SQLException │ OrderMapper.xml L12    │ 78%      │ ⏳ 待审核     ││ │
│  │  └──────┴──────────────┴────────────────────────┴──────────┴───────────────┘│ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  [▶ 运行]  [⏹ 停止]  [📊 导出报告]  [⚙️ 设置]                                 │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 可视化实现方式

#### 4.2.1 方案选择

| 方案 | 说明 | 适用场景 |
|------|------|----------|
| **Multica 原生 UI** | 利用 Multica 的 Web Dashboard 查看 Agent 状态和 Issue 进展 | 基础监控，无需额外开发 |
| **MCP + Visualizer** | 使用 `@modelcontextprotocol/visualizer` 或 `mcp-visualizer` 工具实时展示 | 需要实时日志流和 Agent 协作可视化 |
| **自定义 Dashboard** | 自建 Web 服务，通过 Multica API 获取数据渲染 | 定制化需求高，需要完整控制 |
| **日志 + Markdown 报告** | 循环过程中生成 Markdown 报告，通过 Multica Comment 推送 | 轻量级方案，无额外依赖 |

#### 4.2.2 推荐方案（分层）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  可视化分层架构                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Layer 1: Multica 原生 UI（基础信息）                                       │
│  - Agent 在线状态                                                           │
│  - Issue 列表与状态                                                         │
│  - 执行日志摘要                                                             │
│                                                                             │
│  Layer 2: MCP Visualizer（实时流）                                          │
│  - Agent 间通信可视化                                                       │
│  - 工具调用链路追踪                                                         │
│  - 实时事件流                                                               │
│                                                                             │
│  Layer 3: 自定义 Dashboard（核心监控）                                      │
│  - Loop 状态总览（当前轮次、通过率）                                        │
│  - 测试用例执行详情（逐个用例状态）                                         │
│  - 异常与修复历史                                                           │
│  - 置信度与风险提示                                                         │
│                                                                             │
│  Layer 4: 报告生成（最终交付）                                              │
│  - Markdown 报告（通过 Multica Comment 推送）                               │
│  - HTML 报告（可下载）                                                      │
│  - JSON 数据（供 CI/CD 集成）                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 4.2.3 轻量化实现方式（推荐）

采用 **Multica Comment + 结构化 Markdown 报告** 的方式，最小化依赖：

1. **实时状态推送**：Loop 控制器在每个阶段结束时，通过 Multica Comment 更新状态
2. **可视化 HTML 报告**：在循环结束后生成完整的 HTML 报告，包含图表和统计数据
3. **无需额外服务**：所有可视化内容都在 Multica 环境中展示

```python
# skills/orchestrator/scripts/visualizer.py

class Visualizer:
    def __init__(self, multica_client):
        self.multica = multica_client
        self.dashboard_issue_id = None
    
    def update_status(self, phase, data):
        """通过 Multica Comment 更新状态"""
        markdown = self._render_status(phase, data)
        self.multica.create_comment(
            issue_id=self.dashboard_issue_id,
            content=markdown,
            update_dashboard=True
        )
    
    def render_dashboard(self, loop_state):
        """生成结构化 Markdown Dashboard"""
        md = f"""
# 🧪 自动化测试自愈系统 - 实时状态

## 📊 总览
| 指标 | 值 |
|------|-----|
| 当前循环 | 第 {loop_state.loop_count}/{loop_state.max_retries} 轮 |
| 测试通过 | {len(loop_state.passed_tests)}/{len(loop_state.all_tests)} |
| 通过率 | {loop_state.pass_rate:.1%} |
| 当前状态 | {loop_state.status_emoji} {loop_state.status_text} |

## 🔄 测试用例状态
| 用例 ID | 名称 | 状态 | 耗时 |
|---------|------|------|------|
"""
        for test in loop_state.test_results:
            md += f"| {test.id} | {test.name} | {test.status_icon} | {test.duration}ms |\n"
        
        return md
```

### 4.3 实时更新的事件类型

| 事件类型 | 触发时机 | 可视化内容 |
|----------|----------|------------|
| `loop_start` | 每轮循环开始 | 当前轮次、待执行用例数 |
| `test_start` | 单个用例开始执行 | 用例名称、预计耗时 |
| `test_pass` | 用例执行通过 | 用例名称、耗时 |
| `test_fail` | 用例执行失败 | 用例名称、失败原因 |
| `anomaly_detected` | 检测到异常 | 异常类型、来源 Agent |
| `debugger_investigating` | Debugger 侦查中 | 侦查的文件和行号 |
| `fix_generated` | 修复方案生成 | 修复内容、置信度 |
| `fix_applied` | 修复应用完成 | 修改的文件列表 |
| `service_restarting` | 服务重启中 | 服务名称 |
| `service_healthy` | 服务健康检查通过 | 服务名称 |
| `loop_end` | 循环结束 | 本轮通过/失败统计 |
| `all_passed` | 全部通过 | 总耗时、修复次数 |
| `failed` | 最终失败 | 失败原因、剩余失败用例 |


## 5. 功能划分

### 5.1 主体功能（MVP 必需）

#### 5.1.1 测试执行与监控

| 功能 | 描述 | 实现方式 |
|------|------|----------|
| 后端服务控制 | 以 Debug 模式启动/停止/重启 Java 后端服务 | JetBrains MCP `debug_run` / Windows `sc`/`taskkill` |
| 后端日志监控 | 零侵入式实时扫描服务日志文件，捕获异常栈 | PowerShell `Get-Content -Wait` / Python 文件读取 |
| 前端服务控制 | 以 Debug 模式启动/停止/重启前端服务 | npm scripts + Chrome 远程调试端口 |
| 前端日志监控 | 通过 Chrome DevTools 协议获取 Console 和 Network 数据 | Chrome DevTools MCP `console_logs` / `network_requests` |
| 浏览器自动化 | 使用 Playwright 执行 UI 测试用例 | Playwright MCP `browser_click`/`browser_fill`/`browser_snapshot` |

#### 5.1.2 异常检测与上报

| 功能 | 描述 | 实现方式 |
|------|------|----------|
| 后端异常检测 | 识别日志中的 Exception、Error、FATAL 等关键词 | 正则匹配 + 异常类型分类 |
| 前端异常检测 | 识别浏览器 Console 中的 JS 错误、未捕获 Promise | Chrome DevTools MCP 实时监控 |
| 网络异常检测 | 识别 API 请求 4xx/5xx 状态码 | Chrome DevTools MCP `network_requests` |
| 测试失败检测 | 识别 Playwright 执行中的元素定位失败、断言失败 | Playwright MCP 执行结果解析 |
| 异常上报 | 格式化异常信息（时间、堆栈、上下文）上报主 Agent | Multica Comment/Issue 机制 |

#### 5.1.3 根因分析与修复

| 功能 | 描述 | 实现方式 |
|------|------|----------|
| 异常聚合 | 汇总多个 Agent 上报的异常，去重、关联 | 主 Agent 逻辑 |
| 根因分析 | 调用 LLM 综合多源异常信息，定位根本原因 | LLM API（OpenAI/Claude） |
| 后端代码修复 | 针对 Java 代码生成修复补丁（判空、SQL 修正等） | JetBrains MCP `edit_file` |
| 前端代码修复 | 针对 JS/TS/Vue 代码生成修复补丁 | 文件编辑 + 热更新 |
| 选择器自愈 | 修复断裂的元素定位器 | LLM + 页面快照分析 |

#### 5.1.4 Loop 闭环控制

| 功能 | 描述 | 实现方式 |
|------|------|----------|
| 循环计数器 | 记录当前循环轮次，控制最大重试次数 | LoopController 状态管理 |
| 退出条件判断 | 全部通过 / 达到最大轮次 / 置信度低 | 条件逻辑 |
| 状态管理 | 维护 passed/failed 列表、修复历史 | 内存状态 + Multica Issue |
| 服务重启 | 修复后重启服务准备下一轮 | Windows `sc`/`taskkill` + health check |

#### 5.1.5 可视化与报告

| 功能 | 描述 | 实现方式 |
|------|------|----------|
| 实时状态展示 | 展示当前循环、通过率、用例状态 | Multica Comment + Markdown |
| 执行日志流 | 展示 Agent 执行日志 | Multica 实时日志 |
| 修复历史展示 | 展示所有修复记录 | 结构化 Markdown 表格 |
| 最终报告生成 | 生成完整测试报告（含修复详情） | Markdown/HTML 生成 |

### 5.2 拓展功能（增强与优化）

#### 5.2.1 Debugger 深度侦查能力

| 功能 | 描述 | 触发场景 |
|------|------|----------|
| **异常断点设置** | 在异常抛出行自动设置断点，重现问题时精确捕获现场 | 检测到 `NullPointerException` / `SQLException` 等 |
| **变量值深度检查** | 断点暂停时读取所有相关变量的值、对象字段 | 需要确认异常时的精确状态 |
| **表达式执行验证** | 在调试上下文中执行任意代码片段验证假设 | 需要测试修复方案或确认变量状态 |
| **调用栈逐层分析** | 获取完整调用栈，在不同栈帧间切换查看上下文 | 需要追溯异常根源（如依赖注入失败） |
| **条件断点** | 设置仅当特定条件成立时才暂停的断点 | 偶发问题（如并发竞争、特定数据触发） |
| **附加调试** | 连接到已运行的 Java 进程（无需重启） | 生产环境问题排查、长时间运行的服务 |
| **单步执行** | Step Over/Into/Out，逐步追踪业务逻辑 | 复杂计算逻辑错误（如金额计算偏差） |

#### 5.2.2 高级修复能力

| 功能 | 描述 |
|------|------|
| **修复 PR 自动创建** | 修复完成后自动创建 Pull Request，等待人工审核 |
| **修复置信度评分** | 对生成的修复方案进行置信度评估，低于阈值时标记需人工介入 |
| **历史案例学习** | 记录历史修复案例，用于优化 LLM 提示词 |
| **多版本兼容修复** | 针对不同 Java/框架版本生成不同修复方案 |

#### 5.2.3 测试增强

| 功能 | 描述 |
|------|------|
| **多浏览器兼容测试** | 同时运行 Chrome/Firefox/Edge 测试 |
| **性能指标采集** | 采集页面加载时间、API 响应时间等指标 |
| **截图差异比对** | 对 UI 变化进行视觉回归测试 |


## 6. 各阶段交付件

### 6.1 Phase 1：环境准备与基础验证（1-2 天）

**目标**：搭建 Multica 环境和 MCP 工具链

| 交付件 | 类型 | 说明 |
|--------|------|------|
| `docs/environment-setup.md` | 文档 | Windows 环境配置指南 |
| `scripts/install-multica.ps1` | PowerShell | Multica 一键安装脚本 |
| `scripts/verify-mcp.ps1` | PowerShell | 验证三个 MCP Server 是否正常 |
| `config/mcp-servers.json` | 配置文件 | 三个 MCP Server 的配置 |

### 6.2 Phase 2：核心 Skill 开发（3-5 天）

#### 6.2.1 后端监控 Skill

| 交付件 | 类型 | 说明 |
|--------|------|------|
| `skills/backend-monitor/SKILL.md` | Markdown | Skill 主指令集 |
| `skills/backend-monitor/scripts/scan_logs.py` | Python | 日志扫描脚本 |
| `skills/backend-monitor/scripts/service_control.ps1` | PowerShell | Windows 服务/进程控制 |
| `skills/backend-monitor/scripts/debugger_helper.py` | Python | Debugger 辅助函数 |
| `skills/backend-monitor/config/patterns.yaml` | YAML | 异常关键词配置 |

#### 6.2.2 前端监控 Skill

| 交付件 | 类型 | 说明 |
|--------|------|------|
| `skills/frontend-monitor/SKILL.md` | Markdown | Skill 主指令集 |
| `skills/frontend-monitor/scripts/chrome_helper.py` | Python | Chrome DevTools MCP 调用封装 |
| `skills/frontend-monitor/scripts/frontend_control.ps1` | PowerShell | 前端服务启动/停止 |

#### 6.2.3 浏览器自动化 Skill

| 交付件 | 类型 | 说明 |
|--------|------|------|
| `skills/browser-automation/SKILL.md` | Markdown | Skill 主指令集 |
| `skills/browser-automation/scripts/playwright_helper.py` | Python | Playwright MCP 调用封装 |
| `skills/browser-automation/scripts/selector_healer.py` | Python | 选择器自愈逻辑 |
| `skills/browser-automation/test-cases/` | 目录 | 示例测试用例（JSON/YAML） |

### 6.3 Phase 3：Loop 与可视化开发（3-5 天）

| 交付件 | 类型 | 说明 |
|--------|------|------|
| `skills/orchestrator/SKILL.md` | Markdown | 主 Agent Skill 主指令集 |
| `skills/orchestrator/scripts/loop_controller.py` | Python | Loop 循环控制器核心逻辑 |
| `skills/orchestrator/scripts/anomaly_aggregator.py` | Python | 异常聚合与去重 |
| `skills/orchestrator/scripts/root_cause_analyzer.py` | Python | 根因分析（调用 LLM） |
| `skills/orchestrator/scripts/fix_dispatcher.py` | Python | 修复任务分发 |
| `skills/orchestrator/scripts/visualizer.py` | Python | 可视化状态渲染（Markdown Dashboard） |
| `skills/orchestrator/scripts/report_generator.py` | Python | 最终报告生成 |
| `skills/orchestrator/config/prompts.yaml` | YAML | LLM 提示词模板 |

### 6.4 Phase 4：端到端集成与测试（3-5 天）

| 交付件 | 类型 | 说明 |
|--------|------|------|
| `multica-workspace.yaml` | YAML | Multica Workspace 完整配置 |
| `scripts/deploy-workspace.ps1` | PowerShell | 一键部署到 Multica |
| `test-scenarios/` | 目录 | 端到端测试场景 |
| `docs/troubleshooting.md` | 文档 | 问题排查指南 |


## 7. Debugger 能力在框架中的具体应用场景

### 7.1 场景一：空指针异常（NullPointerException）精准定位

| 步骤 | 操作 | 使用的 Debugger 功能 |
|------|------|---------------------|
| 1 | 日志扫描发现 NPE | `scan_logs.py` 正则匹配 |
| 2 | 设置异常断点 | `set_exception_breakpoint` |
| 3 | 重现测试，断点触发 | 自动等待断点 |
| 4 | 读取变量值 | `get_variables` |
| 5 | 执行表达式验证假设 | `evaluate_expression` |
| 6 | 切换栈帧追溯 | `get_stack_frames` |
| 7 | 生成修复方案 | LLM 分析 + 代码模板 |
| 8 | 应用修复并验证 | `edit_file` + 重新断点检查 |

### 7.2 场景二：复杂业务逻辑错误（如金额计算偏差）

| 步骤 | 操作 | 使用的 Debugger 功能 |
|------|------|---------------------|
| 1 | 测试断言失败，无报错日志 | 测试失败检测 |
| 2 | 在计算方法入口设置断点 | `set_breakpoint` |
| 3 | 单步执行跟踪 | `step_over` / `step_into` |
| 4 | 检查每一步的中间值 | `get_variables` + `evaluate_expression` |
| 5 | 发现折扣率计算错误 | 变量值对比 |
| 6 | 定位到 `getDiscountRate()` 方法 | 栈帧切换 |
| 7 | 生成修复方案 | 修改计算方法或 SQL |
| 8 | 验证修复 | 再次单步执行确认 |

### 7.3 场景三：并发竞争条件（偶现 bug）

| 步骤 | 操作 | 使用的 Debugger 功能 |
|------|------|---------------------|
| 1 | 测试偶发失败 | 循环中多次出现 |
| 2 | 设置条件断点 | `set_conditional_breakpoint` |
| 3 | 附加到运行进程 | `attach_debugger` |
| 4 | 断点触发，检查所有线程 | `get_threads` |
| 5 | 分析锁顺序 | 栈帧检查 |
| 6 | 生成修复方案 | 建议使用 ConcurrentHashMap |
| 7 | 验证修复 | 多次循环测试确认 |

### 7.4 Debugger 能力与日志监控的互补关系

| 维度 | 日志监控 | Debugger 监控 |
|------|----------|---------------|
| **信息类型** | 被动输出的文本行 | 任意时刻的完整内存状态 |
| **触发时机** | 异常发生后，事后分析 | 异常发生时实时介入 |
| **粒度** | 粗粒度，需提前埋点 | 细粒度，可探查任意代码行 |
| **交互性** | 静态查看 | 动态执行表达式、修改变量、控制执行流 |
| **适用场景** | 稳定状态监控、低频错误预警 | 深度调试、复杂逻辑、偶发问题、修复验证 |


## 8. Multica 中的部署形态

### 8.1 整体交付物结构

```
multica-test-automation/
├── README.md                               # 项目说明
├── docs/
│   ├── architecture.md                     # 架构设计文档
│   ├── environment-setup.md                # 环境配置指南
│   ├── debugger-scenarios.md               # Debugger 使用场景
│   ├── troubleshooting.md                  # 问题排查指南
│   └── loop-visualization.md               # Loop 与可视化说明
├── skills/                                 # Multica Skills
│   ├── orchestrator/
│   │   ├── SKILL.md
│   │   ├── config/
│   │   │   ├── prompts.yaml
│   │   │   └── test-suites.yaml
│   │   └── scripts/
│   │       ├── loop_controller.py
│   │       ├── anomaly_aggregator.py
│   │       ├── root_cause_analyzer.py
│   │       ├── fix_dispatcher.py
│   │       ├── visualizer.py
│   │       └── report_generator.py
│   ├── backend-monitor/
│   │   ├── SKILL.md
│   │   ├── config/
│   │   │   ├── patterns.yaml
│   │   │   └── debugger_rules.yaml
│   │   └── scripts/
│   │       ├── scan_logs.py
│   │       ├── service_control.ps1
│   │       └── debugger_helper.py
│   ├── frontend-monitor/
│   │   ├── SKILL.md
│   │   ├── config/
│   │   │   └── chrome-config.yaml
│   │   └── scripts/
│   │       ├── chrome_helper.py
│   │       └── frontend_control.ps1
│   └── browser-automation/
│       ├── SKILL.md
│       ├── test-cases/
│       └── scripts/
│           ├── playwright_helper.py
│           └── selector_healer.py
├── scripts/
│   ├── install-multica.ps1
│   ├── verify-mcp.ps1
│   └── deploy-workspace.ps1
├── config/
│   └── mcp-servers.json
└── multica-workspace.yaml
```

### 8.2 在 Multica 中创建 Agent

| Agent 名称 | 角色 | 关联 Skill | MCP 配置 |
|------------|------|------------|----------|
| `orchestrator` | 主控 Agent（含 Loop 控制） | `orchestrator` | 无 |
| `backend-engineer` | 后端监控与修复 | `backend-monitor` | JetBrains MCP |
| `frontend-engineer` | 前端监控与修复 | `frontend-monitor` | Chrome DevTools MCP |
| `qa-automation` | 浏览器自动化 | `browser-automation` | Playwright MCP |

### 8.3 Agent 协作与 Loop 驱动

Multica 的 Issue 机制天然支持循环式协作：

1. **创建 Root Issue**：`orchestrator` 创建名为 `TestSuite-{timestamp}` 的 Issue，包含所有测试用例
2. **子 Issue 分配**：每个用例作为 Sub-Issue，分配给 `qa-automation`
3. **结果回写**：执行完成后，`qa-automation` 在 Sub-Issue Comment 中写入结果
4. **异常标记**：发现异常时，在 Comment 中添加 `⚠️ ANOMALY` 标记
5. **Loop 驱动**：`orchestrator` 定期扫描所有 Sub-Issue 的状态和标记
6. **修复子 Issue**：需要修复时，`orchestrator` 创建 Fix-Issue 分配给 `backend-engineer`
7. **状态同步**：所有状态变更通过 Comment 更新，可视化 Dashboard 实时反映

### 8.4 部署命令

```bash
# 1. 安装 Multica
./scripts/install-multica.ps1

# 2. 验证 MCP 工具
./scripts/verify-mcp.ps1

# 3. 部署 Workspace
./scripts/deploy-workspace.ps1 --workspace multica-workspace.yaml

# 4. 启动测试
multica agent run orchestrator --task "Run test suite with auto-healing"
```


## 9. 实施路线图

| 阶段 | 任务 | 周期 | 核心交付件 |
|------|------|------|------------|
| **Phase 1** | 环境准备与基础验证 | 1-2 天 | 环境配置文档、安装脚本、MCP 验证脚本 |
| **Phase 2** | 核心 Skill 开发 | 3-5 天 | 4 个 Skill（orchestrator、backend-monitor、frontend-monitor、browser-automation） |
| **Phase 3** | Loop 与可视化开发 | 3-5 天 | Loop 控制器、可视化渲染器、报告生成器 |
| **Phase 4** | Debugger 能力集成 | 2-3 天 | Debugger 工作流脚本、侦查策略配置 |
| **Phase 5** | 端到端集成与测试 | 3-5 天 | Workspace 配置、部署脚本、测试场景 |
| **Phase 6** | 试运行与迭代 | 持续 | 修复案例库、优化提示词、Dashboard 调优 |


## 10. 技术栈与依赖清单

### 10.1 必需组件

| 名称 | 版本 | 作用 |
|------|------|------|
| Multica | latest | 多 Agent 管理框架 |
| Docker Desktop | 4.x | Multica 后端运行环境 |
| JetBrains IDEA / WebStorm | 2025.2+ | 提供 MCP Server（含 Debugger 能力） |
| Node.js | 18+ | 运行 MCP 工具 |
| Chrome | 最新 | 浏览器自动化目标 |
| Git | 最新 | 版本控制 |

### 10.2 MCP 工具

| 名称 | 安装命令 | 说明 |
|------|----------|------|
| `@playwright/mcp` | `npm i -g @playwright/mcp` | Playwright 浏览器自动化 |
| `chrome-devtools-mcp` | `npm i -g chrome-devtools-mcp` | Chrome DevTools 协议控制 |
| `@jetbrains/mcp` | 内置 IDEA 插件 | IDE 调试与文件操作（含 Debugger API） |

### 10.3 可视化依赖

| 名称 | 说明 | 可选性 |
|------|------|--------|
| Multica Web UI | 内置 Dashboard，展示 Agent 和 Issue 状态 | 必需 |
| 自定义 Markdown Dashboard | 通过 Multica Comment 渲染的状态面板 | 推荐 |
| HTML 报告生成器 | 循环结束后生成的完整报告 | 可选 |

**本方案不引入 Redis、NATS、Elasticsearch、Grafana 等额外中间件**，所有通信通过 Multica 内置的 Issue/Comment 机制实现，可视化通过 Multica Web UI + Markdown 渲染实现。


## 11. 安全与审核机制

### 11.1 代码修改安全策略

- 所有修复操作在**独立 Git 分支**（如 `fix/agent-xxx`）上进行
- 修复后自动运行回归测试，通过后生成 Pull Request
- 最终必须由**人工开发者 Review** 后才可合并到主分支

### 11.2 Loop 安全控制

- **最大循环次数**：默认 3 次，防止无限循环
- **置信度阈值**：修复方案置信度低于 60% 时暂停循环，请求人工确认
- **超时控制**：单次循环超过 30 分钟自动超时退出
- **服务健康检查**：重启后必须通过健康检查才进入下一轮

### 11.3 日志审计

- 所有 Agent 操作（读取日志、修改文件、重启服务、Debugger 操作）均记录详细日志
- 每轮循环的状态变更记录到 Multica Issue 的 Comment 中，便于追溯


## 12. 总结

本方案基于 **Multica 多 Agent 框架**，结合 **MCP 生态工具**，构建了一套完整的**自动化测试与自愈闭环系统**。

**核心创新点**：

1. **Loop 闭环控制**：实现“执行 → 检测 → 修复 → 重启 → 重跑”的自动化循环，直到全部用例通过或达到阈值
2. **Debugger 深度集成**：将 JetBrains MCP 的 Debugger 能力纳入修复流程，实现从“日志驱动”到“状态驱动”的升级
3. **可视化实时反馈**：通过 Multica Web UI + Markdown Dashboard 实时展示循环状态、测试进度、修复历史
4. **Multica 原生适配**：所有功能以 Skill 形式打包，通过 Agent + Issue + Skill 机制实现完整的任务生命周期管理
5. **零侵入、低依赖**：不修改现有业务代码，不引入 Redis/NATS 等中间件

**最终交付物**：一个完整的 Multica Workspace 配置包，包含 4 个 Agent 定义、4 个 Skill 实现、MCP 配置文件、Loop 控制器、可视化渲染器、部署脚本和文档，可一键部署到 Multica 环境中运行。