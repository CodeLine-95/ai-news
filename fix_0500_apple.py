# -*- coding: utf-8 -*-
"""2026-11-28 05:00 例行巡检：Apple→果 机翻截断硬伤定稿（4 条历史存量）。

固化三层：news.json 直接回填 + JSON 覆盖表 + （随后 regen_overrides.py）
同步到代码层 manual_overrides.py，再重启服务让内存回填并重生成报告。
"""
import json
import os
import sys

import report
import translate

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

sys.path.insert(0, DATA)
from titles_fix_0500_patrol import TITLE_OVERRIDES      # noqa: E402
from summaries_fix_0500_patrol import SUMMARY_OVERRIDES  # noqa: E402

DATA_FILE = os.path.join(DATA, "news.json")
T_JSON = os.path.join(DATA, "titles_override.json")
S_JSON = os.path.join(DATA, "summaries_override.json")


def main():
    db = json.load(open(DATA_FILE, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    tov = json.load(open(T_JSON, encoding="utf-8")) if os.path.exists(T_JSON) else {}
    sov = json.load(open(S_JSON, encoding="utf-8")) if os.path.exists(S_JSON) else {}

    changed = 0
    for en, zh in TITLE_OVERRIDES.items():
        for it in items:
            if (it.get("title") or "").strip() == en:
                v = translate._fix_cjk_latin_spacing(zh)
                if it.get("title_zh") != v:
                    it["title_zh"] = v
                    it["translated"] = True
                    it["method"] = "nllb+manual"
                    changed += 1
                tov[en] = v
                break
    for en, zh in SUMMARY_OVERRIDES.items():
        for it in items:
            if (it.get("title") or "").strip() == en:
                v = translate._fix_cjk_latin_spacing(zh)
                if it.get("summary_zh") != v:
                    it["summary_zh"] = v
                    it["translated"] = True
                    changed += 1
                sov[en] = v
                break

    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("[fix_0500_apple] 回填条目变更:", changed,
          "| 标题表:", len(tov), "| 摘要表:", len(sov), flush=True)
    report.main()
    print("[fix_0500_apple] 报告已重生成", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
