# Multica 自动化测试与自愈框架

这是根据设计文档实现的本地测试自愈框架：它把 **测试执行、异常收集、根因归因、置信度门控、人工审批、重跑和报告** 做成可单测的 Python 核心，并提供四个 Multica Skill 的工作区模板。

## 目录

| 路径 | 用途 |
|---|---|
| `src/auto_test_healer/` | 可独立测试的 Loop 控制器、用例加载、日志监控、报告与适配器 |
| `cases/e2e_cases.yaml` | Playwright/MCP 测试用例模板，支持依赖关系 |
| `skills/` | Multica 的主控、后端、前端、浏览器自动化四个 Skill |
| `multica-workspace.yaml` | 将四个 Agent 与 Skill/MCP 配置关联的模板 |
| `config/` | 项目和 MCP Server 配置示例 |
| `scripts/` | Windows 环境安装与配置验证脚本 |

## 自愈闭环

1. `qa-automation` 执行待测用例，失败用例及其下游用例会进入下一轮。
2. `backend-monitor`、`frontend-monitor` 和测试执行器上报异常；框架使用 `source/category/case/file/line` 去重。
3. `orchestrator` 选择修复 Agent，要求它给出根因、最小 unified diff、影响文件和置信度。
4. 低于 `confidence_threshold` 的方案立即停止；所有其他方案也必须经过人工 `accept` 才能应用。
5. 应用后重跑，直到全部通过或达到 `max_retries`；最终输出 Markdown 审计报告。

默认实现不会自动写业务代码：`AuditOnlyApplier` 仅记录已获批准的方案。生产接入时，应替换为受 Git 分支保护的补丁应用器，并保留审批检查。

## 本地验证

```powershell
cd D:\documents\github\docs\multica-test-automation
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
auto-test-healer --cases cases/e2e_cases.yaml --report reports\latest.md
```

`auto-test-healer` 是无需浏览器或 MCP 的干跑模式；未提供结果时所有示例用例通过。可用 JSON 模拟重试行为，例如：

```json
{"login": [false, true], "create_order": [true]}
```

然后运行 `auto-test-healer --outcomes outcomes.json`。每个数组按同一用例的执行轮次依次消费。

## 在 Multica 中使用

### 1. 配置环境

1. 将 `config/project.example.yaml` 复制为 `config/project.yaml`，填写目标项目、健康检查和日志路径。
2. 将 `config/mcp-servers.example.json` 复制为 `config/mcp-servers.json`，填写 JetBrains MCP JAR 的绝对路径。
3. 运行 `scripts/install-multica.ps1`，再运行 `scripts/verify-mcp.ps1`。需要 Node.js、Chrome、JetBrains IDE 与目标项目依赖。
4. `multica-workspace.yaml` 是本项目的角色关系参考，不是 Multica CLI 的导入文件。请在 Multica UI 或 CLI 中创建下方的 Agent、Skill 和小队。

### 2. 创建 Agent

| Agent | Skill | MCP |
|---|---|---|
| `orchestrator` | `skills/orchestrator` | 无 |
| `backend-engineer` | `skills/backend-monitor` | JetBrains |
| `frontend-engineer` | `skills/frontend-monitor` | Chrome DevTools |
| `qa-automation` | `skills/browser-automation` | Playwright |

创建 Agent 后，在 UI 的 Agent 详情中分别附加 `skills/*/SKILL.md` 和相应的 MCP 配置。完整的小队、Issue 和审批运行步骤见 `docs/multica-setup.md`。

### 3. 运行任务

向 `orchestrator` 创建任务或 Issue，并提供以下最小上下文：

```text
执行 config/project.yaml 中的测试套件。
测试用例：cases/e2e_cases.yaml。
最大重试：3；置信度阈值：0.70；修复模式：approval_required。
仅在我回复 accept 后应用 unified diff；每轮在 Issue 中更新 Markdown 状态。
```

主控会把用例 Issue 分配给 `qa-automation`。发生异常时，它会将诊断 Issue 分给后端或前端 Agent，收集修复提案后暂停等待 `accept`、`reject` 或修改说明。请在每次补丁应用后让服务恢复健康，再由 QA Agent 重跑失败及下游用例。

## 接入 Playwright 与修复器

`src/auto_test_healer/contracts.py` 定义了四个可替换端口：

- `TestExecutor`：实现为 Playwright MCP 调用器，逐步执行 YAML 中的 `steps`。
- `Monitor`：接入 `LogMonitor`、Chrome Console/Network 事件或 JetBrains Debugger 采集。
- `Diagnoser`：调用团队批准的 LLM，严格返回 `FixProposal`。
- `FixApplier`：先在独立 Git 分支验证 unified diff，再写入工作区。

建议保持 `approval_required`，限制 `allowed_targets`，并把每次修复记录保留在报告与 Multica Issue 中。
