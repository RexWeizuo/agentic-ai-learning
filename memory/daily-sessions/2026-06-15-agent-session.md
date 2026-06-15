---
date: 2026-06-15
day: 周一
type: Agent Session 概括
---

# 2026-06-15 Agent Session — 大重构日

## 产出总览

| 维度 | 内容 |
|------|------|
| 课程进度 | Ch.03 重做（Claude Code 对齐）→ Ch.04-07 全章学完 + 实现 |
| 项目 | quant-agent 修 provenance → life-game 全架构搭建 |
| 记忆 | 实现标准写入记忆 |

## Ch.03 重做（对齐 Claude Code）

**删除**：`_hook_add_provenance`、`model_result` 剥离、`_provenance` 概念
**采用 Claude Code 模式**：
- build_tool 工厂：fail-closed 默认值（全 False → 必须显式覆盖）
- 错误分类：异常类型优先（ConnectionError→recoverable, ValueError→fatal）
- 错误码：1-7 数字码
- 钩子系统保留骨架（PRE_HOOKS/POST_HOOKS 空列表），预留位置

## Ch.04 — 提示词、上下文与缓存

**核心概念全过**：
- KV Cache：注意力机制的 Key/Value 被 Qwen 缓存，前缀相同跳过重算
- OpenAI vs Anthropic 缓存差异：自动 vs 手动标记断点
- 四块滑动窗口：system + 最近 3 条消息各打 cache_control
- 缓存杀手 10 种：Date.now()、工具注册表变化、非确定性排序、背景写入等
- 用户代码自检：全部安全，无缓存破坏者
- 缓存命中率 = cache_read / (cache_read + cache_creation + input)

**代码改动**：无。Qwen 自动缓存，prefix 天然稳定。

## Ch.05 — 短期记忆

**三个视图**：审计日志（logs/run-*.md ✅）、紧凑操作转录（messages，需压缩）、工作记忆（TODO）

**已实现**：
- `_clip_result()`：2000 字符截断 + 可见省略标记
- `_dedupe_tool_results()`：latest-wins 去重，跳过 open_world 工具
- 去重标记注入 messages（`_tool_name`, `_tool_args`）

**TODO stubs**：非对称缩减、摘要（需便宜模型）、工作记忆、压缩触发

## Ch.06 — 长期召回

**核心概念全过**：
- 四种存储形态：markdown、SQLite+FTS、向量索引、外部 provider
- 三种检索范式：向量搜索、全文搜索、策划知识
- RRF（Reciprocal Rank Fusion）：两份排序结果融合
- 三个注入位置：前缀（冻结）、工具结果（实时）、预取（会话开始）
- 渐进式揭示：技能索引只载入摘要，按需 `skill_view(name)` 加载全文
- 记忆命名空间四轴：用户/项目/agent/环境

**已实现**：
- `_load_memory_files()`：从 `memory/` 加载策划知识到 system prompt 前缀
- 前端 matter 剥离（`---...---`）
- `§` 定界符标记文件来源

## Ch.07 — 记忆写入和策展

**核心概念全过**：
- 三种写入模式：内联、后台策展、用户确认
- 安全过滤器：拦截注入模式（"ignore previous instructions" 等）+ API key 检测
- 原子写入：tmp-file + rename（POSIX 原子操作）
- 冲突解决：supersede/merge/drop
- 策展生命周期：Active → Stale(30天) → Archived(90天)
- 后台回顾：成功回合后、限速、限制工具集、用便宜模型
- 隐私分类：public/internal/pii/secret

**已实现**：
- `write_memory` 工具：内联写入 + 安全过滤 + 原子写入
- `_is_safe_memory_candidate()`：注入检测 + 密钥检测
- 后台策展 + 用户确认 stub

## Life Game 项目搭建

**架构**：`workspace/life-game/`，uv 管理，Qwen 驱动

**实现章节映射**：

| Ch | 文件 | 实现 |
|----|------|------|
| Ch.01 | tools.py | 5 工具 schema |
| Ch.02 | loop.py | 五阶段循环 + 4 停止条件 + doom loop |
| Ch.03 | tools.py + loop.py | build_tool + 元数据 + 错误信封 + 钩子 |
| Ch.04 | game_engine.py | SYSTEM_PROMPT 稳定前缀 |
| Ch.05 | loop.py | _clip + _dedupe |
| Ch.06 | data_loader.py | 加载 study-progress 文件 |
| Ch.07 | tools.py | write_memory + 安全过滤 + 原子写入 |

**工具集**：get_progress / get_daily_report / get_ranking / write_memory / final_answer

**数据加载验证**：
- 408-OS: 73.7%, 19 concepts
- 301-数学: 71.4%, 7 concepts
- Agent: 93.6%, 25 concepts
- 排名: 666/1000 (33.3%), 薪资: 7400 元/月

**未跑通**：Qwen 免费额度全部耗尽，需充值或换模型。

## 模型额度状态
- qwen-max ✅ 耗尽
- qwen3.7-max ✅ 耗尽
- qwen3.7-max-2026-06-08 ✅ 耗尽
- qwen3.7-max-2026-05-20 ✅ 耗尽
- 剩余：2026-05-17、preview、qwen-plus

完整对话见：`knowledge-base/生活/2026/2026-06-15-Agent对话.md`
