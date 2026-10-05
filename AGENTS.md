# AGENTS.md — YGO Ruling Evaluation Workflow & RAG

本文件是 Codex、Claude、opencode 等编码代理进入仓库后的项目级行为准则。项目现状见 docs/PROJECT_CONTEXT.md，字段规范见 docs/schema.md 与 docs/operation_case.schema.json，可执行验证及其边界见 VALIDATION.md，当前记忆见 MEMORY.md。

## 1. 项目目标与当前阶段

- 本项目是游戏王 OCG 裁定评测 workflow / RAG 研究项目，核心资产是有来源依据的 gold cases、RAG 查询评测集和知识文档。
- 目标 workflow 将来根据输入场面与候选操作检索相关裁定案例和规则证据，生成受证据支持、可复核的判断。
- 已实现：58 条正式 gold cases、JSON Schema 与业务校验器、151 条 RAG 检索评测查询、领域知识文档、GitHub Actions 数据校验。
- 尚未实现：官方资料 ingestion 管道、可运行的索引/检索服务、agent 编排、RAG 评测 runner。不得将数据、原型脚本、评测集或设计文档描述成已运行的 RAG 产品。
- 项目不做最优操作、胜率、卡组构筑、完整对局模拟或泛化策略建议。越界问题标 invalid_question；信息不足但仍属裁定问题时标 depends。

## 2. 项目地图与边界

- gold_cases/operation_legality_cases.jsonl 是正式 case 批处理入口；gold_cases/json/caseNNN.json 是人读镜像。
- docs/operation_case.schema.json 是 case 的机器约束；check_jsonlschema.py 实施 Schema 以外的业务规则、跨文件一致性和内存负例自测。
- eval/rag_eval_set.jsonl 是检索查询 gold set，不是模型答案分数，也不代表已有检索器。
- docs/llmstudy/ 是领域知识编辑源；RAG/docs/llmstudy_ygo_knowledge_db/ 是供未来 RAG 摄取的整理副本。改动时沿用对应生成流程，避免副本漂移。
- RAG/ 是 RAG 研究工作区。不得假设其中已有可运行的检索或 agent 服务。
- 修改前运行 git status --short。不得覆盖、还原或顺手整理已有用户改动；只触碰当前任务必要文件。

## 3. 权威来源与接手阅读顺序

冲突时按以下顺序裁决：

1. docs/operation_case.schema.json：case 机器结构与枚举。
2. check_jsonlschema.py：跨字段、跨 case、镜像一致性和回归规则。
3. docs/schema.md：字段语义与枚举解释。
4. docs/task_scope.md：裁定任务边界及判断流程。
5. docs/PROJECT_CONTEXT.md：实现内容与状态快照。
6. AGENTS.md、VALIDATION.md、MEMORY.md 与最新 changelog：协作、验证、记忆和变更历史。

新任务先读 README.md、docs/PROJECT_CONTEXT.md、docs/task_scope.md、docs/schema.md，再读相关实现与 changelog。说明文档和可执行 Schema 冲突时，暂停数据扩展并先解决冲突，不得绕过校验器。

## 4. 计划与执行

- 多文件或多步骤变更先提交含 Summary、Implementation Changes、Test Plan、Assumptions 的计划，获用户批准后按计划顺序执行。
- 只修改批准计划列出的文件。步骤验证失败时停止排查，不得跳过。
- 不主动 commit、创建 PR 或修改 git config。
- 完成阶段性工作时用简洁 todo 汇报；结束时列明改动、验证结果和未验证项。

## 5. 开始前与验证纪律

按 VALIDATION.md 选择匹配改动范围的验证级别。涉及 case、Schema 或校验器时，先确认环境：

    conda run -n YGO_PROJECT python --version
    conda run -n YGO_PROJECT python check_jsonlschema.py --self-test

基线为 58 条正式 case 通过 Schema、业务规则、镜像一致性校验，16 个内存负例全部被拒绝。基线失败时，暂停数据或 Schema 修改并定位原因。

- 优先运行确定性、离线、范围最小的检查；外部模型、网络、向量库和大语料不是普通单元验证的前置条件。
- 验证报告区分命令执行成功、指标达标与功能端到端验证；跳过或未运行不算通过。
- 只有相应实现和评测实际可运行时，才报告 RAG、agent、索引、检索、引用或生成行为已验证。报告需说明模型/语料/配置、测试集、指标、结果和限制。
- 调参集不得用来宣称泛化能力。开发/校准集和冻结留出集应分开；异常结果应先复核评测器、gold 标注和指标定义。
- 不把隐含网络访问、付费 API、模型下载或外部服务设为默认验证依赖；需要时说明前置条件和离线替代方案。

## 6. Case 数据修改流程

正式数据只编辑 gold_cases/json/caseNNN.json，然后按序：

