#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _factor_utils import SOURCE_NOTES_TYPES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a factor-research project scaffold.")
    parser.add_argument("factor_name", help="Human-readable factor name.")
    parser.add_argument("--base-dir", default="~/因子研究", help="Base output directory.")
    parser.add_argument(
        "--source-type",
        default="idea",
        help="news, announcement, paper, report, metric, formula, or idea.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite scaffold placeholders.")
    return parser.parse_args()


def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    base_dir = Path(args.base_dir).expanduser()
    project = base_dir / args.factor_name
    project.mkdir(parents=True, exist_ok=True)

    write_file(
        project / "FACTOR_DESIGN.md",
        f"""# 因子设计文档

> 本文档仅用于因子研究设计，不构成投资建议。当前阶段未执行代码回测，不能视为因子有效性的实证结论。

## 1. 原始输入

- 来源类型：{args.source_type}
- 来源名称 / 链接：待补充
- 发布时间 / 论文年份 / 公告日期：待确认
- 原始内容摘要：待补充
- 用户研究问题：待补充

## 2. 事件时间线

待补充。

## 3. 因子假设

- 因子名称：{args.factor_name}
- 因子类型：待确认
- 适用市场：待确认
- 适用股票池：待确认
- 经济逻辑：待补充
- 预期方向：待确认
- 预期生效周期：待确认
- 主要反例：待补充

## 4. 变量字典

待补充。

## 5. 可量化定义

待补充。

## 6. 测试设计

待补充。

## 7. 未来函数检查

待补充。

## 8. 数据可得性

待补充。

## 9. 反证清单

待补充。

## 10. 研究评级

- 评级：待确认

## 11. 交接给 autostrategy

待补充。
""",
        args.force,
    )
    write_file(
        project / "factor_definition.yaml",
        f"""factor:
  name: "{args.factor_name}"
  display_name: "{args.factor_name}"
  type: "composite"
  direction: "uncertain"
  market: "其他"
  universe: "待确认"
  hypothesis: "待补充"
  formula: "待补充"
  variables: []
  timing:
    signal_time: "待确认"
    tradable_time: "待确认"
    rebalance_frequency: "daily"
    holding_period: "待确认"
  preprocessing:
    lag: "待确认"
    winsorization: "待确认"
    standardization: "待确认"
    neutralization: []
  testing:
    start_date: "unknown"
    end_date: "unknown"
    benchmark: "待确认"
    grouping: "待确认"
    metrics:
      - "IC"
      - "RankIC"
  leakage_checks:
    future_data_risk: "待确认"
    survivorship_bias_risk: "待确认"
    sample_selection_bias_risk: "待确认"
  rating:
    grade: "待确认"
    reason: "待补充"
""",
        args.force,
    )
    write_file(
        project / "autostrategy_handoff.yaml",
        f"""handoff:
  source_skill: "factor-research"
  target_skill: "autostrategy"
  status: "design_only"
  factor_name: "{args.factor_name}"
  market: "待确认"
  universe: "待确认"
  strategy_candidate:
    type: "multi_factor_stock_selection"
    signal_direction: "uncertain"
    rebalance_frequency: "daily"
    holding_period: "待确认"
    entry_rule: "待补充"
    exit_rule: "待补充"
    risk_limits: []
  fixed_definitions:
    - "factor_formula"
    - "signal_time"
    - "tradable_time"
    - "universe"
  assumptions_to_test: []
  warnings:
    - "因子尚未完成代码回测，不能视为已验证有效。"
""",
        args.force,
    )

    if args.source_type in SOURCE_NOTES_TYPES:
        write_file(
            project / "source_notes.md",
            "# 来源证据记录\n\n## 来源列表\n\n待补充。\n\n## 关键摘录\n\n待补充。\n",
            args.force,
        )

    print(project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
