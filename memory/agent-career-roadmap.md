---
name: agent-career-roadmap
description: 量化Agent项目+AI求职定位+技能对标，新session入口文件
metadata:
  type: project
  date: 2026-06-08
  status: 启动中
---

# Agent 学习 + 求职定位 三线规划

## 背景

用户是考研学生（301数学 + 408计算机 + 英语），正在系统学习 `agentic-ai-system-course`（22 章 agentic 系统课程）。本周（6/1-6/7）完成了线性代数第五章和 OS 第五章，对 301/408 产生倦怠感。周一休息日切换到 Agent 学习作为换脑。

## 三条线

### 线1：量化交易 Agent（主项目）

**目标**：从零搭建一个量化交易的 Agent 系统，边做边学金融知识。

**为什么选量化**：
- 和 Agent 课程天然契合——量化系统需要数据采集→信号生成→决策→执行→复盘，是完整的 agent loop
- 金融知识可以渐进式学习（不需要金融学位，从基础概念开始）
- 有实际产出可展示（GitHub portfolio）
- 涉及实时数据、API 调用、策略回测、风险管理——全是 agentic 系统的核心技术

**注意事项**：
- 这不是生产级量化系统，是学习项目，重点是"agent 如何做决策"
- 不要过早陷入策略优化——先把 agent loop 跑通
- 金融概念（K线、技术指标、仓位管理）随用随学

### 线2：AI 工程师求职定位

**需要做的事**：
1. **收集 3-5 个目标岗位 JD**——看市场到底要什么（LangChain？LLM fine-tuning？RLHF？MCP？Agent 开发？）
2. **对标课程**——22 章课程中哪些直接命中岗位需求，哪些是加分项
3. **差距分析**——"已有的 vs 还缺的"

**用户当前自述水平**：基础入门（学过编程语法，项目经验不多，需要边学边练）。具体技能栈和工作经历需要在新 session 中详细沟通后填入。

### 线3：工作经历 + 技能梳理

**需要用户在新 session 中详细讲述**：
- 做过什么工作（哪怕不是 AI 相关）——岗位、职责、时间
- 什么项目经历——个人项目、课程项目、工作中的工具开发都算
- 会的语言/工具到什么程度（Python？JS？SQL？Linux？Docker？）
- 目标岗位偏好（Agent 开发？ML/RL？后端 infra？全栈？）

## 课程资源定位

项目根目录 `course/` 下 22 章，量化 Agent 优先关注：

| 章节 | 内容 | 对量化的作用 |
|------|------|------------|
| Ch.00 | 学习方法 | 如何和 AI 搭档学 |
| Ch.01-04 | 工具调用→loop→合同→prompt | Agent 骨架 |
| Ch.05-08 | 记忆和状态 | 策略历史、市场数据缓存 |
| Ch.09-11 | 规划+多智能体 | 信号生成agent+风控agent+执行agent |
| Ch.13 | 连接器/MCP | 行情API、交易API |
| Ch.15-17 | 生产基础设施 | 实盘考虑 |
| Ch.22 | 设计你自己的agent | 总装 |

参考系统：OpenCode（coding agent）、Hermes Agent（个人助手，记忆+skills+cron）、Paperclip（多agent编排+Postgres状态）

## 关联记忆文件

- [[user_profile]] — 用户画像
- [[project-philosophy]] — 核心理念
- [[learning-system]] — 50-10-汇报节奏
- [[daily-rhythm]] — 作息规律
- [[review-priority-rule]] — 错题优先原则

## 第一次对话建议

新 session 建议按这个顺序：
1. 先聊工作经历和技能（让 AI 知道你是谁）
2. 再聊目标岗位和差距
3. 最后落地到量化 Agent 的第一步：搭什么、怎么开始
