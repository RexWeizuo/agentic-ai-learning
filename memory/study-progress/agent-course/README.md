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
| Ch.01 | 一次工具调用 | ✓ | ✓ get_price 三市场 | 加密货币/VIE/港股 | 完成 |
| Ch.02 | Agent 循环 | ✓ 五题+全走读 | ✓ loop+5停止条件 | 夏普比率/最大回撤 | 完成 |
| Ch.03 | 工具验证 | ✓ 全章+钩子+元数据 | ✓ 4工具全量+错误信封 | PE/大盘/基本面/K线 | 完成 |
| Ch.04 | 提示词与缓存 | — | — | — | 待开始 |

## 量化项目状态

`workspace/quant-agent/`：uv 管理，Qwen 驱动。

**数据源**：新浪（行情+K线+大盘）+ 腾讯（基本面）

**工具**（5 个）：get_price / get_kline / get_index / get_financials / final_answer

**Agent 能力**：4 停止条件 + doom loop 检测 + 错误分类信封 + 钩子系统 + 溯源

**日志**：每次运行生成 `logs/run-YYYYMMDD-HHMMSS.md`（执行全追踪）

## 金融知识索引

详见 [金融知识.md](金融知识.md)，按学习章节组织。
