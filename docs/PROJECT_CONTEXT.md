# Yu-Gi-Oh! Ruling Workflow + RAG Project Context

最后同步日期：2026-07-09  
当前 Schema：v2.1.0  
当前正式数据：50 条人工 gold cases  
当前运行环境：Conda `YGO_PROJECT`

本文档是新维护者、Codex 或其他开发代理中途加入项目时的总入口。它说明项目目的、
边界、当前实现、数据契约、证据规范、校验流程和下一阶段工作。字段的最终机器约束以
`docs/operation_case.schema.json` 为准；字段解释和完整枚举以 `docs/schema.md` 为准。

---

## 1. 项目目的

本项目构建一个可供 workflow / RAG 系统使用的游戏王裁定数据集。当前唯一任务是：

> 给定操作或效果处理发生前的局面 `pre_state`，判断候选操作
> `attempted_operation` 在规则上是否合法，并给出可追溯的判断链条。

系统关注规则合法性与裁定正确性，不评价操作收益。

### 当前覆盖

- 卡片或效果能否发动。
- 能否连锁既有连锁项。
- cost 是否可支付、对象是否合法。
- 效果能否按声明方式处理。
- 召唤、攻击宣言、优先权和一回合一次限制。
- 已处理连锁和持续约束对后续处理的影响。

### 当前不覆盖

- 最优操作、最优时点或胜率判断。
- 卡组构筑、换备和环境分析。
- 完整对局模拟或自动寻找获胜路线。
- 没有明确局面与候选操作的泛化策略建议。

越界问题使用 `invalid_question`；信息不足但仍属于裁定任务的问题使用 `depends`。

---

## 2. 当前状态快照

| 项目 | 当前状态 |
|---|---|
| task type | `operation_legality_judgment` (37) / `effect_resolution_judgment` (13) |
| Schema 版本 | `2.1.0` |
| Schema 标准 | JSON Schema Draft 2020-12 |
| 主数据 | `gold_cases/operation_legality_cases.jsonl`，50 行、每行一个对象 |
| 格式化镜像 | `gold_cases/json/case001.json` 至 `case050.json` |
| 输出标签 | `legal` / `illegal` / `depends` / `invalid_question` |
| 证据状态 | 每条 case 均有官方卡片文本及官方 Q&A 或规则书 |
| 自动校验 | Schema 校验、项目业务规则、镜像一致性、13 个负例自测 |
| 环境 | `YGO_PROJECT`，Python 3.13.14，jsonschema 4.26.0 |
| 阶段目标 | 50 条基线已达成；下一阶段为证据复核、质量硬化、CI 与 RAG 评测集 |

---

## 3. 仓库结构与文件职责

```text
yugioh-workflow-rag/
├── check_jsonlschema.py                  # Schema + 项目业务规则校验器
├── environment.yml                       # YGO_PROJECT Conda 环境定义
├── requirements-dev.txt                  # 非 Conda 的校验依赖入口
├── gold_cases/
│   ├── operation_legality_cases.jsonl    # 正式主数据，每行一个 case
│   └── json/
│       ├── case001.json                  # 格式化的人读镜像
│       └── ... case050.json
├── docs/
│   ├── PROJECT_CONTEXT.md                # 本文档，项目交接入口
│   ├── task_scope.md                     # 任务边界与判断流程
│   ├── schema.md                         # v2 字段说明与枚举文档
│   ├── operation_case.schema.json        # 可执行 Draft 2020-12 Schema
│   ├── cases_json_template.md             # case 编写模板
│   └── environment_setup.md              # 环境创建与使用说明
├── log/
│   └── ygo_json_case_changelog.md        # Schema 历史和日常变更日志
├── notes/                                # 裁定研究笔记，不是正式 gold 数据
└── tools/
    └── sync_gold_jsonl.py                # 由格式化 case JSON 重建主 JSONL
```

权威性顺序：

1. `docs/operation_case.schema.json`：机器可接受的数据结构。
2. `check_jsonlschema.py`：Schema 无法表达的跨对象和跨文件规则。
3. `docs/schema.md`：字段语义、设计决策和完整枚举说明。
4. `docs/task_scope.md`：任务边界与输出要求。
5. 本文档：当前状态与接手路线。

