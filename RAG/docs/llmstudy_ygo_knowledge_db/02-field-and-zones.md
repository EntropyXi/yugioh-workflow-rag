---
title: "场地与区域模型"
doc_id: "02"
collection: "llmstudy_ygo_knowledge_db"
tags:
  - 决斗场地
  - 区域
  - 纵列
  - column_index
  - 怪兽区域
  - 魔法陷阱区域
  - 场地区域
  - EX怪兽区域
  - 灵摆区域
  - 墓地
  - 除外
project_bindings:
  - pre_state.self_state.field
  - opponent_state.field
  - column_index
source: "docs/llmstudy/02-field-and-zones.md"
written: "2026-07-28"
---

# 02 — 场地与区域模型

> **撰写日期**：2026-07-28
> **来源**：P0 官方规则书 + P2 `ocg-rulebook.rtfd.io`
> **对应项目**：`pre_state.self_state.field` / `opponent_state.field` 结构、`column_index` 规则

---

## 1. 决斗场地总览

游戏王 OCG 的决斗场地（Field）由双方各半组成。每方有以下区域：

```
┌─────────────────────────────────────────────────────┐
│  [对方场地区]           [对方EX区]  [对方EX区]         │
│  [s5][s4][s3][s2][s1]   对方魔法&陷阱区 (5个)         │
│  [m5][m4][m3][m2][m1]   对方主怪兽区 (5个)            │
├─────────────────────────────────────────────────────┤
│  [m1][m2][m3][m4][m5]   我方主怪兽区 (5个)            │
│  [s1][s2][s3][s4][s5]   我方魔法&陷阱区 (5个)         │
│  [我方场地区]           [我方EX区]  [我方EX区]         │
│  我方卡组  我方额外卡组  我方墓地  我方除外区           │
└─────────────────────────────────────────────────────┘
```

> "场上的卡"（`field`）指放在主怪兽区、EX 怪兽区、魔陷区、场地区、P 区域的卡片。
> 手牌、卡组、额外卡组、墓地、除外区**不算场上的卡**。

---

## 2. 区域详解

### 2.1 主怪兽区域（Main Monster Zone）

- 数量：**5 个**（m1 ~ m5）
- 用途：放置怪兽卡（通常召唤、特殊召唤、盖放）
- 空位：没有怪兽时用 `"card": null` 表示
- 限制：每方最多同时 5 只怪兽在场

### 2.2 魔法&陷阱区域（Spell & Trap Zone）

- 数量：**5 个**（s1 ~ s5）
- 用途：发动或盖放魔法卡、陷阱卡
- 特殊：最左（s1）和最右（s5）同时也是**灵摆区域（Pendulum Zone）**——当灵摆怪兽作为魔法卡发动时放置在此
- 限制：每方最多同时 5 张魔陷（包括盖放的和表侧表示的）

### 2.3 场地区域（Field Spell Zone）

- 数量：**1 个**（每方）
- 用途：放置场地魔法卡
- **不计入**魔陷区的 5 张限制
- 空位：用 `null` 表示

### 2.4 EX 怪兽区域（Extra Monster Zone）

- 数量：**2 个**（emz_left, emz_right），双方共享
- 用途：从 EX 卡组特殊召唤连接怪兽和表侧灵摆怪兽（必须放这里或连接端指向的主怪兽区）
- 规则：每方最多使用 1 个 EX 区（特殊效果例外）；融合/S/X 怪兽可以自由选择放 EX 区或主怪兽区
- 空位：`column_index` 为 `null`

---

## 3. 纵列（Column）规则

### 3.1 基本概念

**纵列**是贯穿双方场地的一条垂直线。共 5 个纵列：

```
纵列 1：self.m1 + self.s1 ←→ opp.s5 + opp.m5
纵列 2：self.m2 + self.s2 ←→ opp.s4 + opp.m4
纵列 3：self.m3 + self.s3 ←→ opp.s3 + opp.m3
纵列 4：self.m4 + self.s4 ←→ opp.s2 + opp.m2
纵列 5：self.m5 + self.s5 ←→ opp.s1 + opp.m1
```

### 3.2 column_index 规则（本项目核心约定）

本项目 Schema 中，`column_index` 以**我方视角**为基准：

```
self:   m1/s1=1, m2/s2=2, m3/s3=3, m4/s4=4, m5/s5=5
opp:    m1/s1=5, m2/s2=4, m3/s3=3, m4/s4=2, m5/s5=1
```

> **关键**：判断同纵列时，只需比较 `self.column_index == opp.column_index`。Workflow 不应再做 `opp_m_i → self_m_(6-i)` 手动换算。

### 3.3 本项目校验规则

`check_jsonlschema.py` 中的 `_validate_column_mapping` 方法会自动校验双方纵列映射是否正确：

```python
# self:  → [1, 2, 3, 4, 5]
# opponent: → [5, 4, 3, 2, 1]
```

---

## 4. 本项目的场上状态表示

### 怪兽区域表示（five_zones）

```json
{
  "monster_zones": {
    "m1": { "column_index": 1, "card": null },
    "m2": { "column_index": 2, "card": { "name": "灰流丽", "status": "face_up", ... } },
    "m3": { "column_index": 3, "card": null },
    "m4": { "column_index": 4, "card": null },
    "m5": { "column_index": 5, "card": null }
  }
}
```

### 魔陷区域表示（five_spell_trap_zones）

同样结构，键名 `s1`~`s5`。

### 场地区域表示

```json
"field_spell_zone": null   // 空
// 或
"field_spell_zone": {
  "card": { "name": "完美卡通世界", "status": "face_up", "card_type": "spell", "spell_type": "field_spell", "controller": "opponent" }
}
```

> 场地魔法区域不包含 `column_index`。

### EX 怪兽区域

```json
"extra_monster_zones": {
  "emz_left":  { "column_index": null, "card": null },
  "emz_right": { "column_index": null, "card": null }
}
```

---

## 5. 区域的规则约束（裁定相关）

### 5.1 区域不可用（zone_availability）

当效果或规则要求特殊召唤但对应区域满时，操作不合法。例如：
- 主怪兽区 5 只全满 → 不能通常召唤
- 魔陷区 5 张全满 → 不能发动新的魔法/陷阱卡
- 连接怪兽只能出在 EX 区或连接端，对应位置被占时可能无法连接召唤

> **case_046**：灵摆召唤因通道限制 + 区域冲突被判定为 `illegal / zone_availability`

### 5.2 同纵列效果

部分卡（如"无限泡影"）影响同纵列的其他卡。本项目在 `known_constraints` 中以以下方式建模：

```json
{
  "type": "same_column_spell_trap_negation",
  "source_card": "无限泡影",
  "source_zone": "self.field.spell_trap_zones.s4",
  "affected_column_index": 4,
  "duration": "until_end_of_turn"
}
```

> **case_002** 的核心问题：泡影的同纵列无效效果，在对象卡因连锁处理离场后是否仍适用。

### 5.3 灵摆区域与魔陷区的重叠

s1 和 s5 同时是灵摆区域。当作魔法卡发动的灵摆怪兽占用该位置，计入魔陷区 5 张限制。

### 5.4 陷阱怪兽与区域释放（2020 规则）

永续陷阱卡发动后特殊召唤到怪兽区域的场合，原来的魔陷区域**被释放**，可以放置新的卡。这改变了旧规则中陷阱怪兽"锁死"一个魔陷区的行为。
