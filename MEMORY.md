# MEMORY.md — 项目记忆快照

> 由 AI 代理于 2026-09-06 通读全仓库后写入，2026-10-05 复核并更新。记录"分散在多处或容易搞错"的当前态、
> 关键决策与坑位。状态类数字以写入日实测为准；使用前先运行
> `conda run -n YGO_PROJECT python check_jsonlschema.py --self-test` 复核基线。
> 行为准则见 `AGENTS.md`。

---

## 1. 一句话定位

游戏王 OCG「操作合法性裁定」数据集项目。当前资产 = 58 条人工 gold cases +
Draft 2020-12 JSON Schema + 双层校验器 + 151 条 RAG 检索评测集 + 20 篇领域知识库 +
20 篇 RAG 化副本、1 篇社区规则书摘录与 1 篇领域文档合并版。
本地二手资料已有确定性切分与 DeepSeek 块上下文化；检索索引、官方知识库、评测 runner 和问答 RAG 引擎仍未实现。

## 2. 当前基线（2026-10-05 实测）

| 项 | 值 |
|---|---|
| Schema 版本 | `2.1.0`（Draft 2020-12，`docs/operation_case.schema.json`） |
| gold cases | 58 条（`case_001`–`case_058`），主 JSONL 58 行 + 镜像 58 个文件 |
| 标签分布 | legal 22 / illegal 34 / depends 2（实测） |
| task_type | `operation_legality_judgment` 45 / `effect_resolution_judgment` 13 |
| operation_type 覆盖 | 10/10（activate_effect 24、activate_card 12、resolve_effect 13、declare_attack 2、special_summon 2、normal_summon/set_card/set_monster/pay_cost/select_target 各 1） |
| failed_check 覆盖 | 15/15（`unknown_missing_info` ×2：case_057/058） |
| 评测集 | `eval/rag_eval_set.jsonl` 151 条：easy 58 / medium 59 / hard 34；覆盖全部 58 case，每 case ≥1 easy + ≥1 medium |
| 校验器 | `--self-test` 通过：58 case 全过 + 16 负例全拒（2026-10-05 实跑） |
| RAG 知识文件 | `RAG/docs/llmstudy_ygo_knowledge_db/` 20 篇带元数据文档；`RAG/docs/ocg_rulebook_2020_zh_cn_2.3_ch3.md` 为社区规则书摘录；合并版位于 `docs/llmstudy_domain_kb.md` |
| RAG 处理产物 | 21 份来源确定性切为 699 块；DeepSeek 上下文化完成 699/699，输出在 gitignored `RAG/artifacts/`；本次 702 次真实调用累计峰时价格估算 $0.4762173（用户上限 $1），不是实际账单 |
| CI | GitHub Actions：push(main,feature) / PR(main) 自动跑 `--self-test` |
| 环境 | Conda `YGO_PROJECT`，Python 3.13，`jsonschema[format]>=4.18,<5` |

## 3. 仓库状态（2026-09-07 整理提交后）

- 基线成果已全部入库并推送 origin/main：case_051–058、151 条评测集、llmstudy
  知识库、`RAG/` 知识文件、文档快照与代理入口（AGENTS.md / MEMORY.md）。
- `.gitignore` 已新增 `docs/sources/`（规则书 PDF；README 承诺不分发官方文档）
  与 `.omo/`（代理 plan 存档）；`learning/` 两本 PDF 已 `git rm --cached`
  解除跟踪（本地文件保留）。
- 分支：本地 `main` + `feature`，远端 `origin`。项目标题已改为
  "YGO Ruling Evaluation Workflow&RAG"（README，GitHub 网页端提交 73729af）。
- 2026-10-05 已将工作区中有语法错误的 `RAG/agent.py` 原型改为可运行的 `chunk` / `contextualize` CLI；仍没有检索接口。根目录 `.vscode/` 是原有未跟踪用户文件，本轮未触碰。

## 4. 关键设计决策（不要回退）

- **case_003**（S:P 限制下全抗怪兽直接攻击）= `legal`；限制建模为
  `effect_scope: "monster"`。怪兽抗性可绕过作用于怪兽的限制，
  不能绕过作用于玩家的限制（`effect_scope: "player"`）。
- **case_005**（I:P 连接召唤）= `illegal / activation_condition`；三个 I:P feature
  必须并存："效果包含特殊召唤处理" ≠ "怪兽因发动的效果被特殊召唤"
  （连接召唤发生在连锁块处理之后）。校验器对 case_003/case_005 有专门回归规则。
