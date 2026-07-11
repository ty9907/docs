# Multica 小队、智能体与 Issue 配置

本框架采用一个小队和四个智能体。小队 Issue 只会先唤醒 **Leader**；Leader 必须在评论中使用 Multica 插入的精确 `@` 提及来分派成员。不要把同一个 Issue 同时分配给多个 Agent。

## 1. 前置条件

1. 在本机安装并登录 Codex CLI 与 Multica CLI。
2. 在 PowerShell 运行 `multica daemon start`，确认 `multica daemon status` 为在线。
3. 在 Multica 创建项目 `本地测试自愈`，绑定仓库或本地目录 `D:\documents\github\docs\multica-test-automation`。本地目录任务会串行执行；开始修复前先提交或暂存你自己的改动。
4. 复制 `config/mcp-servers.example.json` 为 `config/mcp-servers.json`，填入实际 MCP 路径；只给需要的 Agent 配置 MCP。

## 2. 导入 Skill

在 **Skills** 页面使用 **From local** 扫描并导入下列目录；或者将各目录提交到远程仓库后使用 **From GitHub** 导入：

| Skill | 本地目录 | 绑定 Agent |
|---|---|---|
| `orchestrator` | `skills/orchestrator` | `orchestrator` |
| `backend-monitor` | `skills/backend-monitor` | `backend-engineer` |
| `frontend-monitor` | `skills/frontend-monitor` | `frontend-engineer` |
| `browser-automation` | `skills/browser-automation` | `qa-automation` |

Skill 用来表达角色流程；MCP 用来提供浏览器、IDE 和调试工具。不要把修复权限或密钥写入 Skill。

## 3. 创建智能体

在 **Agents → New** 中选择本地 Codex runtime，创建以下 Agent。开发初期保持 `Private`；验证稳定后需要团队成员发起任务时改为 `Workspace`。

| Agent | 并发 | Skill | MCP | System instructions 核心要求 |
|---|---:|---|---|---|
| `orchestrator` | 1 | `orchestrator` | 无 | 仅路由、汇总、审批和报告；不直接改代码 |
| `qa-automation` | 1 | `browser-automation` | Playwright | 执行 YAML 用例并贴出失败证据；不静默改选择器 |
| `backend-engineer` | 1 | `backend-monitor` | JetBrains | 只读诊断，给出最小 diff 和置信度；等待批准 |
| `frontend-engineer` | 1 | `frontend-monitor` | Chrome DevTools | 分析 Console/Network，给出最小 diff；等待批准 |

建议四个 Agent 的 `max_concurrent_tasks` 都设为 `1`：同一套本地服务、浏览器和工作目录不适合并发测试或并发修复。

## 4. 创建小队

在 **Squads → New squad** 中创建：

- **名称**：`test-healing-squad`
- **Leader**：`orchestrator`
- **成员与角色**：
  - `qa-automation`：执行用例、收集 Playwright/Console/Network 证据
  - `backend-engineer`：后端日志与 JetBrains Debugger 诊断
  - `frontend-engineer`：前端运行时与网络诊断

在 Squad Instructions 填入：

```text
你是测试自愈小队的路由者，不直接修改代码。
先 @qa-automation 执行或重跑用例。失败时根据证据只 @ 一个修复 Agent。
修复 Agent 必须回复根因、unified diff、影响文件、置信度和验证步骤。
低于 0.70 的置信度或涉及数据库/认证/删除操作时停止并请求人工处理。
只有 Issue 中出现人类的明确 accept 才可要求修复 Agent 应用补丁。
补丁应用后 @qa-automation 重跑失败用例及下游依赖；最多 3 轮。
每次路由后记录 squad activity，最后评论 Markdown 报告并设置状态。
```

可用 CLI 创建与维护小队：

```powershell
multica squad create --name "test-healing-squad" --leader orchestrator
multica squad member add <squad-id> --member-id <qa-agent-id> --type agent --role "执行用例并收集证据"
multica squad member add <squad-id> --member-id <backend-agent-id> --type agent --role "后端诊断与补丁提案"
multica squad member add <squad-id> --member-id <frontend-agent-id> --type agent --role "前端诊断与补丁提案"
multica squad update <squad-id> --instructions "<粘贴上面的 Squad Instructions>"
```

## 5. 使用 Issue 触发闭环

创建一个普通 Issue，状态设为 `todo`，项目设为 `本地测试自愈`，**Assignee 设为 `test-healing-squad`**。标题示例：`[E2E] 登录与下单回归`。描述使用以下模板：

```markdown
## 目标
执行 `cases/e2e_cases.yaml` 中的 `login` 和 `create_order`。

## 环境
- 前端：`http://localhost:3000`
- 后端健康检查：`http://localhost:8080/actuator/health`
- 配置：`config/project.yaml`

## 安全边界
- 最大重试：3；置信度阈值：0.70。
- 禁止生产环境、删除数据、修改密钥和自动提交。
- 只能在我回复 `accept` 后应用补丁；`reject` 立即停止。

## 验收
- 两个用例均通过；报告包含失败证据、修复 diff、重跑结果和退出原因。
```

分派过程是：Squad 唤醒 `orchestrator` → Leader 在评论里通过 UI 插入的精确 `@qa-automation` 提及启动 QA → QA 评论结果 → Leader 再提及一个修复 Agent 或要求人工审批。成员普通进度评论会重新唤醒 Leader；显式提及其他成员时 Leader 会让路，避免重复调度。

批准时由人工在同一 Issue 评论 `accept`；拒绝时评论 `reject`。需要重新执行时使用 `multica issue rerun <issue-id>`，而不是复制一个新 Issue。

## 6. 是否需要 `AGENTS.md`

需要，但只保留**所有 Agent 共同遵守的仓库规则**。本仓库已经提供 `AGENTS.md`，内容是审批、生产环境禁令、测试命令和协作边界。角色职责不要重复写进它：角色职责放在 Skill，路由规则放在 Squad Instructions，单次目标放在 Issue。

如果将项目绑定为 Multica 的本地目录资源，Multica 也会在目录根部写入自己的 `AGENTS.md`/项目上下文文件。请确认它不会覆盖你的已提交规则；如界面提供追加或保留选项，选择保留。否则把上面的共同规则放到 Agent 的 system instructions，并将 Multica 自动写入的文件加入 `.gitignore`。