如文档与可执行 Schema 不一致，先停止新增数据，确认是否需要升级 Schema；不要通过
绕开校验器来“兼容”新字段。

---

## 4. 开发环境

项目使用独立 Anaconda 环境 `YGO_PROJECT`，环境定义位于 `environment.yml`：

```powershell
conda env create -f environment.yml
conda activate YGO_PROJECT
python check_jsonlschema.py --self-test
```

环境已存在时：

```powershell
conda env update -n YGO_PROJECT -f environment.yml --prune
```

不激活环境也可运行：

```powershell
conda run -n YGO_PROJECT python check_jsonlschema.py --self-test
```

不要把依赖安装到 Anaconda `base` 或系统 Python。若无法使用 Conda，可执行
`python -m pip install -r requirements-dev.txt`，但提交前仍需使用相同版本范围完成校验。

---

## 5. JSON / JSONL 文件标准

正式主文件必须满足：

- UTF-8 编码。
- 每行恰好一个完整 JSON object。
- 不允许注释、空行、尾随逗号或 JSONC 语法。
- case ID 按文件顺序连续：`case_001`、`case_002`……
- 顶层 `schema_version` 固定为 `2.1.0`。
- 主 JSONL 中的每个对象必须与对应格式化 gold JSON 逐对象完全一致。
- `gold_cases/json/caseNNN.json` 用于人工审阅；`gold_cases/` 根层的主 JSONL 是正式批处理入口。

顶层结构：

```json
{
  "id": "case_001",
  "task_type": "operation_legality_judgment",
  "schema_version": "2.1.0",
  "question": "当前这个操作是否在规则内合法？",
  "natural_language_context": "",
  "rule_context": {},
  "pre_state": {},
  "attempted_operation": {},
  "gold_answer": {},
  "case_notes": ""
}
```

除可选的 `case_notes` 外，其余顶层字段均为必填。Schema 大量使用
`additionalProperties: false`，不得擅自加入自由字段。

---

## 6. 核心数据模型

### 6.1 `pre_state`

`pre_state` 是待判断动作发生前的事实快照，不能混入动作执行后的推测结果。核心字段包括：

```json
{
  "state_timing": "before_resolving_C1",
  "phase": "main_phase_1",
  "step": null,
  "damage_step_timing": null,
  "turn_player": "opponent",
  "chain_state": {
    "is_chain_building": true,
    "is_chain_resolving": false,
    "current_chain_links": []
  },
  "resolution_history": [],
  "self_state": {},
  "opponent_state": {},
  "known_constraints": []
}
```

阶段、步骤和伤害步骤时点必须使用 Schema 枚举。未知值使用 `unknown`，不要用空字符串
或临时中文值。

### 6.2 连锁

连锁编号统一为 `C1`、`C2`、`C3`：

- 当前连锁项：`chain_id`。
- 响应某连锁项：`chain_response_to`。
- 待处理连锁项：`chain_id_to_resolve`。
- 已处理连锁项：`resolved_chain_id`。
- 场上卡与连锁关联：`current_chain_id`。

`chain_response_to` 和 `chain_id_to_resolve` 必须引用
`pre_state.chain_state.current_chain_links` 中真实存在的 ID。

### 6.3 场地与纵列

双方主要怪兽区固定为 `m1` 至 `m5`，魔法陷阱区固定为 `s1` 至 `s5`。每个格子统一
使用 `{ "column_index": ..., "card": ... }` 包装；空区域使用 `"card": null`。

`column_index` 从我方视角计算：

```text
self:     m1/s1=1, m2/s2=2, m3/s3=3, m4/s4=4, m5/s5=5
opponent: m1/s1=5, m2/s2=4, m3/s3=3, m4/s4=2, m5/s5=1
```

同纵列判断只比较 `column_index`，不要在 workflow 中再次镜像对方区域。

### 6.4 `attempted_operation`

当前操作类型固定为：

```text
activate_card, activate_effect, normal_summon, special_summon,
set_card, set_monster, select_target, pay_cost, resolve_effect, declare_attack
```

