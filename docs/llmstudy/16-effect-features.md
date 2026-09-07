# 16 — effect_features 详解

> **撰写日期**：2026-07-28
> **对应项目**：`effect_feature` Schema 枚举，56 个注册值（32 个已使用 / 24 个未使用）

---

## 1. effect_features 的设计意图

`effect_features` 是**机器可读的效果特征标签**，标记一个效果的关键属性。设计原则：
- 使用小写英文下划线
- 一个 feature 只表达一个可判断条件/动作/限制
- 取对象、何时选择、处理动作必须拆分
- 不放入自由中文描述（中文写入 `effect_summary`）

---

## 2. 已使用的 features（32 个）

### 2.1 卡组/额外卡组操作

| feature | 含义 | 使用次数 |
|---|---|---|
| `add_from_deck_to_hand` | 从卡组检索 | 3 |
| `special_summon_from_deck` | 从卡组特召 | 2 |
| `special_summon_from_graveyard` | 从墓地特召 | 2 |
| `send_from_deck_to_graveyard` | 从卡组送墓 | 0 |
| `send_level_8_fusion_monster_from_extra_deck_to_graveyard` | 送 LV8 融合怪兽进墓 | 1 |
| `send_albaz_related_monster_from_extra_deck_to_graveyard_as_cost` | 送阿不思相关怪兽为 cost | 1 |

### 2.2 手牌操作

| feature | 含义 | 使用次数 |
|---|---|---|
| `reveal_monster_in_hand` | 展示手牌怪兽 | 1 |
| `discard_revealed_monster` | 舍弃已展示怪兽 | 1 |
| `reveal_card_in_hand_as_cost` | 展示手牌为 cost | 2 |

### 2.3 取对象

| feature | 含义 | 使用次数 |
|---|---|---|
| `target_opponent_face_up_effect_monster` | 取对方表侧效果怪兽为对象 | 1 |
| `target_1_card_on_field` | 取场上 1 卡为对象 | 3 |
| `target_1_face_up_card_on_field` | 取场上 1 表侧卡为对象 | 2 |
| `target_1_opponent_card_on_field` | 取对方场上 1 卡为对象 | 1 |
| `target_1_monster_in_graveyard` | 取墓地 1 怪兽为对象 | 3 |
| `target_quick_play_spell_in_graveyard` | 取墓地速攻魔法为对象 | 0 |

### 2.4 无效

| feature | 含义 | 使用次数 |
|---|---|---|
| `negate_target_monster_effects_until_end_of_turn` | 无效对象怪兽至回合结束 | 1 |
| `negate_face_up_monster_effects_continuously` | 持续无效表侧怪兽 | 1 |
| `negate_spell_trap_effects_in_same_column_if_resolved_on_field` | 同纵列魔陷无效 | 1 |
| `negate_summon_or_special_summon_effect` | 无效召唤/包含特召的发动 | 0 |

### 2.5 破坏/处理时选择

| feature | 含义 | 使用次数 |
|---|---|---|
| `destroy_target` | 破坏发动时取的对象 | 3 |
| `destroy_chosen_card` | 破坏处理时选的卡 | 0 |
| `choose_1_card_on_field_on_resolution` | 处理时选卡 | 0 |
| `prevent_chain_to_activation` | 不能被连锁 | 1 |
| `replacement_destroy_instead` | 替代破坏 | 0 |
| `replacement_destroy_other_card` | 用其他卡替代破坏 | 0 |
| `destroy_target_then_special_summon_from_graveyard` | 破坏对象后从墓地特召 | 1 |

### 2.6 召唤相关

| feature | 含义 | 使用次数 |
|---|---|---|
| `perform_link_summon_after_chain_link_resolution` | 连锁后连接召唤 | 1 |
| `includes_special_summon_effect` | 包含特召效果 | 2 |
| `resulting_monster_not_summoned_by_activated_effect` | 结果不视为因效果特召 | 1 |
| `ignition_effect` | 起动效果 | 0 |
| `self_special_summon_from_graveyard_by_procedure` | 墓地自身特召手续 | 0 |
| `ignore_summoning_conditions` | 无视召唤条件 | 1 |

