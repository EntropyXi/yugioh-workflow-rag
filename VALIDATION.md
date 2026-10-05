# VALIDATION.md — Workflow / Agent / RAG 验证说明

本文区分目前能够重复运行的仓库校验，与尚未实现的 RAG / agent 验证。数据 Schema 自测通过不代表检索、生成或 agent workflow 已验证。项目级协作约束见 AGENTS.md。

## 1. 当前验证状态

截至 2026-10-05，已实现并可运行：

- 58 条正式 gold cases 的 JSON Schema、业务约束与主 JSONL / 格式化镜像一致性检查。
- 16 个内存负例检查；每个负例均须被拒绝。
- GitHub Actions 在 push 到 main / feature，以及针对 main 的 pull request 上运行同一自测。
- `RAG/docs/` 21 份本地二手资料的确定性 Markdown 切分：699 块，附来源 hash、偏移、标题路径与父范围；离线单元测试覆盖切分、正文覆盖、父范围、缓存及预算中止。
- 可选 DeepSeek 块上下文化：使用父范围与当前块生成 `retrieval_text`，缓存支持续跑；真实 API 结果只证明生成步骤可用，不证明检索或裁定质量。

当前尚无可报告指标的部分：

- 官方裁定资料批量 ingestion / chunk / embedding 管道；现有切分仅覆盖本地二手资料。
- 可运行的检索服务或检索接口。
- agent 编排和端到端问答 workflow。
- 为 eval/rag_eval_set.jsonl 计算 Recall@k / MRR 的评测 runner。
- 使用真实检索上下文的引用准确率或答案 groundedness 自动评估。

`RAG/agent.py` 现提供 `chunk` 与 `contextualize` CLI，但不是检索或端到端问答服务。`eval/rag_eval_set.jsonl` 是评测数据，不是评测结果。

## 2. 环境与确定性自测

环境定义见 environment.yml；验证环境为 Conda YGO_PROJECT、Python 3.13 和 jsonschema[format]>=4.18,<5。

在 PowerShell 仓库根目录运行：

    conda run -n YGO_PROJECT python --version
    conda run -n YGO_PROJECT python check_jsonlschema.py --self-test

通过条件：

- CLI 返回码为 0。
- 正式主 JSONL 中 58 条 case 均通过 Schema 和业务校验。
- 所有格式化镜像与主 JSONL 对象一致。
- 16 个内存负例全部被拒绝。

成功输出包含：

    [OK] ...operation_legality_cases.jsonl passed schema and business validation.
    [OK] 16 negative validation scenarios rejected.

CI 在 requirements-dev.txt 安装依赖后运行：

    python check_jsonlschema.py --self-test

修改数据时只编辑 gold_cases/json/caseNNN.json，然后执行：

    python tools/sync_gold_jsonl.py
    conda run -n YGO_PROJECT python check_jsonlschema.py --self-test

自测失败时不得继续下一阶段。

## 3. 验证层次

RAG 切分与上下文化的独立验证命令：

    conda run -n YGO_PROJECT python -m unittest discover -s RAG/tests -v
    conda run -n YGO_PROJECT python -m RAG.agent chunk

第一条验证确定性切分、来源偏移、正文非空白覆盖、父范围、缓存复用、来源变化和预算停止；第二条产出 `RAG/artifacts/chunks.jsonl` 与 manifest。模型集成需要用户授权将语料传给服务商，并设 `DEEPSEEK_API_KEY`：

    conda run -n YGO_PROJECT python -m RAG.agent contextualize --max-cost-usd 1 --max-calls 3

`context_report.json` 记录完成数、缓存命中、usage、累计峰时标价估算和停止原因。预算不足、API 错误或部分结果不能报告为全量通过。上下文 token 长度是本地 tokenizer 估算，需抽查生成内容是否保持来源权威性与规则条件。尚未运行 Recall@k / MRR。

2026-10-05 实测：4 个离线单元测试通过；`chunk` 两次运行均为 21 份来源、699 块、相同 SHA-256；真实上下文化完成 699/699 块，空上下文 0，chunk ID、`retrieval_text` 拼接和 manifest hash 一致。人工抽查文档开头、中段、规则书和末尾块，来源表述与对应章节相符。上下文长度（本地 `cl100k_base`）为 70–145 token，335/699 位于 50–100 token；其余 364 块超过目标但不超过 145。两轮抽样和全量运行累计 702 次 API 调用，按峰时公开单价与返回 usage 估算 $0.4762173，低于用户指定的 $1 上限。未执行检索指标与裁定答案质量评测。

