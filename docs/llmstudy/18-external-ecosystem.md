# 18 — 外部生态与资源导航

> **撰写日期**：2026-07-28
> **维护频率**：当有新资源或链接失效时更新

---

## 1. 官方资源（P0 — 第一顺位）

| 资源 | URL | 语言 | 用途 |
|---|---|---|---|
| **日文官方卡片数据库** | `https://www.db.yugioh-card.com/yugiohdb/` | 日文 | 查卡、查 Q&A、获取 fid/cid |
| **简中官方卡片数据库** | `https://www.db.yugioh-card-cn.com/` | 简中 | 查卡、简中卡片文本 |
| **官方规则手册（亚洲）** | `https://www.yugioh-card.com/asia/zh/play/ocg-rulebook/` | 简中/英文 | 入门规则 |
| **KONAMI 官方 Q&A 搜索** | `https://www.db.yugioh-card.com/yugiohdb/faq_search.action` | 日文 | 裁定原文搜索 |
| **禁限卡表（OCG）** | `https://www.yugioh-card.com/japan/event/forbidden/` | 日文 | 最新限制规章 |

---

## 2. 高质量二次源（P1 — 第二顺位）

| 资源 | URL | 语言 | 用途 |
|---|---|---|---|
| **OCG Rule (最详尽中文规则)** | `https://ocg-rule.readthedocs.io/` | 简中 | 规则参考、FAQ 翻译 |
| **官方规则书中译** | `https://ocg-rulebook.readthedocs.io/` | 简中 | 官方规则完整中文版 |
| **Yugipedia** | `https://yugipedia.com/` | 英文 | 最权威英文 wiki，规则机制文档质量高 |
| **YGOrganization** | `https://ygorganization.com/` | 英文 | OCG 新闻、裁定翻译、新卡信息 |
| **中文卡查 (ygocdb)** | `https://ygocdb.com/` | 简中 | 卡片搜索 |

---

## 3. 简中 wiki 与社区（P2 — 第三顺位）

| 资源 | URL | 语言 | 用途 |
|---|---|---|---|
| **萌娘百科 - 游戏王** | `https://zh.moegirl.org.cn/` 搜索"游戏王" | 简中 | 卡牌种类、规则入门 |
| **NW 论坛** | `https://bbs.newwise.com/` | 简中 | 传统游戏王社区，XYZ龙加农的翻译源 |
| **贴吧** | `https://tieba.baidu.com/` 搜索"游戏王" | 简中 | 裁定讨论（质量参差，需核验） |
| **B站** | bilibili（通过 bilibili-mcp 搜索） | 简中 | 裁定讲解视频/专栏 |

---

## 4. 自动化平台（参考）

| 平台 | 说明 | 规则实现质量 |
|---|---|---|
| **YGOPro / EDOPro** | 开源自动对战平台 | 规则实现高度精确，可作为裁定参考 |
| **Master Duel** | KONAMI 官方电子游戏 | 官方实现，但有部分简化 |
| **Duel Links** | KONAMI 手游 | 规则大幅简化，不可作为裁定参考 |

---

## 5. 本项目内部的资源

| 路径 | 用途 |
|---|---|
| `docs/llmstudy/` | **本知识库** — LLM 学习游戏王裁定的标准入门材料 |
| `docs/PROJECT_CONTEXT.md` | 项目状态快照与交接入口 |
| `docs/schema.md` | v2.1.0 字段说明与枚举文档 |
| `docs/task_scope.md` | 任务边界与判断流程 |
| `notes/` | 裁定研究笔记（7 篇） |
| `log/ygo_json_case_changelog.md` | 变更日志 |
