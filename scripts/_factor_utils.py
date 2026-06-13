from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("PyYAML is required to parse factor-research YAML files.") from exc


REQUIRED_FILES = [
    "FACTOR_DESIGN.md",
    "factor_definition.yaml",
    "autostrategy_handoff.yaml",
]

SOURCE_NOTES_TYPES = {"news", "announcement", "paper", "report", "新闻", "公告", "论文", "研报"}

REQUIRED_DESIGN_SECTIONS = [
    "原始输入",
    "事件时间线",
    "因子假设",
    "变量字典",
    "可量化定义",
    "测试设计",
    "未来函数检查",
    "数据可得性",
    "反证清单",
    "研究评级",
    "交接给 autostrategy",
]

DANGEROUS_PATTERNS = [
    "本因子已验证有效",
    "因子已验证有效",
    "已验证有效，可以",
    "回测证明有效",
    "保证收益",
    "推荐实盘",
    "建议实盘",
    "可以实盘",
]


@dataclass
class CheckResult:
    ok: bool
    messages: list[str]


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def project_path(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def get_nested(data: dict[str, Any], keys: list[str], default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def normalize_risk(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_")


def is_high_future_risk(value: Any) -> bool:
    normalized = normalize_risk(value)
    return normalized in {"high", "高", "高风险"}


def yaml_load_errors(project: Path) -> list[str]:
    errors: list[str] = []
    for name in ("factor_definition.yaml", "autostrategy_handoff.yaml"):
        path = project / name
        if not path.exists():
            continue
        try:
            load_yaml(path)
        except Exception as exc:  # noqa: BLE001 - CLI should report parse errors
            errors.append(f"{name}: YAML parse error: {exc}")
    return errors


def missing_required_files(project: Path, source_type: str | None = None) -> list[str]:
    missing = [name for name in REQUIRED_FILES if not (project / name).exists()]
    if source_type and source_type in SOURCE_NOTES_TYPES and not (project / "source_notes.md").exists():
        missing.append("source_notes.md")
    return missing


def has_dangerous_claims(text: str) -> list[str]:
    return [pattern for pattern in DANGEROUS_PATTERNS if pattern in text]


def infer_factor_name(project: Path, factor_data: dict[str, Any] | None = None) -> str:
    if factor_data:
        display = get_nested(factor_data, ["factor", "display_name"])
        name = get_nested(factor_data, ["factor", "name"])
        if display:
            return str(display)
        if name:
            return str(name)
    return project.name
