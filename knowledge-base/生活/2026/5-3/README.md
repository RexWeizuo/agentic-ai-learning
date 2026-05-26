---
title: 5-3
---

# 5-3

# 5-3 五月 Claude Code 开发全记录
从 5/1 到 5/12 的所有 Claude Code 工作汇总。涵盖 notion-lite 重构、Docmost AI 开发、OCR 识别、life_management 搭建等。
## 时间线总览日期项目主要工作5/1-7408/301教材 OCR 识别、练习题录入5/8/mnt/d/studyCLAUDE.md 项目文档、OCR 进度监控、venv 统一5/9notion-lite重构启动、PostgreSQL 配置、技术栈评估5/10notion-lite继续重构（中断后恢复）5/11 上午life_mgmtClaude Code 三年回顾建议（12 条）5/11 上午docmostAI 功能差距分析（vs Notion AI）5/11 下午docmostAI 模块完整实现（21 个文件）+ 思维导图5/12 全天docmost单词复习算法、子页面索引修复、替代方案调研
---

## 5/1-7：408 & 301 教材处理
### 408 OS 教材 OCR  - 
使用 qwen3.6-plus 多模态模型逐页识别《操作系统》PDF（292 页）  - 
同时对比 OCR（paddleocr）与多模态模型的效果  - 
发现多模态模型识别质量远好于 OCR  - 
每页约消耗 500-1000 tokens  - 
脚本：后台运行，通过 run.log​ 和 progress.json​ 监控进度  - 
API key: sk-bc1bde1e77d444dc9f52cde35d68f8d8
### 408 练习题录入  - 
将 D:\study\408\wd练习题_文本_OCR​ 内容分级录入 notion-lite
---

## 5/8：项目整理 & CLAUDE.md
### 项目文档化  - 
为 /mnt/d/study​ 创建 CLAUDE.md，记录所有项目结构  - 
项目清单：  - 
notion-lite（主项目，FastAPI + Vue3 + PostgreSQL）  - 
301（数学，FastAPI + SQLite）  - 
408（计算机，FastAPI + SQLite）  - 
kaoyan-english（英语，FastAPI + SQLite）  - 
ai_job_assistant（求职助手，FastAPI + SQLite）  - 
长期计划：所有项目合并到 notion-lite  - 
端口分配、venv 环境、数据库表全部文档化
### 环境统一  - 
发现多个 venv 环境（.venv, .venv-wsl）  - 
讨论是否用 uv 替代 pip（WSL 已装 uv）  - 
最终保留现有方案
---

## 5/9-10：notion-lite 重构
### 重构方向  - 
完全对标 Notion：块编辑器、页面树、实时协作  - 
保留：单词模块（Ebbinghaus 复习）、数据库内容  - 
丢弃：旧的前端架构  - 
技术栈讨论：FastAPI + Vue3 vs NestJS + React vs 其他  - 
最终导向 Docmost（发现已经有块编辑器 + 协作）
### 卡住点  - 
重构中途被中断  - 
PostgreSQL 连接配置问题  - 
5/10 恢复后继续，但进度缓慢
---

## 5/11 上午：AI 方向确认
### Life Management 搭建  - 
从 Notion 导出 2024/2025/2026 全部周记  - 
Claude Code 分析三年记录，给出 12 条建议：  - 
追踪过程质量而非覆盖范围  - 
工作学习分离（双线程问题）  - 
恢复每日评分（学习深度/身体健康/心理状态）  - 
naki 问题已有结论，不要再反复  - 
报班价值不仅是课程  - 
最大资产是反思能力，最大负债是情绪波动  - 
设计系统替代了执行系统  - 
对"天赋"的执念在拖累  - 
没有给自己的进步留证据  - 
身体是所有计划的单点故障（腰椎康复）  - 
对环境理解错误——需要"有人在等你交付"  - 
五年规划说了两年没下笔
### Docmost AI 差距分析  - 
完整分析了 Docmost vs Notion AI 的功能差距  - 
发现 EE 后端代码完全缺失（apps/server/src/ee/ 为空）  - 
前端 AI Chat/Editor/Search/MCP UI 已完整  - 
确定了需要实现的功能清单（AI Chat、Editor AI、AI Search、MCP）
---

