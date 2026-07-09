# case_041–case_050 官方 Q&A 扩充计划（含前置 Step 0）

## Summary

前置 Step 0：全量 bump `schema_version` 从 `2.0.0` 到 `2.1.0`。

新增 10 条 gold cases，逐条逐源核验 KONAMI 官方 Q&A、JA 卡片文本、CN 卡片文本。写入 `gold_cases/json/case041.json` 至 `case050.json`，同步主 JSONL 至 50 行。不修改已有 40 条的裁定结论。

## 执行纪律

- 单条流水线。一 case 一核验一写入一校验。每 case 完成后立即跑 `conda run -n YGO_PROJECT python check_jsonlschema.py --self-test`。
- CN 官方详情页不可访问时不伪造来源，暂停该条寻找备选。
- `task_type`：`resolve_effect` → `effect_resolution_judgment`，其余 → `operation_legality_judgment`。

## Step 0 — 已完成

## 10 条 case（按计划顺序，当前进度下一条为准）

1. `case_041`（fid:8194）→ CN 不可用，待替换
2. `case_042`（fid:20246）→ 进行中
3. `case_043`（fid:15529）→ 待定
4. ...

## 终验收

- 主 JSONL 50 行，ID 连续。
- 11 个负例被拒（self-test）。
- 50 个 JSON 镜像一致。
- `schema_version` 全部 `"2.1.0"`。
- CN 不可用的 case 被替换或跳过。

## Assumptions

- 本轮只新增，不改已有 40 条。
- `accessed_at` 使用 `"2026-07-08"`。
