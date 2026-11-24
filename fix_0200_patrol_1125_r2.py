# -*- coding: utf-8 -*-
"""2026-11-25 02:00 巡检第二轮：定稿发布后自动补抓的 3 条 NLLB 硬伤。

覆盖英国网络安全警告、诺华 CEO 谈 AI 药物研发周期、Tidal 下架 AI 音乐。
尤其修正「Novartis→安卓公司」「诺华品牌名」「删歌数量」等明显错译。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "UK warns AI-driven cyberattacks are exposing years of weak security",
        "title_zh": "英国警告：AI 驱动的网络攻击正暴露多年来薄弱的安全防护",
        "summary_zh": (
            "英国网络安全机构表示，由于 AI 黑客工具依赖利用简单的安全漏洞，"
            "「筑牢基础从未如此重要」。"
        ),
    },
    {
        "title": "Novartis CEO says AI will shave four years off drug development, not cure all disease",
        "title_zh": "诺华 CEO：AI 可将药物研发缩短四年，但并非包治百病",
        "summary_zh": (
            "诺华 CEO Vas Narasimhan 同时也是 Anthropic 董事会成员，"
            "他反驳了 Anthropic CEO Amodei 与 DeepMind 创始人 Hassabis 关于 AI「包治百病」的承诺。"
            "他说，AI 会加快药物研发，但不会在十年内攻克癌症。真正的价值「介于两者之间」。"
        ),
    },
    {
        "title": "Tidal will start banning AI-generated music next month",
        "title_zh": "Tidal 下月起封禁 AI 生成音乐",
        "summary_zh": (
            "Tidal 将于 12 月 9 日正式封禁 AI 生成音乐。据 Tidal 音乐负责人 Robert Andersen 介绍，"
            "这一变化将导致平台删除约 2900 万首 AI 生成歌曲，并每天拒收约 8 万至 8.5 万首曲目。"
            "此举距 Tidal 开始对判定为 100% AI 生成的曲目进行标注并取消变现仅数月之遥。"
            "Andersen 在 X 上表示，由于过去 90 天里 AI 音乐占平台分发曲目的 43%，"
            "Tidal 需要采取更「激进」的措施。"
        ),
    },
]


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    by_title = {fx["title"].strip(): fx for fx in FIXES}
    changed = 0
    for it in items:
        fx = by_title.get((it.get("title") or "").strip())
        if fx:
            it["title_zh"] = fx["title_zh"]
            it["summary_zh"] = fx["summary_zh"]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), it.get("title", "")[:60])

    for fx in FIXES:
        titles[fx["title"]] = fx["title_zh"]
        summaries[fx["title"]] = fx["summary_zh"]

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("回填条目:", changed)
    assert changed == len(FIXES), "定稿条目数不符：%d != %d" % (changed, len(FIXES))


if __name__ == "__main__":
    main()
