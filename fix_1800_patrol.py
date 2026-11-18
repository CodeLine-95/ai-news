# -*- coding: utf-8 -*-
"""18:00 例行巡检：人工定稿两条 NLLB 机翻缺陷条目。

问题条目 1（本轮新增，Unite.AI 17:39）：
  'OpenAI to Surface Le Figaro Reporting in ChatGPT Partnership'
  缺陷：动词 surface（呈现/上线）被逐词误译为「向表面…报告」，
  reporting 在此为名词「报道内容」，非「报告」动作。

问题条目 2（历史，Wired 11-17 19:00）：
  'The Apple Watch’s Live Rewind Can Record and Rewind Spoken Conversations. It’s Pretty Awkward'
  缺陷：标题译文被截断成孤立的「Apple」，主体完全丢失；
  摘要中 live rewind 译成「现场回」、social clumsiness 译成「社交拙」。

处理：写入人工定稿标题 + 摘要覆盖表，并回写 data/news.json。
随后由 /api/refresh 触发的 update_cycle 应用覆盖表并同步内存/报告。
全程不加载翻译模型，纯字典写入，不与后台调度器抢内存。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "en": "OpenAI to Surface Le Figaro Reporting in ChatGPT Partnership",
        "title_zh": "OpenAI 将在 ChatGPT 合作中呈现《费加罗报》的报道",
        "summary_zh": (
            "2026 年 11 月 18 日，OpenAI 与费加罗报业集团（Groupe Figaro）宣布达成战略合作，"
            "将通过摘要与摘录（并链接至原文）让用户能在 ChatGPT 中发现《费加罗报》的现刊与历史报道内容。"
            "费加罗报还计划在各个团队中部署 ChatGPT 企业版。"
            "该协议涵盖《费加罗报》及其关联刊物，内容横跨新闻、商业、文化与生活方式领域。"
        ),
    },
    {
        "en": "The Apple Watch’s Live Rewind Can Record and Rewind Spoken Conversations. It’s Pretty Awkward",
        "title_zh": "Apple Watch 的 Live Rewind 可录制并回放对话，但体验相当尴尬",
        "summary_zh": (
            "Live Rewind（实时回放）与 Siri Recap（对话回顾）可以转录你错过的对话片段、"
            "总结你的一天——前提是你不介意那一点点社交上的尴尬。"
        ),
    },
]


def main():
    for path, key, label in ((T_JSON, "title_zh", "标题"), (S_JSON, "summary_zh", "摘要")):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        for fx in FIXES:
            val = fx[key]
            if d.get(fx["en"]) != val:
                d[fx["en"]] = val
                print("[fix_1800_patrol] %s覆盖表写入: %s" % (label, fx["en"][:45]))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        en = (it.get("title") or "").strip()
        for fx in FIXES:
            if en == fx["en"]:
                it["title_zh"] = fx["title_zh"]
                it["summary_zh"] = fx["summary_zh"]
                it["translated"] = True
                hit += 1
                print("[fix_1800_patrol] 回写数据: %s" % en[:45])
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("[fix_1800_patrol] 完成，回写条目 %d" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