- **`resolution_history`** 是每条 case 必填状态词条；`[]` 表示"此前无已处理连锁"，
  不是缺信息；只记逆顺已处理块（C3 先于 C2）；持续限制写 `known_constraints`；
  校验器检查 `state_timing`（`after_Cn_resolved` / `before_resolving_Cn`）与 history 一致。
- **简中卡文覆盖**：官方 zh-CN 正文优先；拿不到时用本地 `cards.cdb` 的
  `secondary_reference`（`authority: local_cards_cdb`，`local-cdb://` URI），
  绝不伪装成 official。case_048 是唯一显式待复核例外。
- **`column_index`** 全局以我方视角（self 1..5，opponent 5..1），同纵列只比较索引。

## 5. 文档漂移处理记录

- 2026-10-05 已将 `docs/schema.md` 的负例数改为 16，并将 README、项目上下文与本文件的
  `docs/llmstudy/` 数量改为 20；RAG 文件路径已按实际仓库修正。
- changelog 2026-07-28 depends 历史条目的 `legal 21 / illegal 35` 是笔误；
  当前实测为 `legal 22 / illegal 34`。历史条目保留，2026-10-05 新条目作勘误。
- `log/codex_history.md`（6400+ 行）是只追加的对话史档案，不代表当前状态，
  别把它当现状来源。

## 6. 未完成（Next Actions，源自 PROJECT_CONTEXT §15）

1. 58 条 case 逐条人工 dry-run + 官方证据复核（Q&A 有 `source_updated_at` 时效风险）。
2. RAG 评测 runner：recall@1/3/5、MRR，按 difficulty 分组报告
   （PROJECT_CONTEXT 提到参考 `savinoo/rag-eval-harness` 的最小实现）。
3. 评估把 eval 集结构校验纳入校验器或 CI。
4. 为 `RAG/artifacts/contextualized_chunks.jsonl` 建 embedding 与 BM25 索引、混合召回和 rerank；按 `eval/rag_eval_set.jsonl` 实测检索指标。现有上下文长度 70–145 本地 token，仅 335/699 落在 50–100 目标区间，后续可缩短提示词并重新验证。
5. 后续扩充：先硬化基线，再按规则类型平衡扩 case；新增 case 时检查既有 easy
   评测题的卡名唯一性是否退化（E1 前瞻规则，见 `docs/rag_eval_plan.md`）。

## 7. 资产地图（容易忘的点）

- `docs/llmstudy/`（20 篇）：给 LLM 的领域知识库，00–19 分层；扩 case 前先查
  `17-case-coverage-map.md`（failed_check × 规则维度 × case 的查重表）。
- `notes/`：人工裁定研究笔记（苏生限制、优先权转移、自排连锁等），非正式数据。
- `docs/sources/`：两份规则书 PDF（KONAMI Master Rule 2020 日文 + 简中社区规则书），
  仅本地参考，不进正式证据链；2026-09-07 起已 gitignore，不入库。
- `RAG/`（2026-09-06 起新增，已入库）：RAG 工程工作区 + 面向 RAG 向量化的知识库
  markdown。`RAG/agent.py`、`chunking.py`、`contextualize.py` 是切分与上下文化 CLI；
  `RAG/tests/` 有 4 个离线单元测试，`RAG/README.md` 记录命令与限制，`RAG/artifacts/` 已忽略且包含本地生成产物。
  知识文件现状 3 处：
  ① `RAG/docs/llmstudy_ygo_knowledge_db/`（20 篇，**RAG 摄取的规范来源**）：
  `docs/llmstudy/` 20 篇的副本并已 RAG 化改造——每篇头部加 YAML frontmatter
  （title / doc_id / collection / tags / project_bindings / cases / source / written，
  cases 已展开 `case_007/037` 缩写），修了 4 处标题后缺空行，正文与原版逐字一致；
  改造脚本 `_ragify_kb.py`（gitignored，重跑会跳过已有 frontmatter 的文件）。
  ② `RAG/docs/ocg_rulebook_2020_zh_cn_2.3_ch3.md` = 社区规则书 2.3 节（p14–17）+
  第 3 章大师规则全文（p18–93）；标题层级 1:1 对应原文编号（可作分块面包屑），
  正文只合并 PDF 断行不改写，3 张表转 Markdown 表格，1 图保留图题，26 条社区
  译注以「注 N」引用块保留。生成脚本 `_extract_rag.py`（重跑需带 `pypdf`+
  `pymupdf` 的 Python，勿装进 `YGO_PROJECT`）。
  ③ `docs/llmstudy_domain_kb.md` = 20 篇的合并版（每篇一章，标题降级，正文逐字），
  由 `_merge_llmstudy.py` 生成；②③与 ① 不同步（①已加 frontmatter，②③未含），
  以 ① 为准，③是否保留待定。
  同步关系：`docs/llmstudy/` 是知识内容的唯一编辑源；改动后须重跑
  `_ragify_kb.py` / `_merge_llmstudy.py` 再生成 RAG 侧文件。
  扩 RAG 知识库时优先摘录 2.2 特选规则、3.6 游戏的进行等裁定相关章节。
