# -*- coding: utf-8 -*-
"""10:00 例行巡检：定稿 09:42 / 09:46 两条 NLLB 机翻硬伤。

- "stuffed animals going rogue" 被译成「料动物会变得脏」——毛绒玩具
  「失控/行为越界」误译为「变得脏」，且 stuffed 漏译。
- "AI Voice startup" 被直译成「AI Voice 创业公司」，应为「语音 AI 创业公司」。

按项目既有模式回填 news.json + JSON 覆盖表，再由
scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

# 英文原标题 -> (定稿中文标题, 定稿中文摘要)
FIX = {
    "New York Bans AI toys amid concern after stuffed animals going rogue": (
        "纽约因担忧毛绒玩具失控而封禁 AI 玩具",
        "纽约州州长凯西·霍楚尔（Kathy Hochul）今日签署立法，将对由人工智能聊天机器人驱动的儿童玩具实施为期五年的禁令。此前有担忧称，玩偶、机器人和毛绒玩具可能会误导儿童，甚至谈论成人内容。",
    ),
    "Voice AI startup ElevenLabs reportedly seeking new funding at $33B valuation": (
        "据报道，语音 AI 创业公司 ElevenLabs 寻求以 330 亿美元估值进行新一轮融资",
        "据报道，人工智能开发商 ElevenLabs Inc. 正就按 330 亿美元估值融资展开早期谈判。彭博社今日援引消息人士称，该公司计划在 2027 年第一季度完成此轮融资；部分投资人希望融资能更早完成。",
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
