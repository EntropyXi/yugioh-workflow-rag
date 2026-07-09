# 游戏王裁定数据集 Schema v2.1.0

本文档固定 `gold_cases/operation_legality_cases.jsonl` 的 case 结构、字段含义与 v2 枚举表。

当前任务只判断：给定 `pre_state` 与 `attempted_operation`，当前操作或当前效果处理是否在规则内合法。本文档不覆盖最优操作、完整对局模拟、卡组构筑或策略评价。

---

# 1. 文件格式

正式数据文件使用 JSONL：

```text
gold_cases/operation_legality_cases.jsonl
```

格式化人工审阅镜像使用独立 JSON 文件：

```text
gold_cases/json/caseNNN.json
```

约束：

- 每一行是一个完整 JSON object。
- 不使用 `//` 或 `/* */` 注释。
- 字段说明、枚举表、命名规范写在本文档中。
- 可执行的 Draft 2020-12 Schema 位于 `docs/operation_case.schema.json`。
- 字符串枚举优先使用稳定英文值，中文说明写入自然语言字段。

---

# 2. 顶层结构

```json
{
  "id": "case_xxx",
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

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|---|---:|---:|---|
| `id` | string | 是 | case 唯一编号，建议 `case_001`、`case_002`。 |
| `task_type` | string | 是 | 允许 `operation_legality_judgment` 或 `effect_resolution_judgment`。 |
| `schema_version` | string | 是 | 当前固定为 `2.1.0`。不允许省略或混用旧版本。 |
| `question` | string | 是 | 被判断的问题，可为操作合法性或处理合法性。 |
| `natural_language_context` | string | 是 | 给人阅读的局面描述。 |
| `rule_context` | object | 是 | 游戏、赛制、语言、规则版本等背景。 |
| `pre_state` | object | 是 | 被判断操作或处理发生前的已知局面。 |
| `attempted_operation` | object | 是 | 当前尝试执行的操作，或声明的效果处理。 |
| `gold_answer` | object | 是 | 人工标注答案。 |
| `case_notes` | string | 否 | 数据集维护备注。 |

---

# 3. `rule_context`

推荐结构：

```json
{
  "game": "Yu-Gi-Oh!",
  "format": "OCG",
  "language": "zh",
  "rule_version": "unspecified"
}
```

允许值：

| 字段 | 推荐值 |
|---|---|
| `game` | `Yu-Gi-Oh!` |
| `format` | `OCG`, `TCG`, `Master Duel`, `unspecified` |
| `language` | `zh`, `ja`, `en`, `unspecified` |
| `rule_version` | 具体版本字符串，未知时用 `unspecified` |

---

# 4. `pre_state`

`pre_state` 表示被判断操作或效果处理发生前的局面。

推荐结构：

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

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|---|---:|---:|---|
| `state_timing` | string/null | 否 | 精确时点，如 `before_resolving_C1`。发动判断类 case 可省略。 |
| `phase` | string | 是 | 当前大阶段。 |
| `step` | string/null | 是 | 阶段内部步骤。非战斗阶段通常为 `null`。 |
| `damage_step_timing` | string/null | 是 | 伤害步骤内部时点。非伤害步骤通常为 `null`。 |
| `turn_player` | string | 是 | 当前回合玩家，`self` 或 `opponent`。 |
| `chain_state` | object | 是 | 当前连锁状态。 |
| `resolution_history` | array | 是 | 当前判断时点之前已经处理完成的连锁结果；没有已处理连锁块时必须显式写 `[]`。 |
| `self_state` | object | 是 | 我方已知状态。 |
| `opponent_state` | object | 是 | 对方已知状态。 |
| `known_constraints` | array | 否 | 已知持续限制或已经适用的约束。 |

## 4.1 阶段枚举

`phase` 固定枚举：

| 值 | 含义 |
|---|---|
| `draw_phase` | 抽卡阶段 |
| `standby_phase` | 准备阶段 |
| `main_phase_1` | 主要阶段 1 |
| `battle_phase` | 战斗阶段 |
| `main_phase_2` | 主要阶段 2 |
| `end_phase` | 结束阶段 |
| `unknown` | 信息不足或未指定 |

`step` 固定枚举：

| 值 | 含义 |
|---|---|
| `null` | 不适用或无需细分 |
| `start_step` | 战斗阶段开始步骤 |
| `battle_step` | 战斗步骤 |
| `damage_step` | 伤害步骤 |
| `end_step` | 战斗阶段结束步骤 |
| `unknown` | 信息不足或未指定 |

`damage_step_timing` 固定枚举：

| 值 | 含义 |
|---|---|
| `null` | 不在伤害步骤，或无需细分 |
| `start_of_damage_step` | 伤害步骤开始时 |
| `before_damage_calculation` | 伤害计算前 |
| `during_damage_calculation` | 伤害计算时 |
| `after_damage_calculation` | 伤害计算后 |
| `end_of_damage_step` | 伤害步骤结束时 |
| `unknown` | 信息不足或未指定 |

---

# 5. 连锁表示

所有连锁编号统一使用大写 `C` 加数字：

```text
C1, C2, C3, ...
```

字段约定：

| 字段 | 用法 |
|---|---|
| `chain_id` | 当前连锁块编号，如 `"C1"`。 |
| `chain_response_to` | 当前发动响应的连锁块，如 `"C1"`。 |
| `chain_id_to_resolve` | 当前将要处理的连锁块，如 `"C1"`。 |
| `resolved_chain_id` | 已经处理完的连锁块，如 `"C3"`。 |
| `current_chain_id` | 场上卡片当前关联的连锁块，如 `"C2"`。 |

禁用写法：

```json
"chain_link": 1
```

---

# 6. 场地区域结构

`self_state.field` 与 `opponent_state.field` 使用相同结构。

```json
{
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

空位统一写作：

```json
"card": null
```

有卡时写入 `card` 对象：

```json
{
  "column_index": 4,
  "card": {
    "name": "无限泡影",
    "status": "face_up",
    "card_type": "trap",
    "trap_type": "normal_trap",
    "controller": "self",
    "current_chain_id": "C2"
  }
}
```

场地魔法区域不使用 `column_index`。空位写 `null`；有卡时统一使用同样的
`card` 包装，禁止直接把卡片对象放入 `field_spell_zone`：

```json
"field_spell_zone": {
  "card": {
    "name": "完美卡通世界",
    "status": "face_up",
    "card_type": "spell",
    "spell_type": "field_spell",
    "controller": "opponent"
  }
}
```

---

# 7. `column_index` 规则

`column_index` 以我方视角为基准：

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

同纵列判断统一使用：

```text
source.column_index == target.column_index
```

workflow 不应再手动使用 `opponent_m_i -> self_m_(6-i)` 换算。

---

# 8. `attempted_operation`

`attempted_operation` 表示当前被判断的操作或处理声明。

发动/连锁类示例：

```json
{
  "player": "self",
  "operation_type": "activate_effect",
  "card": "灰流丽",
  "effect_id": "main_effect",
  "activation_location": "hand",
  "chain_response_to": "C1",
  "declared_cost": [
    {
      "type": "discard",
      "card": "灰流丽"
    }
  ],
  "declared_targets": [],
  "declared_effect_purpose": "negate_the_effect"
}
```

效果处理类示例：

```json
{
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

---

# 9. `operation_type` 固定枚举表

`attempted_operation.operation_type` 当前固定为以下枚举。不得使用自由命名值；新增值必须先更新本表。

| 值 | 含义 | 典型必需字段 | 说明 |
|---|---|---|---|
| `activate_card` | 发动一张卡 | `player`, `card`, `activation_location` | 魔法/陷阱卡从手牌或场上发动时使用。 |
| `activate_effect` | 发动一个效果 | `player`, `card`, `effect_id`, `activation_location` | 怪兽效果、手坑效果、墓地效果等发动时使用。 |
| `normal_summon` | 通常召唤 | `player`, `card` | 包括通常召唤与上级召唤，必要时补充祭品信息。 |
| `special_summon` | 特殊召唤 | `player`, `card` | 判断特殊召唤条件、素材、区域等是否合法。 |
| `set_card` | 盖放魔法/陷阱卡 | `player`, `card` | 魔法/陷阱盖放到魔法与陷阱区域。 |
| `set_monster` | 里侧守备表示通常召唤/盖放怪兽 | `player`, `card` | 怪兽盖放。 |
| `select_target` | 选择对象 | `player`, `card`, `declared_targets` | 单独判断取对象是否合法时使用。 |
| `pay_cost` | 支付 cost | `player`, `card`, `declared_cost` | 单独判断 cost 是否可支付时使用。 |
| `resolve_effect` | 处理效果 | `player`, `card`, `effect_id`, `chain_id_to_resolve`, `declared_resolution` | 判断某个声明的效果处理是否合法。 |
| `declare_attack` | 攻击宣言 | `player`, `card`, `attack_type` | 判断某只怪兽的攻击宣言（含直接攻击）是否合法。 |

禁用值：

| 禁用值 | 替代方式 |
|---|---|
| `chain_response` | 使用 `activate_card` 或 `activate_effect`，并填写 `chain_response_to`。 |
| `resolve_card` | 使用 `resolve_effect`。 |
| `activation` | 按对象拆分为 `activate_card` 或 `activate_effect`。 |

---

# 10. `effect_id` 与 `effect_label`

`effect_id` 是机器可读的效果编号。

推荐枚举：

| 值 | 含义 |
|---|---|
| `main_effect` | 只有一个主要效果，或当前不需要区分编号。 |
| `effect_1` | 第一项效果。 |
| `effect_2` | 第二项效果。 |
| `field_effect` | 场上适用或发动的效果。 |
| `graveyard_effect` | 墓地效果。 |
| `hand_effect` | 手牌效果。 |
| `unspecified` | 原始材料未明确效果编号。 |

若需要保留原文编号，使用：

```json
{
  "effect_id": "effect_1",
  "effect_label": "①"
}
```

不要把 `"①"` 直接作为主要机器可读编号。

---

# 11. `effect_features` 固定枚举表

`effect_features` 只放机器可读的稳定英文枚举。不得放自由中文描述；中文效果文本写入 `effect_summary`。

当前第一版固定枚举如下。新增 feature 必须满足：

- 使用小写英文与下划线。
- 一个 feature 只表达一个可判断条件、动作或限制。
- 是否取对象、何时选择、处理动作必须拆开表达。
- 新增值必须先写入本表，再进入 case。

## 11.1 卡组/额外卡组相关

| 值 | 含义 |
|---|---|
| `add_from_deck_to_hand` | 从卡组把卡加入手牌。 |
| `special_summon_from_deck` | 从卡组特殊召唤。 |
| `special_summon_from_graveyard` | 从墓地特殊召唤。 |
| `send_from_deck_to_graveyard` | 从卡组送去墓地。 |
| `send_level_8_fusion_monster_from_extra_deck_to_graveyard` | 从额外卡组将等级 8 融合怪兽送去墓地。 |
| `send_albaz_related_monster_from_extra_deck_to_graveyard_as_cost` | 将记载有「阿尔白斯之落胤」相关信息的额外卡组怪兽送墓作为 cost。 |

## 11.2 手牌/展示/舍弃相关

| 值 | 含义 |
|---|---|
| `reveal_monster_in_hand` | 展示手牌中的怪兽。 |
| `discard_revealed_monster` | 舍弃已展示的怪兽。 |

## 11.3 取对象相关

| 值 | 含义 |
|---|---|
| `target_opponent_face_up_effect_monster` | 以对方场上表侧表示效果怪兽为对象。 |
| `target_1_card_on_field` | 以场上 1 张卡为对象。 |
| `target_1_face_up_card_on_field` | 以场上 1 张表侧表示卡为对象。 |
| `target_1_opponent_card_on_field` | 以对方场上 1 张卡为对象。 |

## 11.4 无效相关

| 值 | 含义 |
|---|---|
| `negate_target_monster_effects_until_end_of_turn` | 将对象怪兽效果直到回合结束时无效。 |
| `negate_face_up_monster_effects_continuously` | 持续无效场上表侧表示怪兽的效果。 |
| `negate_spell_trap_effects_in_same_column_if_resolved_on_field` | 若处理时满足条件，则本回合同纵列其他魔法/陷阱卡效果无效。 |

## 11.5 盖放/发动条件相关

| 值 | 含义 |
|---|---|
| `set_before_activation` | 该卡是盖放后发动。 |
| `activate_from_hand_if_self_controls_no_cards` | 我方场上没有卡时可从手牌发动。 |

## 11.6 破坏/处理时选择相关

| 值 | 含义 |
|---|---|
| `destroy_target` | 破坏发动时选择的对象。 |
| `choose_1_card_on_field_on_resolution` | 处理时选择场上 1 张卡。 |
| `destroy_chosen_card` | 破坏处理时选择的卡。 |
| `prevent_chain_to_activation` | 该卡/效果的发动不能被连锁响应。 |
| `banish_all_monsters_temporarily` | 将场上的怪兽全部暂时除外。 |
| `special_summon_banished_monsters_as_many_as_possible` | 将以该效果除外的怪兽尽可能特殊召唤回场。 |

## 11.7 召唤手续与效果处理时点

| 值 | 含义 |
|---|---|
| `perform_link_summon_after_chain_link_resolution` | 连锁块处理完成后立即由玩家进行连接召唤。 |
| `includes_special_summon_effect` | 在判断“是否包含特殊召唤效果”时按包含处理。 |
| `resulting_monster_not_summoned_by_activated_effect` | 召唤结果不视为在发动效果的处理时直接特殊召唤。 |
| `ignition_effect` | 起动效果。 |
| `summon_success_activation_window` | 召唤成功时的专门发动窗口。 |
| `prevent_effect_activation_on_summon_success` | 召唤成功时禁止魔法、陷阱、怪兽效果发动。 |
| `negate_summon_or_special_summon_effect` | 无效召唤或包含特殊召唤处理的发动。 |
| `move_attack_target_and_perform_damage_calculation` | 转移攻击对象并在效果处理中进行伤害计算。 |
| `self_special_summon_from_graveyard_by_procedure` | 从墓地特殊召唤自身的不入连锁手续。 |

上述三个 feature 必须分开理解。以「I：P伪装舞会莱娜」为例，其效果包含
特殊召唤效果，因此可被要求“包含特殊召唤效果”的效果响应；但连接召唤在
连锁块处理后立即进行，召唤出的怪兽不视为“因发动的怪兽效果被特殊召唤”。

## 11.8 case_021–case_030 新增处理特征

| 值 | 含义 |
|---|---|
| `send_pendulum_monster_to_graveyard_as_cost` | 将灵摆怪兽送去墓地作为 cost。 |
| `target_1_monster_in_graveyard` | 以墓地 1 只怪兽为对象。 |
| `banish_target_from_graveyard` | 将墓地对象除外。 |
| `activate_pendulum_monster_as_spell` | 将灵摆怪兽作为魔法卡发动。 |
| `allow_pendulum_summon_with_existing_scales` | 已存在灵摆刻度时可进行灵摆召唤。 |
| `set_trap_from_deck` | 从卡组选陷阱卡盖放。 |
| `limit_trap_activations_after_resolution` | 效果适用后限制本回合可发动的陷阱数量。 |
| `prevent_adding_from_deck_to_hand` | 禁止从卡组把卡加入手牌。 |
| `declare_card_type_and_apply_spyral_search_or_summon` | 宣言卡种并按确认结果执行 SPYRAL 检索、墓地回收或特殊召唤处理。 |

## 11.9 case_031–case_040 新增处理特征

| 值 | 含义 |
|---|---|
| `trigger_after_chain_resolution` | 整条连锁处理完毕后另开时点触发或发动。 |
| `target_quick_play_spell_in_graveyard` | 以墓地的速攻魔法为对象。 |
| `restrict_direct_chain_response_only` | 只限制直接对应某发动的连锁。 |
| `reveal_card_in_hand_as_cost` | 展示手牌中的卡作为发动 cost。 |
| `replacement_destroy_instead` | 适用替代破坏。 |
| `destroy_target_then_special_summon_from_graveyard` | 先破坏对象，之后从墓地特殊召唤。 |
| `mandatory_damage_step_trigger` | 伤害步骤同一时点的必发诱发效果。 |
| `optional_damage_step_trigger` | 伤害步骤同一时点的可选诱发效果。 |
| `return_battling_monsters_to_hand_or_extra_deck` | 将战斗双方怪兽返回手牌或额外卡组。 |
| `ignore_summoning_conditions` | 无视召唤条件进行特殊召唤。 |
| `select_once_per_turn_option` | 选择“一回合只能选择一次”的项目。 |
| `activated_effect_cannot_be_negated` | 已成功发动的效果不被无效。 |
| `replacement_destroy_other_card` | 以破坏其他卡代替原本破坏。 |
| `temporarily_banish_until_after_effect_resolution` | 暂时除外直到效果处理后返回。 |
| `self_destroy_when_toons_world_destroyed` | 卡通世界被破坏时自身破坏。 |

禁用或废弃 feature：

| 禁用值 | 替代方式 |
|---|---|
| `destory_target_card` | 拼写错误，使用 `destroy_target`。 |
| `destroy_1_card` | 过粗，按是否取对象/何时选择拆成 `destroy_target` 或 `choose_1_card_on_field_on_resolution` + `destroy_chosen_card`。 |
| `grant_link_summon_opportunity` | 语义过粗且会混淆召唤时点，拆成 11.7 的三个 feature。 |
| 中文自然语言描述 | 写入 `effect_summary`，不要写入 `effect_features`。 |

---

# 12. `resolution_history`

用于记录当前判断时点之前已经按规则处理完成的连锁结果。该字段是 `pre_state`
的必填状态词条；空数组 `[]` 表示“当前判断点前没有已经处理完成的连锁块”，
不是缺失信息。

```json
[
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

填写规则：

- 只记录已经处理完成的连锁块，不记录将要处理、正在声明或玩家希望怎样处理的内容。
- 顺序按实际处理时间排列。连锁处理中通常是高编号先处理，例如先 `C3` 后 `C2`。
- `resolved_chain_id` 应引用当前 case 所描述的连锁上下文；若当前已回到开放状态且
  `current_chain_links` 为空，可用于记录此前已完成并影响当前状态的历史连锁。
- `result` 必须是非空数组；没有结构化结果的已处理效果不要硬写 history item。
- 持续适用的限制写入 `known_constraints`，不要写入 `resolution_history`。
- `resolution_history` 必须与当前场面一致；例如写了特殊召唤，场面状态也应反映怪兽已经移动到场上。

---

# 13. `known_constraints`

用于记录已经适用或持续存在的限制。

```json
[
  {
    "type": "same_column_spell_trap_negation",
    "source_card": "无限泡影",
    "source_zone": "self.field.spell_trap_zones.s4",
    "affected_column_index": 4,
    "duration": "until_end_of_turn"
  }
]
```

常见 `type`：

| 值 | 含义 |
|---|---|
| `same_column_spell_trap_negation` | 同纵列魔法/陷阱效果无效。 |
| `once_per_turn_used` | 某效果本回合已经使用。 |
| `activation_restriction` | 存在发动限制。 |
| `summon_restriction` | 存在召唤限制。 |
| `attack_restriction` | 存在攻击限制；必须继续声明限制类型、玩家与作用对象。 |

攻击限制使用结构化对象：

```json
{
  "type": "attack_restriction",
  "restriction": "cannot_direct_attack",
  "affected_player": "self",
  "effect_scope": "monster",
  "duration": "until_end_of_turn",
  "source_card": "S:P小夜骑士",
  "source_effect": "effect_1"
}
```

`effect_scope` 固定为 `monster` 或 `player`。前者影响怪兽本身，不受该效果
影响的怪兽可绕过限制；后者约束玩家，怪兽自身的效果抗性不能绕过。
`direct_attack_restriction` 已废弃，不得继续使用。

---

# 14. `gold_answer`

推荐结构：

```json
{
  "label": "legal",
  "conclusion": "",
  "failed_check": null,
  "reasoning_steps": [],
  "missing_info": [],
  "required_sources": [
    {
      "id": "src_case005_01",
      "source_type": "official_ruling",
      "authority": "KONAMI",
      "title": "官方Q&A标题",
      "url": "https://www.db.yugioh-card.com/yugiohdb/faq_search.action?ope=5&fid=23173&request_locale=ja",
      "official_id": "fid:23173",
      "language": "ja",
      "source_updated_at": "2025-09-27",
      "accessed_at": "2026-07-07",
      "supports_reasoning_steps": [3, 4, 5],
      "lookup_query": "可选的原检索词"
    }
  ]
}
```

`label` 固定枚举：

| 值 | 含义 |
|---|---|
| `legal` | 当前操作或声明处理合法。 |
| `illegal` | 当前操作或声明处理不合法。 |
| `depends` | 信息不足，结论取决于缺失条件。 |
| `invalid_question` | 问题不属于当前裁定任务边界。 |

`depends` 必须配合非空 `missing_info`；不确定性只通过这两个字段表达。

`failed_check` 推荐枚举：

| 值 | 含义 |
|---|---|
| `activation_window` | 发动窗口不合法。 |
| `activation_condition` | 发动条件不满足。 |
| `chain_speed` | 连锁速度或可连锁性不满足。 |
| `cost_payability` | cost 无法支付。 |
| `target_legality` | 对象不合法。 |
| `card_location` | 卡片位置不满足要求。 |
| `once_per_turn` | 违反一回合一次等次数限制。 |
| `phase_or_step_restriction` | 阶段或步骤限制不满足。 |
| `summon_condition` | 召唤条件不满足。 |
| `material_legality` | 素材不合法。 |
| `zone_availability` | 区域不可用。 |
| `effect_resolution_rule` | 效果处理规则不满足。 |
| `external_restriction` | 其他外部限制导致不合法。 |
| `unknown_missing_info` | 由于缺失信息无法确定。 |
| `null` | 合法或无需指定失败项。 |

---

# 15. `required_sources` 证据契约

`required_sources` 存放已经定位到的证据，不再存放只有 `query` 的检索占位符。

固定 `source_type`：

| 值 | 含义 |
|---|---|
| `official_card_text` | Konami 官方卡片详情。 |
| `official_ruling` | Konami 官方 Q&A 或卡片补充信息。 |
| `official_rulebook` | Konami 官方规则书。 |
| `secondary_reference` | 视频、文章等二手材料，或本地非官方中文卡文补源（`authority: local_cards_cdb`），不能单独支撑正式 gold case。 |

每个证据对象必须包含 `id`、`source_type`、`authority`、`title`、`url`、
`official_id`、`language`、`accessed_at` 与 `supports_reasoning_steps`。
`supports_reasoning_steps` 使用从 1 开始的推理步骤编号。来源存在官方更新日期时，
填写 `source_updated_at`；原搜索词可保留在可选的 `lookup_query`。

每条正式 gold case 至少需要：

- 一项 `official_card_text`；
- 一项 `official_ruling` 或 `official_rulebook`；
- 所有官方来源 URL 必须指向 `db.yugioh-card.com` 或 `yugioh-card.com`；
- 简中官方卡片文本可使用 `request_locale=cn` 的 KONAMI 官方卡片详情页；
  `language` 记为 `zh-CN`。若 `db.yugioh-card-cn.com/card_search.action.html`
  仅返回检索页而非卡片详情正文，不得作为已核验效果文本来源。
- 二手来源不得成为唯一裁定依据。

`official_card_ruling` 与 `rulebook` 是废弃值，分别迁移为
`official_ruling` 与 `official_rulebook`。

---

# 16. cost、处理动作与卡片对象枚举

## 16.1 `declared_cost.type`

| 值 | 附加必填字段 |
|---|---|
| `discard` | `card` |
| `pay_lp` | `amount`，且必须为正数 |
| `banish` | `card`, `from` |
| `send_to_graveyard` | `card`, `from` |

## 16.2 `resolution_history.result.action`

| 值 | 附加必填字段 |
|---|---|
| `destroy` | `card`, `from`, `to` |
| `negate_monster_effects_until_end_of_turn` | `target` |
| `apply_same_column_spell_trap_negation` | `source_card`, `source_zone`, `affected_column_index`, `duration` |
| `banish` | `card`, `from`, `to` |
| `negate_effects_and_halve_atk` | `target`, `duration` |
| `special_summon` | `card`, `from`, `to` |
| `send_to_graveyard` | `card`, `from`, `to` |
| `return_to_hand` | `card`, `from`, `to` |
| `return_to_extra_deck` | `card`, `from`, `to` |
| `return_to_field` | `card`, `from`, `to` |
| `change_to_face_down_defense` | `card` |
| `redirect_battle_damage` | —（无额外必填字段） |
| `apply_attack_decrease_and_restrictions` | `target` |

## 16.3 卡片对象

场上卡片对象必填 `name`、`status`、`card_type`、`controller`。

- `status`: `face_up`, `face_down`
- `position`: `attack`, `defense`
- `card_type`: `monster`, `spell`, `trap`
- `controller`: `self`, `opponent`
- `monster_type`: `normal`, `effect`, `fusion`, `ritual`, `synchro`, `xyz`, `link`, `toon`, `pendulum`
- `spell_type`: `normal_spell`, `quick_play_spell`, `continuous_spell`, `equip_spell`, `field_spell`, `ritual_spell`
- `trap_type`: `normal_trap`, `continuous_trap`, `counter_trap`

当前位置枚举为 `hand`、`deck`、`extra_deck`、`monster_zone`、
`extra_monster_zone`、`spell_trap_zone`、`field_spell_zone`、`graveyard`、
`banished`。新增值必须先登记再进入数据。

---

# 17. 自动校验

校验分为两层：

- `docs/operation_case.schema.json` 使用 JSON Schema Draft 2020-12，负责类型、
  必填字段、枚举、`oneOf` 与 `if/then` 条件。
- `check_jsonlschema.py` 负责跨行、跨文件与引用关系，例如 ID 唯一、连锁引用、
  证据步骤范围、纵列映射以及 gold JSON 镜像一致性。

项目推荐使用仓库根目录 `environment.yml` 定义的 `YGO_PROJECT` Conda 环境。
首次使用先创建并激活环境，再运行校验：

```text
conda env create -f environment.yml
conda activate YGO_PROJECT
python check_jsonlschema.py
python check_jsonlschema.py --self-test
python check_jsonlschema.py -s docs/operation_case.schema.json gold_cases/operation_legality_cases.jsonl
```

已有环境可用 `conda env update -n YGO_PROJECT -f environment.yml --prune` 同步；
详细说明见 `docs/environment_setup.md`。不使用 Conda 时，仍可通过
`python -m pip install -r requirements-dev.txt` 安装同一组校验依赖。

不传参数时默认使用正式 schema 与主 JSONL。`--self-test` 额外执行内存负例，
并检查 `gold_cases/json/` 下的格式化 JSON 镜像与主 JSONL 逐对象一致。
当前负例自测共 13 个，确认以下错误会被拒绝：

- 非法标签；
- 空 `depends.missing_info`；
- 废弃 feature；
- 缺失 URL；
- 非法 cost 字段；
- 错误连锁引用；
- 缺失 `resolution_history`、错误 `resolution_history` 引用、错误处理顺序、空 `result`；
- `task_type` 与 `operation_type` 不一致；
- 正式数据缺少 `official_card_text` 的 `ja` 或 `zh-CN` 来源；
- `official_ruling` 缺少 `source_updated_at`。

正式 gold case 原则上必须同时包含日文 KONAMI 卡片文本与简中官方卡片文本；若确实无法定位有效简中官方正文，不得伪造来源，必须在 `case_notes` 与项目上下文中显式列为待复核例外。

---

# 18. 当前固定枚举版本

| 枚举表 | 版本 | 状态 |
|---|---|---|
| `operation_type` | v1.1 | 固定 |
| `effect_features` | v2 | 固定 |
| `known_constraints` | v2 | 固定 |
| `required_sources.source_type` | v1 | 固定 |
| `declared_cost.type` / `resolution_history.action` | v1 | 固定 |
| `gold_answer.label` | v1 | 固定 |
| `phase` / `step` / `damage_step_timing` | v1 | 固定 |

当前 case schema 版本为 `2.1.0`。后续新增枚举值时，应同步更新本文档、
`check_jsonlschema.py`，并在 changelog 中记录新增原因。
