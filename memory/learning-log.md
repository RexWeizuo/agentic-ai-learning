---
name: learning-log
description: 用户的学习过程记录——关键洞察、概念突破、问答精华
metadata:
  type: project
---

## 学习历程

### 2026-05-23 — Ch.00–03 初次接触（旧模式）

- 克隆了四个参考系统 + Claude-Code 源码还原
- 探索了思源笔记知识库结构（201英语/301数学/408计算机）
- Ch.01–03 以"AI 写代码+讲解"完成，用户指出"功能都是你告诉我的"
- 关键技术决策：DeepSeek API + Anthropic 兼容端点

### 2026-05-24 — 切换到配对学习模式

- 用户明确提出 C 模式
- 全部 23 章翻译为中文（意译）
- Ch.00 配对学习完成（四个问题）

### 2026-05-25 — Ch.01 完成 + 数据基础设施全面建立

- 思源递归导出修复：block 深层遍历后内容暴涨（301: 117K→416K, 408: 59K→559K, 生活: 168K）
- 读取 5.25 日记，了解用户平衡考研班+AI开发的真实困境
- **FlowUs API 打通**：CDP→JWT→REST API，定位 Pre-Master 四个数据库
- **301quiz 重组**：184 道题从 FlowUs 导出的 zip 解析为结构化 knowledge-base
- Ch.01 配对学习完成：三步精准修改 description + system prompt
- 每晚 23:11 定时日志任务设定
- 决定：VS Code 文件系统替代思源作为知识库后端

## 关键洞察

- [[paired-learning-insight]] — "瓶颈是知道该问什么"，旧模式剥夺了"学习怎么问问题"的机会
- [[skeleton-vs-muscle]] — description 写法是骨架，选模型是肌肉；思源是肌肉，文件系统是更好的骨架
- [[four-subsystems]] — 四个子系统：错误分析（先做）、复习管理、进度追踪、知识图谱
- [[learning-agent-insight]] — questions/ + memory/ 日志系统本身就是学习 Agent（Ch.05-07 模式）
- [[error-location]] — "未找到"不能简单归咎厨房或厨师，要根据返回信息定位修复点
- [[tool-choice]] — tool_choice 是 API 参数由循环控制，不是模型决策
- [[flowus-extraction]] — 三层提取路径：IndexedDB→CDP→REST API，最终 API 最可靠
- [[data-structure-design]] — 知识库 = 扁平 markdown + frontmatter + 图片，AI 可 Glob/Grep 直接消费

## Agent 搭建进度

| 章节 | 模式 | 状态 |
|---|---|---|
| Ch.00 | 配对学习 | 完成 |
| Ch.01 | 配对学习 | 完成 |
| Ch.02 | 配对学习 | 待开始 |
| Ch.03 | 配对学习 | 待开始 |
| 错误分析子系统 | — | 数据就绪，待设计 |

**Why:** 记录学习轨迹，让 Agent 未来能追踪用户的认知进步和项目演进。
**How to apply:** 每次重要问答后追加，形成可检索的学习档案。
