---
name: factor-research
description: |
  Use when the user wants to turn a factor idea, news item, announcement, research paper, report, article, metric, formula, event, or investment hypothesis into a testable factor design. Trigger on phrases such as 因子研究, 因子测试, alpha, IC, RankIC, 分层回测, 多因子, 选股因子, 新闻能不能量化, 论文能不能复现, 研报逻辑做成因子, 公告事件影响股价吗, 事件因子, 财务因子, 技术因子, 另类数据因子, or 先找因子再做策略.
---

# Factor Research

> 本 Skill 只用于因子研究设计，不构成投资建议。
> 当前版本产出因子设计与结构化交接文件，不生成代码、不运行回测、不声称已实证验证。

## 定位

`factor-research` 负责把用户看到的新闻、公告、论文、研报、指标公式、投资观点或模糊假设，转成可执行的因子研究设计文档和结构化交接文件。

核心边界：
- `factor-research` 回答：「这个信息如何设计成可检验因子？」
- `autostrategy` 回答：「如何把已验证因子做成可运行策略？」

如果用户要直接生成策略代码、回测策略或优化策略，转交 `autostrategy`。如果用户要先判断某个因子是否值得研究，继续使用本 Skill。

## 入口分流

| 用户输入 | 路径 | 示例 |
|---|---|---|
| 明确因子 | 因子定义路径 | 「研究 ROE 因子在 A 股有没有用」 |
| 新闻事件 | 新闻因子路径 | 「这条 AI 算力订单新闻能不能量化」 |
| 公司公告 | 事件因子路径 | 「大额回购公告后股价表现怎么样」 |
| 论文 | 论文复现路径 | 「把这篇 paper 的 anomaly 做成因子设计」 |
| 研报 | 研报逻辑路径 | 「这篇研报里的高研发投入逻辑能不能做因子」 |
| 指标/公式 | 指标设计路径 | 「经营现金流/市值有没有 alpha」 |
| 模糊假设 | 假设提炼路径 | 「库存下降是不是好公司」 |
| 策略前置 | 因子池路径 | 「先帮我筛几个适合多因子策略的因子」 |

## 输出目录

默认在以下目录创建本次研究工作区：

```text
~/因子研究/[因子名称]/
```

如果无法确定因子名称，使用可读短名：

```text
~/因子研究/[来源类型]-[核心主题]-[YYYYMMDD]/
```

目录内至少包含：

```text
FACTOR_DESIGN.md
factor_definition.yaml
autostrategy_handoff.yaml
```

新闻、公告、论文、研报入口还应包含：

```text
source_notes.md
```

如果用户指定了输出目录，优先使用用户目录。写入前先确认目录是否已存在；若存在同名文件，不覆盖用户已有文件，改用带时间戳的文件名或询问用户。

## 资源文件

按需读取以下资源，不要一次性加载全部：

| 场景 | 读取文件 |
|---|---|
| 需要参考标准产物样式 | `examples/*.md` 中与入口类型匹配的样例 |
| 需要拆分子任务或交给独立 agent | `prompts/hypothesis_agent.md`、`prompts/source_review_agent.md`、`prompts/factor_design_agent.md`、`prompts/handoff_agent.md` |
| 用户明确要求设计回测方案 | `prompts/factor_backtest_agent.md` 和 `references/backtest_module.md` |

可用自动化脚本：

| 脚本 | 用途 |
|---|---|
| `scripts/scaffold_factor_project.py` | 创建标准因子研究工作区和占位产物 |
| `scripts/quality_check.py` | 检查产物完整性、YAML、危险表述和必填字段 |
| `scripts/validate_handoff.py` | 判断是否满足交给 `autostrategy` 的闸门 |
| `scripts/render_summary.py` | 将因子研究工作区渲染成简洁摘要 |

脚本只做结构化辅助检查，不判断因子是否真实有效，不运行回测。

## 信息来源处理

- 用户粘贴原文、截图转写或摘要时，优先基于用户提供内容提炼。
- 用户提供新闻、公告、论文、研报或网页链接时，读取原文后再设计因子。
- 用户只给标题、作者、公司名或事件名时，先查找可靠来源；论文优先找论文原文，公告优先找交易所/公司公告，新闻优先找原始报道或权威媒体。
- 若来源信息不足，明确标注「待确认信息」，不要把推测写成事实。
- 对近期新闻、公告、论文或市场事件，必须核对日期和来源。

### 证据规范

