# -*- coding: utf-8 -*-
"""19:00 例行巡检修复：人工定稿 2 条 NLLB 机翻硬伤。

1) 18:33 Inkling 2 Mini：Thinking Machines（公司名）误译为「思考机」、
   looped transformer 误译为「循环的变压器」、runs 12 of 24 layers three
   times 语义错乱、ties with 误译为「相结合」。
2) 18:27 科技股：标题「由于人工智能疑虑起……每周损失最严重」语句不通。

定稿写入 JSON 覆盖表（持久卷即时生效）+ 回填 news.json；
随后由 regen_overrides.py 同步代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

FIXES = {
    "New open model Inkling 2 Mini thinks in loops to solve problems with fewer words and still runs on a laptop": {
        "title_zh": "新型开放模型 Inkling 2 Mini 以「循环思考」用更少文字解题，且仍可在笔记本电脑上运行",
        "summary_zh": "Thinking Machines 发布了 Inkling 2 Mini——一款开放式循环 Transformer，把 24 层中的 12 层对每个 token 重复运行三次。这让模型在内部推理更久，却无需生成额外文本。在 Artificial Analysis 智能指数上，它与 Qwen3.8 27B 持平，成本却低约六倍。",
    },
    "US technology stocks suffer their worst weekly loss since the pandemic as AI doubts pile up": {
        "title_zh": "随着 AI 疑虑不断累积，美国科技股遭遇自疫情以来最严重的单周亏损",
        "summary_zh": "纳斯达克 100 指数在经历新冠疫情以来最严重的单周亏损后跌入熊市。因 SEC 审查其会计问题，英伟达大跌 14%；Anthropic 在创纪录 IPO 后仅一天就几乎回吐全部涨幅。对 AI 的质疑、丑闻、利率上升和政治逆风正同时冲击着过高的估值。",
    },
}


def main():
    with open(T_JSON, encoding="utf-8") as f:
        titles = json.load(f)
    with open(S_JSON, encoding="utf-8") as f:
        summaries = json.load(f)
    with open(NEWS, encoding="utf-8") as f:
        data = json.load(f)

    for en, fix in FIXES.items():
        titles[en] = fix["title_zh"]
        summaries[en] = fix["summary_zh"]
        for it in data["items"]:
            if (it.get("title") or "").strip() == en:
                it["title_zh"] = fix["title_zh"]
                it["summary_zh"] = fix["summary_zh"]
                it["translated"] = True
                it["method"] = "manual"
                print("[fix] 回填:", fix["title_zh"][:40])
                break
        else:
            print("[fix] 警告: news.json 未找到条目:", en[:50])

    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)
    with open(NEWS, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("[fix] 覆盖表 标题 %d / 摘要 %d" % (len(titles), len(summaries)))


if __name__ == "__main__":
    main()
