---
name: siyuan-knowledge-base
description: 思源笔记考研知识库结构、数据路径和格式说明
metadata:
  type: reference
---

## SiYuan 考研知识库

### 路径
- **主数据目录（正式内容）**: `C:\Users\scott\SiYuan\data\` — `.sy` JSON 树文件，Agent 直接读这里
- **导出 markdown**: `D:\siyuan-export\`（快照导出，方便人工浏览）
- **应用安装**: `D:\tool\siyuan\`

### 笔记本 ID → 科目映射

| 笔记本 ID | 科目代码 | 内容 |
|---|---|---|
| `20260515105227-8myszzy` | 201 (英语) | A–Z 词汇，每字母一个文档，含单词+音标+释义 |
| `20260515155301-wcdv2ip` | 301 (数学) | 三大计算（极限/导数/积分）、高等数学、概率统计 |
| `20260521212645-teyk23o` | 301 (数学) | 概率统计、线性代数、高等数学 |
| `20260515155307-blvk8ai` | 408 (计算机) | 操作系统（OS概述/内存管理/IO管理/死锁） |
| `20260515105258-6yhxbci` | — (生活) | 2024/2025/2026 日记，Agent 暂不索引 |
| `20260515105227-8myszzy.bak` | — | 备份，忽略 |

### .sy 文件格式
- 每个 `.sy` 文件是一个 JSON 树
- 节点类型: `NodeDocument` → `NodeHeading`(H1-H6) → `NodeParagraph` / `NodeList` → `NodeListItem` → `NodeText`(含 `Data` 字段) / `NodeTextMark`(含 `TextMarkTextContent`)
- 文档元信息: `Properties.title`, `Properties.updated`
- 递归遍历 `Children` 数组可提取全部纯文本

### Agent 集成策略
- Agent 直接读取 `C:\Users\scott\SiYuan\data\` 下的 `.sy` 文件（实时数据）
- 通过 `NOTEBOOK_MAP` 将笔记本 ID 映射到科目（201/301/408）
- Agent 不需要做外部搜索——知识点和题库都在本地
- 核心任务：基于已有内容做检索、出题、进度追踪、记忆复习
- 思源是 source of truth，Agent 是交互层

### 数据同步
- **同步脚本**: `workspace/graduate-exam-agent/export_siyuan.py`
- **同步方式**: 运行 `python export_siyuan.py` 即可从 SiYuan 实况重新导出到 `data/`
- **导出原理**: 遍历每个笔记本的顶层 `.sy` 文件 + 对应子目录下的 block `.sy` 文件，合并为 markdown
- **输出**: `data/301/*.md` + `data/408/*.md` + `data/manifest.json`
- **注意**: 同步是单向的（SiYuan → project data），不要在 project data 中编辑——修改应该在 SiYuan 中进行，然后重新同步
- **缺失内容**: 后续由另一个 agent 直接写入 SiYuan，然后重新运行同步脚本