| 来源类型 | 优先证据 | 必填信息 |
|---|---|---|
| 新闻 | 原始报道、权威媒体、公司回应 | 媒体、发布日期、事件主体、原文链接 |
| 公告 | 交易所公告、公司公告、监管披露 | 公司、公告标题、披露日期、披露时间、链接或文件 |
| 论文 | 期刊页、SSRN、arXiv、DOI、作者主页 | 标题、作者、年份、样本市场、核心结论 |
| 研报 | 券商/机构原文、报告摘要页 | 机构、发布日期、分析师、覆盖对象、核心观点 |
| 指标/公式 | 财报口径、行情字段、用户定义 | 字段定义、单位、频率、可得时间 |

来源不完整时，仍可产出设计，但必须在 `source_notes.md` 和 `FACTOR_DESIGN.md` 中标注「待确认」。

## 入口专属要求

### 新闻事件

必须明确：
- 新闻发生日、发布时间、市场可观察时间。
- 事件主体：公司、行业、主题、供应链或政策对象。
- 事件强度代理变量，如订单金额、市值占比、产能变化、情绪强度、覆盖媒体数量。
- 事件窗口，如公告后 1/5/20/60 个交易日。

### 公司公告

必须明确：
- 公告类型：回购、增持、减持、分红、定增、并购、业绩预告、合同订单等。
- 披露时间是否在交易时段内。
- 停牌、复牌、涨跌停、一字板等可交易性限制。
- 事件强度口径，如回购金额/市值、订单金额/营收、增持比例。

### 论文复现

必须明确：
- 原论文研究市场、样本区间、股票池、调仓频率和持有期。
- 原始因子定义与本地市场替代定义。
- 与原论文不同的地方，如数据源、交易制度、财务披露滞后、样本范围。
- 复现优先级：先复现原始定义，再做本地化改造。

### 研报逻辑

必须明确：
- 研报核心判断、覆盖行业/公司、推荐逻辑和假设链。
- 哪些观点能量化，哪些只能作为解释性背景。
- 研报发布时间与市场已有预期之间的关系。
- 是否存在事后解释或选择性样本风险。

### 明确指标/公式

必须明确：
- 指标口径、单位、频率、是否需要行业内比较。
- 指标是领先变量、同步变量还是滞后变量。
- 财务指标必须处理披露滞后，不得使用尚未披露的数据。

## 工作流程

### Phase 1: 输入理解

识别并记录：
- 来源类型：新闻 / 公告 / 论文 / 研报 / 指标 / 公式 / 用户假设
- 市场范围：A股 / 港股 / 美股 / 其他
- 股票池：全市场 / 指数成分 / 行业 / 自定义标的
- 因子类型：价值 / 质量 / 成长 / 动量 / 反转 / 情绪 / 事件 / 另类数据 / 复合因子
- 用户真正想回答的问题

### Phase 2: 因子假设

把原始信息转成一条可检验假设：
- 经济逻辑必须清楚。
- 预期方向必须明确：正向、负向或不确定。
- 必须说明为什么这个信息可能领先于未来收益。
- 如果只是同步指标或结果指标，要标注滞后风险。

### Phase 3: 因子定义

设计一个可落地的因子：
- 原始变量来自哪里。
- 计算公式是什么。
- 数据频率是什么。
- 何时可观测，何时可交易。
- 如何处理滞后、缺失值、极值、标准化和中性化。
- 如何避免未来函数。

### Phase 4: 测试方案

只设计测试，不执行测试：
- 测试区间
- 调仓频率
- 持有期
- 分组数量
- 基准指数
- 手续费和滑点假设
- 样本内 / 样本外划分
- IC、RankIC、分层收益、多空组合、换手率、覆盖率、稳定性等观察指标

### Phase 5: 结论和下一步

给出研究评级，不给实证结论：
- A：设计清晰，数据可得，值得进入代码测试
- B：逻辑成立，但数据或口径需要确认
- C：可研究，但噪声、滞后或可交易性风险较高
- D：暂不建议继续，因果链或数据可得性不足

如果评级为 A/B，建议下一步可以进入代码测试或交给 `autostrategy` 生成策略设计。不要声称因子有效，除非用户已经提供了可靠实证结果。

### Phase 6: 因子回测方案设计（可选）

仅当用户明确要求“回测方案”“IC/RankIC 检验设计”“分层测试方案”或“下一阶段因子测试”时启用。当前版本只设计回测模块，不生成代码、不运行回测。

