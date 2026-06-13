#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _factor_utils import (
    get_nested,
    is_high_future_risk,
    load_yaml,
    missing_required_files,
    project_path,
    yaml_load_errors,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate whether a factor project can hand off to autostrategy.")
    parser.add_argument("project_dir")
    return parser.parse_args()


def handoff_errors(project: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(f"missing required file: {name}" for name in missing_required_files(project))
    errors.extend(yaml_load_errors(project))
    if errors:
        return errors

    factor = load_yaml(project / "factor_definition.yaml") or {}
    handoff = load_yaml(project / "autostrategy_handoff.yaml") or {}

    grade = str(get_nested(factor, ["factor", "rating", "grade"], ""))
    if grade not in {"A", "B"}:
        errors.append(f"rating grade must be A or B for handoff, got {grade}")

    future_risk = get_nested(factor, ["factor", "leakage_checks", "future_data_risk"])
    if is_high_future_risk(future_risk):
        errors.append(f"future_data_risk is high: {future_risk}")

    if get_nested(handoff, ["handoff", "status"]) != "design_only":
        errors.append("handoff.status must be design_only")
    if get_nested(handoff, ["handoff", "source_skill"]) != "factor-research":
        errors.append("handoff.source_skill must be factor-research")
    if get_nested(handoff, ["handoff", "target_skill"]) != "autostrategy":
        errors.append("handoff.target_skill must be autostrategy")

    fixed = set(get_nested(handoff, ["handoff", "fixed_definitions"], []) or [])
    required_fixed = {"factor_formula", "signal_time", "tradable_time", "universe"}
    missing_fixed = required_fixed - fixed
    if missing_fixed:
        errors.append(f"handoff.fixed_definitions missing: {', '.join(sorted(missing_fixed))}")

    warnings = get_nested(handoff, ["handoff", "warnings"], []) or []
    if not any("尚未完成代码回测" in str(item) for item in warnings):
        errors.append("handoff.warnings must mention 尚未完成代码回测")

    return errors


def main() -> int:
    args = parse_args()
    project = project_path(args.project_dir)
    errors = handoff_errors(project)
    if errors:
        print("not eligible")
        for error in errors:
            print(f"- {error}")
        return 1
    print("eligible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
