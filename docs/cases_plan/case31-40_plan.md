# case_031–case_040 官方 Q&A 扩充计划

## Summary

新增 10 条 gold cases，对应刚确认的 10 个不重复官方 Q&A 方向。每条 case 都逐条核验 KONAMI 官方 Q&A、日文官方卡片文本、简中官方卡片文本；写入 `gold_cases/json/case031.json` 至 `case040.json`，再同步 `gold_cases/operation_legality_cases.jsonl`。不修改现有 30 条 case 的裁定结论。

## Implementation Changes

- 新增 case 编号与主题固定如下：

  1. `case_031`：发动窗口 / 连锁处理后触发  
     `fid:23650`，「神碑之泉」②在整条连锁处理后另开时点发动，可选择作为触发原因且已送墓的「神碑」速攻魔法。

  2. `case_032`：连锁限制范围  
     `fid:16924`，“对这个发动不能连锁”只限制直接连锁该发动；发动者自己再连锁别的效果后，对方可以继续连锁。

  3. `case_033`：cost / 已展示手牌复用  
     `fid:24176`，同一连锁上，已经因手牌效果发动或作为 cost 展示的手牌，仍可再次作为展示 cost。

  4. `case_034`：对象与后续处理  
     `fid:20675`，「魂食恐龙 盗蛋龙」②的破坏对象被「失落世界」替代破坏而未破坏时，“之后从墓地特殊召唤”不适用。

  5. `case_035`：伤害步骤 / 同一时点诱发组链  
     `fid:7840`，「A・O・J 灾亡虫」与「N・大地鼹鼠」同在伤害步骤开始时发动；必发效果为 C1，可选效果为 C2，逆顺处理后 C1 可能结果不适用。

  6. `case_036`：召唤限制 / 无视召唤条件仍需正规出场  
     `fid:23799`，从墓地、除外或表侧额外卡组用“无视召唤条件”特殊召唤特殊召唤怪兽时，仍要求该怪兽曾正规特殊召唤过。

  7. `case_037`：一次限制 / 选项被无效仍算选择  
     `fid:23977`，“各效果1回合只能选择1次”的 `●` 项目，即使发动或效果被无效，也视为已经选择过同一项目。

  8. `case_038`：持续效果 / 效果不被无效不等于发动不被无效  
     `fid:21378`，“发动的效果不会被无效”只保护成功发动后的效果，不保护发动本身；仍可被「神之通告」等无效发动。

  9. `case_039`：替代破坏 / 不能选择不受影响或不会被破坏的卡  
     `fid:20948`，替代破坏效果不能选择不受该效果影响的卡，也不能选择不会被效果破坏的卡。

  10. `case_040`：效果处理 / 暂时除外期间事件不追溯  
      `fid:24348`，卡通怪兽暂时除外期间「卡通世界」被破坏，怪兽返回后不会因该已发生事件被自身效果破坏。

- 每条新增 case 必须包含：

  - `schema_version: "2.0.0"`。
  - 必填 `pre_state.resolution_history`：没有已处理连锁时写 `[]`；若判断依赖已处理连锁，按实际处理顺序填写。
  - `required_sources` 至少包含：
    - 1 条 `official_ruling`：KONAMI 日文 Q&A，记录 `fid`、标题、URL、`source_updated_at`。
    - 关键卡的日文 `official_card_text`。
    - 关键卡的简中 `official_card_text`。
  - 中文问题、中文上下文、中文推理步骤、中文结论。
  - 不使用二手来源作为正式依据。

- Schema 与校验：

  - 优先复用现有 `failed_check`、`operation_type`、`resolution_history.action`。
  - 仅在新增 case 真实需要时，最小补充 `effect_features` 或 action 枚举。
  - 若新增枚举，必须同步更新 `docs/schema.md` 和 changelog。
  - 不扩大 schema 语义，不更改已有 30 条 case 的答案。

- 文档与日志：

  - 更新 `docs/PROJECT_CONTEXT.md`：gold cases 从 30 条变为 40 条，补充 `case_031`–`case_040` 列表。
  - 更新 `docs/schema.md`：记录新增枚举或确认无新增枚举。
  - 更新 `log/ygo_json_case_changelog.md`：追加 2026-07-07 的 case_031–case_040 扩充记录。
  - 若模板或校验说明因新增表达方式需要补充，同步更新 `docs/cases_json_template.md`。

## Test Plan

- 每条 case 完成后先做单条结构检查；10 条完成后同步主 JSONL。
- 运行：

  ```powershell
  conda run -n YGO_PROJECT python check_jsonlschema.py --self-test
  ```

- 验收标准：

  - 主 JSONL 共 40 行，无空行，每行一个 JSON object。
  - ID 从 `case_001` 到 `case_040` 连续。
  - `gold_cases/json/case001.json` 至 `case040.json` 与主 JSONL 完全一致。
  - 40 条 case 全部含 `pre_state.resolution_history`。
  - 新增 10 条均有官方 Q&A、日文官方卡片文本、简中官方卡片文本。
  - `case_031`–`case_040` 不复用现有 30 条的核心裁定点。
  - self-test 输出正式数据通过，10 个负例全部被拒绝。
  - 程序化接口返回 `40 0 True`。

## Assumptions

- 本轮只新增 `case_031`–`case_040`，不修改已有 30 条 case 的裁定结论。
- 当前仍使用 `schema_version: "2.0.0"`。
- `accessed_at` 使用当前项目日期 `2026-07-07`。
- 写作时继续逐条核验官方 Q&A 与官方卡片文本；若某条简中官方卡片页无法定位，不伪造来源，暂停该条并替换为同方向备选。
