---
name: implementation-standard
description: 代码实现参考标准——讲义优先+Claude Code源码验证
metadata:
  type: project
  date: 2026-06-14
---

# 实现标准

## 优先级

1. **课程讲义**（`course/` 22 章）——概念和模式的第一来源
2. **Claude Code 源码**（`references/claude-code/src/`）——生产级实现参考
3. **其他参考系统**（OpenCode/Hermes Agent/OpenClaw/Paperclip）——补充视角

## 规则

- 讲义定义"应该做什么"，Claude Code 定义"怎么做"
- 实现有歧义时，看 Claude Code 源码中对应的模块
- 不自己发明模式——先在 references 里找有没有被验证过的做法
- provenance/metadata/error-envelope/hooks 等概念严格按 Claude Code 的实现方式

## 关联

- [[agent-career-roadmap]] — 三线规划
- [[project-philosophy]] — 抓伪学习的核心理念
