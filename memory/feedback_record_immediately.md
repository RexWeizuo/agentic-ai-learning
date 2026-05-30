---
name: feedback-record-immediately
description: 随时记录——每次问答后立即写到对应日志，不等用户催
metadata:
  type: feedback
---

**规则**: 每次 pair study 问答结束后，立即将 Q&A、错题、纠正更新到 `memory/study-progress/` 和 `memory/error-analysis/` 对应文件中。不等用户说"记录"。

**Why**: 用户多次提醒"记得记录"、"回答也记录了吗"、"随时记录这一点写进 agent 记忆了吗"。延迟记录会导致遗漏和重复确认。

**How to apply**: 每反馈完一轮问题的答案，立刻追加到对应的学习日志文件，作为收尾动作。