输出可新增：

```text
factor_backtest_plan.md
```

该文件应包含：
- 数据准备
- 因子计算时点
- 样本内/样本外划分
- IC/RankIC
- 分层收益
- 多空组合
- 换手率与成本
- 稳健性测试
- 未来函数检查

详细规则见 `references/backtest_module.md`。

### 研究评级标准

用以下维度综合评级：

| 维度 | A | B | C | D |
|---|---|---|---|---|
| 经济逻辑 | 因果链清晰，有领先性 | 逻辑基本成立 | 可能只是相关性 | 因果链断裂 |
| 数据可得性 | 免费或公开数据可稳定获得 | 可获得但口径需确认 | 数据稀疏或替代变量较弱 | 关键数据不可得 |
| 时间可交易性 | 信号早于交易决策 | 有轻微滞后但可处理 | 滞后明显 | 主要依赖未来信息 |
| 覆盖率 | 股票池覆盖充分 | 覆盖中等 | 覆盖较低 | 样本过少 |
| 未来函数风险 | 低 | 可控 | 中高 | 高 |
| 策略适配度 | 可直接进入 autostrategy | 稍作整理可交接 | 需先做大量验证 | 不建议进入策略 |

评级规则：
- A：多数维度为 A，且未来函数风险为低。
- B：没有 D，且未来函数风险可控。
- C：存在明显数据、噪声或可交易性问题，但仍可研究。
- D：关键数据不可得、未来函数风险高、或逻辑无法量化。

## 输出要求

默认输出一个主文档和若干轻量交接文件：

```text
FACTOR_DESIGN.md              # 主报告，给用户阅读和验收
factor_definition.yaml        # 机器可读的因子定义
autostrategy_handoff.yaml     # 交给 autostrategy 的最小策略输入
source_notes.md               # 可选；新闻、公告、论文、研报等来源证据
```

不要生成以下文件：
- `factor_test.py`
- `factor_metrics.json`
- `factor_report.html`
- `requirements.txt`
- 回测结果图表

如果用户要求代码、回测或图表，说明当前版本的默认交付范围是因子设计与交接文件，并建议下一阶段扩展到因子测试。

## FACTOR_DESIGN.md 模板

```markdown
# 因子设计文档

> 本文档仅用于因子研究设计，不构成投资建议。当前阶段未执行代码回测，不能视为因子有效性的实证结论。

## 1. 原始输入

- 来源类型：
- 来源名称 / 链接：
- 发布时间 / 论文年份 / 公告日期：
- 原始内容摘要：
- 用户研究问题：

## 2. 事件时间线

> 新闻、公告、研报和论文入口必须填写；纯指标入口可写「不适用」。

| 时间点 | 事件 | 信息来源 | 当时是否可被市场观察 | 对交易决策的含义 |
|---|---|---|---|---|
| T0 |  |  | 是 / 否 / 待确认 |  |
| T+1 |  |  | 是 / 否 / 待确认 |  |

## 3. 因子假设

- 因子名称：
- 因子类型：
- 适用市场：
- 适用股票池：
- 经济逻辑：
- 预期方向：
- 预期生效周期：
- 主要反例：

## 4. 变量字典

| 变量名 | 含义 | 口径 | 单位 | 频率 | 来源 | 可得时间 | 缺失处理 |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

## 5. 可量化定义

- 原始变量：
- 变量来源：
- 计算公式：
- 数据频率：
- 调仓频率：
- 持有期：
- 信号产生时间：
- 可交易时间：
- 滞后处理：
- 缺失值处理：
- 极值处理：
- 标准化方式：
- 行业 / 市值中性化：

## 6. 测试设计

- 测试区间：
- 基准指数：
- 分组方法：
- 评价指标：
  - IC：
  - RankIC：
  - ICIR：
  - 分层收益单调性：
  - 多空组合收益：
  - 最大回撤：
  - 换手率：
  - 覆盖率：
- 手续费和滑点假设：
- 样本内 / 样本外划分：

## 7. 未来函数检查

- 数据发布时间是否晚于交易决策时间：
- 是否使用了未来财报、未来公告或未来收盘价：
- 是否存在幸存者偏差：
- 是否存在样本选择偏差：
- 风险等级：低 / 中 / 高

## 8. 数据可得性

- 必需数据：
- 免费数据源候选：
- 可能缺失的数据：
- 替代变量：
- 数据清洗难点：

## 9. 反证清单

| 反证条件 | 为什么会削弱因子 | 如何验证 | 触发后的处理 |
|---|---|---|---|
|  |  |  |  |

## 10. 研究评级

- 评级：A / B / C / D
- 经济逻辑评级：
- 数据可得性评级：
- 时间可交易性评级：
- 覆盖率评级：
- 未来函数风险评级：
- 策略适配度评级：
- 是否建议进入代码测试：
- 是否适合交给 autostrategy：
- 关键理由：

## 11. 交接给 autostrategy

- 因子名称：
- 因子方向：
- 适用市场：
- 股票池：
- 调仓频率：
- 持有期：
- 入选规则：
- 剔除规则：
- 风控限制：
- 待测试假设：
- 不允许 autostrategy 自行改动的定义：

## 12. 后续动作

- 下一步验证：
- 可尝试的改进版本：
- 不建议继续的条件：
```

