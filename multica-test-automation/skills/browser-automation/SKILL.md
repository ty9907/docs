# Browser Automation

解析 `cases/e2e_cases.yaml`，用 Playwright MCP 逐步执行 `navigate`、`fill`、`click`、`assert_visible`、`api_verify` 和视觉检查。

遇到选择器失效时，先返回 DOM 快照、原选择器和候选选择器；不得静默改变测试用例。将失败证据发布到对应 Issue，供 `orchestrator` 进行根因归因与审批。
