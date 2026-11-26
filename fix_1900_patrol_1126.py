# -*- coding: utf-8 -*-
"""19:00 例行巡检：定稿 1 条新增条目的 NLLB 机翻误译。

19:00 整点抓取净新增 1 条（Wired / Meta Muse）：
- FCA（英国金融行为监管局）被误译为「美国联邦调查局」
- Complains 被弱化为「表示」；标题重复错乱、语序不通

按项目既有模式回填 news.json + JSON 覆盖表，再由
scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "Meta Refused to Share Muse for Testing, UK Financial Watchdog Complains": (
        "英国金融监管机构抱怨 Meta 拒绝分享 Muse 用于测试",
        "英国金融行为监管局（FCA）警告称，在 Meta 拒绝其共同测试请求后，AI 智能体可能带来「另一种攻击力量」。该公司在周二于英国推出个人智能体之前，回绝了 FCA 提出的合作测试请求。",
    ),
}


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    matched = set()
    for it in items:
        en = it.get("title") or ""
        if en not in FIX:
            continue
        matched.add(en)
        title_zh, summary_zh = FIX[en]
        if it.get("title_zh") != title_zh:
            it["title_zh"] = title_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] title:", en[:60], "->", title_zh)
        if it.get("summary_zh") != summary_zh:
            it["summary_zh"] = summary_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] summary:", en[:60])
        tov[en] = title_zh
        sov[en] = summary_zh

    missing = set(FIX) - matched
    if missing:
        print("[warn] 未匹配到条目:", missing)

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 变更 %d 处 | 覆盖表 标题 %d 条 / 摘要 %d 条"
          % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
