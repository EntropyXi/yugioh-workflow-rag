---
title: "operation_type 详解"
doc_id: "15"
collection: "llmstudy_ygo_knowledge_db"
tags:
  - operation_type
  - 操作类型
  - activate_effect
  - activate_card
  - resolve_effect
  - declare_attack
  - special_summon
  - normal_summon
  - set_card
project_bindings:
  - attempted_operation.operation_type
source: "docs/llmstudy/15-operation-types.md"
written: "2026-07-28"
---

# 15 — operation_type 详解

> **撰写日期**：2026-07-28
> **对应项目**：`attempted_operation.operation_type` 枚举、当前覆盖状态

---

## 1. 10 种操作类型一览

| operation_type | 当前覆盖 | case 数量 | 说明 |
|---|---|---|---|
| `activate_effect` | ✅ | 24 | 发动怪兽/魔法/陷阱的效果 |
| `resolve_effect` | ✅ | 13 | 效果处理（需要 effect_resolution_judgment） |
| `activate_card` | ✅ | 12 | 发动一张卡 |
| `declare_attack` | ✅ | 2 | 攻击宣言 |
| `special_summon` | ✅ | 2 | 特殊召唤 |
| `select_target` | ✅ | 1 | 选择对象 |
| `normal_summon` | ✅ | 1 | 通常召唤（case_051） |
| `set_card` | ✅ | 1 | 盖放魔法/陷阱卡（case_052） |
| `set_monster` | ✅ | 1 | 盖放怪兽（case_053） |
| `pay_cost` | ✅ | 1 | 支付 cost（case_054） |

---

## 2. 已覆盖操作类型详解

### 2.1 activate_effect（发动效果）

**最多使用的操作类型**（24 条 case）。

典型场景：
- 手坑发动（灰流丽、效果遮蒙者、尼比鲁）— case_001/006/016
- 墓地效果发动（凤凰人）— case_004
- 场上效果发动（冰剑龙、S:P、赫焉龙）— case_005/007/003
- 卡组/手牌间接效果发动（烙印相关）

关键必填字段：`effect_id`、`activation_location`

### 2.2 resolve_effect（效果处理）

13 条 case，对应 `task_type: effect_resolution_judgment`。

典型场景：
- 泡影同纵列无效已离场卡（case_002）
- 天救龙离场后分项处理（case_008）
- 墓穴指名者对象离场后的处理（case_025）
- 大搜捕对象变里侧后的处理（case_020）

关键必填字段：`effect_id`、`chain_id_to_resolve`、`declared_resolution`

### 2.3 activate_card（发动卡片）

12 条 case。

典型场景：
- 魔法卡发动（增援、闪刀启动、联合机库）— case_001
- 陷阱卡发动（神之通告、神之警告）— case_004/023
- 灵摆怪兽作为魔法发动 — case_027

关键必填字段：`activation_location`

### 2.4 declare_attack（攻击宣言）

2 条 case：case_003（S:P限制下直接攻击）、case_043（卡通世界被破坏后卷回）

关键必填字段：`attack_type`（`direct_attack` 或 `attack_monster`）、`card_location`、`card_zone`

### 2.5 special_summon（特殊召唤）

2 条 case：case_029（王谷下墓地自身特召手续）、case_046（灵摆召唤区域冲突）

用于判断特殊召唤本身是否合法（不是通过效果召唤，而是不入连锁的手续或 P召唤）。

### 2.6 select_target（选择对象）

1 条 case：case_048（暗之咒缚降攻后选择对象）

用于单独判断"取对象"这一环节是否合法。与 `activate_effect` 的区别：这里是拆解了发动过程，聚焦于对象选择这一子操作。

---

## 3. 2026-07-28 补齐的操作类型

原先以下 4 种操作类型没有独立 case，现已各补 1 条示范。

### 3.1 normal_summon（通常召唤）— case_051

被神之宣告无效的通常召唤**不计入**本回合通常召唤次数（2020.04 规则修订），
主要阶段 2 仍可再次通常召唤 → `legal`。

其余核心裁定场景（"不能通常召唤"限制下的效果召唤、上级召唤的祭品要求等）仍可作为扩充方向。

### 3.2 set_card（盖放魔陷）— case_052

暗黑神鸟适用中"不能把卡盖放"，不能盖放魔法/陷阱卡 → `illegal / external_restriction`。

> 魔封之芳香限制下"不能发动"已由 case_027 覆盖，但"盖放本身"的限制由本条 case 独立判断。

### 3.3 set_monster（盖放怪兽）— case_053

同样在暗黑神鸟限制下，不能盖放怪兽 → `illegal / external_restriction`。
盖放占用每回合 1 次的通常召唤名额，与 §3.1 的次数规则呼应。

### 3.4 pay_cost（支付 cost）— case_054

手牌只有发动卡自身时，不能支付"舍弃 1 张手牌"的 cost → `illegal / cost_payability`。

> 与 case_013/case_024 的区别：那两条在 `activate_effect`/`activate_card` 操作中检查 cost 可支付性；
> case_054 单独问"这个 cost 能否支付"而不管发动本身。
