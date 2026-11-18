# -*- coding: utf-8 -*-
"""2026-11-18 21:00 巡检译文定稿脚本。

把本轮人工核对的 5 条标题/摘要写进三层覆盖表，并立即回填数据文件、
重生成摘要报告。不加载翻译模型，纯确定性处理。
"""
import json
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
sys.path.insert(0, DATA)

from titles_fix_2100 import TITLE_OVERRIDES       # noqa: E402
from summaries_fix_2100 import SUMMARY_OVERRIDES  # noqa: E402

import report  # noqa: E402


def load(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def main():
    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    npath = os.path.join(DATA, "news.json")
    for p in (tpath, spath, npath):
        if os.path.exists(p):
            shutil.copy(p, p + ".bak.2100")

    titles = load(tpath)
    summaries = load(spath)
    titles.update(TITLE_OVERRIDES)
    summaries.update(SUMMARY_OVERRIDES)
    dump(tpath, titles)
    dump(spath, summaries)

    db = load(npath)
    items = db["items"] if isinstance(db, dict) else db
    applied = 0
    for it in items:
        key = it.get("title") or ""
        t = titles.get(key)
        s = summaries.get(key)
        if t and it.get("title_zh") != t:
            it["title_zh"] = t
            applied += 1
        if s and it.get("summary_zh") != s:
            it["summary_zh"] = s
            applied += 1
        if t or s:
            it["translated"] = True
            it["method"] = "nllb+manual"

    dump(npath, db)
    report.main()
    print("[fix_2100_1118] 覆盖表：标题 %d 条 / 摘要 %d 条；回填 %d 处"
          % (len(titles), len(summaries), applied))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
