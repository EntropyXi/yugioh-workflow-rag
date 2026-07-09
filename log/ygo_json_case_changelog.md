# Current Snapshot

项目当前使用 `schema_version: "2.1.0"`，正式数据入口为
`gold_cases/operation_legality_cases.jsonl`，共 50 条 gold cases；
格式化镜像位于 `gold_cases/json/case001.json` 至 `case050.json`。

当前 `task_type` 分布：

- `operation_legality_judgment`：37 条；
- `effect_resolution_judgment`：13 条。

当前校验状态：

- `check_jsonlschema.py --self-test` 覆盖 Schema、业务规则、镜像一致性与 13 个内存负例；
- 正式数据规则已强化为：每条 case 原则上必须同时包含日文与简中官方卡片文本来源；
- `official_ruling` 必须填写 `source_updated_at`；
- `case_048` 因关键卡暂未定位有效简中官方正文，作为显式待复核来源例外保留，不伪造来源；
- `.git` 尚未配置为有效仓库，由用户稍后自行处理。

---

# 2026-07-09 - case_047/case_048 本地中文卡文覆盖与待复核清理

## Summary

本轮不新增 case、不改变裁定结论。修正 case_047/case_048 的错误中文卡名、错误的 `resolution_history` action，
并通过本地 `cards.cdb` 的 `secondary_reference` 提供非官方中文卡文覆盖。校验器从硬豁免改为「官方简中或 approved local secondary 二选一」规则。

## Changed

- `case_047`：卡名「三进制术士」→「二进制女巫」、「次元墙」→「次元壁」；
  `resolution_history` action 从错误的 `negate_effects_and_halve_atk` 改为 `redirect_battle_damage`；
  新增 local CDB 中文卡文来源。
- `case_048`：卡名统一为「圣骑士 崔斯坦」「圣骑士 高文」「暗之咒缚」；
  `resolution_history` action 从错误的 `negate_effects_and_halve_atk` 改为 `apply_attack_decrease_and_restrictions`；
  新增 local CDB 中文卡文来源。
- `docs/operation_case.schema.json`：新增 `redirect_battle_damage` 与 `apply_attack_decrease_and_restrictions` 两个 action。
- `check_jsonlschema.py`：
  - 删除仅针对 case_048 的旧 `SOURCE_TEXT_REVIEW_EXEMPTIONS`；
  - 新增「中文卡文覆盖」规则：`official_card_text zh-CN` 或 `secondary_reference zh-CN + authority:local_cards_cdb` 二选一；
  - 新增 3 个负例（缺少 CN 文本覆盖、local 伪装成 official、local 缺少 local-cdb:// URI）；
  - `self_test_count` 从 13 → 16。

## Validation

- 已通过 `conda run -n YGO_PROJECT python check_jsonlschema.py --self-test`：
  50 条正式 case 通过 Schema、业务规则、镜像一致性校验，16 个负例均被拒绝

---
# 2026-07-09 - 项目卫生与来源覆盖质量硬化

## Summary

本轮不新增 case，不修改已有裁定结论；集中处理 50 条数据后的项目卫生、文档真实态、来源覆盖和校验硬化。

## Changed

- 补齐 `case_001`–`case_010`、`case_044`、`case_045`、`case_047`、`case_049`、`case_050` 的日文/简中官方卡片文本覆盖缺口。
- 为 `case_041`、`case_042`、`case_043`、`case_044`、`case_045`、`case_047`、`case_048`、`case_049`、`case_050` 的官方 Q&A 来源补充 `source_updated_at`。
- `case_047` 增加待复核说明：当前 case 叙述卡名与 `fid:21113` 官方 Q&A 标题存在不一致，需要后续人工复核。
- `case_048` 增加待复核说明：相关关键卡未能定位有效简中官方正文，暂列显式来源例外，不伪造 `zh-CN` 来源。
- `check_jsonlschema.py` 新增正式数据来源覆盖规则：原则上要求 `official_card_text` 同时包含 `ja` 与 `zh-CN`；`official_ruling` 必须包含 `source_updated_at`。
- 负例自测从 11 个扩展为 13 个，新增缺少简中卡片文本来源与缺少 Q&A 更新日期的拒绝场景。
- `docs/PROJECT_CONTEXT.md` 更新为 50 条真实当前态，记录 37/13 `task_type` 分布、13 个负例、当前 Pending 与风险。
- `docs/task_scope.md` 将“第一阶段 50 条”改为已达成，并记录下一阶段质量目标。
- `docs/split_effect_resolution_task_type_plan.md` 标记为历史已执行计划。
- `docs/schema.md` 同步来源覆盖规则与 13 个负例说明。

## Validation

- 已通过 `conda run -n YGO_PROJECT python check_jsonlschema.py --self-test`：
  50 条正式 case 通过 Schema、业务规则、镜像一致性校验，13 个负例均被拒绝。

---

# 2026-07-08 - Schema v2.1.0：拆分 effect_resolution_judgment 为独立 task_type

## Summary

将 `task_type` 从单值常量扩展为二值枚举。凡 `operation_type` 为 `resolve_effect`
的 case，其 `task_type` 从 `operation_legality_judgment` 变更为
`effect_resolution_judgment`。不改变任何 case 的裁定结论、pre_state、
attempted_operation 结构或 gold_answer 内容。

## Changed

- `docs/operation_case.schema.json`：`task_type` 从 `const` 改为 `enum`
  `["operation_legality_judgment", "effect_resolution_judgment"]`
- `gold_cases/json/case002.json` 等 11 个镜像文件：`task_type` 值变更
- `gold_cases/operation_legality_cases.jsonl`：11 行同步
- `check_jsonlschema.py`：新增 task_type 与 operation_type 一致性业务规则，
  负例自测从 10 个扩展为 11 个
- 更新 `docs/schema.md`、`docs/PROJECT_CONTEXT.md`、`docs/task_scope.md`、
  `docs/cases_json_template.md` 中的 task_type 说明

## Affected Cases

| ID | 场景 | 新 task_type |
|---|---|---|
| case_002 | 无限泡影同纵列无效烙印之气炎 | `effect_resolution_judgment` |
| case_008 | 天救龙离开手牌后的分项处理 | `effect_resolution_judgment` |
| case_009 | 龙引导呼笛与场上卡名视为 | `effect_resolution_judgment` |
| case_017 | 路西菲尔同时特召两只同名堕天使 | `effect_resolution_judgment` |
| case_018 | 颠茄歌后仍受技能抽取持续效果影响 | `effect_resolution_judgment` |
| case_020 | 大搜捕对象同连锁变里侧后的处理 | `effect_resolution_judgment` |
| case_025 | 墓穴指名者对象处理时离开墓地 | `effect_resolution_judgment` |
| case_030 | 抽牌小丑与封锁鸟下双螺旋特工选择替代处理 | `effect_resolution_judgment` |
| case_034 | 食魂窃蛋龙对象被失落世界替代破坏后的后续处理 | `effect_resolution_judgment` |
| case_035 | 灾难兽与大地鼹鼠在伤害步骤开始时组链处理 | `effect_resolution_judgment` |
| case_036 | 无视召唤条件仍要求特殊召唤怪兽正规出场履历 | `effect_resolution_judgment` |

## Compatibility

- 命令、类接口、退出码保持不变
- case 数据顶层结构不变，仅 `task_type` 多了一个合法值
- 29 条 `operation_legality_judgment` case 与 11 条 `effect_resolution_judgment`
  case 同时合法
- 旧 task_type 值 `operation_legality_judgment` 依然有效
- 裁定结论均未修改

## Validation

