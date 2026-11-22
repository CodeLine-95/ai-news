# -*- coding: utf-8 -*-
"""2026-11-23 02:00 巡检：整点调度新增 2 条（01:25 The Verge、08:00 OpenAI），NLLB 硬伤人工定稿。

  * The Verge《Binding of Isaac developer removes AI music from Repentance Plus》——
    标题 "Binding of Isaac" 被直译成「艾萨克的绑定」（应为游戏名《以撒的结合》）；
    摘要里 "Grand Theft Auto-themed section" 译成「大盗猎自动车主主题部分」（应为 GTA 主题段落）、
    "Suno" 译成「苏诺」、「took to X to apologize」译成「向 X 道歉」（应为「在 X 上道歉」）、
    "Adding to the drama" 译成「在剧情中」（应为「更富戏剧性的是」）。

  * OpenAI《Perplexity and Intelligence》——
    术语 "perplexity"（困惑度）被当成公司名「Perplexity」，标题与摘要均误译。

三层覆盖：news.json 回填 + JSON 覆盖表 + (regen) manual_overrides.py。
"""
import json
import os
import report

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
N_JSON = os.path.join(BASE, "data", "news.json")

FIXES = [
    (
        "cf3322b3a4602d726cf0e81e683d577c",
        "《以撒的结合》开发者从《Repentance Plus》中移除 AI 音乐",
        "《以撒的结合：Repentance Plus》过去几天在 Steam 上遭到差评轰炸，起因是玩家发现游戏中某个特定段落使用了 AI 音乐。"
        "Reddit 用户 ShweetsStuff 发现了《侠盗猎车手》（GTA）主题段落中使用的歌曲——多个音频文件带有 Suno 元数据，"
        "指向 Suno 网站上的曲目。游戏创作者埃德蒙·麦克米伦（Edmund McMillen）随后在 X 上道歉，"
        "称自己「完全不知道」游戏中的 GTA 恶搞桥段用了生成式 AI 音乐。更富戏剧性的是，"
        "Valve 要求开发者披露在开发过程中使用生成式 AI 的方式与时机，而 Nicalis, Inc.……",
    ),
    (
        "d2fc1e262b4cb91300c351549a4a567e",
        "困惑度与智能",
        "困惑度（perplexity）如何衡量 AI 模型的进步，以及它为何能帮助开发者建立一套评估新兴能力的通用方法。",
    ),
]


def main():
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(N_JSON, encoding="utf-8"))
    by_id = {it["id"]: it for it in news["items"]}

    ok = 0
    for iid, zh_t, zh_s in FIXES:
        it = by_id.get(iid)
        if not it:
            print("[WARN] id 未找到:", iid)
            continue
        en = (it.get("title") or "").strip()
        titles[en] = zh_t
        summaries[en] = zh_s
        it["title_zh"] = zh_t
        it["summary_zh"] = zh_s
        it["method"] = "manual"
        it["translated"] = True
        ok += 1
        print("[FIX]", iid[:8], "->", zh_t)

    json.dump(titles, open(T_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(summaries, open(S_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(news, open(N_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[OK] 定稿 %d 条；覆盖表 标题=%d 摘要=%d；news.json=%d 条"
          % (ok, len(titles), len(summaries), len(news["items"])))

    report.main()
    print("[OK] 报告已重生成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
