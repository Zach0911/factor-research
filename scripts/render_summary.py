#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _factor_utils import get_nested, infer_factor_name, load_yaml, project_path
from validate_handoff import handoff_errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a concise factor-research project summary.")
    parser.add_argument("project_dir")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = project_path(args.project_dir)
    factor = load_yaml(project / "factor_definition.yaml") or {}
    handoff = load_yaml(project / "autostrategy_handoff.yaml") if (project / "autostrategy_handoff.yaml").exists() else {}
    errors = handoff_errors(project)
    eligible = not errors

    name = infer_factor_name(project, factor)
    grade = get_nested(factor, ["factor", "rating", "grade"], "unknown")
    direction = get_nested(factor, ["factor", "direction"], "unknown")
    market = get_nested(factor, ["factor", "market"], "unknown")
    universe = get_nested(factor, ["factor", "universe"], "unknown")
    future_risk = get_nested(factor, ["factor", "leakage_checks", "future_data_risk"], "unknown")
    status = get_nested(handoff or {}, ["handoff", "status"], "unknown")

    print(f"# {name}")
    print("")
    print(f"- rating: {grade}")
    print(f"- market: {market}")
    print(f"- universe: {universe}")
    print(f"- direction: {direction}")
    print(f"- future_data_risk: {future_risk}")
    print(f"- handoff_status: {status}")
    print(f"- handoff: {'eligible' if eligible else 'not eligible'}")
    if errors:
        print("")
        print("## blockers")
        for error in errors:
            print(f"- {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
