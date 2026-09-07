---
title: "裁定判断方法论"
doc_id: "14"
collection: "llmstudy_ygo_knowledge_db"
tags:
  - 判断流程
  - label
  - failed_check
  - reasoning_steps
  - missing_info
  - 任务类型
  - 合法性判断
project_bindings:
  - gold_answer.label
  - failed_check
  - reasoning_steps
  - missing_info
source: "docs/llmstudy/14-judgment-methodology.md"
written: "2026-07-28"
---

# 14 — 裁定判断方法论

> **撰写日期**：2026-07-28
> **来源**：项目 `docs/task_scope.md` + `docs/schema.md` + 58 条 case 的分析
> **对应项目**：`gold_answer.label`、`failed_check`、`reasoning_steps`、`missing_info`

---

## 1. 判断流程

本项目的裁定判断遵循 **9 步标准流程**：

```
1. 存在合法操作窗口？
   NO → illegal / activation_window
   YES ↓
2. 操作能在该窗口发动/执行？
   NO → illegal / activation_window
   YES ↓
3. 发动/召唤/攻击条件是否满足？
   NO → illegal / activation_condition (或 summon_condition)
   YES ↓
4. Cost 是否可支付？
   NO → illegal / cost_payability
   YES ↓
5. 对象是否合法（发动时+处理时）？
   NO → illegal / target_legality
   YES ↓
6. 是否违反次数限制（一回合一次等）？
   YES → illegal / once_per_turn
   NO ↓
7. 是否受持续效果/召唤限制/攻击限制/区域限制/伤害步骤限制等约束？
   YES → illegal / external_restriction (或 phase_or_step_restriction / zone_availability)
   NO ↓
8. 效果处理是否按声明方式适用？
   NO → illegal / effect_resolution_rule
   YES ↓
9. 输出结论 + 推理链 + 证据
```

---

## 2. 输出标签（Label）语义

| 标签 | 含义 | 何时使用 | missing_info |
|---|---|---|---|
| `legal` | 操作合法 | 所有检查点通过 | 空数组 |
| `illegal` | 操作不合法 | 某个检查点失败 | 空数组 |
| `depends` | 信息不足 | 缺少关键事实无法判断 | **非空** |
| `invalid_question` | 超出任务边界 | 不属于规则合法性任务 | 空数组 |

### 2.1 为什么前 50 条 case 没有 `depends`，而后补了 2 条示范

游戏王的裁定在**完整场景已知**的前提下是非黑即白的：
- 给了你 pre_state + attempted_operation → 所有判断要素都在数据内
- 不存在"这个情况取决于玩家选择"——因为 attempted_operation 已经固定了玩家的选择
- `depends` 是留给"pre_state 信息确实不完整"的场景

前 50 条 case 的 pre_state 信息都足够判断，因此没有 depends。为示范该标签的用法，
case_057 与 case_058 刻意留白关键信息：

- **case_057**：对方盖卡内容未知，雷击的发动本身合法但破坏结果无法确定 → `depends / unknown_missing_info`，`missing_info` 记录"对方盖卡的内容"。
- **case_058**：缺少对方本回合是否已使用过增殖的 G 的信息 → `depends / unknown_missing_info`，`missing_info` 记录一次使用记录。

---

## 3. failed_check 枚举详解

| failed_check | 检查点 | 典型场景 | 对应 case |
|---|---|---|---|
| `activation_window` | 发动窗口 | 召唤成功时不能先发动起动效果、优先权在对方、非主要阶段不能发速度1效果 | 006, 011, 021, 022 |
| `activation_condition` | 发动条件 | 卡片/效果的发动条件不满足 | 004, 005, 027, 042, 047, 050 |
| `chain_speed` | 连锁速度 | 速度1不能连锁速度2、反击陷阱只能被反击陷阱连锁 | 012 |
| `cost_payability` | Cost 可支付性 | 宏观宇宙下不能送墓cost、灵摆怪兽不能送墓、手牌只有发动卡自身 | 013, 024, 054 |
| `target_legality` | 对象合法性 | 发动时/处理时对象不合法、对象离场 | 025, 048 |
| `card_location` | 卡片位置 | 卡不在应有位置发动 | 055 |
| `once_per_turn` | 次数限制 | 一回合一次已使用、●项目被无效仍算选择 | 007, 037 |
| `phase_or_step_restriction` | 阶段限制 | 不能在该阶段发动（如伤害步骤限制） | 026 |
| `summon_condition` | 召唤条件 | 米德拉什限制、苏生限制 | 016, 036 |
| `material_legality` | 素材合法性 | 融合/同调/超量/连接素材不满足 | 056 |
| `zone_availability` | 区域可用 | 怪兽区满、灵摆召唤区域冲突 | 046 |
| `effect_resolution_rule` | 效果处理规则 | 离场后效果无效、持续效果影响处理、替代破坏后处理 | 002, 018, 034, 035, 040 |
| `external_restriction` | 外部限制 | 王谷限制、卡通世界限制、替代破坏限制、不能盖放限制 | 029, 039, 043, 052, 053 |
| `unknown_missing_info` | 信息缺失 | 无法判断具体哪个 check 失败 | 057, 058 |

---

## 4. 两类 task_type 的判断差异

### 4.1 operation_legality_judgment（45 条）

判断"能不能发动/召唤/攻击"：
- pre_state 通常处于开放状态或连锁构建中
- 重点检查：窗口、条件、cost、对象（发动时）、次数限制、外部限制

### 4.2 effect_resolution_judgment（13 条）

判断"效果处理是否能按声明方式适用"：
- pre_state 通常处于连锁处理中（`state_timing: before_resolving_C1`）
- 必须有 `resolution_history` 记录已处理的连锁块
- 重点检查：处理时对象是否仍合法、是否符合效果处理规则、已处理的连锁结果对当前处理的影响

---

## 5. reasoning_steps 的撰写规范

每条 case 的 `reasoning_steps` 是逐步推理链：

1. **陈述已知事实**：pre_state 的 key facts
2. **引用规则或裁定**：fid/cid 的具体内容
3. **检查一致性**：fact vs rule
4. **得出结论**：legal/illegal + failed_check

---

## 6. 与本项目的校验对应

`check_jsonlschema.py` 中有多种校验直接映射到判断方法论：

| 校验 | 对应方法论 |
|---|---|
| `task_type` 与 `operation_type` 一致性 | resolve_effect ↔ effect_resolution_judgment |
| `chain_response_to` 引用有效性 | 窗口/连锁引用 |
| `resolution_history` 完整性与逆序 | 效果处理判断的前提 |
| case_003/005 防回退 | 关键裁定的建模正确性 |
