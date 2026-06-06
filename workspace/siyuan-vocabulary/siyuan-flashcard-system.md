# SiYuan 闪卡记忆系统

## 概述

SiYuan 是一个本地优先的知识管理工具，内置基于 **间隔重复（Spaced Repetition）** 的闪卡系统。本文档描述其闪卡系统的架构、API、工作流程及考研英语词汇闪卡的实现。

---

## 1. 系统架构

### 1.1 核心概念层级

```
笔记本 (Notebook)
 └─ 文档 (Document)
     └─ 内容块 (Block)
         ├─ 标题块 (Heading Block) → h1/h2/h3...
         ├─ 列表块 (List Block)
         ├─ 段落块 (Paragraph Block)
         └─ ...
```

**闪卡的最小单位是内容块（Block）**，通常是一个标题块（`## word`）。

### 1.2 闪卡类型

| 类型 | 说明 | 适用场景 |
|---|---|---|
| **标准卡** | 正面 = 块标题，背面 = 块下所有子内容 | 词汇释义、概念记忆 |
| **挖空卡 (Cloze)** | 用 `==hidden text==` 标记需隐藏的内容 | 释义挖空、填空测试 |

### 1.3 调度算法

SiYuan 使用 **FSRS (Free Spaced Repetition Scheduler)** 算法，相比传统 Ebbinghaus 固定间隔更精准：

- 根据每张卡的历史表现（复习次数、遗忘次数、响应时间）动态调整间隔
- 卡片状态：`New(0)` → `Learning(1)` → `Review(2)` → `Relearning(3)`
- 每次复习后可选择：`Again`（重来）、`Hard`、`Good`、`Easy`

---

## 2. 卡包 (Deck) 管理

### 2.1 数据结构

```json
{
  "id": "20260517141214-z4t7t8q",
  "name": "201词汇-释义挖空",
  "size": 3766,
  "created": "2026-05-17 14:12:14",
  "updated": "2026-06-05 23:16:14"
}
```

### 2.2 当前卡包

| 卡包 ID | 名称 | 卡片数 | 用途 |
|---|---|---|---|
| `20260517141214-z4t7t8q` | 201词汇-释义挖空 | 3766 | 考研英语词汇（所有字母 A-Z） |
| `20260517140222-urxwkr6` | 201词汇-字母A | 64 | 字母 A 子集（测试用） |

### 2.3 卡包 API

```
GET  /api/riff/getRiffDecks       — 列出所有卡包
POST /api/riff/createRiffDeck     — 创建卡包
POST /api/riff/addRiffCards       — 将内容块注册为闪卡
POST /api/riff/removeRiffCards    — 从卡包移除闪卡
POST /api/riff/getRiffDueCards    — 获取待复习卡片
```

---

## 3. 卡片注册机制

### 3.1 注册方式

卡片通过块的 **IAL (Inline Attribute List)** 属性 `custom-riff-decks` 关联到卡包：

```
custom-riff-decks: "deckID1,deckID2,deckID3"
```

一个块可以同时注册到多个卡包。

### 3.2 卡片内容决定

块在被注册为闪卡时，SiYuan 会自动确定卡片内容：

- **标题块 (h)**：卡片正面 = 标题文本，背面 = 该标题下的所有子块内容
- **挖空标记**：用 `==text==` 包裹的内容在卡片中会被隐藏，复习时点击显示

### 3.3 关键陷阱：父块注册

**如果一个父级标题被注册为闪卡，其所有子块内容都会出现在一张卡上。**

例如：
```
# V                          ← 如果这个被注册 → 一张卡片显示全部 74 个单词 ❌
  ## vacant                  ← 这个被注册 → 一张卡片只显示 vacant 释义 ✅
  ## vaccine                 ← 一张卡片只显示 vaccine 释义 ✅
  ## vacuum                  ← 一张卡片只显示 vacuum 释义 ✅
```

**正确做法**：只注册 `##` 级别的单词标题，不注册 `#` 级别的字母标题。

### 3.4 清理错误的父块注册

```bash
# 1. 从卡包移除卡片
curl -X POST http://127.0.0.1:6806/api/riff/removeRiffCards \
  -H "Content-Type: application/json" \
  -d '{"deckID":"<deck_id>","blockIDs":["<block_id>"]}'

# 2. 清除块的闪卡关联属性
curl -X POST http://127.0.0.1:6806/api/attr/setBlockAttrs \
  -H "Content-Type: application/json" \
  -d '{"id":"<block_id>","attrs":{"custom-riff-decks":""}}'
```

---

## 4. 词汇数据结构

### 4.1 文档组织

- 笔记本：`201`
- 每个字母一个文档：`/A.md`, `/B.md`, ..., `/Z.md`
- 每个单词一个 `##` 标题块

### 4.2 单词 Markdown 结构