- 已通过 `conda run -n YGO_PROJECT python check_jsonlschema.py --self-test`：
   40 条正式 case 均通过 Schema、业务规则、镜像一致性校验，11 个负例均被拒绝

---
# 2026-07-08 - 全量 bump schema_version 至 2.1.0

## Summary

将全部 40 条 case 的 `schema_version` 数据字段及 Schema 文件中的 `const` 值
从 `"2.0.0"` bump 至 `"2.1.0"`。此前 task_type 已拆分为二值 enum 但
schema_version 未同步；此次统一 eliminates 语义矛盾。

## Changed

- `docs/operation_case.schema.json`：`schema_version.const` 从 `"2.0.0"` → `"2.1.0"`
- `gold_cases/json/case001.json`–`case040.json`：全部 40 条 `schema_version` 替换
- `gold_cases/operation_legality_cases.jsonl`：同步
- 更新 `docs/schema.md`、`docs/PROJECT_CONTEXT.md`、`docs/cases_json_template.md`
  中的版本号引用

## Validation

- 已通过 `conda run -n YGO_PROJECT python check_jsonlschema.py --self-test`：
  40 条正式 case 均通过，11 个负例均被拒绝

---
# 2026-07-08 - 扩充官方来源 gold cases 至 50 条

## Summary

新增 `case_041`–`case_050`，均为逐条逐源核验的 KONAMI 官方 Q&A 裁定。
覆盖：陷阱怪兽cost、战斗卷回、攻击条件丧失、跨阶段诱发、维持规则vs效果破坏、
区域限制×灵摆召唤、伤害转嫁归属、持续效果时间差、战斗破坏替代、部分适用性发动条件。

## Added

- `case_041`：`fid:8194`，陷阱怪兽可被当作水属性cost除外；涉及潜海奇袭、金属反射史莱姆。
- `case_042`：`fid:20246`，战斗卷回后取消攻击不视为进行过战斗；涉及魔玩具·钩手海怪。
- `case_043`：`fid:15529`，卡通世界在战斗步骤被破坏后直接攻击卷回；涉及卡通电子龙。
- `case_044`：`fid:16682`，刚角笛让对方抽卡后暗律②可在结束阶段发动；涉及假面－英雄 暗法。
- `case_045`：`fid:12583`，光之护封剑自毁是维持规则≈不受效果破坏保护；涉及白龙忍者。
- `case_046`：`fid:24318`，通道限制与灵摆召唤的EMZ/区域优先冲突；涉及I:P伪装舞会莱娜。
- `case_047`：`fid:21113`，次元墙转嫁伤害不视为怪兽给予的战斗伤害；涉及三进制术士。
- `case_048`：`fid:13728`，连续降攻效果与对象保护的时间差；涉及圣骑士特里斯坦、暗之咒缚。
- `case_049`：`fid:8320`，战斗破坏怪兽替送去牌组仍触发伤害效果；涉及地缚神Ccapac Apu。
- `case_050`：`fid:6408`，投硬币效果两项均不可用时不能发动；涉及阿卡纳解读、雷王。

## Changed

- `gold_cases/json/case041.json`–`case050.json`：新增10条case。
- `gold_cases/operation_legality_cases.jsonl`：同步至50行。
- `docs/PROJECT_CONTEXT.md`：case数量 40→50，更新状态表和case表。

## Validation

- 已通过 `conda run -n YGO_PROJECT python check_jsonlschema.py --self-test`：
  50 条正式 case 均通过 Schema、业务规则、镜像一致性校验，11 个负例均被拒绝

---
# 游戏王裁定数据集 JSON 格式与 Case 构建日志
项目名称：Yu-Gi-Oh! Operation Legality Judgment Dataset | 当前 Schema 版本：v2.1.0 | 当前数据文件：`gold_cases/operation_legality_cases.jsonl` | 当前任务目标：判断给定局面下，当前操作或当前效果处理是否在规则内合法。 | 当前输出标签：`legal` / `illegal` / `depends` / `invalid_question`
---
# 2026-07-07 - 扩充官方来源 gold cases 至 40 条

在 `gold_cases/json/` 中新增 `case031.json` 至 `case040.json`，并通过
`tools/sync_gold_jsonl.py` 同步主数据
`gold_cases/operation_legality_cases.jsonl` 至 40 行。新增 case 均逐条核验
KONAMI 官方 Q&A，并补充日文及简中官方卡片详情来源。

## Added

- `case_031`：`fid:23650`，卢恩神碑之泉②在整条连锁处理后另开时点发动，可选择作为契机且已送墓的「神碑」速攻魔法。
- `case_032`：`fid:16924`，“不能对应这个发动连锁”只限制直接连锁；发动者自己追加连锁后，对方可继续连锁。
- `case_033`：`fid:24176`，同一连锁中已经展示过的手牌仍可再次作为展示 cost。
- `case_034`：`fid:20675`，食魂窃蛋龙对象被失落世界替代破坏而未破坏时，后续墓地特殊召唤不适用。
- `case_035`：`fid:7840`，灾难兽与大地鼹鼠在伤害步骤开始时组链；逆顺处理后灾难兽处理不适用。
- `case_036`：`fid:23799`，无视召唤条件从墓地等区域特殊召唤特殊召唤怪兽时，仍要求正规出场履历。
- `case_037`：`fid:23977`，一回合只能选择一次的 `●` 项目，即使发动或效果被无效也算已选择；因原候选 `cid:18917` 缺有效简中正文，改用同一 Q&A 同样适用列表中的 `cid:16094`。
- `case_038`：`fid:21378`，“发动的效果不会被无效”不保护发动本身不被无效。
- `case_039`：`fid:20948`，替代破坏不能选择不受影响或不会被效果破坏的卡。
- `case_040`：`fid:24348`，卡通怪兽暂时除外期间「卡通世界」被破坏，返回后不追溯自毁。

## Changed

- `docs/operation_case.schema.json` 增补 case_031–case_040 实际使用的最小 `effect_features` 枚举。
- `resolution_history.result.action` 增补 `send_to_graveyard`、`return_to_hand`、`return_to_extra_deck`、`return_to_field`，用于表达已处理连锁造成的送墓与返回类状态变化。
- `docs/schema.md` 同步新增枚举与处理动作说明。
- `docs/PROJECT_CONTEXT.md` 当前快照更新为 40 条 gold cases。

## Validation

- 已通过 `conda run -n YGO_PROJECT python check_jsonlschema.py --self-test`：
  40 条正式 case 均通过 Schema、业务规则、镜像一致性校验，10 个负例均被拒绝。

---
# 2026-07-07 - 全量必填 resolution_history 并规则化校验

## Summary

将 `pre_state.resolution_history` 从可选辅助字段升级为 30 条正式 case 全部显式填写的状态词条。
没有已处理连锁块的 case 使用空数组 `[]`；有已处理连锁块的 case 只记录当前判断点之前已经按规则处理完成的连锁结果。

## Changed

- `docs/operation_case.schema.json`：`pre_state.resolution_history` 加入必填字段。
- `check_jsonlschema.py`：新增 `resolution_history` 业务校验，检查已处理连锁引用、逆顺处理顺序、时点一致性和非空结果。
- `check_jsonlschema.py --self-test`：负例自测从 6 个扩展为 10 个，新增缺失 history、错误 history 引用、错误 history 顺序、空 result。
- `gold_cases/json/case001.json` 至 `case030.json`：全部显式包含 `resolution_history`。
- 修复 `case_025`、`case_028` 的 `resolution_history` 及相关中文字段中由编码问题产生的问号占位。
- 复核并修复 `case_021` 至 `case_030` 中同类问号占位文本；不改变裁定结论和官方来源。
- 更新 `docs/schema.md`、`docs/cases_json_template.md`、`docs/PROJECT_CONTEXT.md` 的必填语义和校验说明。

