# 拆分 `effect_resolution_judgment` 为独立 `task_type` 的迁移计划

> 状态：历史计划，已执行。当前真实状态以 `docs/operation_case.schema.json`、`docs/PROJECT_CONTEXT.md` 与 `log/ygo_json_case_changelog.md` 顶部 Current Snapshot 为准。本文件保留为迁移记录，不再作为当前待执行计划。

## 一、目标

将目前统一为 `operation_legality_judgment` 的 40 条 case 一分为二：凡 `attempted_operation.operation_type` 为 `resolve_effect` 的 case，其 `task_type` 改为 `effect_resolution_judgment`；其余保持 `operation_legality_judgment`。

## 二、影响范围

### 2.1 涉及的 case（11 条）

| ID | 场景 | 当前 `task_type` | 新 `task_type` |
|---|---|---|---|
| case_002 | 无限泡影同纵列无效烙印之气炎 | `operation_legality_judgment` | `effect_resolution_judgment` |
| case_008 | 天救龙离开手牌后的分项处理 | `operation_legality_judgment` | `effect_resolution_judgment` |
| case_009 | 龙引导呼笛与场上卡名视为 | `operation_legality_judgment` | `effect_resolution_judgment` |
| case_017 | 路西菲尔同时特召两只同名堕天使 | `operation_legality_judgment` | `effect_resolution_judgment` |
| case_018 | 颠茄歌后仍受技能抽取持续效果影响 | `operation_legality_judgment` | `effect_resolution_judgment` |
| case_020 | 大搜捕对象同连锁变里侧后的处理 | `operation_legality_judgment` | `effect_resolution_judgment` |
| case_025 | 墓穴指名者对象处理时离开墓地 | `operation_legality_judgment` | `effect_resolution_judgment` |
| case_030 | 抽牌小丑与封锁鸟下双螺旋特工选择替代处理 | `operation_legality_judgment` | `effect_resolution_judgment` |
| case_034 | 食魂窃蛋龙对象被失落世界替代破坏后的后续处理 | `operation_legality_judgment` | `effect_resolution_judgment` |
| case_035 | 灾难兽与大地鼹鼠在伤害步骤开始时组链处理 | `operation_legality_judgment` | `effect_resolution_judgment` |
| case_036 | 无视召唤条件仍要求特殊召唤怪兽正规出场履历 | `operation_legality_judgment` | `effect_resolution_judgment` |

其余 29 条 case 不变。

### 2.2 涉及的文件（9 个）

| 文件 | 改动类型 |
|---|---|
| `docs/operation_case.schema.json` | `task_type` 从 `const` 改 `enum` |
| `gold_cases/json/case002.json` 等 11 个镜像文件 | `task_type` 值替换 |
| `gold_cases/operation_legality_cases.jsonl` | 11 行对应的 `task_type` 值替换（通过 `sync_gold_jsonl.py` 同步） |
| `docs/schema.md` | `task_type` 枚举表说明更新 |
| `docs/PROJECT_CONTEXT.md` | 状态快照、case 表格更新 |
| `docs/task_scope.md` | 增加对两种 task_type 的区分说明 |
| `docs/cases_json_template.md` | 两个模板的 `task_type` 更新（效果处理模板改为 `effect_resolution_judgment`） |
| `check_jsonlschema.py` | 新增跨验证规则 + 新增负例自测 |
| `log/ygo_json_case_changelog.md` | 新增迁移日志 |

## 三、具体步骤

### Step 1：Schema 变更

文件：`docs/operation_case.schema.json`

**改动 1**：`task_type` 字段（第 19 行）

```json
// 旧
"task_type": { "const": "operation_legality_judgment" }

// 新
"task_type": { "enum": ["operation_legality_judgment", "effect_resolution_judgment"] }
```

**改动 2**：Schema 元数据同步

- `$id` 更新为 `v2.1`
- `title` 同步更新版本号

**不 bump `schema_version` 数据字段**：case 数据中 `schema_version` 的 `const` 保持 `"2.0.0"` 不变。因为本次只是 `task_type` 多了一个合法枚举值，case 的 JSON 顶层结构、必填字段、嵌套结构均未改变。这与 v2.0.0 迁移（废弃旧字段、新增必填字段）性质不同。Schema 文件本身的版本在 changelog 中记为 `v2.1.0`。

### Step 2：更新校验器

文件：`check_jsonlschema.py`

**改动 1**：在 `validate_business_rules()` 的 per-case 循环中新增 `task_type` 与 `operation_type` 一致性校验：

```python
# 新增到 validate_business_rules() 的 per-case 循环中
attempted_op_type = attempted.get("operation_type", "")
case_task_type = case.get("task_type", "")

if attempted_op_type == "resolve_effect" and case_task_type != "effect_resolution_judgment":
    report(case_id, "task_type",
           "resolve_effect requires task_type effect_resolution_judgment")

if case_task_type == "effect_resolution_judgment" and attempted_op_type != "resolve_effect":
    report(case_id, "task_type",
           "effect_resolution_judgment requires operation_type resolve_effect")
```

**改动 2**：新增一条负例自测（数量从 10 → 11）：

```python
# 新增：effect_resolution_judgment 搭配错误的 operation_type
bad = copy.deepcopy(by_id["case_002"])
bad["attempted_operation"]["operation_type"] = "activate_effect"
business_must_fail("effect_resolution_judgment with non-resolve operation", bad)
```

**改动 3**：更新 `self_test_count()` 返回值从 `10` 改为 `11`。

### Step 3：编辑 11 个格式化镜像 JSON

对于每个文件（`gold_cases/json/case002.json` 等 11 个），将：

