# -*- coding: utf-8 -*-
"""03:00 例行巡检：定稿 01:06 ML Mastery 那条 NLLB 机翻崩坏条目。

- 原标题 “Prefix Caching and Prompt Reuse” 被机翻为「预写缓存和快速重复使用」，
  术语全错：Prefix Caching 应为「前缀缓存」，Prompt Reuse 应为「提示词复用」。
- 摘要把 “Reusing Prefill Work” 译成「重复预填工作」，“Longest Cached Prefix”
  译成「最长的缓存前标」，且段落标题之间没有分隔。按原文重述，保留技术术语。

回填 news.json + JSON 覆盖表，再由 scripts/regen_overrides.py 同步到
代码层 manual_overrides.py，确保部署端持久卷的旧覆盖表不会回退译文。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "Prefix Caching and Prompt Reuse": (
        "前缀缓存与提示词复用",
        "概览：本文分为五部分——• 复用预填充计算 • 寻找最长缓存前缀 • 块哈希、基数树与兼容性 "
        "• 面向复用的提示词设计 • 容量与度量。在预填充阶段，每一层都会为提示词中的每个 token "
        "计算键和值。",
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
        if en in FIX:
            matched.add(en)
            title_zh, summary_zh = FIX[en]
            for key, value in (("title_zh", title_zh), ("summary_zh", summary_zh)):
                if it.get(key) != value:
                    it[key] = value
                    it["translated"] = True
                    it["method"] = "nllb+manual"
                    changed += 1
                    print("[fix] %s: %s" % (key, en[:58]))
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
