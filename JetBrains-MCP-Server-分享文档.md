# JetBrains MCP Server 使用分享

## 什么是 MCP Server？

MCP（Model Context Protocol，模型上下文协议）是一种开放协议，它使 AI 模型（如 Claude、Codex 等）能够通过标准化的接口与外部工具和数据源进行交互。

JetBrains IDE（IntelliJ IDEA、WebStorm、PyCharm 等）从 2025.2 版本开始内置了 **MCP Server 插件**，将 IDE 的能力以 MCP 工具的形式暴露给外部 AI 客户端。这意味着 AI 可以直接读取、分析、搜索、修改你的代码，甚至运行配置和终端命令。

---

## 一、JetBrains MCP Server 核心功能

### 1. 代码搜索与导航

| 工具 | 功能说明 |
|------|---------|
| `search_symbol` | 按名称搜索类、方法、字段等符号，支持项目和外部库 |
| `search_text` | 在项目文件中搜索文本片段，返回匹配位置的行列号 |
| `search_regex` | 在项目文件中搜索正则表达式匹配 |
| `search_file` | 按 glob 模式匹配文件路径 |
| `get_symbol_info` | 获取符号的快速文档信息，包括签名、类型、文档注释 |

**使用场景**：让 AI 理解项目结构、查找特定实现、分析类之间的关系。

### 2. 文件操作

| 工具 | 功能说明 |
|------|---------|
| `read_file` | 读取文件内容，支持行号和偏移量控制 |
| `write_file` | 创建新文件或覆盖已有文件 |
| `edit` | 精确字符串替换（改代码的推荐方式） |
| `create_new_file` | 在项目中创建新文件并填充内容 |
| `get_file_text_by_path` | 按路径获取文件内容 |
| `get_open_file_paths` | 获取当前在编辑器中打开的所有文件列表 |

**使用场景**：AI 直接读取源代码进行分析，或根据需求生成代码文件。

### 3. 项目分析

| 工具 | 功能说明 |
|------|---------|
| `build_project` | 触发项目编译，返回编译错误和警告 |
| `get_file_problems` | 对指定文件运行 IntelliJ 静态分析，返回错误/警告列表 |
| `get_project_dependencies` | 获取项目所有依赖库列表 |
| `get_project_modules` | 获取项目模块信息 |
| `list_directory_tree` | 以树形结构展示目录内容 |
| `find_files_by_name_keyword` | 按文件名关键词搜索 |
| `find_files_by_glob` | 按 glob 模式搜索文件 |

**使用场景**：验证代码修改是否正确、了解项目依赖结构、分析编译错误。

### 4. 运行与执行

| 工具 | 功能说明 |
|------|---------|
| `execute_run_configuration` | 运行 IDEA 的运行配置，支持程序参数/环境变量/工作目录覆盖 |
| `execute_terminal_command` | 在 IDE 集成终端中执行 Shell 命令 |

**使用场景**：AI 执行测试、启动应用、运行构建脚本。

### 5. 数据库操作

| 工具 | 功能说明 |
|------|---------|
| `list_database_connections` | 列出项目配置的所有数据库连接 |
| `list_database_schemas` | 列出数据库中的 Schema |
| `list_schema_objects` | 列出 Schema 下的表/视图等对象 |
| `get_database_object_description` | 获取数据库对象的列、类型、键、索引等结构信息 |
| `execute_sql_query` | 执行 SQL 查询并返回 CSV 格式结果 |
| `preview_table_data` | 预览表数据 |
| `test_database_connection` | 测试数据库连接是否有效 |

**使用场景**：AI 直接查询数据库分析数据、获取表结构辅助编写代码。

### 6. 其他实用工具

| 工具 | 功能说明 |
|------|---------|
| `reformat_file` | 按照项目代码风格格式化文件 |
| `apply_patch` | 应用补丁文件 |
| `rename_refactoring` | 对符号进行重命名重构（自动更新所有引用） |
| `generate_psi_tree` | 为代码片段生成 PSI 语法树 |
| `find_threading_requirements_usages` | 分析方法的线程约束要求 |
| `find_lock_requirement_usages` | 分析方法的读写锁要求 |

---

## 二、Debugger MCP Toolset — 调试能力扩展

