# -*- coding: utf-8 -*-
"""2026-11-02 20:00 例行巡检：修复 20:00 轮次新增条目 + 存量繁体残留。

巡检发现的问题
--------------
A. 繁体字残留（1 条）
   'OpenAI's Lehane Calls AI the Number-One Issue of the 2028 Election'
   （Unite.AI, 18:50）
   标题「OpenAI 的 Lehane 称 AI 是 2028 年大选的頭號議題」——「頭號議題」
   为繁体。根因是上一轮（19:00）人工定稿时写入了繁体字。

B. 新增条目术语失真（2 条，20:00 轮次新抓）
   1) 'Article: Systemic Approach to Memory, Knowledge, and Context in
      Agentic AI Architectures'（InfoQ AI, 19:00）
      缺陷：标题「…对记忆，知识和背景的系统方法」（context 译成「背景」）；
      摘要「一个环境引擎」（context engine → 环境引擎）、「选择，注射，压缩」
      （inject → 注射，医学校译）、「环境，内存和知识」（context/memory 错译）、
      「层次内存」（tiered memory）、「策划知识」（curated knowledge）、
      「文本填充」（context stuffing 丢失 context 语义）。

   2) 'The AI Agent Memory Stack: Building Blocks, Patterns, and Frameworks'
      （ML Mastery, 19:00）
      缺陷：标题「AI 智能体记忆堆：构建块，图案和框架」——
      memory stack 应为「记忆栈」，patterns 应为「模式」（不是图像义的「图案」）；
      摘要「AI 智能体内存堆，关键内存类型」。

根因修复（translate.py / zh_t2s.py）
-----------------------------------
1. 新增 zh_t2s.py：内置「繁 -> 简」安全映射表（3546 条，零外部依赖），
   在 _clean_zh() 末尾调用 to_simplified()，从主链路上根治繁体输出。
   映射表由 scripts/build_t2s_map.py 生成，安全性用 OpenCC 短语词典过滤
   （排除「乾」「幹」「麼」等 7 个歧义字，避免「乾隆」被改成「干隆」）。
2. TERM_FIXES 新增智能体架构术语规则：context engine / memory stack /
   tiered memory / curated knowledge / context stuffing / building blocks,
   以及 inject → 注入。

本脚本：对上述 3 条做人工定稿（保证线上稳定），并写入覆盖表，
避免下一轮调度重跑时又被引擎译文覆盖回去。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

# ---- A. 繁体残留条目（仅需把标题的繁体字改回简体）----
EN_A = "OpenAI’s Lehane Calls AI the Number-One Issue of the 2028 Election"
ZH_A_TITLE = "OpenAI 的 Lehane 称 AI 是 2028 年大选的头号议题"
ZH_A_SUMMARY = (
    "OpenAI 首席全球事务官克里斯·莱汉（Chris Lehane）撰写了一份备忘录，"
    "主张人工智能将成为 2028 年总统大选的头号议题，并提出他认为"
    "候选人必须回答的五个问题，以构建人工智能议程。"
    "该备忘录于 2026 年 11 月 2 日公开。"
)

# ---- B1. InfoQ AI 19:00 条目 ----
EN_B1 = (
    "Article: Systemic Approach to Memory, Knowledge, and Context in "
    "Agentic AI Architectures"
)
ZH_B1_TITLE = "文章：智能体 AI 架构中记忆、知识与上下文的系统方法"
ZH_B1_SUMMARY = (
    "这篇文章认为，可靠的智能体 AI 架构取决于一个上下文引擎——"
    "它在信息抵达模型之前，先对信息做选择、注入、压缩与过期处理。"
    "文章把上下文、记忆与知识三者区分开来，并建议采用分层记忆、"
    "精选知识与 token 预算等做法。它还梳理了若干常见反模式，"
    "例如上下文填充与陈旧数据循环，并给出了相应的缓解措施。"
)

# ---- B2. ML Mastery 19:00 条目 ----
EN_B2 = (
    "The AI Agent Memory Stack: Building Blocks, Patterns, and Frameworks"
)
ZH_B2_TITLE = "AI 智能体记忆栈：构建模块、模式与框架"
ZH_B2_SUMMARY = (
    "本文将深入剖析 AI 智能体的记忆栈，介绍关键的记忆类型，"
    "以及构建可靠 AI 智能体时常用的模式。"
)

FIXES = (
    (EN_A, ZH_A_TITLE, ZH_A_SUMMARY),
    (EN_B1, ZH_B1_TITLE, ZH_B1_SUMMARY),
    (EN_B2, ZH_B2_TITLE, ZH_B2_SUMMARY),
)


def put_override(path, key, value):
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    d[key] = value
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    n = 0
    for it in data.get("items", []):
        title = it.get("title")
        for en, zh_t, zh_s in FIXES:
            if title == en:
                it["title_zh"] = zh_t
                it["summary_zh"] = zh_s
                it["translated"] = True
                it["method"] = "nllb+manual"
                n += 1
                break

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    for en, t, s in FIXES:
        put_override(T_JSON, en, t)
        put_override(S_JSON, en, s)
        print("[fix_2000b] 已写入覆盖表:", en[:50])

    print("[fix_2000b] 已回写 %d 条" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
