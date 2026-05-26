---
name: quiz-workflow
description: 题库处理工作流规则
metadata:
  type: feedback
---

**规则**: 任务量小（几十道题以内）时，不用脚本统一处理。每道题 AI 直接读题、写解析，逐个文件 Edit。

**Why**: 脚本的正则匹配、格式解析容易出错（已多次验证）。AI 逐题处理能保证每题质量。

**How to apply**: 
1. 逐个读取题目 .md 文件
2. AI 根据题目内容写出解析
3. Edit 追加 `## 解析` 到文件末尾
4. 不计较 token 消耗，质量优先