**Debugger MCP Toolset** 是 JetBrains 官方提供的插件，与 MCP Server 配合使用，为 AI 客户端增加了完整的调试能力。该插件在 IntelliJ IDEA Ultimate 中默认捆绑。

> 官方还提供了一个 `/ij-debugger` skill 文件，可以复制到 AI 客户端的 skills 目录中，让 AI 更智能地使用这些调试工具。

### 调试会话管理

| 工具 | 功能说明 |
|------|---------|
| `xdebug_start_debugger_session` | 启动调试会话，支持按运行配置名称或文件+行号方式 |
| `xdebug_get_debugger_status` | 获取当前所有活跃调试会话的状态 |
| `xdebug_control_session` | 控制会话：暂停、恢复、单步（Step Into/Over/Out）、停止 |

### 断点管理

| 工具 | 功能说明 |
|------|---------|
| `xdebug_set_breakpoint` | 设置断点，支持条件断点、日志断点（Tracepoint）、临时断点 |
| `xdebug_remove_breakpoint` | 移除断点，支持按 ID、按文件+行号、按所有者过滤 |
| `xdebug_list_breakpoints` | 列出所有断点及其属性 |
| `xdebug_run_to_line` | 恢复执行到指定行 |

### 运行时数据探查

| 工具 | 功能说明 |
|------|---------|
| `xdebug_get_stack` | 获取当前线程的调用栈 |
| `xdebug_get_threads` | 获取所有线程列表及状态 |
| `xdebug_get_frame_values` | 获取栈帧中的局部变量和参数值 |
| `xdebug_get_value_by_path` | 按路径深入探查嵌套对象的属性值 |
| `xdebug_evaluate_expression` | 在暂停的上下文中求值任意表达式 |
| `xdebug_set_variable` | 在调试中修改变量的值 |

### Debugger 工具集的独特价值

1. **全流程覆盖**：从启动调试 → 设置断点 → 执行到断点 → 探查数据 → 修改变量 → 恢复执行，完整的调试闭环
2. **断点即服务**：支持条件断点、日志断点（Tracepoint）、临时断点，AI 可以灵活设置探查点
3. **表达式求值**：AI 可以像开发者一样在调试上下文中执行任意表达式，理解运行时状态
4. **变量修改变异**：直接通过断点修改变量值来测试不同的代码路径

---

## 三、使用场景举例

### 场景 1：AI 辅助代码审查
AI 通过 `search_symbol` 定位到改动的方法，用 `read_file` 读取完整代码，用 `get_symbol_info` 查看相关文档，然后给出审查意见。

### 场景 2：AI 辅助 Bug 排查
AI 用 `xdebug_start_debugger_session` 启动调试会话，设置条件断点，当断点命中后用 `xdebug_get_frame_values` 和 `xdebug_evaluate_expression` 探查变量值，定位根因。

### 场景 3：AI 分析编译错误
AI 修改代码后调用 `build_project` 进行编译，发现错误后用 `get_file_problems` 获取具体的代码问题列表，然后迭代修改。

### 场景 4：AI 自动化测试
AI 运行 `execute_run_configuration` 执行测试配置，如果测试失败，用调试工具逐步追踪到失败原因。

### 场景 5：AI 数据库探查
AI 用 `list_database_connections` 获取数据库连接，用 `preview_table_data` 预览数据分布，辅助生成 SQL 或分析数据问题。

### 场景 6：AI 配置管理 — 注入运行参数

**背景**：项目需要一些本地化配置（如用户名、地区等），这些配置在文件 `runconfig.txt` 中维护。

**操作流程**：
1. AI 用 `read_file` 读取 `runconfig.txt` 获取配置项
2. AI 用 `get_run_configurations` 查看已有运行配置
3. AI 使用 `edit` 修改 `.idea/workspace.xml`，在 Spring Boot 运行配置的 `<envs>` 或 VM parameters 中添加配置
4. AI 通过 `xdebug_start_debugger_session` 以 Debug 模式重启应用
5. 在断点处用 `xdebug_evaluate_expression` 验证 `System.getProperty("user")` 的值是否正确

**价值**：无需手动打开 IDE 设置界面，AI 即可完成运行参数的注入和验证。

### 场景 7：AI 运行时诊断 — 监控 API 请求链

**背景**：某个 API 接口响应不符合预期，需要查看请求进入后的完整处理链路。

