# -*- coding: utf-8 -*-
"""2026-11-03 10:00 巡检：人工定稿 09:49 新增的 Apple 条目。

原文标题："Apple may try to increase revenue by doing…something with third-party AI apps"
原文摘要："Apple hinted at ways that it could spur revenue through third-party "opportunities"
during its Monday night earnings call."

本轮定位到三个缺陷，已在 translate.py 做了根因修复（Apple 品牌还原的
后缀表补「可」、earnings call 补「财务电话」形态、弯引号统一为直角引号、
"AI apps" 统一为「AI 应用」）。规则修完后自动译文为：

  标题：Apple 可能会试图通过第三方 AI 应用做一些事情来增加收入
  摘要：Apple 在周一晚上的财报电话会议上暗示了它可以通过第三方「机会」刺激收入的方法。

品牌与术语都对了，但中文仍有三处不通顺，需要人工定稿：

1) 标题语序。「可能会试图…做一些事情」把 "may try to" 拆成「可能会」+
   「试图」两个弱化成分，读起来拖沓。中文习惯把 "may" 与 "try" 合并
   译成「可能尝试」，整句改为「Apple 可能尝试通过第三方 AI 应用做点什么
   来增加收入」。
2) "doing…something" 的省略号语义。原文故意用「…」表示"做某件
   不具体的事"，直译成「做一些事情」把这个"不具体"的意味磨平了，
   也丢了原文的省略号。定稿译作「做点什么」，保留"不具体"的意味。
3) 摘要句式。「暗示了它可以通过第三方「机会」刺激收入的方法」——
   "ways that it could spur revenue" 被译成「刺激收入的方法」，
   绕了一圈且"的方法"冗余。定稿改为「Apple 在周一晚间的财报电话会议上
   暗示，可借第三方「机会」带动收入」。

另：摘要中 "Monday night" 译作「周一晚间」比「周一晚上」更书面，
与站内财经类表述一致。

用法：
    python3.11 fix_1000_apple.py
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

KEY = "Apple may try to increase revenue by doing…something with third-party AI apps"

TITLE_FIX = {
    KEY: "Apple 可能尝试通过第三方 AI 应用做点什么来增加收入",
}

SUMMARY_FIX = {
    KEY: (
        "Apple 在周一晚间的财报电话会议上暗示，可借第三方「机会」带动收入。"
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
        raise SystemExit("覆盖未全部命中，请检查英文原标题是否一致")


if __name__ == "__main__":
    main()
