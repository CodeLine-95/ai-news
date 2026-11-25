# -*- coding: utf-8 -*-
"""21:00 例行巡检：定稿本轮 1 条新增资讯的 NLLB 生硬/错译译文。"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

FIXES = {
    "Has vibe coding made open source the new normal for synths?": (
        "Vibe 编程是否让开源成为合成器的新常态？",
        "强大的 Vibe 编程智能体与 Reverse Engineer Anything 等工具的出现，"
        "在音乐设备领域引发混乱，厂商纷纷忙于应对。有些厂商（如 Roland）目前选择沉默，"
        "另一些则拥抱了改装社区。过去几周，随着人们逐渐意识到没有什么音乐设备能躲过 "
        "Claude 和一个满是好奇极客的子版块，厂商开始把越来越多设备开源。"
        "其中最大牌的「打不过就加入」当属 inMusic——Akai、Moog、Native Instruments 等品牌的母公司。",
    ),
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    titles, summaries = load(T_JSON), load(S_JSON)
    for key, (title_zh, summary_zh) in FIXES.items():
        titles[key] = title_zh
        summaries[key] = summary_zh
    save(T_JSON, titles)
    save(S_JSON, summaries)

    news = load(NEWS)
    fixed = 0
    for it in news["items"]:
        fix = FIXES.get(it.get("title"))
        if not fix:
            continue
        it["title_zh"], it["summary_zh"] = fix
        it["translated"] = True
        it["method"] = "manual"
        fixed += 1
    save(NEWS, news)
    print("定稿条目数:", fixed)


if __name__ == "__main__":
    main()