| 层次 | 验证对象 | 通过证据 | 当前状态 |
|---|---|---|---|
| L0 仓库与环境 | Python、依赖、配置、路径 | 实际版本与退出码 | 可执行 |
| L1 数据契约 | Schema、业务规则、镜像、负例 | validator 完整通过结果 | 可执行 |
| L2 评测集质量 | JSONL 可解析、ID 唯一、目标 case 存在、难度及覆盖规则 | 确定性脚本/runner 报告 | 评测集已存在；自动结构校验未实现 |
| L3 检索质量 | 查询到 gold case 的排序 | Recall@1/3/5、MRR，按难度报告 | runner 未实现 |
| L4 答案质量 | 检索上下文是否支持答案和引用 | 逐题 groundedness / 裁定复核 | 未实现 |
| L5 Agent / workflow | 路由、工具调用、重试、停止、depends/invalid_question、恢复 | 固定场景、工具轨迹、故障注入结果 | 未实现 |
| L6 部署运行 | 启动、服务依赖、吞吐、恢复 | 隔离环境 smoke / load / recovery 记录 | 未实现 |

## 4. RAG 评测集约定

评测集位于 eval/rag_eval_set.jsonl；文档当前基线为 151 条查询，覆盖全部 58 个正式 case，每条 case 至少有一条 easy 和一条 medium。难度标准与卡名唯一性前瞻规则以 docs/rag_eval_plan.md 为准。

评测 runner 建成后：

- 每条查询以 gold_case_id 为目标，按检索实际排序计算指标。
- 报告 Recall@1、Recall@3、Recall@5 和 MRR，区分总体及 easy / medium / hard。
- 记录数据集版本或 hash、索引/语料版本、embedding / reranker / 检索参数、top-k、模型版本（如适用）、运行日期和逐题结果。
- 分开保留开发/校准集与冻结留出集；不得用同一留出集反复挑选配置。
- 若目标含糊或标注本身存在歧义，先修订 gold 约定，不能用放宽指标来掩盖。
- 抽查 hard 题、近邻误召回、正确目标排名、来源追溯和重复运行稳定性。
- 报告负结果、跳过项、超时、API 失败、空结果和评测器限制；失败或未运行不算通过。

## 5. Agent / 端到端验证设计

agent workflow 实现后，至少覆盖以下路径；单个成功演示不代表系统级验证：

1. 检索到支持 case / 规则来源，答案引用与实际上下文一致。
2. 对高频卡名、规则术语和结论相反的近邻 case 做区分。
3. 证据不足时不补造引用；信息不足的裁定问题输出 depends 并列出缺失信息。
4. 策略、卡组构筑、胜率等范围外请求识别为 invalid_question。
5. 空检索、重复结果、无效工具响应、超时、重试上限和部分故障均有确定处理。
6. 用户文本与检索文档作为不可信数据处理，不能覆盖系统约束或扩展工具权限。
7. 每个关键答案主张能对应实际使用的 case / 证据 ID 和来源元数据。
8. 记录 workflow / prompt 版本、模型与参数、语料及索引版本、检索结果、工具轨迹和逐题评分。

先跑 mock / 确定性工具检查，再跑依赖模型或服务的集成检查。保留人工抽查；若 judge 未参与、不可用或结果不稳定，明确写出，不得补造评分。

## 6. 数据与证据检查

数据校验器通过只证明结构与项目业务规则符合约束，不代表裁定结论本身已获证明。正式 case 仍须人工核对：

- pre_state、操作时点、连锁状态和 resolution_history 是否对应同一时刻。
- cost、对象、召唤条件、一次限制、适用范围和持续约束是否准确。
- 推理步骤是否得到正式卡文及 KONAMI 官方 Q&A / 规则书支持。
- 官方来源 ID、URL、访问日期及 source_updated_at 是否真实可核验。
- depends 是否列出足以影响判断的缺失信息。

证据契约不满足或裁定依据不足时，样例留在待复核集合，不进入正式 gold 数据。

## 7. 验证报告模板

每次发布或重要修改，按需记录：

    Scope:
    Environment:
    Commands:
    Results:
    Dataset / index / model versions:
    Skipped or unavailable checks:
    Known limitations:
    Conclusion supported by this evidence:

只记录实际执行的命令与观测结果，并区分静态结构通过与行为通过、检索正确与答案正确、gold 覆盖与留出泛化、离线 mock 与真实服务集成、脚本运行成功与产品级主张成立。
