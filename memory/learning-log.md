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

### 2026-05-27 — 数学学习轨道启动：OCR管线+双标签错题体系+第六章预备

- 确定数学学习流程（含手写OCR环节），与408流程对齐
- OneNote→PDF→PNG→qwen3.5-omni OCR管线验证：20页全部成功，约4万tokens
- 第五章习题AI批改发现3道错题，建立了**双标签体系**（知识点标签+错误类型标签）
- 错题重做节奏确定：次日小节重做 + 一周后章节重做
- 用户决定自行批改手写题（OCR有误识别风险），AI负责标签+重做排程
- 第六章二重积分讲义通读，15道习题待做
- 第五章复习提问已准备（6题覆盖全部6节）

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
- [[recording-three-tier]] — 三级记录体系：日志(时间线) → study-progress简短版(扫描) → study-progress详细版(追细节)
- [[dma-two-requests]] — DMA 有两种请求：传送期间请求总线控制权(HRQ/HLDA)，传完请求中断通知CPU；两者不可混淆
- [[cycle-stealing-vs-interrupt]] — 周期挪用偷总线(CPU内部状态不变，随时可插入)，中断偷CPU执行流(必须指令边界保存现场)
- [[socratic-in-file]] — Socratic 题目预写入 study-progress，学生离线作答，AI 批改追加，自动归档减少来回交互
- [[io-cost-model]] — I/O 方式选择不是看"谁先进"而是算"开销/数据间隔"比值；高频不一定升级中断/DMA，独占查询零切换延迟可能最优
- [[dma-o1-vs-on]] — DMA 的真正优势是 CPU 开销与数据量解耦(O(1))，仅与块数相关；定时查询和中断开销随数据率线性增长(O(n))
- [[io-calc-two-methods]] — I/O 计算题每题都有两种等价视角：比例法(每次耗时/间隔)和按秒算(每秒总耗时/1s)，或时间对比法和频率法

### 2026-05-28 — 第五章复习收尾 + OS 第四章全面推进（4.1-4.4 讲义+Socratic+Quiz）

- 第五章 6 道 Socratic 复习题全部通过（Q5 AC−B²=0 需补方法），错题重做推迟到周末
- **三级记录体系确立**：questions/(时间线) → study-progress 简短版(表格概览) → study-progress 详细版(完整问答)，AI 按任务选读层级
- **Socratic 工作流变更**：题目预写入 study-progress → 学生文件中作答 → AI 批改追加反馈
- **回答时限机制**写入学习方法：每批 Socratic 标注预计时间 + Cron 提醒
- OS 第四章全面推进：4.1 完成 + 4.2-4.4 讲义整理 + 第四章 Quiz OCR（7图→48题）

### 2026-05-29 — 4.2 Socratic 全部完成 + I/O 开销模型核心突破 + Reference 同步

- **4.2 Socratic 13 题全部完成**（5概念+3例题+5真题）：12/13 正确，仅 Q9 计算差一倍
- **关键突破**：
  - I/O 方式选择 = 开销模型（单次开销/数据间隔），不是"高频就该升级"
  - DMA 的真正优势：CPU 开销与数据量解耦(O(1))，定时查询/中断是 O(n)
  - 三个 4% 放到同一 40MB/s 下→定时查询 80% vs DMA 4%，差距显现
  - 每种计算题都有两种等价算法（比例法/按秒算，时间对比法/频率法）
- 五种 Reference 开源项目 fork 到 GitHub (RexWeizuo)，remote 配置 origin→fork / upstream→原始
- **OS 第四章全面推进**：
  - 4.1 完成（7 题 Socratic，Q1 字符/块混淆 + Q5 x86 编址搞反）
  - 4.2 讲义整理完成，12 道 Socratic 已写入（5概念+3例题+5真题），Q1-Q5 已答已批
  - 4.3/4.4 讲义整理完成
  - 4.5 待整理
  - 第四章 Quiz OCR 完成（7图→48题，qwen3.5-omni-flash，~13.6K tokens）

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