## Validation

- `conda run -n YGO_PROJECT python check_jsonlschema.py --self-test` 通过：
  30 条正式 case 均通过 Schema、业务规则、镜像一致性校验，10 个负例均被拒绝。

---
# 2026-07-07 - 扩充官方来源 gold cases 至 30 条

在 `gold_cases/json/` 中新增 `case021.json` 至 `case030.json`，并通过
`tools/sync_gold_jsonl.py` 同步主数据
`gold_cases/operation_legality_cases.jsonl` 至 30 行。新增 case 均逐条核验
KONAMI 官方 Q&A，并补充日文及简中官方卡片详情来源。

## Added

- `case_021`：`fid:10040`，召唤成功时不能先发动起动效果。
- `case_022`：`fid:8159`，欧贝利斯克召唤成功时只在该时点封锁发动。
- `case_023`：`fid:23408`，神之警告可连锁包含特殊召唤处理的卡的发动。
- `case_024`：`fid:24195`，场上灵摆怪兽通常不能送墓作为「禁忌的一滴」cost。
- `case_025`：`fid:10677`，墓穴指名者对象处理时离开墓地则不除外且不适用同名无效。
- `case_026`：`fid:17979`，编号38 效果直接进行伤害计算时没有中间发动窗口。
- `case_027`：`fid:13149`，魔封之芳香适用中不能新发动灵摆怪兽到灵摆区域。
- `case_028`：`fid:22010`，陷阱诡计后陷阱“发动被无效”不计入那 1 次发动。
- `case_029`：`fid:20408`，王家长眠之谷限制墓地自身特殊召唤手续。
- `case_030`：`fid:14784`，抽牌小丑与封锁鸟适用中，秘旋谍－双螺旋可选择墓地回收或特殊召唤等替代处理。

## Changed

- `docs/operation_case.schema.json` 增补 case_021–case_030 实际使用的最小
  `effect_features` 枚举，并为 `monster_type` 增加 `pendulum`。
- `docs/schema.md` 同步新增枚举与 `pendulum` 卡片类型说明。
- `docs/PROJECT_CONTEXT.md` 当前快照更新为 30 条 gold cases。
- `case_030` 按官方 Q&A 正文使用「ドロール＆ロックバード / 抽牌小丑与封锁鸟」，
  不沿用候选描述中错误的「增殖的 G」表述。

## Validation

- 已通过 `conda run -n YGO_PROJECT python check_jsonlschema.py --self-test`：
  30 条正式 case 均通过 Schema、业务规则、镜像一致性校验，6 个负例均被拒绝。

---
# 2026-07-07 - 迁移格式化 gold JSON 至子目录

将 `gold_cases/` 根层的格式化单 case JSON 镜像迁移到
`gold_cases/json/`，避免与正式主数据
`gold_cases/operation_legality_cases.jsonl` 混放。主 JSONL 路径、case
内容、Schema 版本和裁定结论均未改变。

## Changed

- `case001.json` 至 `case020.json` 的当前路径变更为
  `gold_cases/json/case001.json` 至 `gold_cases/json/case020.json`。
- `check_jsonlschema.py` 的镜像一致性检查改为扫描 `gold_cases/json/case*.json`。
- `tools/sync_gold_jsonl.py` 改为从 `gold_cases/json/case*.json` 重建主 JSONL。
- 更新当前有效文档中的格式化镜像路径；历史日志中的旧路径保持原样。

## Validation

- 已通过 `conda run -n YGO_PROJECT python check_jsonlschema.py --self-test`。
- 已确认程序化接口返回 `20 0 True`，且 `gold_cases/` 根层不再残留
  `case*.json`。

---
# 2026-07-07 - 扩充官方来源 gold cases 至 20 条

在 `gold_cases/` 中新增 `case011.json` 至 `case020.json`，并同步主数据
`gold_cases/operation_legality_cases.jsonl` 至 20 行。新增 case 均以 KONAMI
官方 Q&A 为裁定依据，并补充日文及简中官方卡片详情来源；若原候选无法取得
可访问简中官方详情，则替换为证据完整的官方 Q&A。

## Added

- `case_011`：`fid:19471`，联合机库发动处理中同连锁特召联合怪兽，不能另开发动。
- `case_012`：`fid:10824`，超融合禁止任何卡或效果连锁。
- `case_013`：`fid:23815`，替代除外适用中“舍弃”与“舍弃至墓地”cost 差异。
- `case_014`：`fid:8129`，光之护封剑可成为同连锁回手效果对象。
- `case_015`：`fid:23062`，伤害步骤中龙骑兵团怪兽不受技能抽取影响而可发动效果。
- `case_016`：`fid:22804`，神影依・米德拉什限制下不能发动原始生命态 尼比鲁。
- `case_017`：`fid:6900`，同时特殊召唤同名一回合一次怪兽的处理。
- `case_018`：`fid:21716`，“不受发动的效果影响”仍受技能抽取持续效果影响。
- `case_019`：`fid:23819`，世海龙 西兰提斯在水属性特殊召唤限制下的发动与处理。
- `case_020`：`fid:11049`，大搜捕对象在同一连锁上变里侧后的控制权和限制适用。
- 新增 `tools/sync_gold_jsonl.py`，用于从格式化 gold JSON 镜像重建主 JSONL。

## Changed

- `docs/operation_case.schema.json` 增补新增 case 实际使用的最小枚举：
  `special_summon_from_graveyard`、`prevent_chain_to_activation`、
  `negate_face_up_monster_effects_continuously`、
  `banish_all_monsters_temporarily`、
  `special_summon_banished_monsters_as_many_as_possible`、
  `change_to_face_down_defense`。
- `docs/schema.md` 同步新增枚举，并记录简中官方文本可使用
  `request_locale=cn` 的 KONAMI 官方卡片详情页。
- `docs/PROJECT_CONTEXT.md` 当前快照更新为 20 条 gold cases。

## Validation

- `conda run -n YGO_PROJECT python check_jsonlschema.py` 通过：20 条正式 case
  均通过 Schema、业务规则和镜像一致性校验。

---
# Part 1. JSON 格式变化日志
## v0.1.0 - 初始 Case 格式
状态：已废弃；目的：建立最小可用 case 结构。

### Added
初始格式包含以下核心字段：
```json
{
  "id": "case_001",
  "task_type": "operation_legality_judgment",
  "question": "当前这个操作是否在规则内合法？",
  "natural_language_context": "",
  "rule_context": {},
  "pre_state": {},
  "attempted_operation": {},
  "gold_answer": {},
  "case_notes": ""
}
```
### Design Notes
初始设计确定了三段式结构：
```text
pre_state = 操作发生前的局面
attempted_operation = 当前尝试执行的操作
gold_answer = 人工标注的裁定结果
```
### Limitations
- `field` 使用数组表达，例如 `monster_zones: []`，无法表达具体位置。
- 连锁编号使用数字字段 `chain_link: 1`。
- 没有统一的列编号系统，不能稳定判断同纵列。
- 没有 `resolution_history`，不能表达已经处理过的连锁结果。
- `effect_features` 部分仍接近自然语言，workflow 不易读取。
---
## v0.2.0 - 移除 JSON 注释，建立标准 JSON / JSONL 约束
状态：已采用；目的：保证 case 文件可以被标准 JSON parser 直接读取。

### Changed
正式 case 文件不再使用：
```jsonc
"phase": "main_phase_1", // 当前阶段
```

