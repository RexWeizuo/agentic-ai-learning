---
name: qwen-image-model
description: 图片处理使用 qwen3.6-plus 模型，免费额度有限
metadata:
  type: project
  date: 2026-06-06
---

## 图片处理模型配置

当遇到图片任务（用户丢图片、任务涉及图片识别/OCR/图片理解等），使用 **qwen3.6-plus** 调用，不使用默认的 deepseek-v4-pro。

## API Key

`sk-4880953c556543bfa87a8d45f91aa95c`

## 可用模型（有免费额度，按优先级）

1. **qwen3.6-plus**（首选）
2. **qwen3.7-plus**（备用）
3. **qwen3.5-plus**（最后备用）

## 重要规则

- **只能用这三个模型**，因为只有它们有免费额度
- **一旦三个模型的额度全部用尽**，立刻提醒用户，**不要尝试任何其他模型或方案**
- 非图片任务仍使用默认模型（deepseek-v4-pro）

## 关联

- [[graduate-exam-agent-v1]] — 考研 agent 项目