不同分支有不同必填字段：

- `activate_effect`：至少需要 `effect_id`、`activation_location`。
- `activate_card`：至少需要 `activation_location`。
- `resolve_effect`：至少需要 `effect_id`、`chain_id_to_resolve`、
  `declared_resolution`。
- `declare_attack`：至少需要 `attack_type`、`card_location`、`card_zone`。

`chain_response` 不是操作类型，应使用 `chain_response_to` 表达。

### 6.5 cost 与处理动作

cost 类型固定为：

```text
discard, pay_lp, banish, send_to_graveyard
```

各类型字段不能混用：`discard` 需要 `card`；`pay_lp` 需要正整数 `amount`；
`banish` 与 `send_to_graveyard` 需要 `card` 和 `from`。

当前 `resolution_history.result.action` 支持以下动作：

```text
destroy, banish, special_summon, send_to_graveyard,
return_to_hand, return_to_extra_deck, return_to_field,
negate_monster_effects_until_end_of_turn,
negate_effects_and_halve_atk,
apply_same_column_spell_trap_negation,
change_to_face_down_defense
```

`resolution_history` 是每条 case 必填的状态词条。没有已处理连锁块时写空数组 `[]`；
有内容时只记录当前判断点之前已经按规则处理完成的连锁块，并按实际处理顺序排列。
持续限制继续写入 `known_constraints`，不要混入 history。

### 6.6 `effect_features`

`effect_features` 是机器枚举，不接受自由中文描述；自然语言解释写入 `effect_summary`。
新增 feature 前必须同步修改机器 Schema、`docs/schema.md`、校验器或测试以及 changelog。

Schema v2 对 I:P 语义使用三个互相兼容但含义不同的 feature：

```text
perform_link_summon_after_chain_link_resolution
includes_special_summon_effect
resulting_monster_not_summoned_by_activated_effect
```

旧值 `grant_link_summon_opportunity` 已废弃，正式数据中不得出现。

### 6.7 `known_constraints`

持续或已经适用的限制放入 `known_constraints`。S:P 的直接攻击限制使用结构化对象：

```json
{
  "type": "attack_restriction",
  "restriction": "cannot_direct_attack",
  "affected_player": "self",
  "effect_scope": "monster",
  "duration": "until_end_of_turn",
  "source_card": "S:P小夜骑士"
}
```

`effect_scope` 只能是 `monster` 或 `player`。怪兽不受效果影响时，只能绕过作用于怪兽的
限制，不能绕过作用于玩家的限制。

---

## 7. `gold_answer` 与判断标准

```json
{
  "label": "legal",
  "conclusion": "",
  "failed_check": null,
  "reasoning_steps": [],
  "missing_info": [],
  "required_sources": []
}
```

标签语义：

- `legal`：已知局面足以确认操作或声明处理合法。
- `illegal`：已知局面足以确认操作或声明处理不合法。
- `depends`：属于任务范围，但缺失决定性事实；`missing_info` 必须非空。
- `invalid_question`：问题不属于本项目的规则合法性任务。

`failed_check` 应指向判断流程中最先失败的检查点，例如 `activation_window`、
`activation_condition`、`chain_speed`、`cost_payability`、`target_legality`、
`once_per_turn`、`effect_resolution_rule`。合法 case 通常使用 `null`。

推荐判断顺序：

1. 是否存在合法操作窗口。
2. 操作能否在该窗口发动或执行。
3. 发动条件、召唤条件或攻击条件是否满足。
4. cost 是否存在且可支付。
5. 对象是否合法、处理时是否仍满足要求。
6. 一回合一次或状态刷新规则是否限制本次操作。
7. 持续效果、玩家限制、区域和其他外部条件是否影响结论。
8. 输出标签、结论、逐步理由、缺失信息和证据。

---

## 8. 严格证据契约

`gold_answer.required_sources` 存放真实证据对象，不存检索占位符。允许类型：

```text
official_card_text
official_ruling
official_rulebook
secondary_reference
```

每条正式 case 至少包含：

- 一项 `official_card_text`；以及
- 一项 `official_ruling` 或 `official_rulebook`。

