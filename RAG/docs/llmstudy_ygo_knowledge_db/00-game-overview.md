---
title: "游戏王 OCG 游戏本体认知"
doc_id: "00"
collection: "llmstudy_ygo_knowledge_db"
tags:
  - OCG
  - 大师规则
  - Master Rule
  - 决斗
  - 胜利条件
  - KONAMI 官方资源
  - 术语入门
source: "docs/llmstudy/00-game-overview.md"
written: "2026-07-28"
---

# 00 — 游戏王 OCG 游戏本体认知

> **撰写日期**：2026-07-28
> **来源优先级**：P0 官方 → P1 YGOrg/yugipedia → P2 简中 wiki
> **环境**：本知识库聚焦 **OCG（Official Card Game，亚洲区）**，不涉及 TCG（欧美）特殊裁定。

---

## 1. 游戏王 OCG 是什么

**游戏王 Official Card Game（遊☆戯☆王OCG）** 是由 KONAMI 发行的集换式卡牌游戏（TCG），基于漫画《游戏王》中的决斗怪兽（Duel Monsters）玩法。OCG 是游戏王在**亚洲地区**（日本、中国大陆、韩国、东南亚等）发行的版本。

### 与 TCG 的区别

| | OCG | TCG |
|---|---|---|
| 发行区域 | 日本、亚洲 | 北美、欧洲、大洋洲 |
| 卡片语言 | 日文、简中、韩文 | 英文、法文、德文等 |
| 卡池发布节奏 | 先于 TCG 约 3-6 个月 | 滞后 |
| 禁限卡表 | 独立维护 | 独立维护 |
| 裁定 | 以日文 KONAMI Q&A 为准 | 有部分独立裁定 |
| 卡片罕贵度 | 不同分布 | 不同分布 |

> **本项目完全基于 OCG 规则和裁定**。不使用 TCG 特有的裁定或禁限卡表。

### Master Duel

**Master Duel** 是 KONAMI 的官方电子游戏平台（PC/主机/手机），采用独立的禁限卡表和部分简化规则（如无 BO3 side deck）。本项目也不涉及 Master Duel 的特殊处理。

---

## 2. 游戏的基本规则

- **对战人数**：2 人（1v1）
- **卡组**：主卡组 40-60 张，额外卡组 0-15 张，副卡组 0-15 张
- **同名卡限制**：主卡组 + 额外卡组 + 副卡组合计最多 3 张同名卡
- **初始 LP（生命值）**：8000
- **初始手牌**：5 张（先攻第一回合不抽卡）

### 胜利条件

1. 将对方 LP 降至 0
2. 对方需要抽卡时卡组无卡可抽
3. 特定卡片效果的特殊胜利条件（如"艾克佐迪亚"）

### 比赛结构

- **一场 Duel（决斗）**：单局对战
- **一场 Match（比赛）**：BO3（三局两胜），每局之间可以换副卡组

---

## 3. 大师规则（Master Rule）演进

游戏王 OCG 的规则体系称为**大师规则（Master Rule）**，经历了多次重大修订：

| 版本 | 时间 | 核心变化 |
|---|---|---|
| 大师规则 1 | 2008.03 | 术语统一，Speed Spell 体系确立 |
| 大师规则 2 | 2011.03 | 超量召唤（Xyz）引入，优先权概念调整 |
| 大师规则 3 | 2014.03 | 灵摆召唤（Pendulum）引入，场地魔法共存规则改变 |
| 新大师规则 | 2017.03 | 连接召唤（Link）引入，EX 怪兽区域新增，EX 卡组特召必须到 EX 区或连接端 |
| **大师规则 (2020.04 修订)** | **2020.04** | **当前使用版本**。融合/S/X 怪兽可以直接出在主怪兽区；诱发效果场所移动规则改写 |

### 2020 年 4 月修订的关键变化（OCG）

1. **额外卡组特召规则放宽**：融合/同调/超量怪兽从 EX 卡组特召时，可直接放在主怪兽区域（不再强制连接端）。
2. **诱发效果场所移动**：如果一张卡在满足发动条件后、效果发动前移动了位置，效果不再发动。
3. **召唤限制计数规则**：被无效的召唤不计入"本回合已经召唤过"的计数。
4. **同名特召次数限制**：被无效的特召不计入"XX 1 回合只能特召 1 次"。
5. **陷阱怪兽区域释放**：变成怪兽特殊召唤的永续陷阱卡，不再占用原来的魔陷区域。

> **本项目数据基于该版本规则**。

---

## 4. KONAMI 官方资源导航

### 核心官方站点

| 站点 | 用途 | URL |
|---|---|---|
| **官方卡片数据库（日文）** | 查卡、Q&A 裁定 | `https://www.db.yugioh-card.com/yugiohdb/` |
| **简中卡片数据库** | 简中卡查 | `https://www.db.yugioh-card-cn.com/` |
| **官方规则手册（亚洲区）** | 入门规则 | `https://www.yugioh-card.com/asia/zh/play/ocg-rulebook/` |
| **KONAMI 官方 Q&A 搜索** | 裁定原文 | `https://www.db.yugioh-card.com/yugiohdb/faq_search.action` |

### 简中社区权威资源

| 站点 | 用途 |
|---|---|
| **OCG Rule (ocg-rule.readthedocs.io)** | 最详尽的中文 OCG 规则参考，含官方 FAQ 翻译 |
| **官方完全规则书（中文翻译，ocg-rulebook.rtfd.io）** | 官方规则书的中文完整翻译 |
| **yugipedia.com** | 英文权威 wiki，规则机制文档质量高 |
| **YGOrganization** | OCG 新闻和裁定翻译（英文） |

---

## 5. 与本项目的关联

本项目 `yugioh-workflow-rag` 的数据集中，`rule_context` 字段固定指定 OCG 环境：

```json
{
  "rule_context": {
    "game": "Yu-Gi-Oh!",
    "format": "OCG",
    "language": "zh",
    "rule_version": "unspecified"
  }
}
```

每一条 gold case 的裁定依据都来自 KONAMI 官方 Q&A 数据库（`fid:XXXXX` 或 `cid:XXXXX#supplement`）和官方卡片详情页（`cid:XXXXX`）。

---

## 6. 快速术语入门

| 术语 | 英文/日文 | 含义 |
|---|---|---|
| 决斗 | Duel / デュエル | 一局对战 |
| LP | Life Point / ライフポイント | 生命值，初始 8000 |
| 回合玩家 | Turn Player | 当前回合的玩家 |
| 非回合玩家 | Non-Turn Player | 对方的玩家 |
| 手牌 | Hand / 手札 | 手中的卡 |
| 卡组 | Deck / デッキ | 主卡组 |
| 额外卡组 | Extra Deck / EXデッキ | 融合/S/X/连接怪兽存放处 |
| 墓地 | GY (Graveyard) / 墓地 | 被破坏/送墓的卡的去处 |
| 除外 | Banished / 除外 | 从游戏中移除 |
| 优先权 | Priority / 優先権 | 发动卡的权利 |
| 连锁 | Chain / チェーン | 多个效果连续发动的处理机制 |
