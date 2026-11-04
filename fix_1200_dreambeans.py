# -*- coding: utf-8 -*-
"""2026-11-03 12:00 巡检：修正 11:30 / 11:46 两条 Dreambeans 新条目。

背景
----
12:00 轮抓取新增 2 条（Dreambeans 落地印度），机器译文有 4 类缺陷：

1) 标题把品牌名 Dreambeans 意译成「梦」——
   「Google 带来了梦个性化 AI 故事到印度」，中文读者认不出这是产品名。
   （根因已在 translate.py 修好：BRAND_TERMS 登记「梦个性化/梦豆/梦幻豆」。）

2) 摘要里 13 个印度语言名被逐词音译成毫无辨识度的形态，
   其中两种与国名直接撞车：
     Telugu  → 「泰国语」（把印度语言安到泰国语言上）
     Kannada → 「加拿大语」（与加拿大国名撞车）
   （根因已在 translate.py 修好：_fix_language_names。）

3) Punjabi 被模型幻听成「西班牙语」——原文语言清单里根本没有 Spanish，
   结果语言列表凭空多出一种、漏掉一种，读者核对时对不上。
   （根因已在 translate.py 修好：_fix_language_names 的复合判定。）

4) 11:46 那条摘要开头「Google 宣布，Dreambeans，其实验性 Google 实验室
   应用程序，用于个性化日常故事收集」——同位语用逗号硬连，读起来断裂；
   11:30 那条标题「以向大众带来人工智能生成的个人故事」是典型的
   英文直译句式，中文不成句。

本脚本把这两条定稿写回 JSON 覆盖表，再由 scripts/regen_overrides.py
固化为 manual_overrides.py（随发布走，优先级高于模型译文）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_FIX = {
    "Google Brings Dreambeans’ Personalized AI Stories to India":
        "Google 将 Dreambeans 的个性化 AI 故事带到印度",
    "Google takes Dreambeans to India in bid to bring AI-generated personal stories to the masses":
        "Google 将 Dreambeans 带到印度，欲让 AI 生成的个人故事走进大众",
}

SUMMARY_FIX = {
    "Google Brings Dreambeans’ Personalized AI Stories to India":
        "Google 于 2026 年 11 月 3 日宣布，其 Google Labs 实验性应用 "
        "Dreambeans（每日个性化故事合集）正扩展至印度 18 岁及以上人群，"
        "Android 与 iOS 端支持 14 种语言。语言支持包括印地语、孟加拉语、"
        "泰卢固语、马拉地语、泰米尔语、乌尔都语、古吉拉特语、卡纳达语、"
        "马拉雅拉姆语、奥迪亚语、旁遮普语、阿萨姆语与尼泊尔语。",
    "Google takes Dreambeans to India in bid to bring AI-generated personal stories to the masses":
        "Google 最新的 AI 实验应用 Dreambeans 现已支持 13 种印度语言。",
}


def main():
    with open(T_JSON, "r", encoding="utf-8") as f:
        titles = json.load(f)
    with open(S_JSON, "r", encoding="utf-8") as f:
        summaries = json.load(f)

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

    print("[fix_1200_dreambeans] 标题定稿 %d 条 / 摘要定稿 %d 条"
          % (added_t, added_s))
    print("[fix_1200_dreambeans] 标题覆盖表 %d 条 / 摘要覆盖表 %d 条"
          % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