二手材料只能补充解释，不能成为唯一裁定依据。官方来源要求：

- `authority` 为 `KONAMI`。
- URL 来自 `yugioh-card.com` 官方域名。
- 卡片文本使用 `cid:<数字>`。

若某张关键卡没有可访问的 KONAMI 简中官方卡片正文页，允许使用本地 `cards.cdb`/`cards.db` 中的中文卡名和效果文本作为 `secondary_reference`（`authority: local_cards_cdb`，URL 使用 `local-cdb://` 前缀），以满足中文文本覆盖要求。非官方中文卡文仅供中文本地化参考，不得伪装成 `official_card_text`，也不得成为独立裁定依据。
- Q&A 使用 `fid:<数字>`；卡片补充页可使用 `cid:<数字>#supplement`。
- 规则书使用 `rulebook:<标识>`。
- `accessed_at` 使用 `YYYY-MM-DD`。
- `supports_reasoning_steps` 使用从 1 开始的推理步骤编号，不能越过
  `reasoning_steps` 长度。

来源 ID 格式为 `src_case_001_01`，并要求在整个主 JSONL 内全局唯一。找不到足够官方
证据的样例不得进入正式主数据，应保留在待复核集合中，禁止伪造 URL、标题、cid 或 fid。

---

## 9. Schema v2 的关键裁定决策

### case_003：S:P 直接攻击限制

最终结论保持 `legal`。限制建模为 `effect_scope: "monster"`；因此“不受其他卡效果影响”
的电子界到临者可以绕过该怪兽效果施加的直接攻击限制。若同一限制被建模为
`effect_scope: "player"`，则不能用怪兽抗性绕过。

### case_005：I:P 的召唤语义

最终结论保持 `illegal / activation_condition`。I:P 的效果“包含特殊召唤效果”，但连接
召唤在连锁块处理后执行，结果怪兽不视为“因发动的怪兽效果被特殊召唤”。这正是三个
v2 feature 必须同时存在、又不能合并成单一布尔值的原因。

---

## 10. 当前 50 条 gold cases