改为标准 JSON：
```json
"phase": "main_phase_1"
```
### Added
字段说明迁移到独立文档：
```text
schema.md
```

正式数据文件建议使用：
```text
operation_legality_cases.jsonl
```
### Decision
- `cases.jsonl` 中不写注释。
- 字段解释、枚举表、命名规范写入 `schema.md`。
- 若开发阶段确实需要注释，可另建 JSONC 草稿文件，但进入评测前必须转换为标准 JSON。
---
## v0.3.0 - 增加阶段与步骤字段
状态：已采用；目的：表达操作发生的规则时点。

### Added
在 `pre_state` 中加入：
```json
{
  "phase": "main_phase_1",
  "step": null,
  "damage_step_timing": null
}
```
### Field Definition
`phase` 表示当前大阶段：
```text
draw_phase
standby_phase
main_phase_1
battle_phase
main_phase_2
end_phase
unknown
```

`step` 表示阶段内部步骤：
```text
null
start_step
battle_step
damage_step
end_step
unknown
```

`damage_step_timing` 表示伤害步骤内部时点：
```text
null
start_of_damage_step
before_damage_calculation
during_damage_calculation
after_damage_calculation
end_of_damage_step
unknown
```
### Decision
第一批 cases 可以主要使用：
```json
"phase": "main_phase_1",
"step": null,
"damage_step_timing": null
```

涉及伤害步骤时再填写 `damage_step_timing`。
---
## v0.4.0 - 重构场上区域 field 结构
状态：已采用；目的：表达怪兽区、魔法陷阱区、场地魔法区、额外怪兽区的具体位置。

### Changed
旧格式：
```json
"field": {
  "monster_zones": [],
  "spell_trap_zones": [],
  "field_spell_zone": null,
  "extra_monster_zones": []
}
```

新格式：
```json
"field": {
  "monster_zones": {
    "m1": { "column_index": 1, "card": null },
    "m2": { "column_index": 2, "card": null },
    "m3": { "column_index": 3, "card": null },
    "m4": { "column_index": 4, "card": null },
    "m5": { "column_index": 5, "card": null }
  },
  "spell_trap_zones": {
    "s1": { "column_index": 1, "card": null },
    "s2": { "column_index": 2, "card": null },
    "s3": { "column_index": 3, "card": null },
    "s4": { "column_index": 4, "card": null },
    "s5": { "column_index": 5, "card": null }
  },
  "field_spell_zone": null,
  "extra_monster_zones": {
    "emz_left": { "column_index": null, "card": null },
    "emz_right": { "column_index": null, "card": null }
  }
}
```
### Decision
- 空位统一使用 `"card": null`。
- 卡片不直接写在 `s1` 或 `m1` 中，而是写入 `card` 对象。
- 该结构同时用于 `self_state.field` 和 `opponent_state.field`。
---
## v0.5.0 - 统一场地魔法区域命名
状态：已采用；目的：避免 `field.field_zone` 语义混淆。

### Changed
旧字段：
```json
"field_zone": null
```

新字段：
```json
"field_spell_zone": null
```
### Decision
统一使用：
```text
field_spell_zone
```

含义为：场地魔法区域。
---
## v0.6.0 - 增加 column_index 统一纵列判断
状态：已采用；目的：解决我方与对方区域左右方向相反的问题。

### Added
每个主怪兽区与魔法陷阱区加入：
```json
"column_index": 4
```
### Mapping Rule
以我方视角为基准：
```text
self m1 / s1 = column_index 1
self m2 / s2 = column_index 2
self m3 / s3 = column_index 3
self m4 / s4 = column_index 4
self m5 / s5 = column_index 5

opponent m1 / s1 = column_index 5
opponent m2 / s2 = column_index 4
opponent m3 / s3 = column_index 3
opponent m4 / s4 = column_index 2
opponent m5 / s5 = column_index 1
```
### Use Case
判断「无限泡影」同纵列时，只比较：
```text
source.column_index == target.column_index
```
### Decision
不再在 workflow 中通过 `opponent_m_i -> self_m_(6-i)` 手动换算，统一使用 `column_index`。
---
## v0.7.0 - 规范 effect_features 枚举
状态：已采用；目的：让 workflow 能直接读取效果特征。

### Changed
旧写法：
```json
"effect_features": [
  "从卡组把卡加入手卡"
]
```

新写法：
```json
"effect_features": [
  "add_from_deck_to_hand"
]
```
### Added Feature Examples
灰流丽相关：
```text
add_from_deck_to_hand
special_summon_from_deck
send_from_deck_to_graveyard
```

无限泡影相关：
```text
target_opponent_face_up_effect_monster
negate_target_monster_effects_until_end_of_turn
set_before_activation
negate_spell_trap_effects_in_same_column_if_resolved_on_field
```

破坏类效果：
```text
target_1_card_on_field
target_1_face_up_card_on_field
target_1_opponent_card_on_field
destroy_target
choose_1_card_on_field_on_resolution
destroy_chosen_card
```
### Fixed
修正拼写错误：
```text
destory_target_card -> destroy_target
```
### Decision
- `effect_summary` 保留自然语言。
- `effect_features` 使用稳定英文枚举。
- 是否取对象、何时选择、处理动作必须拆开表达。
---
## v0.8.0 - 明确 operation_type 与 effect_id 规则
状态：已采用；目的：区分发动卡、发动效果、效果处理等不同裁定对象。

### Added
`attempted_operation.operation_type` 枚举：
```text
activate_card
activate_effect
normal_summon
special_summon
set_card
set_monster
select_target
pay_cost
resolve_effect
```
### Changed
连锁响应不再作为独立 `operation_type`：
```json
"operation_type": "chain_response"
```

改为：
```json
"operation_type": "activate_effect",
"chain_response_to": "C1"
```
### Added
`effect_id` 用于区分同一张卡的不同效果：
```json
"effect_id": "effect_1",
"effect_label": "①"
```
### Decision
- 只有一个主要效果时，可以使用 `"effect_id": "main_effect"`。
- 需要表达①②效果时，使用 `"effect_id": "effect_1"` / `"effect_id": "effect_2"`。
- 原文编号可写入 `"effect_label": "①"` / `"effect_label": "②"`。
---
## v0.9.0 - 连锁编号改为 C1 / C2 / C3
状态：已采用；目的：统一连锁表示，避免数字与字段语义混淆。

### Changed
旧格式：
```json
"chain_link": 1
```

新格式：
```json
"chain_id": "C1"
```

旧格式：
```json
"chain_response_to": 1
```

新格式：
```json
"chain_response_to": "C1"
```

旧格式：
```json
"current_chain_link": 2
```

新格式：
```json
"current_chain_id": "C2"
```
### Changed Related Fields
```text
resolved_chain_link -> resolved_chain_id
chain_link_to_resolve -> chain_id_to_resolve
before_resolving_chain_link_1 -> before_resolving_C1
```
### Decision
所有连锁编号统一使用大写：
```text
C1, C2, C3, ...
```
---
## v1.0.0 - 增加效果处理型 case 支持
状态：已采用；目的：支持“当前效果处理是否在规则内合法”的 case。

### Added
`state_timing`：
```json
"state_timing": "before_resolving_C1"
```

`is_chain_resolving`：
```json
"is_chain_resolving": true
```

`resolution_history`：
```json
"resolution_history": [
  {
    "resolved_chain_id": "C3",
    "card": "落胤与圣女",
    "result": [
      {
        "action": "destroy",
        "card": "烙印之气炎",
        "from": "opponent.field.spell_trap_zones.s2",
        "to": "opponent.graveyard"
      }
    ]
  }
]
```

