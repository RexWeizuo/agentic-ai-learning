---
date: 2026-06-08
day: 周一
type: Agent Session 概括
---

# 2026-06-08 Agent Session

## 产出总览

| 维度 | 内容 |
|------|------|
| 课程进度 | Ch.01 通过，Ch.02 五道题待答 |
| 项目 | `workspace/quant-agent/` 启动，`get_price` 工具可运行 |
| 金融知识 | 13 个概念（加密货币→VIE→港股规则）|
| 求职 | 长沙 AI Agent 岗位调研完成 |

## Ch.01 学习

- 工具调用四步循环：描述工具→模型发请求→代码执行→结果返回
- Schema 是合同：名称+描述（含"不要用于X"边界）+输入schema
- 错误返回为 tool_result，不抛异常：抛异常杀死进程，模型看不到错误
- 代码追踪：`_detect_market` 隐式调用、secid 前缀规则、模型视野边界

## 量化 Agent 项目

- 路径：`workspace/quant-agent/`
- 工具：uv 管理，依赖 akshare + ccxt + yfinance
- `src/quant_agent/tools/prices.py`：三市场统一 `get_price`
- A 股跑通（茅台 1263元，跌 0.77%），加密货币需 VPN，美股限速
- 参考项目：`references/ai-quant-book-main/`（历史量化事故+风控）

## 金融知识

加密货币价值/跨境转账刚需、以太坊智能合约、USDT 机制与风险、挖矿vs质押、NFT 泡沫、Tether 对手方风险、蓝筹股、A 股板块分层（主板/科创板/创业板）、外商投资负面清单、VIE 架构、港股规则

## 长沙 AI 岗位调研

- 目标档：中级 10K-20K
- 市场特点：传统行业 AI 转型为主，不要求顶会/大厂
- 技能栈：Python + LangChain/LangGraph + RAG + MCP
- 用户优势：一年实战搭过 5 种 agent，缺的是框架术语和系统化

## Ch.02 待答五题

1. 五阶段循环在量化场景的具体映射
2. 只有 step cap 没 final_answer 的问题
3. Doom loop 检测——为什么只看调用不看结果
4. 错误也是回合——三次失败同一个工具
5. Step boundary 五种能力，实盘最关键的两个

## 学习方式调整

用户要求：先考察讲义理解→再讨论搭建方案→互动改进。金融随用随学。每日双记录（完整对话+概括版）。周一回顾。与主项目考研记录同步。

完整对话见：`knowledge-base/生活/2026/2026-06-08-完整对话.md`
