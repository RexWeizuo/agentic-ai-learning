---
title: 5-13-outline-attempt
---

# 5-13-outline-attempt

# 5-13 Outline 迁移尝试记录
## 目标
将 Docmost 迁移到 Outline（开源 wiki），保留单词复习模块 + 导入全部历史笔记。
## 完成事项
### 1. Outline 本地部署  - 
源码路径: ~/outline​  - 
数据库: notionuser:notionpass@localhost:5432/outline​  - 
端口: 6006 (生产单端口)  - 
启动: NODE_ENV=production corepack yarn start​  - 
首次登录: http://localhost:6006/api/vocab.devLogin​
### 2. 单词复习模块（已集成进 Outline）  - 
后端: server/routes/api/vocab/vocab.ts​ (7 个 API 端点)  - 
前端: app/scenes/VocabReview.tsx​ (Outline React 页面)  - 
数据: vocab_words​ 表 3743 词 (从 Docmost 导入)  - 
辅助表: word_progress​, review_sessions​, app_config​  - 
Ebbinghaus 算法: 间隔 [1, 3, 7] → mastered 90天
### 3. Docmost → Outline 数据导入  - 
3 个集合: 301, 408 note, Life Management  - 
157 篇文档 (周记/日报/五年计划/学习笔记)  - 
方式: 读取 Docmost PostgreSQL → 直接写入 Outline 数据库
### 4. Outline 单机改造（8 个修复）#问题根因状态1端口 EADDRINUSEthrong 多核集群✅ 绕过2前端白屏/CSP 报错Vite 3001 硬编码✅ 改为生产模式3端口散落 4 个文件团队部署假设✅ 统一 6006/60074无法登录OAuth/email 依赖✅ devLogin 端点5API 500 错误​ctx.state.auth.user​✅ 修正路径6.env 被覆盖.env.development 优先级✅ 统一 production7kill 进程不干净lsof 漏杀 worker✅ fuser -k8导入数据不可见​publishedAt IS NULL​ + user_permissions​✅ 补数据
记忆文件: [[outline-single-user-fixes]]​
## 结论
Outline 现在能用（单词模块 + 历史笔记 + Outline 原生功能），但每次加新功能都可能遇到"团队设计 vs 单人场景"的冲突。
## 考察的替代项目项目特点风险SiYuan中文、块编辑、本地优先、AGPLGo+TS，前端非 ReactYank NoteMonaco 编辑器(VS Code 同款)、AI Copilot、KaTeXElectron，不够轻量NeverWrite"Cursor+Obsidian"、AI inline diff极新(2026.5)，不够稳定NoteGenTauri(20MB)、Ollama+RAG、MIT功能较少Tolaria"Claude Code 可打开笔记库"、Tauri极新、macOS 优先Open Notebook开源 NotebookLM、Docker、16+ AI不是笔记编辑器
## 下一步  - 
实际尝试 1-2 个替代项目  - 
决定继续修 Outline 还是换项目  - 
单词复习模块需要移植到新项目（如果是 Outline 则已完成）  - 
数学 408 英语的学习内容需要用笔记系统管理起来