### 2.7 时点/阶段

| feature | 含义 | 使用次数 |
|---|---|---|
| `summon_success_activation_window` | 召唤成功窗口 | 0 |
| `prevent_effect_activation_on_summon_success` | 禁止召唤成功时发动 | 0 |
| `trigger_after_chain_resolution` | 连锁后触发 | 0 |
| `mandatory_damage_step_trigger` | 必发伤害步骤诱发 | 1 |
| `optional_damage_step_trigger` | 选发伤害步骤诱发 | 1 |
| `set_before_activation` | 盖放后发动 | 1 |
| `restrict_direct_chain_response_only` | 只限直接连锁 | 1 |

### 2.8 伤害/战斗

| feature | 含义 | 使用次数 |
|---|---|---|
| `move_attack_target_and_perform_damage_calculation` | 转移攻击对象并伤害计算 | 1 |
| `return_battling_monsters_to_hand_or_extra_deck` | 战斗怪兽回手/额外 | 1 |

### 2.9 其他

| feature | 含义 | 使用次数 |
|---|---|---|
| `banish_all_monsters_temporarily` | 暂时除外全场怪兽 | 0 |
| `special_summon_banished_monsters_as_many_as_possible` | 尽可能特召回除外怪兽 | 0 |
| `select_once_per_turn_option` | 选择一回合一次的●项 | 0 |
| `activated_effect_cannot_be_negated` | 已发动的效果不被无效 | 1 |
| `prevent_adding_from_deck_to_hand` | 禁止从卡组检索 | 0 |
| `declare_card_type_and_apply_spyral_search_or_summon` | 宣言卡种并检索/召唤 | 1 |

### 2.10 灵摆/陷阱

| feature | 含义 | 使用次数 |
|---|---|---|
| `send_pendulum_monster_to_graveyard_as_cost` | 送灵摆怪兽去墓地cost | 0 |
| `activate_pendulum_monster_as_spell` | 灵摆怪兽作魔法发动 | 0 |
| `allow_pendulum_summon_with_existing_scales` | 已有刻度时可灵摆召唤 | 0 |
| `set_trap_from_deck` | 从卡组盖放陷阱 | 0 |
| `limit_trap_activations_after_resolution` | 限制陷阱发动次数 | 0 |

### 2.11 除外/卡通

| feature | 含义 | 使用次数 |
|---|---|---|
| `temporarily_banish_until_after_effect_resolution` | 暂时除外至效果处理后 | 0 |
| `self_destroy_when_toons_world_destroyed` | 卡通世界破坏时自身破坏 | 0 |
| `banish_target_from_graveyard` | 除外墓地对象 | 1 |
| `activate_from_hand_if_self_controls_no_cards` | 自己无卡时手牌发动 | 0 |

---

## 3. 未使用 features（24 个）的可能用途

这些 feature 在 Schema 中注册但未被任何 case 使用：

- **灵摆相关** (`activate_pendulum_monster_as_spell`, `allow_pendulum_summon_with_existing_scales`, `send_pendulum_monster_to_graveyard_as_cost`)：对应 case_024/027 的场景，但当前 case 中没有将灵摆操作作为 chain link 中的 effect_feature
- **召唤窗口** (`summon_success_activation_window`, `prevent_effect_activation_on_summon_success`)：对应 case_021/022 可能用到
- **暂时除外** (`banish_all_monsters_temporarily`, `special_summon_banished_monsters_as_many_as_possible`, `temporarily_banish_until_after_effect_resolution`)：对应 case_040
- **区域/卡通** (`self_destroy_when_toons_world_destroyed`)：对应 case_040/043

> **部分 feature 的缺失可能是因为 58 条 case 覆盖到了对应的规则场景，但效果的具体表达放在了 `effect_summary`（自然语言）而非 `effect_features`（机器枚举）中。**
