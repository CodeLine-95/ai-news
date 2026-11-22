# -*- coding: utf-8 -*-
"""2026-11-22 22:00 巡检：本轮新增 3 条（21:00 The Decoder / 21:00 The Verge / 20:54 InfoQ AI），
NLLB 硬伤人工定稿。

  * The Decoder《AI is getting better faster than experts can reliably test ...》——
    NLLB 译成「人工智能正在变得更好，比专家能够可靠地测试...」句式生硬，缺「METR 警告」主干；
    "dangerous acceleration" 应为「危险加速（失控提速）」；"overestimate" 应为「高估」。
  * The Verge《The vibe-coding revolution is coming to all the gadgets》——
    "vibe-coding" 被译成「振动编码」（应为「Vibe 编程 / 氛围编程」）；
    "The Stepback" 被译成「步骤背后」（应为栏目名《The Stepback》）；
    "hacking, modding, jailbreaking" 被译成「黑客，调整，jailbreaking」，语义混乱。
  * InfoQ AI《PostgreSQL 19 Released with Online Table Repacking ...》——
    "PostgreSQL Global Development Group" 被音译成「普斯特格瑞 SQL 全球开发集团」（应为「PostgreSQL 全球开发组」）；
    "Online Table Repacking" 应为「在线表重组」；"administrative overhead" 应为「管理开销」。

三层覆盖：news.json 回填 + JSON 覆盖表 + (regen) manual_overrides.py。
"""
import json
import os
import report

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
N_JSON = os.path.join(BASE, "data", "news.json")

FIXES = [
    (
        "b3be30d51f4684c8262edc465fbdfd7f",
        "METR 警告：AI 能力提升速度快于专家可靠检验新系统安全性的速度",
        "METR 报告称，Opus 5.5 和 GPT-6 Astra 等领先 AI 模型在研究任务上的进步速度很快，"
        "但越来越难以衡量。该机构警告，现有数据无法排除 AI 研发出现危险加速的可能；"
        "不过它也表示，常见的测试可能高估了模型的实际能力。",
    ),
    (
        "564b8081b7bd00089ca3e7d686ebbd86",
        "Vibe 编程革命正席卷各类智能设备",
        "这是《The Stepback》——每周一封通讯，拆解科技界的一个重要故事。想了解更多关于万物"
        "「Vibe 黑客化」的内容，请关注 David Pierce。《The Stepback》于美国东部时间周日上午 8 点"
        "送达订阅者邮箱，可在此处订阅。事情是如何开始的？和许多与 AI 有关的事情一样，并不是大语言"
        "模型开启了某种全新能力。自从有了智能设备，就有少数用户在对它们进行破解、改装、越狱，"
        "并按自己的喜好调整。新的变化在于：现在这件事变得容易了。",
    ),
    (
        "904320729ec7428523778519b7aabe29",
        "PostgreSQL 19 发布：支持在线表重组与查询规划控制",
        "PostgreSQL 全球开发组发布了 PostgreSQL 19，在数据库维护、查询规划、复制和应用开发方面"
        "带来多项变化。该版本聚焦降低管理开销并提升性能，新增无需停机即可重组表的工具，"
        "并强化了对查询计划的控制。",
    ),
]


def main():
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(N_JSON, encoding="utf-8"))
    by_id = {it["id"]: it for it in news["items"]}

    ok = 0
    for iid, zh_t, zh_s in FIXES:
        it = by_id.get(iid)
        if not it:
            print("[WARN] id 未找到:", iid)
            continue
        en = (it.get("title") or "").strip()
        titles[en] = zh_t
        summaries[en] = zh_s
        it["title_zh"] = zh_t
        it["summary_zh"] = zh_s
        it["method"] = "manual"
        it["translated"] = True
        ok += 1
        print("[FIX]", iid[:8], "->", zh_t)

    json.dump(titles, open(T_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(summaries, open(S_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(news, open(N_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[OK] 定稿 %d 条；覆盖表 标题=%d 摘要=%d；news.json=%d 条"
          % (ok, len(titles), len(summaries), len(news["items"])))

    report.main()
    print("[OK] 报告已重生成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