```json
"task_type": "operation_legality_judgment"
```

替换为：

```json
"task_type": "effect_resolution_judgment"
```

> **注意**：case_002 的 `current_chain_links` 中各连锁项有自己的 `operation_type` 字段（如 `"activate_card"`），那些是描述连锁块性质的内嵌字段，与顶层的 `task_type` 无关，不要误改。

### Step 4：同步主 JSONL

```powershell
conda run -n YGO_PROJECT python tools/sync_gold_jsonl.py
```

`sync_gold_jsonl.py` 会从 `gold_cases/json/case*.json` 按文件名排序重建主 JSONL，生成 40 行、每行一个完整 JSON object。

### Step 5：运行校验

```powershell
conda run -n YGO_PROJECT python check_jsonlschema.py --self-test
```

预期输出：

```
Validating D:\yugioh-workflow-rag\gold_cases\operation_legality_cases.jsonl...
[OK] ... passed schema and business validation.
[OK] 11 negative validation scenarios rejected.
```

验收标准：
- 40 条 case 全部通过 Schema 校验
- 11 条 case 通过新增的 task_type/operation_type 一致性规则
- 40 个格式化 gold JSON 与主 JSONL 完全一致
- 11 个负例均被拒绝（含新增的 1 个）
- 退出码为 0

### Step 6：更新文档

**`docs/schema.md`**：

- 第 55 行：`task_type` 说明从 "当前固定为 `operation_legality_judgment`" 改为 "允许 `operation_legality_judgment` 或 `effect_resolution_judgment`"
- 第 38 行：顶层结构示例的 `task_type` 值改为 `"operation_legality_judgment"`，并注明另可选 `"effect_resolution_judgment"`

**`docs/PROJECT_CONTEXT.md`**：

- 第 47 行状态表：task type 列改为 `operation_legality_judgment (29) / effect_resolution_judgment (11)`
- 第 58-59 行：删除 "目前 `resolve_effect` 仍属于同一个 `operation_legality_judgment` task type；是否拆分 `effect_resolution_judgment` 尚未决定"
- 第 384-425 行 case 表格：11 条 `resolve_effect` case 的行增加新 task_type 标注
- 第 539-546 行 Pending：删除 "决定是否将效果处理判断拆成独立 task type"

**`docs/task_scope.md`**：

- 在 "1. 任务目标" 或适当位置增加段落，区分两种 task_type 的语义：
  - `operation_legality_judgment`：判断发动、召唤、攻击宣言等操作是否合法。`pre_state` 通常 `is_chain_building: true` 或 `is_chain_resolving: false`
  - `effect_resolution_judgment`：判断效果处理是否按声明方式合法。`pre_state` 通常 `is_chain_resolving: true`，含 `state_timing` 和实际的 `resolution_history`

**`docs/cases_json_template.md`**：

- 发动/连锁合法性模板（第 21 行）：`task_type` 保持 `operation_legality_judgment`
- 效果处理合法性模板（第 157 行）：`task_type` 改为 `effect_resolution_judgment`

### Step 7：更新 Changelog

文件：`log/ygo_json_case_changelog.md`

在当前 changelog 顶部（"# Part 1. JSON 格式变化日志" 之前）插入新条目：

```markdown
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
```

同时更新文件底部 `# Open Items` 区域：

- **Completed**：新增 "已将 `effect_resolution_judgment` 拆分为独立 task_type"
- **Pending**：删除 "决定是否将 `operation_legality_judgment` 和 `effect_resolution_judgment` 分成两个 task_type"

## 四、执行顺序

```
1. 改 Schema        → task_type const → enum
2. 改校验器         → 新增一致性规则 + 新负例 + self_test_count
3. 改 11 个镜像     → 逐个替换 task_type 值
4. 同步 JSONL       → python tools/sync_gold_jsonl.py
5. 运行校验         → conda run -n YGO_PROJECT python check_jsonlschema.py --self-test
6. 改 5 个文档      → schema.md / PROJECT_CONTEXT / task_scope / template / changelog
7. 再次校验         → --self-test 确认全部通过
```

步骤 1-4 如有任何一步校验失败，停止并排查，不得跳过校验进入下一步。

## 五、兼容性评估

| 维度 | 影响 |
|---|---|
| Schema | 向后兼容——旧值 `operation_legality_judgment` 仍在 enum 中 |
| 下游 workflow | 如按 `task_type` 硬编码了单值断言，需更新为枚举匹配；如按 `operation_type` 做分支（当前推荐做法），无影响 |
| 校验器 CLI / 类接口 | 参数、输出格式、退出码语义均不变 |
| 现有 29 条 case | 完全不修改 |
| `tools/sync_gold_jsonl.py` | 不需要改 |
| case ID 连续、来源 ID 全局唯一 | 不受影响 |
| `resolution_history` 引用、逆顺处理顺序、时点一致性 | 不受影响 |
| `column_index` 纵列映射 | 不受影响 |
| case_003 / case_005 防回退规则 | 不受影响 |

## 六、不建议做的扩展

- **不要**新增 `operation_type` 枚举值。`resolve_effect` 已经存在且语义明确。
- **不要**为 `effect_resolution_judgment` 新增不同的 Schema 顶层约束（如 Schema 层强制 `is_chain_resolving: true`）。两类 case 在数据结构层面完全相同，差异是填写惯例而非结构差异，硬约束会破坏灵活性。
- **不要** bump 数据字段 `schema_version` 的 `const` 值。case 数据结构未变，仍然是 `"2.0.0"` 兼容的数据形态。
- **不要**改变 `gold_answer.label` 或 `failed_check` 的枚举。拆分的是任务类型，不是输出判断标准。
