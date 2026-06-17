---
date: 2026-06-16
day: 周二
type: Agent Session 概括
---

# 2026-06-16 Agent Session — Life Game 世界观设计 + Ch.01-07 代码实现

## 产出总览

| 维度 | 内容 |
|------|------|
| 课程进度 | Ch.01-07 全量代码实现（life-game 新项目） |
| 设计 | 5 份完整世界观文档（异世界穿越 RPG） |
| 金融/职业 | 两周计划补全 Agent + 简历栏 |

## 计划补全

更新 `2026-06-15.md` 日计划——每晚 agent+简历 栏补充具体任务：
- Week 1 (6/16-22): Ch.08-19 → life-game 实现
- Week 2 (6/23-29): Ch.20-22 + 5 简历项目终版 + 投递
- 5 个简历项目映射：销售 agent(Ch.13)、策划 agent(Ch.10)、医疗 agent(Ch.06-07)、数据库 agent(Ch.03)、地址识别(Ch.01)

## 参考调研

搜索 Habitica（开源游戏化任务管理）及其他 7 个开源 RPG habit tracker 项目。
关键发现：Habitica 经验公式 `300 + level × 100`，三级任务类型（习惯/每日/待办），生命值惩罚，10 级选职业，组队打 Boss。

用户方向调整："赶进度没用，ch01-07 要跟着新项目从头学。""我感觉什么也没学到。"→ 放弃赶进度，重新从头搭建。

## Life Game 世界观设计

**核心设定**：纯异世界穿越——只有你从现实穿越到埃特尼亚。现实中的学习/编程/锻炼同步转化为异世界的力量。全 NPC 为原住民，不知道地球。

**5 份设计文件**：
1. `01-core-system.md` — 六大属性 + 15 阶位 + HP/MP/SP 三资源
2. `02-classes-skills.md` — 六大職業（剣聖/鍛冶神/守護神/錬金術師/吟遊詩人/戦術師）+ 技能进化 + 12 称号
3. `03-npcs.md` — 10 人完整角色卡（伊修卡/加尔德/莉莉艾拉/泽法尔/诺克斯/泰拉/辛/米拉/凡/伊格尼斯）
4. `04-world-mechanics.md` — 魔物討伐=学習、副本=復習、釣り=輕鬆復習、市場/経済
5. `05-mentors.md` — 奥尔德/菲奥/克洛 + 格里莫尔（世界管理者）

**语言调整**：初版全日文 RPG 风格 → 用户要求 → 全部改为中文。

## Ch.01-07 代码实现

**项目**：`workspace/life-game/`，uv 管理，Qwen 驱动。

**文件结构**：
```
src/tutor/
├── game_engine.py  # 游戏状态 + NPC 数据 + 排名引擎 + 系统提示词
├── tools.py        # 5 工具 + build_tool 工厂 + 元数据
└── loop.py         # Agent 循环 + 错误信封 + 剪辑 + 去重 + 钩子
main.py             # 入口
```

**章节对应**：

| 章 | 实现 | 文件 |
|----|------|------|
| Ch.01 | 5 工具 schema + handler | tools.py |
| Ch.02 | 五阶段循环 + 4 停止 + doom loop | loop.py |
| Ch.03 | build_tool 工厂 + 元数据 + 错误信封 + 钩子 | tools.py + loop.py |
| Ch.04 | SYSTEM_PROMPT 稳定前缀 | game_engine.py |
| Ch.05 | _clip 截断 + _dedupe 去重 | loop.py |
| Ch.06 | GAME_STATE 策划知识 + NPC roster | game_engine.py |
| Ch.07 | write_memory + 安全过滤 + 原子写入 | tools.py |

**5 个工具**：get_status / get_npc / get_ranking / write_memory / final_answer

**验证结果**：
- 玩家：穿越者 Lv.1 HP:180/180 MP:50/50
- NPC：10 人（伊修卡、加尔德...）
- 排位：933/1000 (6.7%)，薪资：6200

**开始代码走读**（进行到 game_engine.py 第 50 行，被定时任务中断）

## 模型
- qwen3.7-max-2026-05-17 当前，额度有限
- 轮换列表：max → 05-20 → 06-08 → 05-17 → preview

完整对话见：`knowledge-base/生活/2026/2026-06-16-Agent对话.md`
