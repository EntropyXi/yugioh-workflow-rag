# 待复核 case 的本地中文卡文来源修正规划

## Summary

本轮只处理当前明确待复核的 `case_047` 与 `case_048`，不新增 case，不改变裁定结论。核心策略为：日文 KONAMI 卡片文本与官方 Q&A 仍是裁定权威；若卡片没有可定位的 KONAMI 简中官方页面，则允许使用本地 `cards.cdb` / `cards.db` 作为“非官方中文卡文覆盖”，但必须标为非官方来源，不能伪装成 `official_card_text`。

已只读确认：

- `cards.cdb` 是 SQLite，可查询 `texts(id, name, desc, ...)`。
- `cards.db` 不是 SQLite，而是 UTF-8 管道分隔文本，可作为 fallback。
- `cards.cdb` 可查到：
  - `79016563`：二进制女巫
  - `67095270`：次元壁
  - `53550467`：圣骑士 崔斯坦
  - `29267084`：暗之咒缚
  - `19680539`：圣骑士 高文

## Key Changes

- 调整来源覆盖规则：
  - 保持 `official_card_text` 只用于 KONAMI 官方日文/简中卡片页面。
  - 新增或复用 `secondary_reference` 表示本地非官方中文卡文。
  - 校验器把“中文卡文覆盖”改为：优先 `official_card_text + zh-CN`；若官方简中缺失，则允许 `secondary_reference + zh-CN + authority: local_cards_cdb` 满足中文文本覆盖。
  - 非官方中文卡文不得作为唯一裁定依据；每条 case 仍必须有官方 Q&A 与日文官方卡片文本。

- 修改 `case_047`：
  - 将自然语言、场面、声明操作、推理步骤、结论中的错误中文名「三进制术士」统一改为本地卡库译名「二进制女巫」，与 KONAMI Q&A 标题 `バイナル・ソーサレス` 对齐。
  - 保留裁定结论：不能发动。
  - 为 `バイナル・ソーサレス / 二进制女巫` 与 `ディメンション・ウォール / 次元壁` 增加 `secondary_reference` 中文卡文来源：
    - `local-cdb://cards.cdb/texts/79016563`
    - `local-cdb://cards.cdb/texts/67095270`
  - 修正 `resolution_history` 中「次元墙/次元壁」的错误 action，不再使用 `negate_effects_and_halve_atk`，改为新增结构化动作 `redirect_battle_damage`。

- 修改 `case_048`：
  - 将中文卡名按本地卡库统一为：
    - `聖騎士トリスタン` → 「圣骑士 崔斯坦」
    - `闇の呪縛` → 「暗之咒缚」
    - `聖騎士ガウェイン` → 「圣骑士 高文」
  - 保留裁定结论：既已适用的「暗之咒缚」不因后续保护失效，但之后不能再以当前攻击力不足 1800 的「圣骑士 高文」为新效果对象。
  - 为三张关键卡增加 `secondary_reference` 中文卡文来源：
    - `local-cdb://cards.cdb/texts/53550467`
    - `local-cdb://cards.cdb/texts/29267084`
    - `local-cdb://cards.cdb/texts/19680539`
  - 修正 `resolution_history` 中「暗之咒缚」的错误 action，不再使用 `negate_effects_and_halve_atk`，改为新增结构化动作 `apply_attack_decrease_and_restrictions`，表达降攻、不能攻击、不能变更表示形式的持续适用。

- 更新 Schema / 校验 / 文档：
  - 在 `docs/operation_case.schema.json` 中增加两个 `resolution_history.result.action` 分支：
    - `redirect_battle_damage`
    - `apply_attack_decrease_and_restrictions`
  - 更新 `check_jsonlschema.py`：
    - 删除仅针对 `case_048` 的旧 `SOURCE_TEXT_REVIEW_EXEMPTIONS` 语义。
    - 改为检查“中文卡文覆盖”：官方简中或 approved local secondary reference 二选一。
    - 新增负例：缺少中文覆盖、把本地译文伪装成 `official_card_text`、本地来源缺少 `local-cdb://` URI 均应拒绝。
  - 更新 `docs/schema.md`、`docs/PROJECT_CONTEXT.md`、`log/ygo_json_case_changelog.md`：
    - 说明“官方裁定来源”和“非官方中文译文辅助来源”的边界。
    - 记录 `cards.cdb` / `cards.db` 的使用规则。
    - 移除 `case_047` / `case_048` 的待复核来源债，改为“非官方中文卡文已标注”。

## Test Plan

- 同步主 JSONL：

```powershell
conda run -n YGO_PROJECT python tools/sync_gold_jsonl.py
```

- 运行完整校验：

```powershell
conda run -n YGO_PROJECT python check_jsonlschema.py --self-test
```

- 验收标准：
  - 主 JSONL 仍为 50 行，无空行。
  - `case_001` 到 `case_050` 连续。
  - 50 个镜像 JSON 与主 JSONL 完全一致。
  - `case_047`、`case_048` 裁定结论不变。
  - `case_047` 不再出现「三进制术士」。
  - `case_048` 中文卡名统一为「圣骑士 崔斯坦」「圣骑士 高文」「暗之咒缚」。
  - `resolution_history` 不再错误使用 `negate_effects_and_halve_atk` 表示「次元壁」或「暗之咒缚」。
  - 新增本地中文卡文来源均为 `secondary_reference`，不得出现伪造的 KONAMI 简中 URL。
  - 程序化接口返回 `50 0 True`。

## Assumptions

- 本地 `cards.cdb` 的中文文本可以作为“中文卡文覆盖”，但不是 KONAMI 官方卡片文本。
- `cards.db` 仅作为 fallback；本轮优先使用已验证可查询的 `cards.cdb`。
- 本轮不改已有官方 Q&A、日文官方卡片文本、裁定结论或 case 编号。
- 本轮继续使用 `schema_version: "2.1.0"`；若后续认为“非官方中文卡文覆盖”属于重大契约变化，再单独规划 v2.2.0。
