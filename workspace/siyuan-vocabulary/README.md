# SiYuan 考研英语词汇 & 闪卡系统

## 目录结构

```
siyuan-vocabulary/
├── README.md                           ← 本文件
├── CLAUDE.md                           ← 词汇 Agent 行为指南
├── siyuan-flashcard-system.md          ← SiYuan 闪卡系统完整文档
├── A-Z/                                ← 原始字母排序词汇（26 文件，3741 词）
├── groups/                             ← ★ AI 智能分组（Qwen3.7-max）
│   ├── README.md                       ←   分组索引
│   ├── 01-词根聚类/   (84 组)         ←   共享词根/词缀的词
│   ├── 02-近义词/     (101 组)        ←   意思相近的词
│   ├── 03-易混淆/     (48 组)         ←   拼写相近易看错的词
│   ├── 04-词族/       (50 组)         ←   同一词根的派生词
│   ├── 05-主题场景/   (118 组)        ←   同领域的专业术语
│   └── 06-随机池/     (1622 词)       ←   不便归类的词，每天抽 30 个
├── all_words.json                      ← 全部词汇结构化数据
├── wordlist_chunks/                    ← AI 分组的输入词表
├── ai_groups.json                      ← AI 分组的原始 JSON
└── *.py                                ← 工具脚本
```

**总计：3,741 个考研英语词汇** | **401 组** | **2,122 词已分组** | **1,622 词随机池**

## 学习方式

### 第一轮：全部刷一遍

1. 每天从分组文件里挑 1-2 组（~10 词）+ 从随机池抽 ~20 词 = 30 纯新词
2. SiYuan 同步安排当天需复习的旧词
3. 和 Agent（Claude Code）面对面：单词 + 提示 → 回忆释义 → 自评
4. 会的过，不会的标记进入第二轮

### 第二轮：薄弱词深挖

1. 第一轮标记的不熟悉词
2. Agent 追问式互动：词根拆解、近义辨析、例句翻译
3. 更新的理解写回单词文件

### 闪卡复习

见 [siyuan-flashcard-system.md](./siyuan-flashcard-system.md)：
- FSRS 间隔重复算法
- 卡包 `20260517141214-z4t7t8q`（201词汇-释义挖空，3766 张卡）
- SiYuan API：`http://127.0.0.1:6806`

## 数据来源

从 SiYuan 笔记本 `201`（英语词汇）实时导出。

## 相关项目

- `d:/study/kaoyan-english/` — 考研英语练习项目
- `d:/learn/agentic-ai-system-course-main/references/siyuan-data/` — SiYuan 数据备份
