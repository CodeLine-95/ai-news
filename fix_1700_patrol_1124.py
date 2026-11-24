# -*- coding: utf-8 -*-
"""2026-11-24 17:00 例行巡检：定稿 4 条历史 NLLB 机翻硬伤。

17:00 整点调度 0 新增（total 保持 2695），质量门禁全 0；但巡检发现 4 条
历史译文存在明确硬伤，属"译文质量差"，予以人工定稿：

1) "Signal"（加密通信协议/应用）被误译为「信号」——两条；
2) "Sumitomo Life" 被音译为「苏米托莫生命」，应为日本保险公司「住友生命」，
   "ChatGPT Enterprise" 被译为「ChatGPT 企业」；
3) "keep AI slop out of mathematics" 语义颠倒，被译为「让人工智能从数学中
   脱而出」，应为「把 AI 垃圾内容挡在数学之外」；
4) "formal verification" 术语被误译为「正式验证」，应为「形式化验证」。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "How Sumitomo Life’s leaders helped teams adopt ChatGPT Enterprise",
        "title_zh": "住友生命（Sumitomo Life）的领导者如何帮助团队采用 ChatGPT Enterprise",
        "summary_zh": (
            "住友生命（Sumitomo Life）使用 ChatGPT Enterprise 研究保险公司、"
            "准备投资分析的提案与草案代码。高管的率先使用推动了团队采纳。"
        ),
    },
    {
        "title": "Google DeepMind just mathematically verified key parts of Signal",
        "title_zh": "Google DeepMind 刚刚用数学方法验证了 Signal 加密协议的关键部分",
        "summary_zh": (
            "DeepMind 研究人员使用智能体人工智能，以数学方式证明并形式化验证了"
            " Signal 协议若干关键的加密保障，这是广泛使用的加密技术以及 Google "
            "人工智能自身的里程碑式进展。该工作在四周内作为概念验证项目完成，意义有二："
            "其一，它为保护全球大量通信的 Signal 应用（包括 Google 消息与 WhatsApp "
            "等平台所用协议）提供了进一步的独立安全验证；其二，它展示了 Google DeepMind "
            "借助名为 AlphaProof Code 的系统所具备的形式化验证能力。"
        ),
    },
    {
        "title": "A New AI Tool From Google DeepMind Proved the Signal Protocol Is Secure",
        "title_zh": "Google DeepMind 的新 AI 工具证明 Signal 协议是安全的",
        "summary_zh": (
            "DeepMind 研究人员能够形式化验证广泛使用的加密协议是否按预期运行。"
            "他们的延伸目标？对全世界所有软件做同样的事。"
        ),
    },
    {
        "title": "Axiom Math wants to keep AI slop out of mathematics",
        "title_zh": "Axiom Math 希望把 AI 垃圾内容挡在数学之外",
        "summary_zh": (
            "随着人工智能用未经核查的证明淹没数学领域，Axiom Math 押注于验证技术。"
            "这家初创公司的 AI 智能体刚刚形式化验证了数学界最大的文献库之一——"
            "Stacks Project。"
        ),
    },
]


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    by_title = {}
    for fx in FIXES:
        by_title[fx["title"].strip()] = fx

    changed = 0
    for it in items:
        key = (it.get("title") or "").strip()
        fx = by_title.get(key)
        if not fx:
            continue
        it["title_zh"] = fx["title_zh"]
        it["summary_zh"] = fx["summary_zh"]
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), key[:60])

    for fx in FIXES:
        titles[fx["title"]] = fx["title_zh"]
        summaries[fx["title"]] = fx["summary_zh"]

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1700_1124] news.json 回填 %d 条；覆盖表 %d / %d 条"
          % (changed, len(titles), len(summaries)))
    return 0 if changed == len(FIXES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
