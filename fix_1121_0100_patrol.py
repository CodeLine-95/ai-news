# -*- coding: utf-8 -*-
"""2026-11-21 01:00 巡检：人工定稿 2 条历史机翻硬伤。

1) Unite.AI《AI Can Scale Security. But Scale What?》(11-20 23:56)
   标题「但规模什么？」语义崩坏；摘要「远程测量」错译 telemetry。
2) SiliconANGLE《Anthropic goes public, but is it too late to save the AI trade?》(11-20 23:00)
   标题「是否已为拯救人工智能贸易而已？」语义崩坏；
   摘要「首次公开募集…只是在人工智能行业的顶峰」错译 signal a top。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

T1 = "AI Can Scale Security. But Scale What?"
T2 = "Anthropic goes public, but is it too late to save the AI trade?"

TITLE_FIX = {
    T1: "AI 可以规模化安全能力，但规模化的到底是什么？",
    T2: "Anthropic 上市了，但 AI 交易是否已见顶、为时已晚？",
}

SUMMARY_FIX = {
    T1: (
        "如今企业安全团队面临的活动、遥测数据与告警数量，远超其人工调查的实际能力。"
        "各方估计不一，一些研究表明，平均每个安全运营团队每天会收到 4,400 多条告警。"
        "随着组织扩张、工具增多，AI 也让更多攻击成为可能，这一数字势必继续增长。"
    ),
    T2: (
        "Anthropic 周四完成了首次公开募股（IPO），但这是否预示着 AI 交易已经见顶？"
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        touched = False
        if en in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[en]
            touched = True
        if en in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[en]
            touched = True
        if touched:
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), en[:55])
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    added_t = added_s = 0
    for k, v in TITLE_FIX.items():
        if titles.get(k) != v:
            titles[k] = v
            added_t += 1
    for k, v in SUMMARY_FIX.items():
        if summaries.get(k) != v:
            summaries[k] = v
            added_s += 1
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1121_0100] news.json 回填 %d 条；标题定稿 %d 条 / 摘要定稿 %d 条" %
          (changed, added_t, added_s))
    print("[fix_1121_0100] 覆盖表 %d 条 / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