`known_constraints`：
```json
"known_constraints": [
  {
    "type": "same_column_spell_trap_negation",
    "source_card": "无限泡影",
    "source_zone": "self.field.spell_trap_zones.s4",
    "affected_column_index": 4,
    "duration": "until_end_of_turn"
  }
]
```
### Added attempted_operation for effect resolution
```json
"attempted_operation": {
  "player": "opponent",
  "operation_type": "resolve_effect",
  "card": "烙印之气炎",
  "effect_id": "effect_1",
  "effect_label": "①",
  "chain_id_to_resolve": "C1",
  "activation_location_at_activation": "spell_trap_zone",
  "activation_zone_at_activation": "s2",
  "activation_column_index": 4,
  "current_card_location": "graveyard",
  "declared_resolution": "resolve_successfully",
  "declared_effect_purpose": "apply_branded_in_high_spirits_effect"
}
```
### Decision
若判断的是“某个效果是否能成功处理”，则：
```text
attempted_operation.operation_type = resolve_effect
```

其他连锁块、cost、对象、已经处理的结果，分别写入：
```text
pre_state.chain_state.current_chain_links
pre_state.resolution_history
 pre_state.known_constraints
 ```
---
## v2.0.0 - 拆分召唤语义、结构化攻击限制并引入可追溯证据
状态：已采用；目的：消除 schema 与正式数据之间的枚举漂移，并使 gold answer 的依据可审计。

### Changed
- 所有正式 case 新增 `schema_version: "2.0.0"`。
- 废弃 `grant_link_summon_opportunity`，拆分为：
  - `perform_link_summon_after_chain_link_resolution`
  - `includes_special_summon_effect`
  - `resulting_monster_not_summoned_by_activated_effect`
- 废弃 `direct_attack_restriction`，改用 `attack_restriction`，并明确
  `restriction`、`affected_player`、`effect_scope` 与 `duration`。
- `required_sources` 从检索词占位符迁移为含 URL、官方 ID、访问日期和
  推理步骤映射的证据对象。
- `source_type` 固定为 `official_card_text`、`official_ruling`、
  `official_rulebook`、`secondary_reference`。
- `official_card_ruling` 与 `rulebook` 分别迁移为 `official_ruling` 与
  `official_rulebook`。

### Ruling Basis
- Konami FAQ 23173：I:P 进行的连接召唤不使结果怪兽成为“被发动的怪兽效果特殊召唤”。
- Konami FAQ 23933：进行连接召唤的效果仍包含“特殊召唤效果”。
- 「S:P小夜骑士」官方补充信息：直接攻击限制持续影响怪兽，不受怪兽效果影响的怪兽可以直接攻击。

### Compatibility
v2 是破坏性迁移。缺少 `schema_version`、使用废弃枚举或仍只有 `query` 的
来源对象均不能进入正式 JSONL。

### Decision
后续枚举变更必须同时更新 `schema.md`、校验器与 changelog；正式 gold case
至少需要官方卡片文本，以及官方 Q&A 或规则书之一。

---
# Part 2. 日常更新日志
## 2026-07-07 - 集中整理正式 gold 数据目录
### Summary
将 `gold cases` 重命名为无空格的 `gold_cases`，并把正式聚合 JSONL 从仓库根目录
移入该目录，使主数据与 10 个格式化人工审阅镜像集中管理。

### Changed
- 正式主数据路径变更为 `gold_cases/operation_legality_cases.jsonl`。
- `check_jsonlschema.py` 的 `GOLD_DIR` 与 `DEFAULT_JSONL` 同步指向新位置。
- 更新环境说明、case 模板、Schema 文档和 `PROJECT_CONTEXT.md` 中的活动路径。
- 主 JSONL 仍是唯一正式批处理入口，`case001.json` 至 `case010.json` 仍是逐对象镜像。

### Compatibility
- `python check_jsonlschema.py`、`--self-test`、类接口和退出码保持不变。
- Schema 版本、字段结构、10 条 case 内容及裁定结论均未修改。
- 历史日志中的旧路径保留；`.obsidian/workspace.json` 由编辑器自行刷新。

### Validation
- `gold_cases` 包含 1 个主 JSONL 和 10 个格式化 JSON。
- 主 JSONL 保持 10 行且无空行。
- `python check_jsonlschema.py --self-test` 通过 Schema、业务规则、镜像一致性与
  6 个内存负例测试。

---
## 2026-07-07 - 将 JSONL 校验器重构为面向对象结构
### Summary
在不改变 Schema、业务规则、命令行参数、输出格式和退出码语义的前提下，对
`check_jsonlschema.py` 进行结构性重构，使校验能力既可由 CLI 使用，也可由后续
workflow、测试或编辑工具直接调用。

### Changed
- 新增 `ValidationIssue` dataclass，统一保存文件、行号、JSON 路径和错误信息。
- 新增 `ValidationResult` dataclass，统一返回已解析 cases、错误集合、`is_valid` 和
  `error_count`。
- 新增 `CaseDatasetValidator`，集中管理预编译的 `Draft202012Validator`、Schema 路径、
  主 JSONL、gold 目录、业务规则、镜像校验及负例自测。
- 将 `case_003` 与 `case_005` 的防回退规则拆成独立方法，并通过 case rule 注册表调用。
- 将场地区域纵列映射提取为独立校验方法。
- 将参数构建抽离为 `build_parser()`；`main()` 只保留 CLI 编排、打印和退出码处理。
- `docs/PROJECT_CONTEXT.md` 补充校验器的对象模型与程序化调用定位。

### Compatibility
- `python check_jsonlschema.py`、`--self-test`、`--schemafile/-s` 和多 JSONL 文件参数
  保持不变。
- 成功、失败、自测和 `--help` 的用户可见输出保持原格式。
- Schema 内容、10 条 gold cases 及其裁定结论均未修改。

### Validation
- 源码通过内存语法编译检查。
- `python check_jsonlschema.py --self-test` 通过：10 条正式 case 合法，6 个负例被拒绝。
- `CaseDatasetValidator().validate_file(DEFAULT_JSONL)` 返回 10 条 cases、0 个错误，
  `is_valid == True`。
- 重构前后 `--help` 与成功校验输出一致。

---
## 2026-07-07 - 完整同步项目上下文与接手规范
### Summary
依据 Schema v2、10 条正式 seed cases、严格证据契约、双层校验器及新建的
`YGO_PROJECT` Conda 环境，完整重写 `docs/PROJECT_CONTEXT.md`，替换只记录
case_001、case_002 的早期项目说明。

### Changed
- 当前快照更新为 Schema v2.0.0、10 条 gold cases、Draft 2020-12 Schema 与
  Python 业务校验并行的实际状态。
- 补充真实仓库结构、权威文件顺序、Conda 环境、JSON/JSONL 镜像规则、严格来源
  契约、Schema v2 兼容性和新增 case 工作流。
- 记录 `case_003` 的攻击限制作用域与 `case_005` 的 I:P 三段召唤语义，防止后续
  维护时发生裁定语义回退。
- 补充 changelog 维护规范、当前风险、Pending、Next Actions 和接手检查清单。
- 刷新本文件底部 Open Items，使环境配置、项目上下文和标准校验命令与当前实现一致。

### Validation
- 使用 `YGO_PROJECT` 运行 `python check_jsonlschema.py --self-test`：10 条正式 case
  通过 Schema 与业务校验，6 个内存负例均被拒绝。
- 人工核对主 JSONL、10 个格式化 gold JSON、Schema、校验器和上下文中的版本、
  文件名及枚举描述。

