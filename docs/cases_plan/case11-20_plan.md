# case_011–case_020 官方来源扩充计划

> 当前路径补注：本计划执行后，格式化镜像 JSON 已迁移至 `gold_cases/json/caseNNN.json`；主 JSONL 仍为 `gold_cases/operation_legality_cases.jsonl`。下方历史计划文本保留当时路径表述。

## Summary

新增 10 条 gold cases，对应之前筛出的 10 个 KONAMI 官方 Q&A 裁定；每条 case 都使用：

- 裁定依据：KONAMI 官方日文 Q&A / 规则来源；
- 卡片效果文本：KONAMI 日文卡片数据库 + 简中官方卡片数据库 `https://db.yugioh-card-cn.com/card_search.action.html`；
- 结论与推理：全部翻译为中文；
- 数据位置：继续写入 `gold_cases/operation_legality_cases.jsonl`，并新增 `gold_cases/case011.json` 至 `gold_cases/case020.json`。

## Implementation Changes

- 写入 10 条新 case，编号固定为：

  1. `case_011`：发动窗口，Union Hangar 在同一连锁处理中的特殊召唤后不能另开诱发。
  2. `case_012`：连锁限制，超融合发动后对方不能连锁反击陷阱等。
  3. `case_013`：cost 支付，宏观宇宙/次元吸引者下“丢弃”与“送墓作为 cost”的差异。
  4. `case_014`：对象合法性，已发动的通常魔陷是否能成为回手/回卡组效果对象。
  5. `case_015`：伤害步骤，伤害步骤中怪兽不受陷阱/技能抽取影响的适用。
  6. `case_016`：召唤限制，结界像限制下不能选择最终会变属性的非 DARK 原属性怪兽。
  7. `case_017`：一回合一次，同时特殊召唤同名怪兽不违反“一回合一次特殊召唤”。
  8. `case_018`：持续效果，“不受发动的效果影响”仍会受技能抽取等持续效果影响。
  9. `case_019`：效果处理，世海龙在召唤限制下能发动，处理时只返回可特殊召唤的怪兽。
  10. `case_020`：对象关系/持续适用，强夺类控制效果对象变里侧后的处理差异。

- 为支持简中官方卡片数据库，最小化更新 schema 与校验器：

  - `official_card_text` 允许官方来源域名新增 `https://db.yugioh-card-cn.com/`；
  - 简中卡片来源使用 `language: "zh-CN"`；
  - 日文 KONAMI 卡查继续使用 `language: "ja"`；
  - 裁定来源仍必须是 `official_ruling`，优先 `www.db.yugioh-card.com/yugiohdb/faq_search.action?...fid=...`。

- 扩展当前 schema 中不足以表达新增 case 的枚举：

  - 仅补充 case_011–case_020 实际需要的 `effect_features`；
  - 必要时补充 cost/action 的最小字段表达；
  - 不改变现有 10 条 case 的结论、字段含义或文件路径。

- 每条 case 的 `required_sources` 至少包含：

  - 1 条日文 KONAMI Q&A：`official_ruling`；
  - 1 条日文 KONAMI 卡片文本：`official_card_text`；
  - 1 条简中官方卡片文本：`official_card_text`；
  - 若一个 case 涉及多张关键卡，则关键卡都补齐官方卡查来源。

- 更新项目文档和日志：

  - `docs/schema.md`：记录 CN 官方卡查域名、语言标记、扩展枚举；
  - `docs/PROJECT_CONTEXT.md`：更新 gold cases 数量为 20/20；
  - `log/ygo_json_case_changelog.md`：追加 2026-07-07 的 case_011–case_020 扩充记录。

## Test Plan

- 运行：

  ```powershell
  conda run -n YGO_PROJECT python check_jsonlschema.py --self-test
  ```

- 验收标准：

  - 主 JSONL 共 20 行，无空行，每行一个 JSON object；
  - `case_001` 至 `case_020` 顺序连续；
  - `case011.json` 至 `case020.json` 与主 JSONL 对应对象完全一致；
  - 所有 source URL 可追溯，且正式 case 不使用二手来源作为唯一依据；
  - 现有 10 条 case 仍全部通过；
  - 新增 10 条 case 的中文结论、推理步骤与官方裁定一致。

## Assumptions

- “KONAMI 官网”指日文官方卡片数据库与官方 Q&A。
- “卡的效果文本必须出自 CN 官方数据库”理解为：新增 case 的中文效果文本依据必须能追溯到 `db.yugioh-card-cn.com`。
- 如果某个候选 Q&A 涉及的关键卡在简中官方数据库无法定位可访问页面，则不伪造来源；替换为另一条同类型官方 Q&A 候选。
