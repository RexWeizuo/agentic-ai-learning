---
date: 2026-06-09
day: 周二
type: Agent Session 概括
---

# 2026-06-09 Agent Session

## 产出总览

| 维度 | 内容 |
|------|------|
| 课程进度 | Ch.01 深挖 + Ch.02 理论/考试/代码实现 |
| 项目 | Agent loop 跑通：`get_price` → 模型分析 → `final_answer` |
| 金融知识 | 夏普比率、最大回撤 |

## Ch.01 深挖

- `input` vs `arguments`：都是"工具参数"而非用户输入，不同 provider 不同名字
- Adapter 模式：薄封装层统一 provider 差异，换模型只改一行
- OpenCode `Tool.define`：类型化生命周期追踪每次调用
- Hermes `ToolEntry`：schema + handler + 大小限制 + 错误分类（可恢复/致命）
- OpenClaw/Paperclip："任何遵守 name+schema+result 合同的都是工具"

## Ch.02 理论与实践

### 五题回答评估
1. ⚠️ Five-stage mapping to quant scenario — direction right, missed multi-step detail
2. ✅ model-driven vs final_answer distinction
3. ✅ doom loop detection rationale
4. ⚠️ compatible model = different physical model, not different request mode
5. ✅ step boundary — permission + human approval for real-money trading

### Loop 代码实现
- `loop.py`：五阶段循环 + 4 种停止条件 + doom loop 检测 + 错误清洗
- `registry.py`：工具注册表 + final_answer + 预留位（get_kline, get_financials 等）
- `main.py`：入口，API key 检查，demo 问题

### Bug 修复历程
1. **Return path bug**：model-driven stop break 后落入 hard-cap return → 改为直接 return
2. **Doom loop 实现**：3 次相同 tool_name + args → 中断（Ch.02 实战）
3. **东方财富被墙**：TCP 层面拒连接 → 切换到新浪 API（GBK 编码）
4. **JSON 控制字符**：模型输出含非法控制字符 → 正则清洗后重试

### 最终结果
```
Step 1: get_price → 茅台 1256元，跌 0.55%，成交 350亿
Step 2: final_answer → 完整分析 → 干净停止
2 steps, 2163 tokens
```

## 金融知识
- 夏普比率：(收益-无风险利率)/波动率，衡量"每冒多少风险赚多少"
- 最大回撤：峰顶到谷底的最大跌幅，比收益率更影响"能否拿住"

完整对话见：`knowledge-base/生活/2026/2026-06-09-完整对话.md`