---
## 2026-07-07 - 建立项目专用 Conda 环境
### Summary
新增独立的 `YGO_PROJECT` 开发环境，为 Schema 与 JSONL 校验提供可复现的
Python 运行时，避免依赖系统 Python 或 Anaconda base 环境。

### Added
- 新增 `environment.yml`，固定环境名为 `YGO_PROJECT`、Python 为 3.13，
  并声明 `jsonschema[format]>=4.18,<5`。
- 新增 `docs/environment_setup.md`，记录环境创建、激活、同步及免激活运行方式。
- `docs/schema.md` 的自动校验章节改为优先使用项目 Conda 环境，并保留
  `requirements-dev.txt` 作为非 Conda 安装入口。

### Validation
- 环境创建于 `D:\anaconda3\envs\YGO_PROJECT`。
- 实际版本为 Python 3.13.14、jsonschema 4.26.0。
- 在该环境中运行 `python check_jsonlschema.py --self-test` 成功：10 条正式 case
  通过 Schema 与业务校验，6 个内存负例均被拒绝。

---
## 2026-07-07 - 新增可执行 JSON Schema 并升级校验器
### Summary
新增 Draft 2020-12 格式的 `docs/operation_case.schema.json`，将字段类型、枚举、
cost/action 分支、来源条件和 `depends` 条件从 Python 常量迁移到机器可读 schema。

### Changed
- `check_jsonlschema.py` 从逐行调用 `jsonschema.validate()` 改为预编译一次
  `Draft202012Validator` 并通过 `iter_errors()` 返回每条 case 的全部错误。
- Schema 在校验数据前通过 `check_schema()` 自检，并启用 URI/date 格式检查。
- 空行由静默跳过改为正式错误；错误信息增加 JSON 路径。
- 保留 Python 业务层，检查全局 ID、连锁引用、纵列映射、证据步骤范围和
  gold JSON 镜像一致性。
- 新增 `requirements-dev.txt`，声明 `jsonschema[format]` 依赖。

### Validation
10 条 schema v2 case 通过 Schema 与业务双层校验；6 个内存负例均被拒绝。

---
## 2026-07-07 - 完成 Schema v2 与 10 条 seed case 证据迁移
### Summary
将全部 `case_001` 至 `case_010` 迁移到 v2，补齐 Konami 官方卡片详情、Q&A
或规则书链接，并建立自动校验。

### Changed
- `case_003` 使用结构化 `attack_restriction`，结论保持 `legal`。
- `case_005` 使用三项召唤语义 feature，结论保持 `illegal / activation_condition`。
- 10 个格式化 gold JSON 与主 JSONL 同步增加 `schema_version` 和严格证据对象。
- 统一任务边界文档中的输出标签。

### Validation
- 主 JSONL 共 10 行，全部可解析且 ID 连续唯一。
- 10 个 gold JSON 与主 JSONL 逐对象一致。
- 负例覆盖废弃 feature、废弃 constraint、废弃 source type、缺失 URL、
  非法 cost、空 `depends.missing_info` 与错误的攻击限制作用对象。

### Decision
第一批 seed cases 已达到 10/10。下一阶段转为官方证据持续复核、自动校验维护
及扩充到 50 条人工 gold cases。

---
## 2026-07-05 - 建立 case_003：全抗怪兽直击宣言 / 新增 declare_attack 操作类型
### Summary
构建第三条 case，覆盖战斗阶段攻击宣言裁定，同步扩展 `operation_type` 枚举。

### Scenario
```text
我方在额外怪兽区域 Link 召唤了 S:P小夜骑士，发动效果①除外了对方怪兽。
进入战斗阶段，我方使用主要怪兽区域的电子界到临者@火灵天星进行直接攻击宣言。
```
### Added
- `operation_type: declare_attack`（schema.md 枚举 v1 → v1.1）
- `attempted_operation.attack_type`
- `known_constraints` 新 type：`direct_attack_restriction`
- `resolution_history` 中 `banish` action 使用例

### Gold Answer
```json
"label": "legal"
```
### Reason
S:P小夜骑士的"自己的怪兽不可直接攻击"属于影响怪兽的限制（非对玩家效果），而电子界到临者@火灵天星不受其他卡的效果影响，因此该限制不适用，直接攻击宣言合法。裁定依据来自"关于全抗怪兽攻击宣言的一些裁定"笔记。

---
## 2026-07-05 - 建立 case_004：凤凰人准备阶段特召 / 神之通告无效效果特召
### Summary
构建第四条 case，覆盖神之通告（无效特召侧）能否无效效果产生的延迟不入连锁特召。

### Scenario
```text
上回合对方场上的命运英雄 毁灭凤凰人被雷击破坏，效果③发动并处理，下个准备阶段从墓地不入连锁特殊召唤自身。
我方盖放了神之通告。进入对方准备阶段，凤凰人效果③的延迟特召适用，我方试图发动神之通告（无效特召侧）无效该特召。
```
### Added
- `declared_cost` 新 type：`pay_lp`
- `phase: standby_phase` 使用例

### Gold Answer
```json
"label": "illegal"
```
### Reason
凤凰人效果③在破坏时已入连锁发动并处理，准备阶段的特召是效果的延迟应用。该特召虽不入连锁，但属于"效果产生的特殊召唤"而非"召唤手续"。神之通告的无效特召侧只能无效召唤手续类的不入连锁特召（如同调、超量、连接），不能无效效果产生的特召。因此神之通告无法发动。素材来源于B站视频 BV1RvrUYBEhJ。

---
## 2026-07-05 - 建立 case_005：IP连接召唤 / 赫焉龙②发动条件
### Summary
构建第五条 case，覆盖"进行连接召唤的效果"是否满足"让怪兽特殊召唤的效果"这一发动条件。

### Scenario
```text
对方场上存在 I：P伪装舞会莱娜，发动其怪兽效果宣言连接召唤。
我方场上存在赫焉龙 大木偶剧场龙，试图连锁发动其②效果（对方发动的怪兽效果让怪兽特殊召唤的场合可以发动）。
```
### Added
- `effect_features` 新增：`grant_link_summon_opportunity`

### Gold Answer
```json
"label": "illegal"
```
### Reason
IP的效果是"进行连接召唤的效果"——赋予玩家连接召唤机会，实际召唤通过游戏规则完成，不属于"用卡的效果特殊召唤"。赫焉龙②以"对方效果让怪兽特殊召唤"为发动条件，IP不满足该条件，因此赫焉龙不能发动。素材来源于B站视频 BV1Zjcne1EDo。

---
## 2026-07-05 - 建立 case_006：连接召唤后优先权 / 尼比鲁抢先发动
### Summary
构建第六条 case，覆盖连接召唤等不入连锁操作后优先权是否转移。

### Scenario
```text
我方回合进行了多次召唤（含连接召唤镇魂棺），进入自由时点。我方尚未选择是否发动效果，
对方试图抢先C1从手牌发动尼比鲁的①效果。
```
### Gold Answer
```json
"label": "illegal"
```
### Reason
连接召唤不转移优先权，回合玩家在召唤后仍持有优先权。非回合玩家必须等回合玩家放弃优先权或发动效果后才能行动。素材来源于B站视频 BV17bPVeKE1X。

---
## 2026-07-05 - 建立 case_007：冰剑龙②效果被日全食之书盖放后下回合能否再用
### Summary
构建第七条 case，覆盖怪兽在里侧状态下处理自身效果并附加自我限制后，翻开是否保留该限制。

