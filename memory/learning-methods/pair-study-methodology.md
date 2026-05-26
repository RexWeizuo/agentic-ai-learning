---
name: pair-study-methodology
description: Pair Study 学习方法的定义、流程和在三个板块中的应用
metadata:
  type: reference
  date_adopted: 2026-05-24
---

## 定义

Pair Study = 学生先读讲义 → AI 提问检查理解 → 学生回答 → AI 反馈纠错 → 错题记录到错误分析 → 定时复习

**Why:** Ch.00 提出的"结对学习比被动学习快十倍"。学生用自己的话解释概念，AI 追问细节和边界，错题驱动复习。

## 流程

### 初学阶段（每小节首次学习）

```
1. 学生阅读讲义 + 复习笔记
2. AI 提出 4-6 个问题（覆盖面广，包含基础概念和边界 case）
3. 学生逐一回答
4. AI 逐题反馈：对→确认/补充，错→纠错+追问
5. 记录到 study-progress/{章节}/{小节}.md
6. 错题记录到 error-analysis/{章节}/{小节}-错题.md
```

### 复习阶段（艾宾浩斯节点触发）

```
1. AI 根据 error-analysis 挑出薄弱知识点
2. 每个薄弱点 1-2 个问题（精准打击，不复述已掌握的）
3. 重做错题
4. 更新掌握程度评分
```

## 初学 vs 复习对比

| | 初学 | 复习 |
|---|---|---|
| 问题数量 | 4-6 题/小节 | 1-2 题/薄弱点 |
| 覆盖范围 | 全面 | 只打薄弱点 |
| 重点 | 建立知识框架 | 修补漏洞 |
| 记录位置 | study-progress | error-analysis + review-schedule |

## 三个板块的联动

```
study-progress ──记录──→ 学到了什么、掌握程度
error-analysis  ←──输入── 错题、理解偏差
review-schedule ──触发──→ 艾宾浩斯时间点 → 启动复习 session
learning-methods ──优化──→ 学习方法迭代改进整个流程
```

**How to apply:** 每完成一个小节，更新三段记录；复习节点到达时 AI 主动提醒。