## 5/11 下午：AI 模块完整实现
### EE Backend（21 个文件）  - 
​ee/ee.module.ts​ — 主模块，动态加载  - 
​ee/licence/​ — License 验证 + Feature Registry（4 层 plan）  - 
​ee/ai/ai-provider.service.ts​ — 封装 Vercel AI SDK v6（OpenAI/Gemini/Ollama）  - 
​ee/ai/ai-chat/​ — AI 聊天（CRUD + SSE 流 + 20 个 Tool Calls）  - 
​ee/ai/ai-generate/​ — 编辑器 AI（9 操作 + 3 语气 + 12 语言）  - 
​ee/ai/ai-answers/​ — RAG 语义搜索（pgvector）  - 
​ee/ai/processors/​ — BullMQ 队列处理器（embeddings 生成/删除）  - 
​ee/mcp/​ — MCP Server（JSON-RPC 2.0，20 工具）
### 踩坑：AI SDK v6 类型系统  - 
​CoreMessage​ → ModelMessage​  - 
​chunk.textDelta​ → chunk.text​  - 
​chunk.args​ → chunk.input​  - 
​chunk.result​ → chunk.output​  - 
​usage.promptTokens​ → usage.inputTokens​  - 
​tool()​ → dynamicTool()​  - 
​parameters​ → inputSchema​
### 最终编译通过  - 
418 个文件 SWC 编译通过  - 
所有 API 端点注册正确  - 
DeepSeek API 配置完成（deepseek-v4-pro/flash）
---

## 5/12 全天：功能完善 & Bug 修复
### 单词复习算法（3 轮迭代）  - 
第 1 版：保留 kaoyan-english 原始算法（间隔 [1,3,7]）  - 
第 2 版：改为 [7,30,90]，Round 2 只给不认识词  - 
第 3 版：修复分类映射（不认识→还没学习）  - 
新增：点击后自动跳转下一词（不需要手动点"下一词"）
### 思维导图（5/11 完成，5/12 图标误删恢复）  - 
Markmap 基于 Markdown 渲染  - 
Ctrl+M 选中文字转公式（7 个入口全部加了 $ 剥离）  - 
深色模式开关（Docmost 已有 CSS，只缺按钮——加到侧边栏）
### 子页面索引 —— 最大坑
从 5/11 持续到 5/12，反复尝试了 6 种方案才解决
尝试过的方案：  - 
❌ 数据库手动加 Subpages 块 → yDoc 覆盖  - 
❌ 清 yDoc → 编辑保存后复现  - 
❌ 后端 PageService.create 自动添加 → 并发竞态重复  - 
❌ AutoPageChildren 前端组件 → 和原生 Subpages 冲突  - 
❌ PL/pgSQL 全量去重 → yDoc 再次复现  - 
✅ persistence.extension.ts onStoreDocument 去重
```
// 最终方案：持久化层去重
const seen = new Set<string>();
tiptapJson.content = tiptapJson.content.filter(node => {
  const key = node.type + '|' + (node.attrs?.id || '');
  if (seen.has(key)) return false;
  seen.add(key);
  return true;
});

```

### Life Management 导入  - 
100+ 篇周记从 /mnt/d/life_management 导入 Docmost  - 
发现 152 个页面 position 只有单字符（'a','b'...）  - 
用 generateJitteredKeyBetween(null, null)​ 重新生成所有合法 key  - 
导入脚本后来被 git clean 删除
### SWC 编译问题（未彻底解决）  - 
@swc/core 1.15.33 vs 1.5.25 版本不兼容  - 
输出格式差异导致循环依赖错误  - 
最终方案：后端用原始 dist，不改后端代码时直接 node dist/main.js​  - 
新后端功能用独立 tsx cron 脚本
### 替代项目调研
克隆了 Outline、AFFiNE、AppFlowy 做对比：OutlineAFFiNEAppFlowy技术栈React+TS+YjsRust+TSDart/FlutterIssues62611950迁移难度低（同栈）中高（重写）数学公式内置 ✅无无
结论：如果换项目选 Outline，当前继续用 Docmost。
### 其他修复  - 
端口：3000→6006（后端），5173→6007（前端）  - 
​nest build​ 不可用，后端 dist 从 /mnt/d 复制  - 
项目路径：从 /mnt/d/study/docmost 迁到 ~/docmost（WSL 原生，快 10 倍+）  - 
GitHub 仓库：RexWeizuo/premaster  - 
全局记忆：GitHub 账号跨项目存储  - 
README 多次更新
---