## 入口专属补充模板

根据来源类型，在 `FACTOR_DESIGN.md` 的相关章节补充以下内容。

### 新闻事件补充

```markdown
## 新闻事件补充

- 新闻事件：
- 事件主体：
- 发布时间：
- 市场首次可观察时间：
- 事件强度代理变量：
- 事件窗口：
- 可能已被市场定价的证据：
```

### 公司公告补充

```markdown
## 公告事件补充

- 公司：
- 公告类型：
- 公告标题：
- 披露日期：
- 披露时间：
- 交易时段状态：
- 停牌 / 复牌 / 涨跌停限制：
- 事件强度公式：
```

### 论文复现补充

```markdown
## 论文复现补充

- 论文标题：
- 作者：
- 年份：
- 原始市场：
- 原始样本区间：
- 原始因子定义：
- 本地化替代定义：
- 与原论文的差异：
- 复现优先级：
```

### 研报逻辑补充

```markdown
## 研报逻辑补充

- 机构：
- 报告标题：
- 发布日期：
- 分析师：
- 覆盖对象：
- 核心判断：
- 可量化观点：
- 不可量化背景：
- 选择性样本风险：
```

## factor_definition.yaml 模板

```yaml
factor:
  name:
  display_name:
  type:
  direction: positive # positive / negative / uncertain
  market:
  universe:
  hypothesis:
  formula:
  variables:
    - name:
      meaning:
      source:
      frequency:
      available_at:
      missing_value_handling:
  timing:
    signal_time:
    tradable_time:
    rebalance_frequency:
    holding_period:
  preprocessing:
    lag:
    winsorization:
    standardization:
    neutralization:
      - industry
      - market_cap
  testing:
    start_date:
    end_date:
    benchmark:
    grouping:
    metrics:
      - IC
      - RankIC
      - ICIR
      - group_return_monotonicity
      - long_short_return
      - turnover
      - coverage
  leakage_checks:
    future_data_risk:
    survivorship_bias_risk:
    sample_selection_bias_risk:
  rating:
    grade:
    reason:
```

### YAML 字段约束

生成 `factor_definition.yaml` 时遵守：
- `factor.direction` 只能是 `positive`、`negative`、`uncertain`。
- `factor.market` 只能是 `A股`、`港股`、`美股`、`其他`。
- `factor.type` 只能是 `value`、`quality`、`growth`、`momentum`、`reversal`、`sentiment`、`event`、`alternative`、`composite`。
- `factor.timing.rebalance_frequency` 使用 `daily`、`weekly`、`monthly`、`quarterly`、`event_driven`。
- `factor.rating.grade` 只能是 `A`、`B`、`C`、`D`。
- 日期使用 `YYYY-MM-DD`；未知日期写 `unknown`，不要编造。
- 不确定字段写 `null` 或 `待确认`，不要留空。

## autostrategy_handoff.yaml 模板

```yaml
handoff:
  source_skill: factor-research
  target_skill: autostrategy
  status: design_only
  factor_name:
  market:
  universe:
  strategy_candidate:
    type: multi_factor_stock_selection
    signal_direction:
    rebalance_frequency:
    holding_period:
    entry_rule:
    exit_rule:
    risk_limits:
  fixed_definitions:
    - factor_formula
    - signal_time
    - tradable_time
    - universe
  assumptions_to_test:
    - 
  warnings:
    - 因子尚未完成代码回测，不能视为已验证有效。
```

