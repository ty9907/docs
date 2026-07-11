from __future__ import annotations

from pathlib import Path

from .models import LoopState, TestResult


def render_markdown(state: LoopState, results: list[TestResult]) -> str:
    lines = ["# 自动化测试与自愈报告", "", "## 总览", "", "| 指标 | 值 |", "|---|---|", f"| 退出原因 | `{state.exit_reason.value if state.exit_reason else 'UNKNOWN'}` |", f"| 循环次数 | {state.loop_count}/{state.max_retries} |", f"| 通过用例 | {len(state.passed_case_ids)} |", f"| 修复次数 | {len(state.fixes)} |", "", "## 用例结果", "", "| 用例 | 状态 | 信息 |", "|---|---|---|"]
    lines.extend(f"| `{result.case_id}` | {'✅ 通过' if result.passed else '❌ 失败'} | {result.message} |" for result in results)
    lines += ["", "## 修复记录", "", "| 轮次 | 目标 | 置信度 | 决策 | 已应用 |", "|---|---|---:|---|---|"]
    lines.extend(f"| {fix.round_number} | {fix.proposal.target} | {fix.proposal.confidence:.0%} | {fix.decision} | {'是' if fix.applied else '否'} |" for fix in state.fixes)
    return "\n".join(lines) + "\n"


def write_report(path: str | Path, state: LoopState, results: list[TestResult]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(render_markdown(state, results), encoding="utf-8")
