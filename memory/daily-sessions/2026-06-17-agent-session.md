---
date: 2026-06-17
day: 周三
type: Agent Session 概括
---

# 2026-06-17 Agent Session — Life Game 代码走读 + Ch.01 stash 缺口补全

## 产出总览

| 维度 | 内容 |
|------|------|
| 课程进度 | Ch.01-07 代码走读（game_engine.py 全量 + tools.py 全量 + loop.py 部分）|
| 新工具 | fetch_full_result（Ch.01 "大结果不内联" 缺口补全） |
| 设计讨论 | RESULT_STASH 分层（基础设施 vs 游戏层），fail-closed 默认值原理 |

## 代码走读

从昨天中断处继续，以苏格拉底问答方式走完：

### game_engine.py（全量 147 行）

**遗留四问解答**：
- `ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent` → 从 `game_engine.py` 上溯 5 级到项目根目录，但目前未被使用（死变量）
- `GAME_STATE = dict(INITIAL_STATE)` → 浅拷贝，保留出厂模板不被污染
- `_sync_derived()` → 派生值不复存原则：hp_max/mp_max/sp_max/exp_to_next 由属性+等级计算，不独立存储，避免数据不一致
- 初始属性 INT=10 最高、RES=4 最低 → 叙事与机制统一：穿越者靠智力生存，无魔法抗性

**NPC 系统**（57-71 行）：NPC_ROSTER（静态模板）+ social_links（动态好感度）= 关注点分离。`get_full_status()` 返回 `dict(GAME_STATE)` 防御性拷贝。

**排名引擎**（92-113 行）：`score = level × avg_attr × 0.5`，`pct` 封顶 95%（不可见天花板设计），当前穿越者 Lv.1 → 933/1000 (6.7%)。

**SYSTEM_PROMPT**（123-146 行）：Ch.04 稳定前缀，冻结在 messages[0]，Qwen 自动 KV 缓存。

### tools.py（全量 250→319 行）

**Tool 数据类**：5 个元数据 flag，4 个默认 False（fail-closed），仅 `open_world=True`。安全假设：不知道就按不安全的处理。

**build_tool 工厂**：Claude Code 源码模式，默认安全底子 + 按需覆盖。

**5→6 工具**：
| 工具 | read_only | idempotent | 要点 |
|------|-----------|------------|------|
| get_status | ✅ | ✅ | 代理层，委托 get_full_status() |
| get_npc | ✅ | ✅ | 精确查/全列两路，合并动态 social_link_level |
| get_ranking | ✅ | ✅ | 纯计算 |
| write_memory | ❌ | ❌ | Ch.07 安全过滤器 + 原子写入（mkstemp+os.replace） |
| fetch_full_result | ✅ | ❌ | **新增**，一次性取回被截断的完整结果 |
| final_answer | ✅ | ✅ | Ch.02 工具驱动停止 |

## Ch.01 缺口补全：result stash

**触发**：学生阅读 `course/01-function-calling.md`「Tool results have shape」段落，发现代码只做了截断（`_clip()`）但没做 "stash the full thing somewhere the model can ask for"。

**实现**（3 文件修改）：
- `tools.py`：新增 `RESULT_STASH` 字典 + `stash_result()` 函数 + `fetch_full_result` 工具（one-shot 取后即删）
- `loop.py`：`_clip()` 返回值从 `(text, was_clipped)` 扩展为 `(text, was_clipped, stash_id_or_none)`，超限时自动 stash
- `game_engine.py`：SYSTEM_PROMPT 新增 Rule 6，引导模型使用 fetch_full_result

**设计讨论**：为什么 RESULT_STASH 不放在 GAME_STATE？因为 GAME_STATE 是游戏语义层（属性/等级/NPC），RESULT_STASH 是基础设施层（上下文窗口管理），混在一起就是上帝对象。用内存字典而非文件是因为截断缓存在会话结束后无意义。

**验证**：6 工具注册 → stash_001 → 取回成功 → 二次取回返回 False（one-shot 正确）。

## 关键概念讲授

- **id 回环**：tool_call_id 让模型把 N 个并行调用的结果一一对应到请求，用"三人同时回微信"类比
- **原子写入**：`mkstemp` + `os.replace` 保证文件要么完整要么不变，永不出半截状态
- **提示注入防御**：write_memory 的黑名单过滤 `ignore previous`、`<system>` 等注入载荷
- **分层存储**：GAME_STATE（游戏层）≠ RESULT_STASH（设施层）≠ 文件持久化（硬盘层）

## 文件变更

```
workspace/life-game/src/tutor/
├── game_engine.py  # SYSTEM_PROMPT +Rule 6
├── tools.py        # +RESULT_STASH, +stash_result(), +fetch_full_result 工具（6 工具）
└── loop.py         # _clip() 扩展为 3 返回值
```

完整对话见：`knowledge-base/生活/2026/2026-06-17-Agent对话.md`
