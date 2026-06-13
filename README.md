# Factor Research

`factor-research` is a Codex skill for turning investment information into testable factor designs.

It helps convert news, announcements, papers, research reports, metrics, formulas, and rough investment hypotheses into structured factor research artifacts.

> This skill is for research design only. It does not provide investment advice, does not run live trading, and does not claim that a factor is valid before testing.

## What It Does

- Turns a factor idea into a precise factor definition.
- Converts news and announcements into event-factor designs.
- Converts papers and research reports into local-market factor designs.
- Produces handoff files for downstream strategy generation with `autostrategy`.
- Checks generated artifacts for structural completeness and dangerous claims.

## Main Artifacts

Each factor project can produce:

```text
FACTOR_DESIGN.md
factor_definition.yaml
autostrategy_handoff.yaml
source_notes.md
```

Optional next-stage planning:

```text
factor_backtest_plan.md
```

## Directory Structure

```text
factor-research/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── examples/
├── prompts/
├── references/
├── scripts/
└── tests/
```

## Usage

Invoke the skill explicitly in Codex:

```text
使用 factor-research，把这篇论文设计成可测试因子
```

or:

```text
[$factor-research](/path/to/factor-research/SKILL.md)
```

Example requests:

```text
使用 factor-research，研究 ROE 因子在 A 股有没有用
```

```text
使用 factor-research，把这条 AI 算力订单新闻设计成可测试事件因子
```

```text
使用 factor-research，把这篇 anomaly 论文复现成 A 股因子设计
```

## Scripts

Create a project scaffold:

```bash
python3 scripts/scaffold_factor_project.py "回购强度因子" --source-type announcement
```

Check artifact quality:

```bash
python3 scripts/quality_check.py ~/因子研究/回购强度因子 --source-type announcement
```

Validate whether a design is ready to hand off to `autostrategy`:

```bash
python3 scripts/validate_handoff.py ~/因子研究/回购强度因子
```

Render a concise summary:

```bash
python3 scripts/render_summary.py ~/因子研究/回购强度因子
```

## Tests

Run:

```bash
python3 -m unittest discover -s tests
```

## Scope

This skill currently focuses on:

- Factor hypothesis design
- Source review
- Factor definition
- Testing plan design
- Handoff to strategy-generation workflows
- Structural validation

It intentionally does not:

- Run factor backtests
- Generate trading recommendations
- Execute trades
- Claim a factor is effective before empirical testing

