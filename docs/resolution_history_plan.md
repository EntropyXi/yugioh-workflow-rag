# 全量 `resolution_history` 官方规则化迁移计划

## Summary

为全部 30 条 case 显式维护 `pre_state.resolution_history`，并把它从“可选辅助字段”升级为每条 case 都必须存在的状态词条。迁移时不改变任何裁定结论；只补齐、规范或修正“当前判断点之前已经实际处理完成的连锁结果”。没有已处理连锁结果的 case 使用空数组 `[]`，不得编造历史。

## Implementation Changes

- 统一数据语义：

  - `resolution_history` 只记录“当前判断时点之前已经处理完成的连锁块”。
  - 顺序按实际处理时间排列，即连锁逆顺处理中的已处理顺序，例如 `C3` 后 `C2`。
  - 仍在连锁构建中、尚未开始处理的 case 使用 `[]`。
  - 开放状态、召唤成功窗口、cost 支付前、单纯发动合法性判断等没有已处理连锁块的 case 使用 `[]`。
  - 不把未处理的计划、规则解释、持续限制写入 `resolution_history`；持续限制继续放 `known_constraints`。

- 逐条迁移 30 个镜像 JSON：

  - 缺失 `resolution_history` 的 case 补为 `[]` 或按已知官方场景补真实历史。
  - 已有 `resolution_history` 的 case 逐条复核，不只保留原值。
  - 修正 `case_025`、`case_028` 当前 `resolution_history` 中疑似编码损坏的中文字段。
  - 只使用官方规则允许的已处理结果：破坏、除外、特殊召唤、变里侧、无效、同纵列适用等；若现有 action 不足，再做最小 schema 扩展。

- 更新 Schema 与校验器：

  - 将 `pre_state.resolution_history` 加入必填字段。
  - 保留 `[]` 作为合法值，表示当前判断点前没有已处理连锁块。
  - 增加业务校验：
    - `resolved_chain_id` 必须引用 `current_chain_links` 中存在的连锁编号。
    - `resolution_history` 中不得出现尚未按连锁逆顺处理到的连锁块。
    - `is_chain_resolving: true` 且 `state_timing` 表示“after_Cn_resolved / before_resolving_Cn”时，history 必须与该时点一致。
    - `result` 不允许为空；无结果或未处理不得写 history item。
  - 自测新增负例：缺失 `resolution_history`、引用不存在连锁编号、处理顺序错误、空 `result` 均应被拒绝。

- 更新文档与日志：

  - `docs/schema.md`：明确 `resolution_history` 的官方规则语义、顺序、空数组含义、与 `known_constraints` 的边界。
  - `docs/cases_json_template.md`：模板中保留必填 `resolution_history: []`，并补充填写规范。
  - `docs/PROJECT_CONTEXT.md`：把 `resolution_history` 标为全量必填状态词条，说明其在效果处理类 case 中的因果作用。
  - `log/ygo_json_case_changelog.md`：新增 2026-07-07 的全量迁移记录，说明不改变裁定结论。

## Official-rule Policy

- 只记录已经在规则上完成处理的连锁块，不能记录“将要处理”或“玩家声明想这样处理”。
- 连锁处理必须遵守游戏王规则的逆顺处理：高编号连锁块先处理，低编号后处理。
- 若某效果处理没有造成结构化状态变化，原则上不写入 history；必要时先扩展 action 枚举，而不是用自然语言硬塞。
- `resolution_history` 与当前场面必须一致：例如 history 写了特殊召唤，`self_state/opponent_state` 中也应反映该怪兽已移动到场上。
- 官方 Q&A 若只证明规则结论，不直接描述某个已处理结果，不得据此伪造额外历史。

## Test Plan

- 运行：

  ```powershell
  conda run -n YGO_PROJECT python check_jsonlschema.py --self-test
  ```

- 验收标准：

  - 30 条 case 全部含有 `pre_state.resolution_history`。
  - 主 JSONL 仍为 30 行、无空行、ID 从 `case_001` 到 `case_030` 连续。
  - `gold_cases/json/case001.json` 至 `case030.json` 与主 JSONL 完全一致。
  - 所有已有裁定结论不变。
  - `case_025`、`case_028` 的 history 中文字段不再有问号占位。
  - 新增负例能拒绝缺失 history、错误连锁引用、错误处理顺序和空 result。
  - 程序化接口返回 `30 0 True`。

## Assumptions

- 本轮不新增 case，不改变官方来源，不重查所有 Q&A；仅在修正具体 history 内容需要时查看对应现有来源。
- `resolution_history: []` 是有意义的显式状态，表示“当前判断点前没有已处理连锁块”，不是缺失信息。
- 本轮继续使用 `schema_version: "2.0.0"`；如果后续认为“可选改必填”需要版本升级，再单独规划 v2.1 或 v3。
