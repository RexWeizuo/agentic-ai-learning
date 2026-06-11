---
name: agent-course-进度
description: Agentic AI System Course 22章学习进度
metadata:
  type: project
  subject: Agent
  start_date: 2026-06-08
---

## 概述

以量化 Agent 项目为主线，逐章学习 `course/` 22 章，每章理论+代码实战。

参考项目：`references/ai-quant-book-main/`（量化知识补充）

## 总体进度

| 章节 | 内容 | 理论学习 | 代码实战 | 金融知识 | 状态 |
|------|------|---------|---------|---------|------|
| Ch.00 | 学习方法 | ✓ | — | — | 完成 |
| Ch.01 | 一次工具调用 | ✓ | ✓ `get_price` 三市场适配 | 加密货币/USDT/挖矿/NFT/VIE/蓝筹/港股 | 完成 |
| Ch.02 | Agent 循环 | ✓ 五题考试 | ✓ loop跑通（2步2163tk） | 夏普比率/最大回撤 | 完成 |
| Ch.03 | 工具验证 | — | — | — | 待开始 |

## 量化项目状态

`workspace/quant-agent/`：uv 管理，Qwen-max 驱动，新浪 API（A股）。

已实现：`get_price`（A股/加密货币/美股）、`final_answer`、Agent loop（4停止条件+doom loop检测）。

## 金融知识索引

详见 [金融知识.md](金融知识.md)，按学习章节组织。