1. 运行 python tools/sync_gold_jsonl.py 重建主 JSONL。
2. 运行 conda run -n YGO_PROJECT python check_jsonlschema.py --self-test。
3. 人工核对判断链：时点、cost、对象、一次限制、持续约束和证据。
4. 按 changelog 规范记录变更。

新增 case 前先查 docs/llmstudy/17-case-coverage-map.md，按规则类型补缺口；ID 按末尾连续编号（目前下一个为 case_059），source ID 使用全局唯一格式 src_case_NNN_NN。每条新 case 同步在 eval/rag_eval_set.jsonl 增加至少一条 easy 和一条 medium 查询。难度与覆盖规则见 docs/rag_eval_plan.md。

## 7. Schema 与证据契约

- 新增或更改枚举时，先更新 docs/operation_case.schema.json，再同步 docs/schema.md、校验器/负例和受影响文档，最后才能更新数据。评估 Schema 版本与兼容性并记录 changelog。
- 正式 case 至少有一项 official_card_text（原则上含 ja 与 zh-CN）及一项 official_ruling 或 official_rulebook。
- 官方来源 authority 必须为 KONAMI；URL 指向 db.yugioh-card.com 或 yugioh-card.com；卡文 ID 为 cid:<数字>，Q&A ID 为 fid:<数字>，规则书为 rulebook:<标识>。official_ruling 必须有 source_updated_at；accessed_at 格式为 YYYY-MM-DD。
- 本地 cards.cdb / cards.db 仅可作 secondary_reference，authority 为 local_cards_cdb，URI 使用 local-cdb://；禁止伪装 KONAMI 来源或编造 URL、标题、cid、fid。
- B 站视频及其他二手资料只能作为 secondary_reference，不能是唯一裁定依据。证据不足的样例留在待复核集合。
- supports_reasoning_steps 从 1 编号，不得超过 reasoning_steps 长度。

## 8. RAG 与 agent workflow 设计要求

当工作确实涉及检索或 agent 组件时：

- 保留查询、检索结果、分块到来源文档的稳定 ID 和 provenance；每个结论可追到实际使用的 case 或证据。
- 区分数据校验、检索质量、答案 groundedness 和 agent 工具/workflow 行为。单个阶段通过不代表其他阶段通过。
- 检索评测目标为 eval/rag_eval_set.jsonl 中的 gold_case_id；runner 建成后报告 Recall@1/3/5、MRR，并按 difficulty 分组。runner 未实现前不得编造或手工模拟指标。
- 扩充 case 后复查 easy 查询依赖的卡名唯一性；姐妹 case 和语义混淆查询遵循评测计划。
- agent 对工具响应做结构校验、边界检查与充分性判断；证据不足时输出 depends 或停止确定性裁定，不补造来源。
- 工具权限、外部写操作和网络范围保持最小。测试使用隔离临时目录、临时向量库或 mock，不污染用户数据和正式索引。

## 9. 必须守住的回归项

- case_003 保持 legal，攻击限制为 effect_scope: "monster"；怪兽抗性不绕过作用于玩家的限制。
- case_005 保持 illegal / activation_condition，三个 feature 同时存在：perform_link_summon_after_chain_link_resolution、includes_special_summon_effect、resulting_monster_not_summoned_by_activated_effect。
- 不改任何 case 的 gold_answer.label / failed_check，除非批准计划明确包含此项。
- depends 必须配非空 missing_info。
- 不复活废弃值：grant_link_summon_opportunity、direct_attack_restriction、official_card_ruling、rulebook、数字 chain_link、movement_correct、movement_incorrect。
- 连锁编号使用 C1 / C2 / C3；被引用的 ID 必须真实存在。column_index 统一以我方视角；resolution_history 只记当前判断点前已处理的连锁块；effect_features 仅用机器枚举，自然语言写在 effect_summary。

## 10. 文档、日志和记忆维护

- Schema 或 case 字段语义变化时同步 docs/schema.md、docs/PROJECT_CONTEXT.md、docs/cases_json_template.md 和 changelog，并更新受影响快照。
- log/ygo_json_case_changelog.md 历史条目只追加、不重写；数据、Schema、校验器及联动文档变更应列明影响文件。
- 有新文件产出或基线状态改变的任务完成后更新根目录 MEMORY.md；状态数字以当日实测为准。纯只读问答无需更新。

## 11. 文件与风格

- 保留现有数据格式和校验器 CLI / 输出 / 退出码契约；CaseDatasetValidator 持有规则与预编译 Schema validator，main() 只做 CLI 编排。
- 遵循所在文件风格；不添加非必要注释，不用临时自然语言值代替 Schema 枚举。
- 不将官方 PDF、整库抓取数据、API key、模型权重、向量缓存或机器专属产物加入版本控制。许可范围不确定时保留原件并标记待核实。