## 杂谈 — 2026/5/12 Claude Code 分析
### 对 Docmost 的最终判断
Docmost 问题太多，一个个改不如找更稳定的开源项目。但 Outline 的 BSL 协议是隐患。
当前策略：继续用 Docmost + Outline 备用方案。
### Yjs CRDT 持久化原理
​onLoadDocument​ 从 DB 读 ydoc/content JSON → 转为 Yjs Document → 编辑器修改 → onStoreDocument​ 把 Yjs Document 转回 TipTap JSON 存 DB → TiptapTransformer​ 是转换桥梁。重复 Bug 出在没有去重保护。
### 开发效率问题  - 
花最多时间修 Bug 而非开发新功能（子页面索引几乎占一整天）  - 
​/mnt/d/​ 跨文件系统慢（几十倍差距），已解决  - 
后端编译环境脆弱，依赖特定 SWC 版本  - 
前端 HMR 秒级生效，后端需要杀进程重启  - 
​kill -9 $(lsof -ti:6006)​ 是日常操作
### 工具选择反思  - 
Vercel AI SDK v6 类型系统和文档差距大  - 
NestJS + SWC 的编译链不够稳定  - 
PostgreSQL + pgvector 是 AI Search 的好方案  - 
BullMQ 队列用于异步任务（embeddings 生成）是正确的  - 
TipTap + Yjs 的块编辑器方向对，但 Docmost 的实现有 bug
### 本周评分  - 
学习深度: ⭐⭐（大量时间在修 Bug）  - 
身体健康: ⭐⭐⭐  - 
心理状态: ⭐⭐（Docmost 的 Bug 消耗耐心——尤其是子页面索引）
---

## 给开发小白的经验总结
你只有前后端皮毛 + AI 略懂，但五月你做了什么？用 Claude Code 写了完整的 AI 后端（21 个文件）、改了一个开源项目、调了数据库、修了 Yjs 持久化 Bug。以下是给你自己的经验。
### 1. AI 写代码不是"AI 帮你写"，是"你指挥 AI 写"
五月最大的误区：以为 AI 能自己搞定一切。实际上：  - 
AI 写了 21 个 AI 模块文件，但类型错误来回修了 5 轮  - 
AI 给的代码 90% 正确，但剩下 10% 你不检查就崩  - 
你的价值不在写代码，在于知道要什么、能看懂对错、能把 Bug 定位到根因
记住：你是导演，AI 是演员。导演不需要会背台词，但必须懂剧本。
### 2. 花时间选对工具，比花时间修 Bug 重要一万倍
Docmost 的经验教训：  - 
子页面索引修了一整天 → 因为 Docmost 的 Yjs 持久化有根本 bug  - 
SWC 编译反复失败 → 因为版本兼容问题你根本无法解决  - 
如果当初花 1 小时调研替代方案，可能省下 8 小时的 Bug 修复时间
以后做新项目时，先花 30 分钟搜一下有没有更成熟的开源方案。 不要直接开干。
### 3. 数据库操作要小心——你改的东西会被覆盖
你的操作流程经常是：psql → UPDATE → 好像修好了 → 过一会儿又坏了​
问题在于：你直接改数据库，但 Docmost 的 Yjs 协作层会从内存中覆盖你的修改。
规则：  - 
前端显示的 Bug → 优先从前端或后端逻辑修，不要直接改数据库  - 
如果必须改数据库 → 同时清掉 yDoc 字段 + 重启服务  - 
改完数据库一定要验证持久化（刷新、编辑、再刷新）
### 4. 跨文件系统（/mnt/d/）在 WSL 里慢 40 倍
你经历过：node dist/main.js​ 在 /mnt/d/​ 启动要 2 分钟，在 ~/​ 只要 2 秒。
规则：WSL 里所有代码项目放 ~/​ 下，不要放 /mnt/d/​。Git 仓库克隆到 ~/projects/​，npm/pnpm install 在 ~/​ 跑。
### 5. 前端改完不动？先硬刷新
你遇到过的：改了代码，页面没变化。原因可能是：  - 
浏览器缓存（Ctrl+Shift+R 强制刷新）  - 
Vite 没热更新（重启 pnpm dev​）  - 
数据库里 yDoc 缓存了旧内容（清 yDoc）
排查顺序：硬刷新 → 重启前端 → 检查数据库 → 重启后端
### 6. 你的技术栈已经够用了
五月你接触的东西：  - 
后端：NestJS, PostgreSQL, Redis, BullMQ, pgvector  - 
前端：React, TipTap, Vite, Mantine UI  - 
AI：Vercel AI SDK, DeepSeek API, RAG, embeddings  - 
工具：WSL, Git, pnpm, Docker, psql, curl  - 
协议：SSE, JSON-RPC (MCP), CRDT (Yjs)
一个只有皮毛基础的小白，一个月碰了这么多东西。不需要什么都深究——知道每个东西做什么用、怎么排查问题就够了。
### 7. 下次开发前问自己三个问题
在让 Claude Code 写代码之前：  - 
这个功能是不是已经有人做过了？（先搜开源方案，不要重复造轮子）  - 
我选的这个基础项目稳定吗？（看 GitHub Issues 数量、最近 commit、社区活跃度）  - 
我能独立验证 AI 写的代码吗？（如果不确定，先让 AI 解释逻辑，再说"实现"）
### 8. 你已经有能力做独立开发了
五月你完成的事情：  - 
从零搭建了一个完整 AI 系统（前端 + 后端 + 数据库）  - 
修改了一个开源项目的底层持久化逻辑  - 
用 cron 脚本实现了 AI 日报自动生成  - 
调研对比了 4 个开源项目并给出结论  - 
把 100+ 篇周记从 Notion 迁移到自己搭建的系统
大部分计算机专业的学生四年都没做过这些。
下一步不是学更多技术，而是把已有东西做成产品——让这个系统真正能用起来。学数学学英语的目标是考研上岸，开发系统的目标是让学习更高效。不要搞反了。
---

