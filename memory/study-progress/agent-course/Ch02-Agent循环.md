---
name: Ch02-Agent循环
description: Ch.02 The Agent Loop 理论考试+代码实现
metadata:
  type: project
  section: Ch.02
  date: 2026-06-09
  status: 完成
  learning_phase: 完成
---

## 学习时间线

- 读讲义（06-08 自读，06-09 上午复习）
- 06-09：五题理论考试 + 评估
- 06-09：Loop 代码实现 + 四轮 bug 修复

## 理论考试

| Q# | 主题 | 得分 | 关键纠正 |
|----|------|------|---------|
| 1 | 五阶段在量化场景的映射 | ★★★ | 模型每步决定还需要什么，不是一次规划所有调用 |
| 2 | model-driven vs final_answer | ★★★★★ | 都是模型主动停；final_answer 保证结构化输出 |
| 3 | doom loop 检测原理 | ★★★★★ | 三次相同调用→中断；参数变但无进展需进度追踪 |
| 4 | 错误处理三次失败 | ★★★★ | compatible model = 换物理模型(Opus→Sonnet)，非换请求模式 |
| 5 | step boundary 能力 | ★★★★★ | 权限+审批在Act前挂（不可逆）；其他三个Act后挂 |

## 代码实现

**文件**：
- `src/quant_agent/loop.py`：五阶段循环
- `src/quant_agent/tools/registry.py`：工具注册表+final_answer+预留位
- `main.py`：入口

**已实现的 Ch.02 能力**：

| 能力 | 实现位置 | 状态 |
|------|---------|------|
| Model-driven stop | `if not msg.tool_calls: return` | ✅ |
| final_answer stop | 注册 `final_answer` 工具，调用即返回 | ✅ |
| Step cap | `for step in range(MAX_STEPS)` | ✅ |
| Doom loop 检测 | 3 次相同 name+args → 中断 | ✅ |
| Errors as turns | JSON 控制字符清洗 + 错误作为 tool_result | ✅ |
| Observability | `StepTrace` dataclass + verbose 打印 | ✅ |

**待实现**：token/cost cap、grace call、abort token、并发工具调用、human approval

## Bug 修复记录

| Bug | 现象 | 根因 | 修复 |
|-----|------|------|------|
| Return path | model-driven stop 标为 PARTIAL | `break` 落入 hard-cap return | 改为 `return` |
| Doom loop | get_price 连调3次失败 | 东方财富 TCP 拒连接 | 切新浪 API |
| 东方财富封 IP | Connection aborted | 频繁请求触发反爬 | 换新浪 `hq.sinajs.cn` |
| JSON 控制字符 | `json.loads` 失败 | 模型输出含 `\x00-\x1f` | 正则清洗后重试 |
| GBK 编码 | 新浪返回乱码 | requests 默认 UTF-8 | `resp.encoding = "gbk"` |

## 最终结果

```
Step 1: CONTINUE | get_price    |  778 tk
Step 2: STOP     | final_answer | 1385 tk | final_answer
✅ 2 steps, 2163 tokens
茅台 1256元，跌 0.55%，成交 350亿
```

## 关联金融知识

见 [金融知识.md](金融知识.md) § Ch.02
