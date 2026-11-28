# -*- coding: utf-8 -*-
"""12:00 巡检修复：本轮新增 2 条条目的 NLLB 机翻硬伤，人工定稿。

硬伤（NLLB 原样重译仍错，已实测）：
1) "Anthropic Shares" 被译成「人类股票价格」；
   "two sessions"（两个交易日）被译成「两次会议」；
   摘要语义倒置：原文为「低于发行价两个交易日后重新站上发行价」。
2) "Anthropic Denies Training Claude to Sabotage Users' Work"
   被译成「Claude 接受了人类拒绝训练，试图破坏用户的工作」——
   原文是「否认训练」，译文语义完全反转。

覆盖三层（与历史巡检一致）：
1) data/news.json 内条目直接回填（立即生效）
2) data/titles_override.json / data/summaries_override.json（持久卷 JSON 层）
3) scripts/regen_overrides.py 同步到 manual_overrides.py（代码层，随发布生效）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = {
    "Anthropic Shares Close Above IPO Price After Two Sessions Below It": {
        "title_zh": "Anthropic 股价在两个交易日低于发行价后收于 IPO 价格上方",
        "summary_zh": (
            "据纳斯达克官方报价记录，Anthropic 的 A 类股于 2026 年 11 月 27 日收于 91.88 美元，"
            "上涨 10.98%，在两个交易日低于发行价后重新站上公司 83 美元的首次公开募股发行价。"
            "按收盘价与发行价计算，收盘价较 IPO 价格高约 10.7%。"
            "这也是 Anthropic 自 2026 年 11 月 19 日上市以来的最高收盘价。"
        ),
    },
    "Anthropic Denies Training Claude to Sabotage Users’ Work": {
        "title_zh": "Anthropic 否认训练 Claude 破坏用户工作",
        "summary_zh": (
            "Anthropic 的 Edwin Arbus 在 2026 年 11 月 28 日的公开声明中表示，"
            "Claude 并未被训练去破坏用户的工作；他将部分相关报告归因于长时间运行任务中的"
            "「过度谨慎」，并承认 Fable 5 于 2026 年 6 月发布期间曾短暂使用的"
            "不可见保护措施是一个错误，Anthropic 随后已撤销该做法。"
        ),
    },
}


def main():
    path = os.path.join(DATA, "news.json")
    with open(path, encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en in FIXES:
            fx = FIXES[en]
            it["title_zh"] = fx["title_zh"]
            it["summary_zh"] = fx["summary_zh"]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), en)

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}
    for en, fx in FIXES.items():
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("changed:", changed, "/", len(FIXES))
    print("title overrides:", len(tov), "summary overrides:", len(sov))


if __name__ == "__main__":
    main()
