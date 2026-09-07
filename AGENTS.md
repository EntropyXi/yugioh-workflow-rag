# AGENTS.md — AI 代理工作指南

本文件是任何 AI 代理（Codex / opencode / Claude 等）中途加入本项目时的行为准则入口。
项目全貌与人用入口见 `docs/PROJECT_CONTEXT.md`；从 Codex 协作史提炼的行事标准见
`OPENCODE.md`；当前状态快照与坑位记录见根目录 `MEMORY.md`。

---

## 1. 项目是什么

- 游戏王 OCG「操作合法性裁定」数据集项目：给定 `pre_state` 与 `attempted_operation`，
  判断该操作或效果处理是否规则合法，并输出可追溯的判断链。
- **不是** RAG 引擎、规则引擎或对局模拟器。官方知识库、检索管道、评测 runner 均未实现。
- 明确不做：最优操作、胜率、卡组构筑、完整对局模拟、泛化策略建议。
- 越界问题标 `invalid_question`；属于裁定任务但信息不足的标 `depends`。

## 2. 环境与校验（先跑通再干活）

```powershell
conda run -n YGO_PROJECT python --version
conda run -n YGO_PROJECT python check_jsonlschema.py --self-test
```

- 环境：Conda `YGO_PROJECT`（Python 3.13，`jsonschema[format]>=4.18,<5`），
  定义见 `environment.yml`，说明见 `docs/environment_setup.md`。
- 验收标准：58 条 case 通过 Schema + 业务规则 + 镜像一致性校验，
  16 个内存负例全部被拒绝，退出码 0。
- **每次数据或 Schema 变更后必须运行**；不通过不得进入下一步、不得提交。
- CI（`.github/workflows/ci.yml`）在 push(main,feature) / PR(main) 自动运行同一命令。

## 3. 必读文档与权威性顺序

新接手的阅读顺序：`README.md` → `docs/PROJECT_CONTEXT.md` → `docs/task_scope.md` →
`docs/schema.md` → changelog 最新条目。

修改数据时的冲突裁决顺序（高 → 低）：

1. `docs/operation_case.schema.json` — 机器约束唯一权威
2. `check_jsonlschema.py` — Schema 无法表达的跨对象/跨文件规则
3. `docs/schema.md` — 字段语义与完整枚举
4. `docs/task_scope.md` — 任务边界与判断流程
5. `docs/PROJECT_CONTEXT.md` — 当前状态快照

文档与可执行 Schema 冲突时，先停止新增数据，确认是否需要升级 Schema；
禁止通过绕开校验器来"兼容"新字段。

## 4. 数据修改标准流程

1. 只编辑格式化镜像 `gold_cases/json/caseNNN.json`。
2. 运行 `python tools/sync_gold_jsonl.py` 重建主 JSONL
   （双写结构：主 JSONL 是批处理入口，镜像必须与主 JSONL 逐对象一致）。
3. 运行 `--self-test`。
4. 人工 dry-run 判断链：时点、cost、对象、一次限制、持续约束。
5. 在 `log/ygo_json_case_changelog.md` 顶部追加记录。

新增 case 额外要求：

- ID 从现有末尾连续编号（当前到 `case_058`，下一个是 `case_059`）。
- source ID 全局唯一，格式 `src_case_NNN_NN`。
- 同步补充 `eval/rag_eval_set.jsonl` 评测题：每条新 case 至少 1 条 easy + 1 条 medium，
  难度标准与卡名唯一性前瞻规则见 `docs/rag_eval_plan.md`。
- 扩 case 前先查 `docs/llmstudy/17-case-coverage-map.md`，按规则类型补缺口，
  不要围绕少数卡片堆相似问题。

## 5. Schema-First 铁律

1. 新增任何枚举值（`operation_type`、`effect_features`、`cost.type`、`action`、
   `failed_check`、`known_constraints.type` 等）必须**先改**
   `docs/operation_case.schema.json`。
2. 再同步 `docs/schema.md` 枚举表，以及受影响的校验器/自测负例。
3. 最后才能进入 case 数据；禁止在数据中使用未登记枚举值。
4. 评估是否需要升级 Schema minor/major 版本，并在 changelog Part 1 记录
   Added/Changed、裁定依据、迁移方式与兼容性影响。

## 6. 证据契约（不可妥协）

- 每条正式 case 至少包含：一项 `official_card_text`（原则上同时覆盖 ja 与 zh-CN），
  以及一项 `official_ruling` 或 `official_rulebook`。
- 官方来源要求：`authority: "KONAMI"`；URL 必须指向 `db.yugioh-card.com` 或
  `yugioh-card.com`；卡片文本用 `cid:<数字>`，Q&A 用 `fid:<数字>`，规则书用
  `rulebook:<标识>`；`official_ruling` 必须填 `source_updated_at`；
  `accessed_at` 用 `YYYY-MM-DD`。
- 关键卡无有效 KONAMI 简中官方正文时，用本地 `cards.cdb`/`cards.db` 的
  `secondary_reference` 补中文卡文（`authority: local_cards_cdb`，URL 用
  `local-cdb://` 前缀）。**禁止**把 local 来源伪装成 `official_card_text`，
  **禁止**伪造 URL、标题、cid 或 fid。