### Scenario
```text
上回合 C1 冰剑龙②效果 → C2 日全食之书将冰剑龙盖放。C1处理时冰剑龙已是里侧，除外怪兽并适用"下个回合不可使用此效果"。
结束阶段日全食之书将冰剑龙翻开。本回合对方主要阶段，我方试图再次发动冰剑龙②效果。
```
### Gold Answer
```json
"label": "illegal"
```
### Reason
冰剑龙处理②效果时自身为里侧，限制在里侧状态下被适用。日全食之书结束阶段翻开（里→表）不丢失已适用的限制信息，因此下回合不可使用②效果。与表→里（丢失信息）相反。素材来源于B站视频 BV1b7VgzZEXu。

---
## 2026-07-05 - 建立 case_008：天救龙被一滴送墓后●项是否独立处理
### Summary
构建第八条 case，覆盖多项●效果中某一项因条件不满足无法执行时，后续项是否仍可正常处理。

### Scenario
```text
C1 对方史拿奇①效果 → C2 我方天救龙展示手牌此卡与额外5只同步怪兽（合计6张）→ C3 我方禁忌的一滴将天救龙作为cost送墓。
C3处理后天救龙在墓地。C2处理时●2特召无法执行（不在手牌），●4将马龙送墓和●6破坏对方怪兽是否仍可处理。
```
### Gold Answer
```json
"label": "legal"
```
### Reason
天救龙的●项之间互不干涉，前一项不成功不影响后续项。●2特召虽无法执行，●4送墓和●6破坏仍可正常处理。素材来源于B站视频 BV1kL6jBmEhb。

---
## 2026-07-05 - 建立 case_009：龙引导呼笛特召黑衣龙后因卡名视为阿不思再特召阿不思
### Summary
构建第九条 case，覆盖改变卡名的永续效果在怪兽登场时是否即时生效，从而影响"同名怪兽"判断。

### Scenario
```text
我方场上有白之圣女·艾克莉西娅（魔法师族），对方场上有3只青眼白龙。
我方发动龙引导呼笛①效果，先从牌组特召黑衣龙·阿尔比昂（Lv5以上龙族）。
黑衣龙的永续效果使其在场上卡名视为阿尔白斯之落胤，进而宣言从牌组特召阿不思作为同名怪兽。
```
### Gold Answer
```json
"label": "legal"
```
### Reason
改变卡名的永续效果在怪兽召唤・特召时以改变后的状态直接登场。黑衣龙特召到场上时卡名已是阿不思，因此龙引导呼笛的第二段效果可从牌组特召真正的阿不思。素材来源于B站视频 BV1jCQMB2ERm。

---
## 2026-07-05 - 建立 case_010：看透心灵之眼下闪刀姬火刀与手牌露世自排连锁
### Summary
构建第十条 case，覆盖手牌被持续公开时手牌诱发效果是否能与其他公开区域诱发效果自排连锁。

### Scenario
```text
对方场上有看透心灵之眼（使我方手牌持续公开）、完美卡通世界和卡通怪兽。
我方零解放自身特召篝至EX区，触发窗口打开。篝①和手牌露世①均满足条件，
我方试图自排连锁：C1篝①（回收魔法）、C2露世①（从手牌特召自身）。
```
### Gold Answer
```json
"label": "legal"
```
### Reason
手牌诱发效果通常有延迟发动的特权，但当手牌被持续公开（看透心灵之眼）时该特权失效，变为公开区域选发诱发，与篝①同层级，可按玩家喜好自排连锁。素材来源于B站视频 BV1vGVd6UEA7。

---
## 2026-06-10 - 建立裁定数据集任务边界
### Summary
确定第一阶段任务不是构筑完整规则引擎，而是先建立可评测的裁定样例数据。

### Added
- 定义任务类型：`operation_legality_judgment`
- 定义核心问题：`当前这个操作是否在规则内合法？`
- 定义输出标签：
  - `legal`
  - `illegal`
  - `depends`
  - `invalid_question`

### Decision
第一阶段重点判断：
```text
给定 pre_state 与 attempted_operation，判断该操作是否规则合法。
```
### Notes
不在当前任务中引入裁定合法性以外的评价目标。
---
## 2026-06-10 - 建立第一版 case_001：灰流丽连锁交闪
### Summary
构建第一条 seed case：对方发动「闪刀启动：交闪」，我方连锁发动「灰流丽」。

### Added
`case_001` 初始内容：
```text
C1：对方发动「闪刀启动：交闪」
Attempted Operation：我方从手牌发动「灰流丽」连锁 C1
Gold Answer：legal
```
### Added Fields
- `natural_language_context`
- `pre_state.chain_state`
- `attempted_operation`
- `gold_answer.reasoning_steps`
- `required_sources`

### Decision
该 case 的结论为：
```text
legal
```

理由：
```text
对方效果包含从卡组加入手牌；
灰流丽在手牌；
本回合未发动过灰流丽；
存在连锁发动窗口。
```
---
## 2026-06-10 - 标准 JSON 与 schema 文档分离
### Summary
确认 JSON 无合法注释语法，因此正式 case 文件必须为纯 JSON。

### Changed
开发说明不再写入 case JSON 内部。

### Added
建议文件结构：
```text
cases/
  operation_legality_cases.jsonl

schemas/
  operation_legality_schema.md
  operation_legality_schema.json
```
### Decision
- 正式数据使用 JSONL。
- 字段说明写入 Markdown schema 文档。
- 不在 case 中使用 `//` 或 `/* */` 注释。
---
## 2026-06-10 - 场上区域位置建模
### Summary
将 `field` 从简单数组升级为固定槽位结构。

### Changed
旧格式：
```json
"monster_zones": []
```

改为：
```json
"monster_zones": {
  "m1": { "column_index": 1, "card": null },
  "m2": { "column_index": 2, "card": null },
  "m3": { "column_index": 3, "card": null },
  "m4": { "column_index": 4, "card": null },
  "m5": { "column_index": 5, "card": null }
}
```
### Added
- `m1` 至 `m5`
- `s1` 至 `s5`
- `field_spell_zone`
- `extra_monster_zones`
- `column_index`

### Decision
空位使用：
```json
"card": null
```

有卡时写成：
```json
"card": {
  "name": "无限泡影",
  "status": "face_down",
  "card_type": "trap",
  "controller": "self"
}
```
---
## 2026-06-10 - 统一同纵列判断方式
### Summary
确定使用 `column_index` 解决双方视角左右相反的问题。

### Added
对方区域映射：
```text
opponent m1 / s1 = column_index 5
opponent m2 / s2 = column_index 4
opponent m3 / s3 = column_index 3
opponent m4 / s4 = column_index 2
opponent m5 / s5 = column_index 1
```
### Decision
workflow 判断同纵列时，不直接比较 `m1`、`s1`，只比较：
```text
column_index
```
---
## 2026-06-10 - 规范无限泡影 effect_features
### Summary
为「无限泡影」建立可复用的效果特征枚举。

### Added
盖放发动「无限泡影」的标准 features：
```json
"effect_features": [
  "target_opponent_face_up_effect_monster",
  "negate_target_monster_effects_until_end_of_turn",
  "set_before_activation",
  "negate_spell_trap_effects_in_same_column_if_resolved_on_field"
]
```
### Decision
- 从手牌发动「无限泡影」时才加入：
  - `activate_from_hand_if_self_controls_no_cards`
- 盖放发动时不加入该 feature。
---
## 2026-06-10 - 规范破坏类 effect_features
### Summary
将“破坏一张卡”拆成对象选择和处理动作。

### Added
取对象破坏：
```json
"effect_features": [
  "target_1_card_on_field",
  "destroy_target"
]
```

