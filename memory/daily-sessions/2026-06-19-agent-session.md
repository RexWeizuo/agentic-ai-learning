---
date: 2026-06-19
day: 周五
type: Agent Session 概括
---

# 2026-06-19 Agent Session — tool_call_id 机制深挖 + Ch.01 Provider Knobs 对照

## 产出总览

| 维度 | 内容 |
|------|------|
| 课程进度 | Ch.01 收尾：tool_call_id 跨 turn 行为 + Provider-specific knobs 六项 |
| 概念深挖 | tool_call_id 不是微信好友 ID，是快递单号；跨 turn 靠 messages 数组 |
| 代码对照 | Ch.01 六个 provider 开关逐一检查 life-game 代码——全部未使用 |

## tool_call_id 机制澄清

**学生纠正了上次的类比**："tool_call_id 应该更像是微信人 id 吧，区分谁给我回的消息。"

**精确化**：tool_call_id 是**快递单号**。模型同时下三单，每单一个单号，到了靠单号区分哪个是汉堡哪个是奶茶。但每次调用都换新 id——不是持久标识符。

**核心澄清**：模型执行复杂多步任务时，**不看 id 查历史，看 messages 数组**。

三段式任务示例（get_status → get_npc → final_answer）：

```
Turn 1: tool_call id=call_A → get_status()  → result: {hp:180, INT:10}
Turn 2: tool_call id=call_B → get_npc("凡")  → result: {level:52}    ← 新 id
Turn 3: tool_call id=call_C → final_answer()                          ← 又一个新 id
```

Turn 3 的模型怎么知道 hp=180 和凡 Lv.52？不是靠 id。是靠 **messages 数组**——所有历史 tool_call + tool_result 全堆在上下文里，模型每轮读整个数组。

**结论**：tool_call_id 的职责只有一个——当前 turn 内把结果和请求配对。跨 turn 不管。

| 错误理解 | 正确理解 |
|---------|---------|
| 三人回微信，靠备注名区分 | 同一 turn 内，靠单号区分并发调用的返回值 |
| 跨 turn 用 id 追溯历史 | 跨 turn 靠 messages 数组 |

## RESULT_STASH 持久化讨论

**学生质疑**："RESULT_STASH 不用保存吗？不是有 log 保存所有的完整信息吗？agent 下次要检索这一块的内容但是 RESULT_STASH 里面没有了怎么办？"

**三分层澄清**：

| 层 | 职责 | 生命周期 |
|----|------|---------|
| RESULT_STASH | 当前会话内，模型临时取回被截断的原始结果 | 一次 fetch 或会话结束 |
| logs/ | 所有对话的完整记录，给人看和调试 | 永久磁盘 |
| write_memory | 模型认定的长期有价值知识 | 跨会话 curated |

**结论**：RESULT_STASH 解决的是"同一个 turn 内，结果太长被截断，模型需要完整数据才能回答"——不是"三天后查上次被截断的结果"。后者应走 write_memory（如果是知识）或重新调用原工具（如果是数据）。

**决策**：暂不持久化 stash。等 Ch.08 之后做多 agent 协作时再评估。

## Ch.01 Provider-specific Knobs 六项对照

**学生**（选中 course/01-function-calling.md Provider-specific knobs 段落）："这一段有没有用到"

**逐一对照 life-game 代码**：

| Knob | 状态 | 说明 |
|------|------|------|
| `tool_choice` | ❌ 未用 | 默认 auto，模型自己决定调不调工具 |
| parallel_tool_calls | ⚠️ 隐式兼容 | 没显式开关，但 for 循环能接住多个 tool_call |
| strict schema | ❌ 未用 | 靠手动 try/except JSON 防御（loop.py:207-215）|
| structured outputs | ❌ 未用 | 用 tool calls 不用 response_format，叙事文本不适合 JSON |
| hosted tools | ❌ 未用 | 全部 6 个工具自己写 handler |
| refusals | ❌ 未处理 | 模型拒答会被当普通文本返回，未特殊标记。Ch.18 才深入 |

**结论**：六项全部是生产环境才需要的开关。目前学习阶段最小可行循环，一个都没用是正常的——等 Ch.08+ 多 agent 协作和部署时，至少 4 个会自然出现。

## 关键概念

- **messages 数组是模型的唯一记忆**：不是 tool_call_id，不是数据库，是 messages 列表
- **快件单号 vs 通讯录**：tool_call_id 每次换新；跨 turn 追溯靠上下文累积
- **三层存储**：RESULT_STASH（临时缓存）、logs（调试记录）、write_memory（长期知识）各司其职
- **provider knobs 是生产开关**：学习阶段不碰，但要知道存在

完整对话见：`knowledge-base/生活/2026/2026-06-19-Agent对话.md`