| ID | 场景 | 操作 | 结论 | task_type |
|---|---|---|---|---|
| `case_001` | 灰流丽连锁闪刀启动：交闪 | `activate_effect` | `legal` | `operation_legality_judgment` |
| `case_002` | 无限泡影同纵列无效烙印之气炎 | `resolve_effect` | `illegal / effect_resolution_rule` | `effect_resolution_judgment` |
| `case_003` | S:P 限制下全抗怪兽直接攻击 | `declare_attack` | `legal` | `operation_legality_judgment` |
| `case_004` | 凤凰人延迟特召与神之通告 | `activate_card` | `illegal / activation_condition` | `operation_legality_judgment` |
| `case_005` | I:P 连接召唤与赫焉龙②条件 | `activate_effect` | `illegal / activation_condition` | `operation_legality_judgment` |
| `case_006` | 连接召唤后优先权与尼比鲁 | `activate_effect` | `illegal / activation_window` | `operation_legality_judgment` |
| `case_007` | 冰剑龙被盖放后下回合再次发动 | `activate_effect` | `illegal / once_per_turn` | `operation_legality_judgment` |
| `case_008` | 天救龙离开手牌后的分项处理 | `resolve_effect` | `legal` | `effect_resolution_judgment` |
| `case_009` | 龙引导呼笛与场上卡名视为 | `resolve_effect` | `legal` | `effect_resolution_judgment` |
| `case_010` | 公开手牌中的露世与篝自排连锁 | `activate_effect` | `legal` | `operation_legality_judgment` |
| `case_011` | 联合机库发动处理中同连锁特召联合怪兽 | `activate_effect` | `illegal / activation_window` | `operation_legality_judgment` |
| `case_012` | 超融合禁止任何卡或效果连锁 | `activate_card` | `illegal / chain_speed` | `operation_legality_judgment` |
| `case_013` | 宏观宇宙下舍弃至墓地 cost 不可支付 | `activate_effect` | `illegal / cost_payability` | `operation_legality_judgment` |
| `case_014` | 光之护封剑可成为同连锁回手对象 | `activate_effect` | `legal` | `operation_legality_judgment` |
| `case_015` | 伤害步骤中龙骑兵团不受技能抽取影响 | `activate_effect` | `legal` | `operation_legality_judgment` |
| `case_016` | 米德拉什限制下不能发动尼比鲁 | `activate_effect` | `illegal / summon_condition` | `operation_legality_judgment` |
| `case_017` | 路西菲尔同时特召两只同名堕天使 | `resolve_effect` | `legal` | `effect_resolution_judgment` |
| `case_018` | 颠茄歌后仍受技能抽取持续效果影响 | `resolve_effect` | `illegal / effect_resolution_rule` | `effect_resolution_judgment` |
| `case_019` | 西兰提斯在水属性特召限制下处理 | `activate_effect` | `legal` | `operation_legality_judgment` |
| `case_020` | 大搜捕对象同连锁变里侧后的处理 | `resolve_effect` | `legal` | `effect_resolution_judgment` |
| `case_021` | 召唤成功时不能先发动起动效果 | `activate_effect` | `illegal / activation_window` | `operation_legality_judgment` |
| `case_022` | 欧贝利斯克召唤成功时封锁发动 | `activate_card` | `illegal / activation_window` | `operation_legality_judgment` |
| `case_023` | 神之警告连锁包含特殊召唤处理的发动 | `activate_card` | `legal` | `operation_legality_judgment` |
| `case_024` | 场上灵摆怪兽不能送墓作为 cost | `activate_card` | `illegal / cost_payability` | `operation_legality_judgment` |
| `case_025` | 墓穴指名者对象处理时离开墓地 | `resolve_effect` | `illegal / target_legality` | `effect_resolution_judgment` |
| `case_026` | 编号38 效果直接进行伤害计算 | `activate_effect` | `illegal / phase_or_step_restriction` | `operation_legality_judgment` |
| `case_027` | 魔封之芳香限制灵摆怪兽作为魔法发动 | `activate_card` | `illegal / activation_condition` | `operation_legality_judgment` |
| `case_028` | 陷阱诡计后陷阱发动被无效的次数计算 | `activate_card` | `legal` | `operation_legality_judgment` |
| `case_029` | 王家长眠之谷限制墓地自身特召手续 | `special_summon` | `illegal / external_restriction` | `operation_legality_judgment` |
| `case_030` | 抽牌小丑与封锁鸟下双螺旋特工选择替代处理 | `resolve_effect` | `legal` | `effect_resolution_judgment` |
| `case_031` | 卢恩神碑之泉在整条连锁处理后另开触发 | `activate_effect` | `legal` | `operation_legality_judgment` |
| `case_032` | "不能对应这个发动连锁"只限制直接连锁 | `activate_card` | `legal` | `operation_legality_judgment` |
| `case_033` | 同一连锁中已展示手牌可再次作为展示 cost | `activate_effect` | `legal` | `operation_legality_judgment` |
| `case_034` | 食魂窃蛋龙对象被失落世界替代破坏后的后续处理 | `resolve_effect` | `illegal / effect_resolution_rule` | `effect_resolution_judgment` |
| `case_035` | 灾难兽与大地鼹鼠在伤害步骤开始时组链处理 | `resolve_effect` | `illegal / effect_resolution_rule` | `effect_resolution_judgment` |
| `case_036` | 无视召唤条件仍要求特殊召唤怪兽正规出场履历 | `resolve_effect` | `illegal / summon_condition` | `effect_resolution_judgment` |
| `case_037` | 一回合一次的 ● 项目被无效仍算已选择 | `activate_effect` | `illegal / once_per_turn` | `operation_legality_judgment` |
| `case_038` | 发动的效果不被无效不保护发动本身 | `activate_card` | `legal` | `operation_legality_judgment` |
| `case_039` | 替代破坏不能选择不受影响或不会被破坏的卡 | `activate_effect` | `illegal / external_restriction` | `operation_legality_judgment` |
| `case_040` | 暂时除外期间发生的卡通世界破坏不追溯 | `activate_effect` | `illegal / effect_resolution_rule` | `operation_legality_judgment` |
| `case_041` | 陷阱怪兽作为潜海奇袭cost | `activate_effect` | `legal` | `operation_legality_judgment` |
| `case_042` | 战斗卷回取消后不视为进行过战斗 | `activate_effect` | `illegal / activation_condition` | `operation_legality_judgment` |
| `case_043` | 卡通世界被破坏后直接攻击卷回 | `declare_attack` | `illegal / external_restriction` | `operation_legality_judgment` |
| `case_044` | 刚角笛使对方抽卡后暗律跨阶段发动 | `activate_effect` | `legal` | `operation_legality_judgment` |
| `case_045` | 光之护封剑自毁不受白龙忍者保护 | `resolve_effect` | `legal` | `effect_resolution_judgment` |
| `case_046` | 通道限制下灵摆召唤区域冲突 | `special_summon` | `illegal / zone_availability` | `operation_legality_judgment` |
| `case_047` | 次元墙转嫁伤害不触发三进制术士 | `activate_effect` | `illegal / activation_condition` | `operation_legality_judgment` |
| `case_048` | 暗之咒缚降攻后特里斯坦保护时间差 | `select_target` | `illegal / target_legality` | `operation_legality_judgment` |
| `case_049` | 战斗破坏替送去牌组仍给予伤害 | `resolve_effect` | `legal` | `effect_resolution_judgment` |
| `case_050` | 阿卡纳解读两项处理均不可用 | `activate_card` | `illegal / activation_condition` | `operation_legality_judgment` |

