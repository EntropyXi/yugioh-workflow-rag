---
title: "Cost、效果、处理"
doc_id: "06"
collection: "llmstudy_ygo_knowledge_db"
tags:
  - cost
  - 代价
  - 效果分类
  - 发动
  - 适用
  - 效果处理
  - declared_cost
  - 无效
project_bindings:
  - declared_cost
  - resolution_history
  - attempted_operation
source: "docs/llmstudy/06-cost-effect-resolution.md"
written: "2026-07-28"
---

# 06 — Cost、效果、处理

> **撰写日期**：2026-07-28
> **来源**：P0 官方规则书 + P2 `ocg-rule`
> **对应项目**：`declared_cost`、`resolution_history`、`attempted_operation` 中的 cost 和效果处理相关字段

---

## 1. Cost（代价）的概念

Cost 是发动卡片或效果时必须**先支付**的代价。关键特性：

- **在效果处理之前支付**（发动时立即支付）
- **不能撤回**：即使效果被无效，cost 也不退还
- **不是效果**：cost 不能被效果无效
- **不进入连锁**：cost 支付本身不能被连锁

### 1.1 Cost 的支付流程

```
发动宣言 → 支付 cost → 选择对象（如需要）→ 双方确认 → 效果进入连锁
```

> 如果 cost 无法支付，**不能发动**该效果。这就是 `failed_check = "cost_payability"` 的场景。

---

## 2. 本项目的 Cost 枚举

Schema 中 `declared_cost.type` 固定为四种：

| cost 类型 | 附加必填字段 | 说明 | 对应 case |
|---|---|---|---|
| `discard` | `card` | 从手牌舍弃 | case_001 (灰流丽舍弃自身) |
| `pay_lp` | `amount`（正整数） | 支付 LP | — |
| `banish` | `card`, `from` | 除外 | — |
| `send_to_graveyard` | `card`, `from` | 送墓 | case_024 (灵摆怪兽不能送墓) |

### 2.1 Cost 相关裁定案例

| 场景 | case | 裁定 |
|---|---|---|
| 灰流丽舍弃自身为 cost | case_001 | 合法，cost 先支付 |
| 宏观宇宙下不能以送墓为 cost | case_013 | `cost_payability` — 卡被除外而不是送墓 |
| 灵摆怪兽不能送墓为 cost | case_024 | 场上灵摆怪兽送墓时改为表侧加额外卡组 |

---

## 3. 效果（Effect）的分类

### 3.1 怪兽效果的 5 种分类

| 分类 | 咒文速度 | 入连锁 | 说明 | 典型卡片 |
|---|---|---|---|---|
| **起动效果** | 1 | 是 | 自己主要阶段主动发动 | 救援兔 |
| **诱发效果** | 1 | 是 | 满足条件时发动 | 元素英雄 天空侠 |
| **诱发即时效果** | 2 | 是 | 对方回合也能发动 | 灰流丽、效果遮蒙者 |
| **永续效果** | — | 否 | 只要在场就持续适用 | 技能抽取、王家长眠之谷 |
| **无种类效果** | — | 否 | 规则文本、召唤手续等 | "这张卡不能通常召唤" |

### 3.2 魔法/陷阱卡的效果

魔法陷阱卡没有上述怪兽效果的分类体系，但类似的效果也存在：
- **永续魔法/陷阱**：类似永续效果，持续适用
- **诱发类效果**：魔法陷阱卡被送墓时发动的效果（如"技能抽取"的①效果不适用）

---

## 4. "发动" vs "适用" vs "处理"

### 4.1 发动（Activate）

- 卡的发动：把魔法/陷阱卡从手牌放到场上、或把盖放的卡翻开
- 效果的发动：宣言使用某个效果

> 被"魔宫的贿赂"等无效的是**发动**，整个连锁块不存在。
> 被"灰流丽"等无效的是**效果**，发动本身有效但效果不适用。

### 4.2 适用（Apply）

- 永续效果不"发动"，直接"适用"
- "得到以下效果"、"当作……使用"等也是适用

### 4.3 处理（Resolve）

- 效果处理是连锁逆顺处理中执行效果内容的过程
- 效果处理中可能出现"不适用"的情况（如对象不合法）

---

## 5. 本项目的效果处理表示

### 5.1 resolution_history 的 action 枚举

| action | 说明 |
|---|---|
| `destroy` | 破坏 |
| `banish` | 除外 |
| `special_summon` | 特殊召唤 |
| `send_to_graveyard` | 送墓 |
| `return_to_hand` | 回手牌 |
| `return_to_extra_deck` | 回额外卡组 |
| `return_to_field` | 回场上 |
| `negate_monster_effects_until_end_of_turn` | 无效怪兽效果至回合结束 |
| `negate_effects_and_halve_atk` | 无效效果并攻击力减半 |
| `apply_same_column_spell_trap_negation` | 适用同纵列魔陷无效 |
| `change_to_face_down_defense` | 变成里侧守备表示 |
| `redirect_battle_damage` | 转嫁战斗伤害 |
| `apply_attack_decrease_and_restrictions` | 适用攻击力降低和限制 |

### 5.2 effect_features

`effect_features` 是机器可读的效果特征枚举，用于标记一个效果的关键特性：

```json
"effect_features": [
  "add_from_deck_to_hand",   // 从卡组检索
  "discard_revealed_monster" // 舍弃已展示的怪兽
]
```

当前 Schema 中有 56 个 feature，58 条 case 中实际使用了 32 个。

---

## 6. 效果处理的重要规则

### 6.1 效果处理中的场所移动

- 效果处理中，卡片从发动场所移动到其他场所 → 效果可能不适用
- 2020.04 规则：诱发效果在发动前场所移动 → 不发动

### 6.2 效果处理中不能插入其他效果

- 一个效果正在处理时，不能发动别的效果
- 例：融合召唤在处理中 → 不能插入神之宣告无效融合召唤

### 6.3 效果处理中的"尽可能"规则

- "尽可能适用"：能适用的部分就适用
- "才能发动"：必须全部条件满足才适用

### 6.4 离场后的效果处理

卡片离场后，部分效果仍然适用（取决于效果文本）。
> **case_002** 的核心问题：烙印之气炎因连锁被破坏送墓后，无限泡影的同纵列无效效果是否仍然影响它。
