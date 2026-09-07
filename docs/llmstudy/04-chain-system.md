# 04 — 连锁系统（Chain）

> **撰写日期**：2026-07-28
> **来源**：P0 官方规则书 (SD_RuleBook_EN_10.pdf) + P1 yugipedia + P2 ocg-rule
> **对应项目**：`pre_state.chain_state`、`current_chain_links`、`resolution_history` 字段

---

## 1. 什么是连锁（Chain）

连锁是处理多个卡片效果发动的**顺序机制**。当一方发动效果后，对方总是有机会用另一个效果来响应（"连锁"），形成一个 Chain。

**核心原则**：
- 每次有人发动效果，就形成一个"连锁块"（Chain Link）
- 双方轮流决定是否要追加发动效果
- 当双方都放弃追加时，连锁构建完成
- 然后**逆序处理**（最后发动的先处理）

---

## 2. 咒文速度（Spell Speed）

每个效果都有一个咒文速度（1-3），决定它能否响应其他效果：

| 速度 | 类型 | 能否连锁 | 能被谁连锁 |
|---|---|---|---|
| **1** | 通常魔法、装备魔法、场地魔法、永续魔法、仪式魔法、怪兽的起动/诱发/反转效果 | 不能主动连锁其他效果 | 速度 2 或 3 |
| **2** | 速攻魔法、通常陷阱、永续陷阱、怪兽的诱发即时效果（Quick Effect） | 可以连锁速度 1 或 2 | 速度 2 或 3 |
| **3** | 反击陷阱 | 可以连锁任何速度 | **只有**速度 3 |

> **核心限制**：只能连锁**等于或高于**前一个效果的咒文速度。速度 1 的效果只能是 Chain Link 1（除非多个速度 1 效果同时触发）。

---

## 3. 连锁的构建与处理

### 3.1 构建阶段（Chain Building）

```
C1: 玩家 A 发动"增援"（通常魔法，Spell Speed 1）
  ↓ 询问玩家 B：是否连锁？
C2: 玩家 B 发动"灰流丽"（诱发即时效果，Spell Speed 2）
  ↓ 询问玩家 A：是否连锁？
  （玩家 A 放弃）
  ↓ 询问玩家 B：是否继续？
  （玩家 B 放弃）
连锁构建完成 ← is_chain_building: false
```

### 3.2 逆顺处理（Chain Resolving）

构建完成后，从**最后一个连锁块开始向前处理**：

```
C2 先处理：灰流丽的效果→无效 C1 增援的效果
C1 后处理：增援被无效，效果不适用
```

> **关键概念**：处理 C2 时 C1 还没处理——卡片仍在场上。如果 C2 破坏了 C1 的卡，C1 处理时卡已不在场上（这会产生裁定问题，如 case_002）。

---

## 4. 同时触发的效果（SEGOC）

当多个诱发效果在同一时点满足条件时，按以下顺序组成连锁：

1. **回合玩家的必发效果**（任意顺序）
2. **非回合玩家的必发效果**（任意顺序）
3. **回合玩家的选发效果**（任意顺序）
4. **非回合玩家的选发效果**（任意顺序）

> 这就是"自排连锁"（SEGOC: Simultaneous Effects Go On Chain）。
> **case_010** 涉及公开手牌中露世的诱发效果与场上篝的诱发效果——是否仍适用自排连锁规则。

---

## 5. 快速效果时机（Fast Effect Timing）

非回合玩家也能在对方回合发动效果，但必须遵循**快速效果时机表**：

| 游戏状态 | 谁有优先权 | 可进行的操作 |
|---|---|---|
| **开放状态（Box A）** | 回合玩家 | 任何合法操作（通常召唤、发动速度 1 效果等） |
| **不启动连锁的动作后（Box B）** | 回合玩家 | 只能发动快速效果（速度 2+） |
| **回合玩家放弃后（Box C）** | 非回合玩家 | 快速效果 |
| **连锁构建中（Box D）** | 最后一个发动者的对方 | 追加连锁 |
| **阶段转换前（Box E）** | 非回合玩家 | 快速效果 |

### 关键规则

