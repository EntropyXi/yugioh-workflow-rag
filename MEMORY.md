# MEMORY.md — 项目记忆快照

> 由 AI 代理于 2026-09-06 通读全仓库后写入。记录"分散在多处或容易搞错"的当前态、
> 关键决策与坑位。状态类数字以写入日实测为准；使用前先运行
> `conda run -n YGO_PROJECT python check_jsonlschema.py --self-test` 复核基线。
> 行为准则见 `AGENTS.md`。

---

## 1. 一句话定位

游戏王 OCG「操作合法性裁定」数据集项目。当前资产 = 58 条人工 gold cases +
Draft 2020-12 JSON Schema + 双层校验器 + 151 条 RAG 检索评测集 + 19 篇领域知识库 +
`RAG/` 知识库 markdown（2 篇）。
检索管道、官方知识库、评测 runner、RAG 引擎全部**未实现**。

## 2. 当前基线（2026-09-06 实测）

| 项 | 值 |
|---|---|
| Schema 版本 | `2.1.0`（Draft 2020-12，`docs/operation_case.schema.json`） |
| gold cases | 58 条（`case_001`–`case_058`），主 JSONL 58 行 + 镜像 58 个文件 |
| 标签分布 | legal 22 / illegal 34 / depends 2（实测） |
| task_type | `operation_legality_judgment` 45 / `effect_resolution_judgment` 13 |
| operation_type 覆盖 | 10/10（activate_effect 24、activate_card 12、resolve_effect 13、declare_attack 2、special_summon 2、normal_summon/set_card/set_monster/pay_cost/select_target 各 1） |
| failed_check 覆盖 | 15/15（`unknown_missing_info` ×2：case_057/058） |
| 评测集 | `eval/rag_eval_set.jsonl` 151 条：easy 58 / medium 59 / hard 34；覆盖全部 58 case，每 case ≥1 easy + ≥1 medium |
| 校验器 | `--self-test` 通过：58 case 全过 + 16 负例全拒（2026-09-06 实跑） |
| RAG 知识文件 | `RAG/` 2 篇：`ocg_rulebook_2020_zh_cn_2.3_ch3.md`（社区规则书 2.3 节+第 3 章，约 193KB）+ `llmstudy_domain_kb.md`（llmstudy 00–19 合并版，约 114KB），均 2026-09-06 生成 |
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

## 5. 已知文档漂移（下次顺手修，改动后同步 changelog）

- `docs/schema.md` §17 仍写"负例自测共 13 个"，实际 16（PROJECT_CONTEXT 与
  changelog Current Snapshot 已是 16）。
- changelog 2026-07-28 depends 条目写 "legal 21 / illegal 35"，实测 22 / 34
  （`docs/llmstudy/17-case-coverage-map.md` 的 22 正确）。
- `log/codex_history.md`（6400+ 行）是只追加的对话史档案，不代表当前状态，
  别把它当现状来源。

## 6. 未完成（Next Actions，源自 PROJECT_CONTEXT §15）

1. 58 条 case 逐条人工 dry-run + 官方证据复核（Q&A 有 `source_updated_at` 时效风险）。
2. RAG 评测 runner：recall@1/3/5、MRR，按 difficulty 分组报告
   （PROJECT_CONTEXT 提到参考 `savinoo/rag-eval-harness` 的最小实现）。
3. 评估把 eval 集结构校验纳入校验器或 CI。
4. 后续扩充：先硬化基线，再按规则类型平衡扩 case；新增 case 时检查既有 easy
   评测题的卡名唯一性是否退化（E1 前瞻规则，见 `docs/rag_eval_plan.md`）。

## 7. 资产地图（容易忘的点）

- `docs/llmstudy/`（19 篇）：给 LLM 的领域知识库，00–19 分层；扩 case 前先查
  `17-case-coverage-map.md`（failed_check × 规则维度 × case 的查重表）。
- `notes/`：人工裁定研究笔记（苏生限制、优先权转移、自排连锁等），非正式数据。
- `docs/sources/`：两份规则书 PDF（KONAMI Master Rule 2020 日文 + 简中社区规则书），
  仅本地参考，不进正式证据链；2026-09-07 起已 gitignore，不入库。
- `RAG/`（2026-09-06 起新增，已入库）：RAG 工程工作区 + 面向 RAG 向量化的知识库
  markdown。工程骨架：`RAG/agent.py`（空）、`RAG/.vscode/`、`RAG/docs/`。
  知识文件现状 3 处：
  ① `RAG/docs/llmstudy_ygo_knowledge_db/`（20 篇，**RAG 摄取的规范来源**）：
  `docs/llmstudy/` 20 篇的副本并已 RAG 化改造——每篇头部加 YAML frontmatter
  （title / doc_id / collection / tags / project_bindings / cases / source / written，
  cases 已展开 `case_007/037` 缩写），修了 4 处标题后缺空行，正文与原版逐字一致；
  改造脚本 `_ragify_kb.py`（gitignored，重跑会跳过已有 frontmatter 的文件）。
  ② `RAG/ocg_rulebook_2020_zh_cn_2.3_ch3.md` = 社区规则书 2.3 节（p14–17）+
  第 3 章大师规则全文（p18–93）；标题层级 1:1 对应原文编号（可作分块面包屑），
  正文只合并 PDF 断行不改写，3 张表转 Markdown 表格，1 图保留图题，26 条社区
  译注以「注 N」引用块保留。生成脚本 `_extract_rag.py`（重跑需带 `pypdf`+
  `pymupdf` 的 Python，勿装进 `YGO_PROJECT`）。
  ③ `RAG/llmstudy_domain_kb.md` = 20 篇的合并版（每篇一章，标题降级，正文逐字），
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
