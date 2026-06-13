#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _factor_utils import (
    get_nested,
    has_dangerous_claims,
    load_yaml,
    missing_required_files,
    project_path,
    read_text,
    yaml_load_errors,
    REQUIRED_DESIGN_SECTIONS,
)


VALID_GRADES = {"A", "B", "C", "D", "待确认"}
VALID_STATUS = {"design_only"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check factor-research project quality.")
    parser.add_argument("project_dir")
    parser.add_argument("--source-type", default=None)
    return parser.parse_args()


def check_project(project: Path, source_type: str | None = None) -> list[str]:
    errors: list[str] = []

    missing = missing_required_files(project, source_type)
    errors.extend(f"missing required file: {name}" for name in missing)
    errors.extend(yaml_load_errors(project))

    design_path = project / "FACTOR_DESIGN.md"
    if design_path.exists():
        design = read_text(design_path)
        for section in REQUIRED_DESIGN_SECTIONS:
            if section not in design:
                errors.append(f"FACTOR_DESIGN.md missing section: {section}")
        dangerous = has_dangerous_claims(design)
        for pattern in dangerous:
            errors.append(f"dangerous claim in FACTOR_DESIGN.md: {pattern}")

    factor_path = project / "factor_definition.yaml"
    if factor_path.exists():
        factor = load_yaml(factor_path) or {}
        grade = str(get_nested(factor, ["factor", "rating", "grade"], ""))
        if grade not in VALID_GRADES:
            errors.append(f"invalid factor.rating.grade: {grade}")
        if not get_nested(factor, ["factor", "name"]):
            errors.append("factor.name is required")
        if not get_nested(factor, ["factor", "formula"]):
            errors.append("factor.formula is required")
        if get_nested(factor, ["factor", "leakage_checks", "future_data_risk"]) is None:
            errors.append("factor.leakage_checks.future_data_risk is required")

    handoff_path = project / "autostrategy_handoff.yaml"
    if handoff_path.exists():
        handoff = load_yaml(handoff_path) or {}
        status = str(get_nested(handoff, ["handoff", "status"], ""))
        if status not in VALID_STATUS:
            errors.append(f"invalid handoff.status: {status}")
        if get_nested(handoff, ["handoff", "source_skill"]) != "factor-research":
            errors.append("handoff.source_skill must be factor-research")
        if get_nested(handoff, ["handoff", "target_skill"]) != "autostrategy":
            errors.append("handoff.target_skill must be autostrategy")
        warnings = get_nested(handoff, ["handoff", "warnings"], []) or []
        if not any("尚未完成代码回测" in str(item) for item in warnings):
            errors.append("handoff.warnings must mention 尚未完成代码回测")

    return errors


def main() -> int:
    args = parse_args()
    project = project_path(args.project_dir)
    errors = check_project(project, args.source_type)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
