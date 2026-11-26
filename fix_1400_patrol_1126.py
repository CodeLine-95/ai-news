# -*- coding: utf-8 -*-
"""14:00 例行巡检：定稿 13:38 新增条目（XEBO.ai A 轮融资）的 NLLB 机翻腔。

- "Emirates Growth Fund (EGF)" 被直译为「阿联增长基金」，定稿为
  「阿联酋增长基金（Emirates Growth Fund，EGF）」。
- "voice-of-customer (VoC)" 被直译为「客户语音」，定稿为行业术语
  「客户之声（VoC）」；标题去掉「筹集了……资金」的直译腔。

按项目既有模式回填 news.json + JSON 覆盖表，再由
scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "XEBO.ai Raises $10.5M Series A to Expand Agentic AI and Analytics": (
        "XEBO.ai 完成 1050 万美元 A 轮融资，扩展智能体 AI 与分析业务",
        "2026 年 11 月 26 日，XEBO.ai 宣布获得阿联酋增长基金（Emirates Growth Fund，EGF）1050 万美元 A 轮投资，该基金成为这家 AI 原生体验管理公司的首个机构投资者。资金将用于扩展更广泛的客户之声（VoC）产品组合，包括通话分析与数字体验分析，并进一步在平台上开发智能体 AI。",
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
    for it in items:
        en = it.get("title") or ""
        if en not in FIX:
            continue
        title_zh, summary_zh = FIX[en]
        if it.get("title_zh") != title_zh:
            it["title_zh"] = title_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] title:", en[:60], "->", title_zh)
        if it.get("summary_zh") != summary_zh:
            it["summary_zh"] = summary_zh
            changed += 1
            print("[fix]  summary:", en[:60])
        tov[en] = title_zh
        sov[en] = summary_zh

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 变更 %d 处 | 覆盖表 标题 %d 条 / 摘要 %d 条"
          % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
