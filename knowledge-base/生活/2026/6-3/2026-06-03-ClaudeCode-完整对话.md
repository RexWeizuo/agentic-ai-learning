---
title: 2026-06-03 Claude Code 对话
date: 2026-06-03
---

# 2026-06-03 Claude Code 对话

## OCR 批量处理 + 模型策略

**用户**：记住不要用我指定以外的qwen模型 如果我指定的模型免费额度都没有了就直接汇报 用qwen3.6-plus模型ocr...所有解析文件并且放到项目的相应位置 apikey是sk-4880953c556543bfa87a8d45f91aa95c

**AI**：写入 memory/qwen-model-policy.md（规则：只使用用户指定模型，额度耗尽直接汇报），测试 qwen3.6-plus OCR 单页效果——LaTeX 数学公式识别优秀

**用户**：还有线代和概率论的解析

**AI**：统计线代 6PDF/43页 + 概统 6PDF/40页，写脚本批量 OCR，修复 Unicode 字符问题后全部成功

## GitHub 同步

**用户**：我的github连不上是因为什么key过期了来着

**AI**：检查 remote 中的 GitHub PAT (`ghp_SYn1gHf...`)，dry-run push 成功，token 未失效

**用户**：同步到github

**AI**：33 files changed, +6706/-133, push `7060a71` → GitHub