- `learning/`：两本 workflow 理论 PDF。2026-09-07 已 `git rm --cached` 解除跟踪
  （本地文件保留，gitignore 生效）；README 强调仓库不分发 KONAMI 官方文档，
  处理 `docs/sources/`、`learning/` 时保持这一口径。
- `_*.py` / `_*.txt`（如 `_check_src.py`）：临时检查脚本，已 gitignore。
- `.mcp.json` / `.codex/`：配置 bilibili-mcp，用于检索 B 站裁定讲解（仅限
  `secondary_reference`）。`.claude/`、`.agents/` 已 gitignore。
- `.omo/`（已 gitignore）：代理 plan 存档（llmstudy-plan、p1-p2-p3-fix-plan，均已执行完）。
- 历史已执行计划（只读参考）：`docs/split_effect_resolution_task_type_plan.md`、
  `docs/rag_eval_fix_plan.md`、`docs/resolution_history_plan.md`、
  `docs/cases_plan/`（case11-50 分批计划）。
- `tools/sync_gold_jsonl.py`：从镜像重建主 JSONL 的唯一同步方式；
  一次性迁移脚本已删除，不存在自动反向同步（JSONL → 镜像）。

## 8. 权威性顺序（冲突裁决）

`docs/operation_case.schema.json` > `check_jsonlschema.py` > `docs/schema.md` >
`docs/task_scope.md` > `docs/PROJECT_CONTEXT.md`。文档与 Schema 冲突时先停下
确认是否需要升级 Schema，禁止绕开校验器。
## 9. 2026-10-05 — Workflow / Agent / RAG 协作与验证规范

- 根目录 AGENTS.md 已调整为 workflow / agent / RAG 研究项目的代理协作规范；保留正式 case、Schema、KONAMI 证据契约和 case_003 / case_005 回归要求。
- 新增根目录 VALIDATION.md，区分现有 case / Schema 自测与尚未实现的 ingestion、检索、评测 runner、agent workflow；未运行的 RAG 指标不得写成验证结果。
- 本次执行前实测：Conda YGO_PROJECT 的 Python 为 3.13；check_jsonlschema.py --self-test 通过，58 条 case 全过，16 个内存负例全拒。
- RAG 评测集文档基线为 151 条，覆盖 58 cases；Recall@k / MRR 检索 runner 尚未实现。
- 当时的文档漂移修正任务没有触碰 RAG/agent.py 或 .vscode/；后续获批的 RAG 切分任务已修改 RAG/agent.py，.vscode/ 仍未触碰。

## 10. 2026-10-05 — RAG 切分与上下文化实测

- 修改/新增：`RAG/agent.py`、`RAG/chunking.py`、`RAG/contextualize.py`、`RAG/prompts/context_v1.txt`、`RAG/environment.yml`、`RAG/tests/test_chunking.py`、`RAG/tests/test_contextualize.py`、`RAG/README.md`；同步 `.gitignore`、`README.md`、`docs/PROJECT_CONTEXT.md`、`VALIDATION.md`、changelog 与本文件。
- 21 份 `RAG/docs/` 来源生成 699 块，重复运行 SHA-256 相同：`2454948fd274d1ef3918f76b8f93b12818c9693aa843c8bb6dff6b63992ada1b`。合并版 `docs/llmstudy_domain_kb.md` 未重复摄取。所有来源为 `secondary_reference`。
- 真实 `deepseek-flash` 上下文化完成 699/699；样本与全量共 702 次调用（首版提示词样本 3 次、修订提示词样本 3 次、全量续跑 696 次），累计峰时标价估算 $0.4762173，低于用户设置的 $1 上限。原始分块与生成上下文分离，缓存记录在 gitignored `RAG/artifacts/`。
- 离线单元测试 4/4 通过；manifest hash、chunk ID 对齐、`retrieval_text` 拼接和空上下文检查通过。上下文长度按本地 `cl100k_base` 估算 70–145 token：335/699 在 50–100；其余 364 块超过目标，须视为后续质量改进项。未执行 Recall@k、MRR 或裁定答案评测。
- `check_jsonlschema.py --self-test` 仍通过：58 条正式 case、16 个负例。没有修改 gold case、Schema、校验器或评测集，也没有提交 Git。