生成 `autostrategy_handoff.yaml` 时遵守：
- `handoff.status` 固定为 `design_only`。
- `handoff.source_skill` 固定为 `factor-research`。
- `handoff.target_skill` 固定为 `autostrategy`。
- `strategy_candidate.type` 默认使用 `multi_factor_stock_selection`；事件因子可使用 `event_driven_stock_selection`。
- `fixed_definitions` 必须包含 `factor_formula`、`signal_time`、`tradable_time`、`universe`。
- `warnings` 必须包含「因子尚未完成代码回测」。

## source_notes.md 模板

```markdown
# 来源证据记录

## 来源列表

| 来源 | 类型 | 日期 | 链接 / 文件 | 可信度 | 备注 |
|---|---|---|---|---|---|
|  | 新闻 / 公告 / 论文 / 研报 |  |  | 高 / 中 / 低 |  |

## 关键摘录

- 来源：
- 摘要：
- 与因子设计相关的信息：
- 待确认信息：
```

## 质量检查

输出前确认：
- 所有文件写入同一个因子研究工作区。
- `FACTOR_DESIGN.md` 包含原始输入、事件时间线、因子假设、变量字典、可量化定义、测试设计、未来函数检查、数据可得性、反证清单、研究评级、autostrategy 交接块。
- `factor_definition.yaml` 包含机器可读的因子定义、变量、时点、预处理、测试设计和风险检查。
- `autostrategy_handoff.yaml` 只包含策略生成需要的最小输入，并明确 `status: design_only`。
- 新闻、公告、论文、研报入口应输出 `source_notes.md`；纯指标或用户假设入口可省略。
- 新闻、公告、论文、研报入口已使用对应补充模板。
- 对新闻、论文、研报、公告均保留来源、日期和可核查信息。
- 明确区分「设计假设」和「实证结论」。
- 没有生成代码、JSON、HTML 或回测结果。
- 没有推荐实盘交易。

产物生成后运行：

```bash
python3 scripts/quality_check.py <因子研究工作区> --source-type <news|announcement|paper|report|metric|idea>
```

如果准备交给 `autostrategy`，再运行：

```bash
python3 scripts/validate_handoff.py <因子研究工作区>
```

需要快速汇报时运行：

```bash
python3 scripts/render_summary.py <因子研究工作区>
```

## 与 autostrategy 协作

当用户确认进入策略阶段时，把 `FACTOR_DESIGN.md` 和 `autostrategy_handoff.yaml` 作为输入交给 `autostrategy`：

```text
factor-research -> FACTOR_DESIGN.md + autostrategy_handoff.yaml -> autostrategy -> STRATEGY_DESIGN.md
```

### 交接闸门

只有同时满足以下条件，才建议进入 `autostrategy`：
- `FACTOR_DESIGN.md` 已生成。
- `factor_definition.yaml` 已生成。
- `autostrategy_handoff.yaml` 已生成。
- 研究评级为 A 或 B。
- 未来函数风险为低或可控。
- `autostrategy_handoff.yaml` 中 `status: design_only`。

如果评级为 C/D，或未来函数风险高，停止在 `factor-research`，不要交给 `autostrategy` 生成策略。交接时只传递已确认的因子定义、适用市场、股票池、调仓频率、持有期和风险限制。未验证的假设必须标注为「待测试」。

## 示例请求

更多完整样例见 `examples/` 目录。使用时只读取与当前入口匹配的样例。

### 新闻事件

```text
使用 factor-research，把这条 AI 算力订单新闻设计成可测试的事件因子，并输出 FACTOR_DESIGN.md 和 autostrategy_handoff.yaml。
```

预期产物：
- `~/因子研究/新闻-AI算力订单-[日期]/FACTOR_DESIGN.md`
- `factor_definition.yaml`
- `autostrategy_handoff.yaml`
- `source_notes.md`

### 公司公告

```text
使用 factor-research，研究上市公司回购公告能否设计成 A 股事件因子。
```

预期重点：
- 回购金额 / 市值
- 回购上限比例
- 公告披露时间
- 公告后 5/20/60 个交易日窗口

### 论文复现

```text
使用 factor-research，把这篇动量 anomaly 论文复现成适合 A 股的因子设计。
```

预期重点：
- 原论文定义
- A 股本地化替代定义
- 财务披露和涨跌停制度差异
- 复现优先级

### 研报逻辑

```text
使用 factor-research，把这篇研报里的高研发投入逻辑设计成成长因子。
```

预期重点：
- 研发费用 / 营收
- 研发资本化处理
- 行业内标准化
- 高研发但低转化效率的反证条件
