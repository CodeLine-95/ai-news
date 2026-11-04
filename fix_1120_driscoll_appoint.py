# -*- coding: utf-8 -*-
"""2026-11-03 11:20 巡检：定向人工定稿 OpenAI Driscoll 任命公告（第二条）。

原文摘要：OpenAI appoints Dan Driscoll to advise on responsible AI for
national security modernization, cyber resilience, and collaboration with
U.S. allies.

自动译文问题：
  a) "responsible AI"（负责任的 AI）里 responsible 被整个丢掉，
     产出「为负责国家安全现代化…的 AI 提供建议」，语义完全走样；
  b) "advise on X for Y" 的语序被颠倒，中文不成句；
  c) "cyber resilience"（网络韧性）译作「网络弹性」，与站内
     「网络安全 / 网络韧性」写法不一致；
  d) "collaboration with U.S. allies" 译成「与美国盟国合作」，
     语序与用词都生硬。

处理顺序与 server.py 调度周期一致：
    人工定稿 → 术语确定性重清洗 → 应用人工标题覆盖 → 应用人工摘要覆盖
    → 重新生成报告
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
DATA = os.path.join(BASE, "data")

import server  # noqa: E402

KEY = "OpenAI appoints Dan Driscoll as Senior Counselor for National Security Modernization"

TITLE_FIX = {
    KEY: "OpenAI 任命丹·迪斯科尔担任国家安全现代化高级顾问",
}
SUMMARY_FIX = {
    KEY: (
        "OpenAI 任命丹·迪斯科尔，就负责任的 AI 提供建议，议题涵盖国家安全现代化、"
        "网络韧性以及与美国盟友的协作。"
    ),
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    hit_t = hit_s = 0
    for it in items:
        t = it.get("title", "")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_t += 1
            print("fix title:", it["date"], it["time"], it["source"])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_s += 1
            print("fix summary:", it["date"], it["time"], it["source"])

    server.apply_term_cleanup(items)
    server.apply_title_overrides(items)
    server.apply_summary_overrides(items)

    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    for name, fix in (("titles_override.json", TITLE_FIX),
                      ("summaries_override.json", SUMMARY_FIX)):
        path = os.path.join(DATA, name)
        cur = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                cur = json.load(f)
        cur.update(fix)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=2)

    print("fixed titles:", hit_t, "/", len(TITLE_FIX))
    print("fixed summaries:", hit_s, "/", len(SUMMARY_FIX))
    if hit_t != len(TITLE_FIX) or hit_s != len(SUMMARY_FIX):
        raise SystemExit("覆盖未全部命中")

    import report
    report.main()


if __name__ == "__main__":
    main()
