import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run_script(name, *args):
    return subprocess.run(
        [PYTHON, str(ROOT / "scripts" / name), *map(str, args)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class ScriptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="factor-research-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_scaffold_creates_standard_paper_project(self):
        result = run_script(
            "scaffold_factor_project.py",
            "测试论文因子",
            "--base-dir",
            self.tmp,
            "--source-type",
            "paper",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        project = self.tmp / "测试论文因子"
        self.assertTrue((project / "FACTOR_DESIGN.md").exists())
        self.assertTrue((project / "factor_definition.yaml").exists())
        self.assertTrue((project / "autostrategy_handoff.yaml").exists())
        self.assertTrue((project / "source_notes.md").exists())
        self.assertIn(str(project), result.stdout)

    def test_quality_check_accepts_valid_project(self):
        project = self._write_valid_project("A", "low")

        result = run_script("quality_check.py", project, "--source-type", "paper")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_quality_check_rejects_dangerous_claim(self):
        project = self._write_valid_project("A", "low")
        (project / "FACTOR_DESIGN.md").write_text(
            (project / "FACTOR_DESIGN.md").read_text(encoding="utf-8")
            + "\n\n本因子已验证有效，可以推荐实盘。\n",
            encoding="utf-8",
        )

        result = run_script("quality_check.py", project, "--source-type", "paper")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dangerous", result.stdout)

    def test_validate_handoff_accepts_ab_rating_and_design_only(self):
        project = self._write_valid_project("B", "low_to_medium")

        result = run_script("validate_handoff.py", project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("eligible", result.stdout)

    def test_validate_handoff_rejects_c_rating(self):
        project = self._write_valid_project("C", "low")

        result = run_script("validate_handoff.py", project)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not eligible", result.stdout)

    def test_render_summary_outputs_key_fields(self):
        project = self._write_valid_project("A", "low")

        result = run_script("render_summary.py", project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("测试因子", result.stdout)
        self.assertIn("rating: A", result.stdout)
        self.assertIn("handoff: eligible", result.stdout)

    def _write_valid_project(self, grade, future_risk):
        project = self.tmp / f"project-{grade}"
        project.mkdir()
        (project / "FACTOR_DESIGN.md").write_text(
            """# 因子设计文档

## 1. 原始输入
论文复现。

## 2. 事件时间线
不适用。

## 3. 因子假设
测试假设。

## 4. 变量字典
变量。

## 5. 可量化定义
公式。

## 6. 测试设计
IC、RankIC、分层收益。

## 7. 未来函数检查
风险低。

## 8. 数据可得性
公开数据。

## 9. 反证清单
反证。

## 10. 研究评级
评级。

## 11. 交接给 autostrategy
待测试。
""",
            encoding="utf-8",
        )
        (project / "factor_definition.yaml").write_text(
            f"""factor:
  name: test_factor
  display_name: 测试因子
  type: value
  direction: positive
  market: A股
  universe: 沪深300
  formula: value_metric
  variables:
    - name: value_metric
      meaning: 测试变量
      source: public
      frequency: daily
      available_at: T日开盘前
      missing_value_handling: drop
  timing:
    signal_time: T日开盘前
    tradable_time: T日开盘后
    rebalance_frequency: daily
    holding_period: 1d
  preprocessing:
    lag: 1d
    winsorization: 1%/99%
    standardization: zscore
    neutralization:
      - industry
      - market_cap
  testing:
    start_date: '2020-01-01'
    end_date: '2025-12-31'
    benchmark: 沪深300
    grouping: quintile
    metrics:
      - IC
      - RankIC
  leakage_checks:
    future_data_risk: {future_risk}
    survivorship_bias_risk: low
    sample_selection_bias_risk: low
  rating:
    grade: {grade}
    reason: 测试
""",
            encoding="utf-8",
        )
        (project / "autostrategy_handoff.yaml").write_text(
            """handoff:
  source_skill: factor-research
  target_skill: autostrategy
  status: design_only
  factor_name: 测试因子
  market: A股
  universe: 沪深300
  strategy_candidate:
    type: multi_factor_stock_selection
    signal_direction: positive
    rebalance_frequency: daily
    holding_period: 1d
    entry_rule: top quintile
    exit_rule: rebalance
    risk_limits:
      - max_single_stock_3pct
  fixed_definitions:
    - factor_formula
    - signal_time
    - tradable_time
    - universe
  assumptions_to_test:
    - 测试假设
  warnings:
    - 因子尚未完成代码回测，不能视为已验证有效。
""",
            encoding="utf-8",
        )
        (project / "source_notes.md").write_text(
            "# 来源证据记录\n\n论文来源待确认。\n", encoding="utf-8"
        )
        return project


if __name__ == "__main__":
    unittest.main()