**操作流程**：
1. AI 用 `search_symbol` 或 `search_text` 定位处理该请求的 Controller 方法
2. AI 在 Controller 入口、Service 层、Model 调用处分别设置断点
3. AI 让用户在页面上触发请求，断点依次命中
4. 在每个断点处 AI 用 `xdebug_get_value_by_path` 探查关键变量：
   - 请求 DTO（消息内容、会话 ID、文件列表）
   - 上下文环境（Agent 信息、模型配置、历史消息）
   - 返回结果（SSE Emitter）
5. AI 用 `xdebug_get_stack` 查看调用堆栈，确认执行路径
6. AI 结合 `read_file` 读取日志文件，分析 ERROR/WARN 日志

**价值**：无需埋点、无需加日志，AI 通过断点即可实时捕获完整的请求生命周期数据，快速定位问题根因。

### 场景 8：AI 日志驱动的问题分析

**背景**：应用运行中出现重复的 ERROR 日志，需要在运行时排查。

**操作流程**：
1. AI 用 `execute_terminal_command` 或 `read_file` 读取应用日志文件
2. AI 用 `search_text` 或 `grep` 筛选 ERROR/WARN 级别日志
3. AI 分析异常堆栈，发现是数据库列名不匹配（实体类字段 `@TableField("model_endpoint")` 但 DB 中列名为 `model_id`）
4. AI 用 `search_symbol` 定位实体类和迁移脚本，对比发现 schema 不一致
5. AI 给出修复方案：统一实体类字段名与数据库列名

**价值**：AI 结合日志读取与代码分析能力，从现象到根因一步到位。

### 场景 9：AI 管理断点生命周期

**背景**：AI 设置了多个断点用于数据探查，探查完成后需要清理。

**操作流程**：
1. AI 用 `xdebug_list_breakpoints` 检查当前所有断点
2. AI 用 `xdebug_remove_breakpoint` 清理不再需要的断点（按文件+行号或按所有者）
3. AI 用 `xdebug_control_session` 恢复暂停的调试会话
4. AI 用 `xdebug_get_debugger_status` 确认应用正常运行

**价值**：避免断点残留导致应用停滞，保证调试过程的干净和可控。

### 场景 10：AI 多步重构 — 重命名符号并验证

**背景**：需要将一个类名从 `OldName` 重命名为 `NewName`，涉及多处引用。

**操作流程**：
1. AI 用 `rename_refactoring` 执行重命名重构（自动更新所有引用）
2. AI 调用 `build_project` 编译验证是否通过
3. 如果编译出错，用 `get_file_problems` 获取具体错误位置
4. AI 修复问题后再次编译，直到构建成功
5. AI 用 `execute_run_configuration` 运行相关测试确认功能正常

**价值**：安全重构 + 自动验证，避免人工遗漏引用点。

---

## 四、快速启用

### 步骤 1：确认插件已启用
在 IDEA 中打开 `Settings → Plugins → Installed`，确保 **MCP Server** 插件已勾选。

### 步骤 2：开启 MCP Server
在 `Settings → Tools → MCP Server` 中点击 **Enable MCP Server**。

### 步骤 3：配置外部客户端
在 `Clients Auto-Configuration` 区域，为你的 AI 客户端（Claude Desktop、Codex、Cursor、Windsurf 等）点击 **Auto-Configure**。

### 步骤 4：启用 Debugger 工具集
Debugger MCP Toolset 默认已包含，在 `Exposed Tools` 页面中可以查看和开关所有调试工具。

### 步骤 5：（可选）复制 Debugger Skill
通过 `Search Everywhere (Shift+Shift)` 搜索 "Copy Debugger Skills to Agents"，将 `/ij-debugger` skill 复制到 AI 客户端的 skills 目录中（支持 Claude Code 和 Codex）。

---

## 五、注意事项

- **文件范围**：所有工具默认仅操作项目目录内的文件
- **权限控制**：可以在 `Settings → Tools → MCP Server → Exposed Tools` 中按需启用/禁用特定工具
- **安全模式**：终端命令和运行配置默认需要用户确认，可在设置中启用 "Brave Mode" 绕过确认
- **数据库只读建议**：数据库操作建议使用只读用户，确保安全性
- **行号约定**：代码行号和列号均为 1-based
