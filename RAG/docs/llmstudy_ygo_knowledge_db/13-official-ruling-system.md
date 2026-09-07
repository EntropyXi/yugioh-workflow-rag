---
title: "官方裁定体系"
doc_id: "13"
collection: "llmstudy_ygo_knowledge_db"
tags:
  - KONAMI
  - 官方Q&A
  - 裁定数据库
  - 证据契约
  - fid
  - cid
  - 权威层级
  - 二手材料
project_bindings:
  - required_sources
source: "docs/llmstudy/13-official-ruling-system.md"
written: "2026-07-28"
---

# 13 — 官方裁定体系

> **撰写日期**：2026-07-28
> **来源**：P0 KONAMI 官方 Q&A 数据库 + 项目 `docs/PROJECT_CONTEXT.md`
> **对应项目**：`required_sources` 字段、证据契约、fid/cid 体系

---

## 1. KONAMI 官方 Q&A 数据库

### 1.1 数据库结构

KONAMI 维护了官方卡片数据库和 Q&A 系统：

| 数据库 | URL | 语言 |
|---|---|---|
| **日文官方 DB** | `https://www.db.yugioh-card.com/yugiohdb/` | 日文 |
| **简中官方 DB** | `https://www.db.yugioh-card-cn.com/` | 简中 |

每张卡在日文 DB 中有：
- 卡片详情页（效果文本、属性、卡包信息）
- Q&A 列表（该卡相关的官方裁定）
- 补充页面（`cid:XXXXX#supplement`，部分卡有额外的裁定说明）

### 1.2 裁定标识符

| 标识符 | 格式 | 说明 | 本项目 source_type |
|---|---|---|---|
| **cid** | `cid:数字` | Card ID — 指向卡片详情页 | `official_card_text` |
| **fid** | `fid:数字` | FAQ ID — 指向具体 Q&A 条目 | `official_ruling` |
| **cid#supplement** | `cid:数字#supplement` | 卡片的补充裁定页面 | `official_ruling` |
| **rulebook** | `rulebook:标识` | 官方规则书引用 | `official_rulebook` |

---

## 2. 裁定为什么"不过期"

### 2.1 裁定的本质

KONAMI 官方 Q&A 是**对游戏规则和卡片文本的权威解释**，不是随环境变化的"策略建议"。一条裁定回答的是一个特定的规则交互问题。只要：

1. 涉及的**卡片效果文本没有 errata（修订）**
2. 涉及的**游戏规则没有修订**

→ 该裁定就仍然有效。裁定数据库中的 `source_updated_at` 记录的是该条目最后一次被 KONAMI 更新/添加的日期。**没有更新意味着裁定没有变化**。

### 2.2 裁定何时会变化

| 变化原因 | 示例 |
|---|---|
| 卡片文本 errata | 卡的効果文本被修订（如"处刑人-摩休罗"2020 年新文本） |
| 规则修订 | 2020.04 大师规则修订导致部分旧裁定被替换 |
| 新裁定覆盖旧裁定 | KONAMI 发布更精确的解释 |

> 因此，**不存在"太久远的裁定自动失效"**。如果一张卡从 2017 年到 2026 年没有被 errata，其裁定依然有效。

---

## 3. 裁定来源的权威层级

| 层级 | 来源 | 权威性 | 本项目中对应 source_type |
|---|---|---|---|
| 1 | KONAMI 官方 Q&A 数据库 | 最高 | `official_ruling` |
| 2 | KONAMI 官方规则书 | 最高 | `official_rulebook` |
| 3 | KONAMI 官方卡片详情页（卡的效果文本） | 最高 | `official_card_text` |
| 4 | KONAMI 官方新闻/公告 | 高 | — |
| 5 | 二手材料（B站、Reddit、贴吧） | 参考 | `secondary_reference` |

> 本项目**证据契约**要求：每条正式 case 至少含 1 个 `official_card_text` + 1 个 `official_ruling` 或 `official_rulebook`。

---

## 4. 日文原文 vs 简中翻译

### 4.1 权威性差异

- **日文原文**：裁定原文，最高权威，不可争议
- **简中翻译**：翻译版本，权威性由官方运营方保证。部分卡无简中裁定翻译时，需引用日文原文
- **简中官方卡片文本**（`db.yugioh-card-cn.com`）：等于日文原文的权威性

### 4.2 本项目的语言覆盖规则

校验器（`check_jsonlschema.py`）强制要求每条 case 同时包含：
- `ja` (日文) 的 `official_card_text`
- `zh-CN` (简中) 的 `official_card_text` 或经批准的 `secondary_reference`（用于确实无简中官方正文的卡）

---

## 5. 二手材料的定位

### 5.1 允许的使用方式

- `secondary_reference`（`source_type`）
- 只能作为**补充解释**，不能成为**唯一裁定依据**
- 来源可以是：B站裁定讲解视频、YGOrganization 翻译、贴吧精华帖等

### 5.2 本地 cards.cdb 的使用

对于无法在 KONAMI 简中官方 DB 中访问的卡，允许使用：

```json
{
  "source_type": "secondary_reference",
  "authority": "local_cards_cdb",
  "url": "local-cdb://cards.cdb/texts/99999999",
  "language": "zh-CN"
}
```

> 本地 CDB 来源**不能**伪装为 `official_card_text`。

---

## 6. 裁定数据库的实际查询流程

当为本项目新增一条 case 时：

1. 确定涉及的卡片 → 用日文 DB 搜索卡名
2. 查看卡的 Q&A 列表 → 找对应的裁定条目
3. 记录 `fid`（FAQ ID）和 `source_updated_at`
4. 在日文 DB 和简中 DB 中都确认卡片详情页可访问
5. 如果简中 DB 无该卡 → 寻找 `local-cdb://` 补源或替换候选

---

## 7. 与本项目的关联

本项目的 `gold_answer.required_sources` 字段完整实现了这套证据体系。每条 case 的证据链都是可追溯、可验证的，URL 指向 KONAMI 官方域名（`yugioh-card.com`），ID 格式符合 `fid:数字` 或 `cid:数字`。