这些 case 是 seed 集合，不代表已经覆盖完整规则空间。官方数据库更新后仍需复核其
`source_updated_at`、卡片文本和裁定有效性。

---

## 11. 自动校验

校验分两层。

### JSON Schema 层

`docs/operation_case.schema.json` 使用 `Draft202012Validator` 和 `FormatChecker`，检查：

- JSON 类型、必填字段和 `additionalProperties`。
- 固定枚举、正则格式和日期/URI。
- cost / action 的 `oneOf` 分支。
- 各 `operation_type` 的条件必填字段。
- `depends` 与非空 `missing_info`。
- 官方来源类型、域名和 ID 格式。
- 每条 case 的官方卡片文本及官方裁定/规则书覆盖。

### Python 业务层

`check_jsonlschema.py` 额外检查：

- JSONL 不含空行且每行可解析。
- case ID 全局唯一、连续且顺序正确。
- 连锁 ID 唯一，引用指向当前连锁。
- `resolution_history` 必填；已处理连锁引用、逆顺处理顺序、时点描述与非空结果必须一致。
- source ID 全局唯一，证据步骤不越界。
- 正式 case 原则上必须同时包含 `official_card_text` 的 `ja` 与 `zh-CN` 来源；无法定位有效简中官方正文时必须列入显式待复核例外，不得伪造来源。
- `official_ruling` 必须填写 `source_updated_at`。
- 双方 `column_index` 映射正确。
- `case_003` 和 `case_005` 的关键语义及结论不回退。
- 50 个格式化 gold JSON 与主 JSONL 完全一致。

校验器采用面向对象结构：`CaseDatasetValidator` 持有预编译的 Schema validator、
项目路径和业务规则注册表；`ValidationIssue` 表示单项错误；`ValidationResult` 汇总
解析后的 cases 与全部错误。命令行 `main()` 只负责参数解析、结果展示和退出码，其他
Python 模块也可以直接调用类接口，不需要捕获终端输出。

标准验收命令：

```powershell
conda run -n YGO_PROJECT python check_jsonlschema.py --self-test
```

当前期望输出：正式数据通过 Schema 和业务校验，13 个内存负例全部被拒绝。校验器返回
非零退出码时，不得合并数据变更。

---

## 12. 新增或修改 case 的标准流程