## 5/13：五年规划 & 项目方向确认
### 核心定位确立
Docmost 项目的最终目标是个人生活操作系统：记录行为 → AI 自动分析 → 每日/每周评估 → 对标五年规划。
关键决策：  - 
Docmost → Outline：Docmost Bug 太多，Outline 同栈（React+TS+Yjs），62 Issues，BSL 个人使用无影响。自定义模块（AI、单词复习、思维导图、手写）需要在 Outline 上重做  - 
策略：只搭骨架不雕花纹。考研期间系统能用就行，进度赶上后再搞 Agent
### 五年规划
想成为：高效学习、突破舒适圈、快速切入新领域、迅速抓重点的人。
路径：考研上岸（400分：政70+英80+数一125+408 125）→ 读研（副业养自己）→ 进 DeepSeek 类公司 / 副业变主线
考研院校：浙大、南大、中科院、清华、北大、上交、复旦、中科大、哈工大、华科、西交、电子科大、东南、武大、北航、中大、同济共 17 所，分三档跟踪。10 月根据学习情况确定最终 2-3 所。已建立每月信息收集机制。
技术方向：世界模型（最看好）> 具身智能+AI+物联网 > LLM 优化
健康：腰突康复 + 健康作息 + 投篮练习
### 当前优先级
```
现在 → 讨论五年规划 + 迁移到 Outline + 搭记录骨架
1-2月 → 赶考研进度，每天记录行为，AI 自动评估，不开发新功能
进度赶上后 → Agent 开发 + 技术学习
下半年 → 简历/面试

```

副业方向、五年规划硬指标等一两个月后完善。
### 已有工作经验（一两个月后整理入简历）
AI 销售 Agent、AI 策划、AI 医疗顾问（开处方）、AI 地址识别、AI 报表生成、AI CRM 操作
### 补充 5/12 内容
5/12 还做了：  - 
端口切换：3000→6006（后端），5173→6007（前端）  - 
​nest build​ 不可用，直接 node dist/main.js​ 启动  - 
项目路径从 /mnt/d/study/docmost​ 迁到 ~/docmost​（WSL 原生，快 10 倍+）  - 
GitHub 仓库：RexWeizuo/premaster