# OPENCODE 行事标准

本文档从与 Codex 的协作历史中提炼，作为 opencode 在本项目的行事逻辑。

## 一、项目核心认知

- 项目是"游戏王 OCG 操作合法性裁定数据集"，不是 RAG 引擎或规则引擎。
- 当前核心资产：`gold_cases/` 下的 40 条 gold cases + JSON Schema + 双层校验器。
- 权威性顺序：`docs/operation_case.schema.json` > `check_jsonlschema.py` > `docs/schema.md` > `docs/PROJECT_CONTEXT.md`。
- 环境：Conda `YGO_PROJECT`，标准命令 `conda run -n YGO_PROJECT python check_jsonlschema.py --self-test`。

## 二、Schema-First 铁律

1. 新增任何枚举值（`operation_type`、`effect_features`、`action`、`cost` 等），必须**先改** `docs/operation_case.schema.json`。
2. 再改 `docs/schema.md` 同步枚举表。
3. 最后才能进入正式 case 数据。
4. 禁止在 case 数据中使用未登记的枚举值。

## 三、严格证据契约

1. 每条正式 gold case 至少包含一项 `official_card_text` + 一项 `official_ruling` 或 `official_rulebook`。
2. 卡片效果文本必须能追溯到 KONAMI 官方卡片数据库（日文 `db.yugioh-card.com`，简中 `db.yugioh-card-cn.com`）。
3. 裁定依据必须是 `fid` 或 `cid#supplement`，不能拿搜索词冒充证据。
4. 如果某张关键卡的 CN 官方详情页不可访问，必须替换候选，**禁止伪造来源**。
5. 二手材料（B站视频等）只能作为 `secondary_reference`，不得成为唯一裁定依据。

## 四、Plan-Then-Execute 工作流

1. 涉及多文件、多步骤的改动，**先写 plan** 让用户审核。
2. Plan 必须包含：Summary、Implementation Changes、Test Plan、Assumptions。
3. 用户批准后再执行。
4. 执行时严格按照 plan 的步骤顺序，不做计划外的事情。

## 五、执行纪律

1. **不做超过任务边界的事**。完成计划内容即停止，不主动扩展范围。
2. 步骤间有依赖时，任一步骤校验失败须立即停止并排查，**不得跳过校验**。
3. 改动的文件严格限制在 plan 列出的清单内。
4. 不改动任何 case 的裁定结论（`gold_answer.label`、`failed_check`），除非 plan 明确要求。
5. 不重写历史 changelog 条目，只在顶部追加新记录。

## 六、校验铁律

1. **每次数据或 Schema 变更后**，必须运行：
   ```powershell
   conda run -n YGO_PROJECT python check_jsonlschema.py --self-test
   ```
2. 验收标准：40 条 case 全部通过 Schema + 业务规则 + 镜像一致性校验，所有负例被拒绝，退出码 0。
3. 校验不通过不得进入下一步。

## 七、Changelog 规范

1. `log/ygo_json_case_changelog.md` 分为 Part 1（Schema 版本演进）和 Part 2（日常日志）。
2. 历史条目不重写；当前快照、Completed、Pending、Risks、Next Actions 可随项目刷新。
3. 数据、Schema、校验器和文档发生联动时，日志必须明确列出影响文件。
4. 裁定结论变化必须记录旧结论、新结论、证据和受影响 case。

## 八、文档一致性

1. 修改数据结构或枚举后，同步更新 `docs/schema.md`、`docs/PROJECT_CONTEXT.md`、`docs/cases_json_template.md` 及 changelog。
2. `PROJECT_CONTEXT.md` 的状态快照必须与当前实际数据一致（case 数量、task type、Schema 版本等）。
3. 文档中的过期描述必须清除，不保留"待决定"的已决议事项。

## 九、代码风格

1. 校验器保持面向对象结构：`CaseDatasetValidator` 管理规则，`main()` 只做 CLI 编排。
2. 不添加注释（除非项目已有注释风格）。
3. 遵循现有缩进（2 空格）、命名和 imports 约定。
4. 保持 CLI 参数、输出格式和退出码语义不变。

## 十、与用户协作

1. 简洁直接地回复，最小化输出 token。
2. 需要决策时使用提问工具，提供明确选项。
3. 完成阶段性工作后，以 todo 列表报告进度。
4. 不主动 commit、不主动创建 PR、不修改 git config。
