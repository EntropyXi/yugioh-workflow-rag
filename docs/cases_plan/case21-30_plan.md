# case_021–case_030 逐条官方裁定写作计划

## Summary

基于你给定的 10 个新候选，新增 `case_021` 至 `case_030`。本轮采用“一个 case 一个 case 处理”的方式：每条都先逐页核验 KONAMI 官方 Q&A、日文官方卡片文本、简中官方卡片文本，再写入镜像 JSON，单条校验通过后才进入下一条。最终同步主 JSONL，并更新文档与 changelog。

## Implementation Changes

- 新增 10 条镜像 case：

  - `case_021`：召唤成功时不能先发动起动效果，`fid:10040`
  - `case_022`：「欧贝利斯克的巨神兵」召唤成功时发动封锁，`fid:8159`
  - `case_023`：「神之警告」连锁包含特殊召唤处理的效果，`fid:23408`
  - `case_024`：场上灵摆怪兽不能送墓作为 cost，`fid:24195`
  - `case_025`：「墓穴的指名者」对象处理时离开墓地，`fid:10677`
  - `case_026`：效果直接进行伤害计算时没有中间发动窗口，`fid:17979`
  - `case_027`：「魔封的芳香」与灵摆区域 / 灵摆召唤，`fid:13149`
  - `case_028`：「陷阱诡计」适用后，陷阱发动被无效与效果被无效的差异，`fid:22010`
  - `case_029`：「王家长眠之谷」与墓地自身特殊召唤手续，`fid:20408`
  - `case_030`：「SPYRAL－双螺旋特工」在不能从卡组加入手牌时的替代处理，`fid:14784`

- 每条 case 的固定流程：

  1. 访问并核验对应 KONAMI 日文 Q&A 正文，不用记忆补裁定。
  2. 逐张核验关键卡的日文官方卡片数据库文本。
  3. 逐张核验关键卡的简中官方数据库文本。
  4. 翻译并写成中文问题、中文上下文、中文推理步骤和中文结论。
  5. 写入 `gold_cases/json/case0NN.json`。
  6. 单条运行校验；若 schema 枚举不足，只补充该 case 实际需要的最小枚举。
  7. 单条通过后再进入下一条。

- 来源字段继续遵守现有 v2 规则：

  - Q&A 用 `source_type: "official_ruling"`，记录 `fid:xxxxx`、标题、URL、语言、访问日期、支持的推理步骤。
  - 日文卡片文本用 `official_card_text` + `language: "ja"`。
  - 简中卡片文本用 `official_card_text` + `language: "zh-CN"`。
  - 不用二手来源作为正式依据，不伪造无法访问的来源。

- 最后统一同步：

  - 用 `tools/sync_gold_jsonl.py` 从 `gold_cases/json/case*.json` 重建 `gold_cases/operation_legality_cases.jsonl`。
  - 更新 `docs/PROJECT_CONTEXT.md`、`docs/schema.md` 和 `log/ygo_json_case_changelog.md`。
  - 若新增枚举或表达模式，记录到 schema 文档和 changelog。

## Important Verification Notes

- `case_030` 的候选描述里写了「增殖的 G」等“不能从卡组加入手牌”的效果；实现时必须以 `fid:14784` 官方正文为准。如果官方 Q&A 实际对应的是「小丑与锁鸟」等禁止检索效果，则 case 文本应改用官方裁定中的真实卡名，不沿用错误 paraphrase。
- 如果某个候选的关键卡无法在简中官方数据库定位，先暂停该 case，列出缺失来源；不直接跳过、不伪造、不批量替换。
- 如果某条候选和既有 `case_001`–`case_020` 的规则点过近，保留该候选但在写作中明确差异焦点；若差异不足以成立新 case，则暂停并报告。

## Test Plan

- 每完成一条 case 后运行针对该单 case 的 JSON Schema / 业务规则检查。
- 10 条完成后运行：

  ```powershell
  conda run -n YGO_PROJECT python check_jsonlschema.py --self-test
  ```

- 验收标准：

  - 主 JSONL 共 30 行，无空行，每行一个 JSON object。
  - `case_001` 至 `case_030` ID 连续。
  - `gold_cases/json/case001.json` 至 `case030.json` 与主 JSONL 完全一致。
  - 30 条 case 均至少有官方 Q&A 或官方规则书依据。
  - 新增 10 条均包含日文官方 Q&A、日文官方卡片文本、简中官方卡片文本。
  - 现有 20 条 case 内容、结论和来源不被改动，除非必要的 schema 枚举兼容更新。

## Assumptions

- 本轮只新增 `case_021`–`case_030`，不改已有 20 条裁定结论。
- 继续使用 `schema_version: "2.0.0"`。
- 当前日期按 `2026-07-07` 写入 `accessed_at`。
- 仍坚持逐条访问、逐条写入、逐条校验；不批量抓取、不凭记忆补正文。