```markdown
## abandon

- **音标**: /əˈbændən/
- **词性**: v.
- **释义**: ==抛弃，遗弃；放弃==
- **英文释义**: to leave somebody...
- **同义词**: desert, forsake, relinquish
- **反义词**: keep, retain, maintain
- **词根词缀**: a(加强)+band(带子)+on...
- **搭配**: abandon hope, abandon the idea
- **例句**:
  - Those who abandon hope will never achieve their goals.
  - The crew abandoned the sinking ship.
- **考频**: 91
```

### 4.3 字段说明

| 字段 | 说明 | 闪卡行为 |
|---|---|---|
| `## word` | 单词（标题块 = 卡片正面） | 显示为问题 |
| `音标` | 国际音标 | 始终可见 |
| `释义` | 中文释义，`==` 包裹 = 挖空 | 复习时隐藏 |
| `英文释义` | 英文释义 | 始终可见 |
| `同义词/反义词` | 词汇关联 | 始终可见 |
| `词根词缀` | 词源分析 | 始终可见 |
| `例句` | 使用场景 | 始终可见 |
| `考频` | 考试出现次数 | 用于优先级排序 |

### 4.4 词库统计

| 指标 | 数值 |
|---|---|
| 总单词数 | 3,741 |
| 最大字母 | C (452 词) |
| 最小字母 | X (1 词) |
| 平均每字母 | ~144 词 |
| 卡包 ID | `20260517141214-z4t7t8q` |
| 卡包名称 | 201词汇-释义挖空 |

---

## 5. 复习工作流

### 5.1 每日复习

1. 打开 SiYuan → 闪卡面板
2. 选择卡包 "201词汇-释义挖空"
3. 系统按 FSRS 算法排定当日需复习的卡片
4. 每张卡：看单词 → 回忆释义 → 点击显示挖空内容 → 自评 (Again/Hard/Good/Easy)

### 5.2 卡片状态流转

```
New ──(首次复习)──→ Learning ──(连续正确)──→ Review ──(遗忘)──→ Relearning
                      │                           │                    │
                      └──(遗忘)──→ Relearning ←───┘                    │
                                                                       │
                                              ←──(掌握)────────────────┘
```

### 5.3 最佳实践

- **每天 30 个新词 + 复习旧词**：3000 词约 100 天完成一轮
- **释义挖空**：`==释义==` 让卡片更有交互性，不仅仅是"看答案"
- **考频排序**：先背高频词（考频 >10），再背低频词
- **多卡包管理**：可按主题创建子卡包（如"真题生词"）

---

## 6. 常见问题与修复

### 6.1 一张卡显示多个单词

**原因**：字母文档的 `# X` 主标题被注册为闪卡，导致所有子块内容合并。

**修复**：移除父标题的卡片注册（见 3.4 节）。

**历史记录**：
- 2026-05-14：修复 P（296 词挤在一张）
- 2026-06-05：修复 V（74 词挤在一张）、Q（16 词挤在一张）

### 6.2 卡片未注册

**原因**：`## word` 标题块的 `custom-riff-decks` 属性缺失或指向已删除的卡包。

**修复**：重新注册标题块到目标卡包：
```bash
curl -X POST http://127.0.0.1:6806/api/riff/addRiffCards \
  -H "Content-Type: application/json" \
  -d '{"deckID":"<deck_id>","blockIDs":["<block_id_1>","<block_id_2>",...]}'
```

### 6.3 卡包 ID 引用不存在的卡包

**现象**：`custom-riff-decks` 中包含已删除卡包的 ID（如 `20260515230752-oxgqgk8`）。

**影响**：通常无害——SiYuan 会忽略不存在卡包的引用。但建议清理以保持整洁。

---

## 7. 技术细节

### 7.1 SiYuan API 认证

- 未设置访问授权码时：`localhost` 自动免密
- 设置授权码后：需在请求中携带 token

### 7.2 扩展机制层级

```
插件 (Plugin) > 闪卡 (Riff) > Widget > 模板 (Template)
```

闪卡系统是内置的一等公民，不需要额外安装插件。

### 7.3 FSRS 参数

FSRS 的核心参数通过历史数据动态校准：
- **稳定性 (Stability)**：记忆保持的时间长度
- **难度 (Difficulty)**：卡片的固有难度
- **可提取性 (Retrievability)**：当前时刻能回忆起来的概率

---

## 相关资源

- [SiYuan 官方文档](https://github.com/siyuan-note/siyuan)
- [FSRS 算法论文](https://github.com/open-spaced-repetition/fsrs4anki)
- 词汇导入脚本：`/d/study/kaoyan-english/.claude/siyuan_import.py`
- 词汇数据文件：`A-Z/*.md`（同目录下）
- 卡包 API 交互记录：`d:/learn/agentic-ai-system-course-main/memory/daily-sessions/2026-06-05.md`