1. 明确问题属于当前任务边界，并写清被判断的唯一操作。
2. 检索官方卡片文本、官方 Q&A 或官方规则书；记录访问日期和官方 ID。
3. 先编辑对应的格式化 `gold_cases/json/caseNNN.json`。
4. 只使用 Schema 已登记字段和枚举；需要新枚举时先走 Schema 版本变更。
5. 将同一对象压成单行，同步到 `gold_cases/operation_legality_cases.jsonl` 的正确位置。
6. 确认 ID 连续、来源 ID 全局唯一、推理步骤与证据覆盖对应。
7. 运行 `python check_jsonlschema.py --self-test`。
8. 人工 dry-run 判断链，重点检查时点、cost、对象、一次限制与持续约束。
9. 更新 `log/ygo_json_case_changelog.md`；若改变结构，同时更新 Schema 和相关文档。

十条 seed case 的 v2 迁移已经完成，一次性迁移脚本不再保留。后续数据变更必须通过
人工编辑、主 JSONL 同步和镜像一致性校验完成。

---

## 13. Changelog 规范

`log/ygo_json_case_changelog.md` 分为两部分：

- Part 1：Schema 版本历史。结构或兼容性变化使用语义化版本，并写明 Added / Changed、
  裁定依据、迁移方式和兼容性影响。
- Part 2：日常更新日志。按日期倒序追加 Summary、Changed/Added、Validation、Decision
  等必要小节。

维护规则：

- 历史条目不重写；当前快照、Completed、Pending、Risks、Next Actions 可随项目刷新。
- 数据、Schema、校验器和文档发生联动时，日志必须明确列出影响文件。
- 裁定结论变化必须记录旧结论、新结论、证据和受影响 case。
- 只更新环境或工具时，也要记录实际版本和验证命令。

---

## 14. 兼容性与废弃项

- 当前正式数据只接受 `schema_version: "2.1.0"`。
- `grant_link_summon_opportunity` 已废弃，拆分为三个 I:P 语义 feature。
- 旧的自由字符串 `direct_attack_restriction` 已废弃，改用结构化
  `attack_restriction`。
- `official_card_ruling` 合并为 `official_ruling`。
- `rulebook` 更名为 `official_rulebook`。
- `movement_correct` / `movement_incorrect` 不再是输出标签。
- 数字 `chain_link: 1` 不再使用，统一为字符串 `chain_id: "C1"`。

新增字段或枚举会影响现有 50 条数据、JSON Schema、校验器、自测和下游 workflow。
任何此类修改都必须先评估是否升级 minor/major 版本。

---

## 15. 风险与待办

### 主要风险

- Git 尚未配置为有效仓库：根目录 `.git` 为空，由用户稍后自行处理。
- 官方 Q&A 或卡片文本会更新，当前证据日期不代表永久有效。
- `effect_features` 自由扩张会造成 workflow 匹配不稳定。
- 忽略 `resolution_history` 会使复杂连锁处理失真。
- 错误区分“效果包含特殊召唤”与“怪兽因发动的效果被特殊召唤”会回退 case_005。
- 错误区分作用于怪兽与作用于玩家的限制会回退 case_003。
- 主 JSONL 与格式化 gold 文件双写，必须依赖镜像一致性校验防止漂移。

### Pending

- 持续复核 50 条 gold case 的官方 Q&A 更新日期和裁定有效性。
- 为新增场景扩充枚举时建立更系统的回归负例。
- 建立 CI，设计 RAG 检索评测集。
- 评估是否在 CI 中自动执行 `check_jsonlschema.py --self-test`。

### 下一步

1. 对现有 50 条 case 做逐条人工 dry-run 和官方证据复核。
2. 建立新增 case 的候选与待复核集合，证据齐全后再进入主 JSONL。
3. 按规则类型平衡扩充数据，而不是只围绕少数卡片堆叠相似问题。
4. 后续扩充前先完成 50 条基线的证据复核与质量硬化。

---

## 16. 接手者最短检查清单

开始工作前依次确认：

```powershell
conda env list
conda run -n YGO_PROJECT python --version
conda run -n YGO_PROJECT python check_jsonlschema.py --self-test
```

然后阅读：

1. `docs/task_scope.md`
2. `docs/schema.md`
3. `docs/operation_case.schema.json`
4. `log/ygo_json_case_changelog.md` 中最新日期条目和底部 Open Items

若三条校验命令通过、`gold_cases` 内主 JSONL 为 50 行且 `gold_cases/json/` 内格式化镜像为 50 个文件，
则当前基线完整。
