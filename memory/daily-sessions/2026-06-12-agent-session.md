---
date: 2026-06-12
day: 周五
type: Agent Session 概括
---

# 2026-06-12 Agent Session

## 产出总览

| 维度 | 内容 |
|------|------|
| 课程进度 | Ch.01-02 代码全量走读 |
| 项目 | 日志增强（执行全记录）+ get_kline 工具实现 |
| 金融知识 | K线结构（开/高/低/收/量） |

## 代码走读（逐行教学）

### main.py
- `from __future__ import annotations`：类型注解延迟求值
- `os.environ.get("KEY")`：防止 git push 泄露 API key
- `sys.exit(1)`：非零退出码 = 异常终止
- `result.get('partial')` vs `result['total_steps']`：不确定存在用 .get()，确定存在用 []
- `if __name__ == "__main__"`：import 时不执行 main()

### loop.py StepTrace
- `@dataclass`：自动生成 __init__
- `field(default_factory=list)`：防止可变默认值共享（`= []` 会所有实例共享同一列表）
- `field(default_factory=lambda: datetime.now())`：延迟求值，每次创建实例重新算
- StepTrace 是给人看的（observability），不是给模型看的
- `final_text` 跨步骤，`recent_calls` 跨步骤——不在 StepTrace 里

### loop.py 循环体
- `messages` 四种角色：system/user/assistant/tool
- 每次调 API 都带完整 messages（无状态模型）
- tool_calls 必须写回 messages，否则模型失忆
- `tool_map.get()` vs `tool_map[]`：不存在的工具名 → None vs KeyError
- `**args` 解包：`func(**{"a":1})` = `func(a=1)`
- `choices` 是候选回复列表，`[0]` 取第一个
- `partial` 标记只在 step cap 耗尽时出现
- verbose 模式当前硬编码问茅台，需改进

### 日志增强
- `_log()`：同时输出到 stdout 和 log_lines
- `_save_log()`：flush 到 `logs/run-YYYYMMDD-HHMMSS.md`
- `_log_step()`：格式化步骤摘要
- `_log_messages()`：完整 messages 数组状态
- 每条 return 路径前都记录

### get_kline 工具
- 新浪 K 线 API：`CN_MarketData.getKLineData`
- scale 参数：5/15/30/60/240 分钟（D 不支持，用 240 代替日线）
- 返回 `{trend: {...}, bars: [{time,open,high,low,close,volume},...]}`

## 金融知识
- K 线一根 = 时间段内四个价格（开/高/低/收）+ 成交量
- 多根 K 线排列 = 走势图，agent 可判断趋势

## 待完成
- kline 函数逐行问答（已提问 7 题，待答）
- get_kline 当前仅 A 股，加密货币和美股待补

完整对话见：`knowledge-base/生活/2026/2026-06-12-Agent对话.md`