- 二手材料（B站视频、文章等）只能作 `secondary_reference`，不得成为唯一裁定依据。
- `supports_reasoning_steps` 用从 1 开始的推理步骤编号，不得越过
  `reasoning_steps` 长度。
- 找不到足够官方证据的样例留在待复核集合，不得进入正式主数据。

## 7. 回归红线（校验器与人工都必须守住）

- `case_003` 必须保持 `legal`，且攻击限制为 `effect_scope: "monster"`：
  怪兽抗性可以绕过作用于怪兽的限制，不能绕过作用于玩家的限制。
- `case_005` 必须保持 `illegal / activation_condition`，I:P 语义用三个 feature 并存表达
  （`perform_link_summon_after_chain_link_resolution` +
  `includes_special_summon_effect` +
  `resulting_monster_not_summoned_by_activated_effect`），
  不得合并为单一布尔值或回退到废弃值。
- 不改动任何 case 的 `gold_answer.label` / `failed_check`，除非 plan 明确要求。
- `depends` 必须配合非空 `missing_info`（Schema `minItems: 1`）。
- 废弃值不得复活：`grant_link_summon_opportunity`、`direct_attack_restriction`
  （改用结构化 `attack_restriction`）、`official_card_ruling`、`rulebook`、
  数字 `chain_link`、`movement_correct` / `movement_incorrect`。

## 8. Plan-Then-Execute

1. 涉及多文件、多步骤的改动，**先写 plan** 给用户审核；plan 必须包含
   Summary、Implementation Changes、Test Plan、Assumptions。
2. 用户批准后再执行；执行时严格按 plan 步骤顺序，不做计划外的事。
3. 改动的文件严格限制在 plan 列出的清单内。
4. 步骤间校验失败须立即停止排查，不得跳过校验。

## 9. Changelog 规范

- `log/ygo_json_case_changelog.md` 分两部分：Part 1 Schema 版本历史；
  Part 2 日常日志（按日期倒序，含 Summary / Changed / Validation / Decision 等小节）。
- 历史条目不重写，只在顶部追加；Current Snapshot、Pending、Next Actions 可随项目刷新。
- 数据、Schema、校验器、文档联动时，日志必须列出影响文件。
- 裁定结论变化必须记录旧结论、新结论、证据和受影响 case。
- 只更新环境或工具时也要记录实际版本和验证命令。

## 10. 代码与文档风格

- 校验器保持面向对象：`CaseDatasetValidator` 持有规则与预编译 Schema validator，
  `main()` 只做 CLI 编排；保持 CLI 参数、输出格式、退出码语义不变。
- 不添加注释（除非沿用项目已有注释风格）；遵循现有 2 空格缩进与命名约定。
- 修改数据结构或枚举后，同步更新 `docs/schema.md`、`docs/PROJECT_CONTEXT.md`、
  `docs/cases_json_template.md` 及 changelog；文档快照（case 数量、task_type 分布、
  Schema 版本、负例数、评测集统计）必须与实际数据一致。

## 11. 与用户协作

- 简洁直接地回复，最小化输出 token。
- 需要决策时使用提问工具，提供明确选项。
- 完成阶段性工作后，以 todo 列表报告进度。
- 不主动 commit、不主动创建 PR、不修改 git config。

## 12. 常见陷阱速查

- 连锁编号一律字符串 `C1` / `C2` / `C3`；`chain_response_to` 与
  `chain_id_to_resolve` 必须引用 `pre_state.chain_state.current_chain_links`
  中真实存在的 ID。
- `column_index` 全局以我方视角：self 1..5，opponent 5..1；同纵列判断只比较
  索引值，不要在 workflow 里再做镜像换算。
- `resolution_history` 是每条 case 必填状态词条：只记录当前判断点之前已按连锁
  逆顺处理完成的块（高编号先处理，如先 C3 后 C2）；空数组 `[]` 是合法显式状态；
  持续限制写 `known_constraints`，不要混入 history。
- 场地格子统一 `{ "column_index": ..., "card": ... }` 包装，空位写 `"card": null`；
  `field_spell_zone` 不使用 `column_index`。
- 发动类 case 通常 `is_chain_building: true`；效果处理类通常 `is_chain_resolving: true`
  且必填 `state_timing` 与 `resolution_history`；`operation_type: resolve_effect`
  强制 `task_type: effect_resolution_judgment`（双向校验）。
- 阶段、步骤、伤害步骤时点必须用 Schema 枚举；未知值用 `unknown`，
  不用空字符串或临时中文值。
- `effect_features` 只放机器枚举，自然语言解释写 `effect_summary`。

## 13. 任务后记忆更新（必做）

- **每次做完一项新任务就要更新根目录 `MEMORY.md`**：把新产出/变更的文件与资产、
  基线数字变化、新决策与坑位同步进去；状态类数字以当日实测为准，先跑校验再写。
- 纯只读的调研、问答可不更新；凡是产出了文件或改变了基线状态的任务必须更新，
  更新完成后再向用户汇报结果。
- `effect_features` 只放机器枚举，自然语言解释写 `effect_summary`。