处理时选择破坏：
```json
"effect_features": [
  "choose_1_card_on_field_on_resolution",
  "destroy_chosen_card"
]
```
### Decision
不使用过粗枚举：
```text
destroy_1_card
```

因为它不能表达：
```text
是否取对象；
什么时候选择；
破坏范围是什么。
```
---
## 2026-06-10 - 建立复杂 case_002：烙印之气炎 / 无限泡影 / 落胤与圣女
### Summary
构建第二类 case：效果处理是否合法。

### Scenario
```text
C1：对方发动「烙印之气炎」
C2：我方连锁盖放发动「无限泡影」，取对象「死狱乡的导化 阿尔贝」
C3：对方连锁发动「落胤与圣女」，送墓「烙印龙 白界龙」作为 cost，取对象「烙印之气炎」
处理：
C3 破坏「烙印之气炎」
C2 处理「无限泡影」
C1 尝试成功处理「烙印之气炎」
```
### Added
- `operation_type: resolve_effect`
- `resolution_history`
- `known_constraints`
- `state_timing: before_resolving_C1`

### Corrected
最初错误判断为：
```text
烙印之气炎已经离场，因此不受无限泡影同纵列无效影响。
```

后经官方裁定方向校正为：
```text
即使同纵列发动的魔法/陷阱效果在处理时已不在场上，仍会受到无限泡影同纵列无效影响。
```
### Gold Answer
```json
"label": "illegal"
```
### Reason
声明「烙印之气炎」效果成功处理不合法；正确处理应为该效果被无效。
---
## 2026-06-10 - 连锁编号统一为 C1 / C2 / C3
### Summary
统一所有连锁编号，避免混用数字与 CL 表示。

### Changed
旧字段：
```json
"chain_link": 1
```

新字段：
```json
"chain_id": "C1"
```

旧字段：
```json
"chain_response_to": 1
```

新字段：
```json
"chain_response_to": "C1"
```

旧字段：
```json
"chain_link_to_resolve": 1
```

新字段：
```json
"chain_id_to_resolve": "C1"
```
### Decision
后续所有 case 统一使用：
```text
C1, C2, C3, ...
```
---
## 2026-06-10 - 将 case_001 迁移到新格式
### Summary
将第一条灰流丽 case 迁移到新版 schema。

### Changed
- `chain_link: 1` 改为 `chain_id: "C1"`
- `chain_response_to: 1` 改为 `chain_response_to: "C1"`
- `field` 数组改为固定槽位对象
- 补充 `activation_zone`
- 补充 `activation_column_index`
- 补充 `is_chain_resolving: false`

### Current Status
`case_001` 当前作为合法发动类样例：
```text
task_type = operation_legality_judgment
operation_type = activate_effect
gold_answer.label = legal
```
---
## 2026-06-10 - 建立 schema.md 与固定枚举表
### Summary
完成正式 `schema.md`，将 case 字段含义、允许值、命名规范集中到独立文档。

### Added
- 新增 `schema.md`。
- 固定 `operation_type` 第一版枚举表。
- 固定 `effect_features` 第一版枚举表。
- 补充 `gold_answer.label`、`failed_check`、阶段、步骤、伤害步骤时点等推荐枚举。
- 写明 JSONL 文件约束、连锁编号规则、场地区域结构、`column_index` 同纵列判断规则。

### Decision
后续新增 `operation_type` 或 `effect_features` 值时，必须先更新：
```text
schema.md
```

再进入正式 case 数据。

### Current Status
已确认当前 `gpt_to_codex/operation_legality_cases.jsonl` 中已有 case 使用的 `operation_type` 与 `effect_features` 均被 `schema.md` 覆盖。
---
# Current Schema Snapshot
当前推荐 case 顶层结构：
```json
{
  "id": "case_xxx",
  "task_type": "operation_legality_judgment",
  "schema_version": "2.1.0",
  "question": "当前这个操作是否在规则内合法？",
  "natural_language_context": "",
  "rule_context": {
    "game": "Yu-Gi-Oh!",
    "format": "OCG",
    "language": "zh",
    "rule_version": "unspecified"
  },
  "pre_state": {},
  "attempted_operation": {},
  "gold_answer": {},
  "case_notes": ""
}
```

当前推荐 `pre_state` 核心结构：
```json
{
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

当前推荐 `attempted_operation` 发动类结构：
```json
{
  "player": "self",
  "operation_type": "activate_effect",
  "card": "",
  "effect_id": "main_effect",
  "activation_location": "",
  "chain_response_to": "C1",
  "declared_cost": [],
  "declared_targets": [],
  "declared_effect_purpose": ""
}
```

当前推荐 `attempted_operation` 效果处理类结构：
```json
{
  "player": "opponent",
  "operation_type": "resolve_effect",
  "card": "",
  "effect_id": "effect_1",
  "effect_label": "①",
  "chain_id_to_resolve": "C1",
  "activation_location_at_activation": "",
  "activation_zone_at_activation": "",
  "activation_column_index": null,
  "current_card_location": "",
  "declared_resolution": "",
  "declared_effect_purpose": ""
}
```
---
# Open Items
## Completed
- 已建立 `schema.md`，写明主要字段含义和允许值。
- 已为 `effect_features` 建立正式枚举表。
- 已为 `operation_type` 建立正式枚举表（v1.1，含 `declare_attack`）。
- `case_002` 已补全为完整 JSON，包括 `gold_answer`。
- `case_003` 已建立，覆盖全抗怪兽攻击宣言裁定场景。
- `case_004` 已建立，覆盖神之通告无效效果特召裁定场景。
- `case_005` 已建立，覆盖"进行连接召唤的效果"与"因效果被特殊召唤"区分裁定。
- 第一批 10 条 seed cases 已全部建立并迁移到 schema v2.0.0。
- 已完成 `required_sources` 官方证据对象迁移。
- 已建立 Draft 2020-12 JSON Schema、双层校验器及负例自测。
- 已建立并验证项目专用 Conda 环境 `YGO_PROJECT`。
- 已完整同步 `PROJECT_CONTEXT.md`，覆盖当前结构、数据契约、证据、校验与接手流程。
- 已将 `effect_resolution_judgment` 拆分为独立 task_type。
- 已建立 50 条 gold cases 基线（含 case_041–case_050）。
- 已硬化来源覆盖校验：日文/简中官方卡片文本、`source_updated_at`、16 个负例自测。
- 已完成 case_047/048 中文卡名修正、本地 `cards.cdb` 中文卡文补源及 `secondary_reference` 本地来源规则。

## Pending
- 对 50 条 case 做逐条官方证据与裁定有效性复核。
- 评估将 `python check_jsonlschema.py --self-test` 接入 CI。
- 设计 RAG 检索评测集。

## Risks
- `effect_features` 如果继续自由命名，会导致 workflow 难以稳定匹配。
- 如果不强制使用 `column_index`，同纵列裁定容易出错。
- 如果缺少 `resolution_history`，效果处理类 case 会无法判断。
- 如果 `gold_answer` 未引用官方裁定依据，复杂 case 的可靠性不足。
- 主 JSONL 与格式化 gold JSON 采用双写，若跳过校验可能发生镜像漂移。
- 错误合并 I:P 的三个召唤语义或忽略攻击限制的 `effect_scope` 会导致 v2 裁定回退。

## Next Actions
1. 在每次数据变更后通过 `YGO_PROJECT` 运行 `python check_jsonlschema.py --self-test`。
2. 对 10 条 seed cases 持续做官方来源复核与人工 dry-run。
3. 建立候选/待复核集合，仅将官方证据齐全的 case 纳入主 JSONL。
4. 扩展到 50 条人工核验 gold cases。
