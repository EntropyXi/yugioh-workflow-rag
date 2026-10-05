# RAG 文档切分与上下文化

本目录现有可运行的离线 Markdown chunk 管道，以及可选的 DeepSeek 上下文化步骤。输入固定为 `RAG/docs/` 下的 21 份 Markdown：20 篇领域学习资料和 1 份社区规则书摘录。全部标为 `secondary_reference`，不能充当正式 case 的 KONAMI 官方证据。根目录 `docs/llmstudy_domain_kb.md` 是合并版，不进入本语料，避免重复。

## 环境

`environment.yml` 声明 `YGO_RAG`、Python 3.13、PyYAML 6.0.3 和 tiktoken 0.13.0。已有这些依赖的 `YGO_PROJECT` 环境也可运行：

```powershell
conda run -n YGO_PROJECT python -m RAG.agent chunk
conda run -n YGO_PROJECT python -m unittest discover -s RAG/tests -v
```

`chunk` 不访问网络。默认目标 400 token、上限 600 token、同节最多 50 token 重叠；按 Markdown 标题和段落拆分，长段落再按句子与 token 上限拆分。YAML frontmatter 作为元数据保留，不进入 `raw_text`。每块保存稳定 ID、源文件 hash、字符及行位置、标题路径、父文档范围及 hash。小文档使用全文作父上下文；长规则书选择上限内覆盖范围最大的标题子树，必要时退到紧邻标题的正文块，父范围上限 12000 token。无合适父范围时明确报错，不静默截断。纯标题块可用标题本身作父范围。

输出在忽略 Git 的 `RAG/artifacts/`：`chunks.jsonl` 与 `chunks_manifest.json`。重复运行在输入和版本不变时应得到相同 hash。覆盖检查保证 Markdown 正文中的非空白字符都属于某个 chunk 的核心范围。

## 可选模型上下文化

须先设置 `DEEPSEEK_API_KEY`，并明确允许将语料和提示词发送给 DeepSeek。以下命令会产生付费网络调用：

```powershell
conda run -n YGO_PROJECT python -m RAG.agent contextualize --max-cost-usd 1 --max-calls 3
conda run -n YGO_PROJECT python -m RAG.agent contextualize --max-cost-usd 1
```

默认模型 `deepseek-flash`。模型看到当前 chunk 与其完整父范围，并按 `prompts/context_v1.txt` 生成简短的块专属上下文。`retrieval_text` 是上下文加原始 chunk；`raw_text` 保持原文，供追溯和展示。缓存键包含源、父范围、提示词和模型 hash，重跑复用已完成结果。`--max-cost-usd` 是该缓存文件所有已记录调用和本轮调用的累计上限；请求前按 UTF-8 字节数加余量、模型最大输出和峰时公开标价预留额度，响应后按实际 token usage 计入累计估算。网络故障后可直接重跑，缓存会保留已完成块。预算不足或 `--max-calls` 达到上限时输出部分结果，并在报告中写明停止原因。

输出为 `contextualized_chunks.jsonl`、`context_cache.jsonl` 和 `context_report.json`。缓存与产物包含语料内容，不提交 Git。缓存中的费用是按公开标价计算的估算，不代表服务商账单；若请求已送达但未返回 usage，该调用无法由本地缓存精确计费。更换模型或提示词后会重新生成上下文，旧缓存用量仍计入同一个预算上限。

这里尚无 embedding、BM25 索引、混合召回、rerank、问答 agent 或 Recall@k/MRR 评测 runner。当前只能验证切分和上下文生成，不能声称检索效果提升。

## 2026-10-05 实测

- 21 份来源生成 699 块；重复切分的 `chunks_sha256` 均为 `2454948fd274d1ef3918f76b8f93b12818c9693aa843c8bb6dff6b63992ada1b`。
- DeepSeek 上下文化完成 699/699 块，空上下文 0；ID 顺序、原文拼接和 manifest hash 检查均通过。
- 本地 `cl100k_base` 估算的上下文长度为 70–145 token：335 块落在 50–100，364 块为 101–145。文章中的 50–100 token 在此作为目标长度，当前仍有超出目标的生成结果。
- 两轮各 3 次抽样加全量续跑共记录 702 次 API 调用（最后一轮新增 696 次、复用 3 次缓存）。按 DeepSeek 峰时公开标价与返回 usage 估算累计 $0.4762173，低于本次 $1 上限；此值不是实际账单。
