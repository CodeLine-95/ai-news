# -*- coding: utf-8 -*-
"""05:00 巡检：批量修复 Jensen Huang 错误译名（詹森·胡安/詹森·黄 → 黄仁勋）。

通过 translate._restore_terms 应用新登记的 TERM_FIXES 规则，
对存量译文做确定性回填（不调用模型），并把结果写入三层覆盖表。
"""
import json
import os
import translate

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    for it in items:
        if it.get("lang") != "en":
            continue
        en = it.get("title") or ""
        summary_en = it.get("summary") or ""
        # 标题或摘要任一提及 Huang 即纳入处理（部分条目标题仅写 "Huang"
        # 或完全不提，全名只在摘要出现）
        if "huang" not in en.lower() and "huang" not in summary_en.lower():
            continue
        # 用合并英文作为触发源，确保"詹森·黄"译名形态也能命中 huang 触发词
        trigger_source = en + " " + summary_en
        t = translate._restore_terms(it.get("title_zh") or "", trigger_source)
        s = translate._restore_terms(it.get("summary_zh") or "", trigger_source)
        if t != it.get("title_zh") or s != it.get("summary_zh"):
            it["title_zh"] = t
            it["summary_zh"] = s
            tov[en] = t
            sov[en] = s
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), en[:60])

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("changed:", changed)


if __name__ == "__main__":
    main()
