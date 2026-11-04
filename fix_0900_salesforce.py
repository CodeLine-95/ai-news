# -*- coding: utf-8 -*-
"""2026-11-03 09:00 巡检：人工定稿 09:33 新增的 Salesforce 条目。

原文："Salesforce Agrees to Buy Cresta for Voice-Led Customer Service AI"

自动规则修复后（BRAND_TERMS 收录 Salesforce、GLOSSARY 补 "for Voice-Led"）
得到：「Salesforce 同意购买 Cresta 面向语音交互的客户服务 AI」——
品牌与未译片段都对了，但中文语序仍生硬：
"Buy" 在并购语境应为「收购」而非「购买」，
"for Voice-Led Customer Service AI" 是定语从句，理应前置修饰「AI」。

这里人工定稿为通顺中文，并把摘要一并润色：
- "Salesforce's fiscal 2028" 译作「Salesforce 2028 财年」；
- "assistance for human representatives" 译作「人工坐席协助」；
- "customary closing conditions" 译作「常规交割条件」。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    "Salesforce Agrees to Buy Cresta for Voice-Led Customer Service AI":
        "Salesforce 同意收购 Cresta：面向语音交互的客服 AI",
}

SUMMARY_FIX = {
    "Salesforce Agrees to Buy Cresta for Voice-Led Customer Service AI":
        "Salesforce 于 2026 年 11 月 2 日宣布，双方已签署最终协议，"
        "Salesforce 将收购 Cresta。该平台将语音智能体、人工坐席协助"
        "与对话分析能力结合起来。此次交易预计将于 Salesforce 2028 财年第一季度"
        "完成，但仍需获得必要的监管批准并满足常规交割条件。",
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