- **通常召唤后**：触发效果（如有）先组成连锁（黄框）→ 然后才轮到快速效果（B/C 框）
- **连锁处理完后**：游戏状态**不是开放状态**——先检查触发效果（黄框），然后双方轮流获得快速效果机会
- 只有在连锁完全处理完 + 没有新连锁 + 双方都放弃快速效果后，游戏状态才回到"开放"

---

## 6. 本项目的连锁表示

### 6.1 连锁编号

所有连锁编号统一使用大写 C 加数字：
```
C1, C2, C3, ...
```

禁用旧写法 `chain_link: 1`（v2.0.0 已废弃）。

### 6.2 连锁状态（chain_state）

```json
{
  "chain_state": {
    "is_chain_building": true,     // 正在构建连锁（还能追加）
    "is_chain_resolving": false,    // 不是正在逆顺处理
    "current_chain_links": [        // 当前连锁上的所有连锁块
      {
        "chain_id": "C1",
        "player": "opponent",
        "card": "闪刀启动：交闪",
        "operation_type": "activate_card",
        "effect_id": "main_effect",
        "effect_summary": "从卡组把一张「闪刀」卡加入手卡",
        "effect_features": ["add_from_deck_to_hand"],
        "activation_start_location": "hand",
        "activation_location": "spell_trap_zone",
        "activation_zone": "s3",
        "activation_column_index": 3
      }
    ]
  }
}
```

### 6.3 关键字段对应

| 字段 | 用途 | 示例 |
|---|---|---|
| `chain_id` | 连锁块的编号 | `"C1"` |
| `chain_response_to` | 表示本发动响应的连锁块 | `"C1"`（表明是 C2 连锁 C1） |
| `chain_id_to_resolve` | 当前要处理的连锁块 | `"C1"`（用于 resolve_effect 操作类型） |
| `resolved_chain_id` | 已经处理完成的连锁块 | `"C3"`（用于 resolution_history） |
| `current_chain_id` | 场上卡关联的当前连锁块 | `"C2"`（表明此卡在 C2 上发动） |

### 6.4 校验规则

`check_jsonlschema.py` 对连锁有以下校验：
- 所有 `chain_id` 必须在当前 case 内唯一
- `chain_response_to` 和 `chain_id_to_resolve` 必须引用 `current_chain_links` 中真实存在的连锁块
- `resolution_history` 中的 `resolved_chain_id` 必须引用当前连锁上下文中的 ID

---

## 7. 连锁相关裁定案例

| 场景 | 对应 case | 核心裁定点 |
|---|---|---|
| 灰流丽连锁增援 | case_001 | 诱发即时效果可以在对方回合发动，连锁速度 2 对速度 1 |
| 超融合不能被连锁 | case_012 | 卡的效果文本"不能对应这张卡的发动把卡的效果发动"→ 直接连锁不合法 |
| C1 魔法被 C3 炸掉后 C2 泡影是否还影响 | case_002 | 同纵列无效效果在对象卡离场后是否仍适用 |
| 整条连锁处理后另开触发 | case_031 | 卢恩神碑之泉的诱发时机 |
| "不能对应发动连锁"只限制直接连锁 | case_032 | C2 不能回应，但 C3 可以回应 C2… |

---

## 8. resolution_history（已处理连锁历史）

`resolution_history` 是 `pre_state` 的**必填字段**，记录当前判断时点之前已经处理完成的连锁结果：

```json
{
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
}
```

### 关键规则

1. **只记录已处理完成的连锁块**，不记录将要处理的内容
2. **顺序按实际处理时间**：连锁逆顺处理中高编号先处理（`C3 → C2 → C1`）
3. **空数组 `[]` 是有意义的**：表示"当前判断点前没有已处理连锁块"，不是缺失信息
4. **result 必须是非空数组**：没有结构化结果的不要写 history item
5. **持续限制写入 `known_constraints`**，不要写入 `resolution_history`

> 在 `effect_resolution_judgment` 类 case 中，`resolution_history` 帮助判断"已经处理完成的结果对当前待处理效果的影响"——这是效果处理合法性判断的核心依赖。
