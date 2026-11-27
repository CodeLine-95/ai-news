# -*- coding: utf-8 -*-
"""21 点巡检：定稿 3 条 NLLB 机翻硬伤并写回覆盖表。

问题条目（均为本轮新增，来源 Unite.AI）：

  1) 'Greenpeace Reports Construction Halt at Google’s Belgian Data Center'
     缺陷：标题语序生硬；摘要把「比利时」误译为「贝利时」，且措辞重复冗余。
  2) 'The Scaling Problem No One Talks About in Education: Who Checks the Teacher?'
     缺陷：摘要「规模很少被资本，房地产或需求限制」属于典型机翻被动句，
     语义不清。
  3) 'The Prototype Paradox: What to Do When AI-Built Apps Outgrow the People Who Made Them'
     缺陷：标题「超过它们制造者的时」存在明显语法错误；摘要把 export
     译为「出口」、clean 译为「清洁」，语义完全偏离。

本脚本把人工定稿结果写回数据与覆盖表，随后运行
    python3.11 scripts/regen_overrides.py
同步到代码层覆盖表，使后续轮次不再被模型译文覆盖。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    (
        "Greenpeace Reports Construction Halt at Google’s Belgian Data Center",
        "绿色和平组织称 Google 比利时数据中心建设已停工",
        "据多家媒体报道，比利时绿色和平组织于 2026 年 11 月 27 日表示，"
        "瓦隆大区已于 11 月 26 日下令停止 Google 位于 Aiseau-Presles 的"
        "数据中心建设。此前绿色和平组织于 11 月 23 日致信瓦隆区政府，"
        "要求立即停工；尽管相关许可证变更被撤销，该组织仍要求紧急停工。",
    ),
    (
        "The Scaling Problem No One Talks About in Education: Who Checks the Teacher?",
        "教育领域无人谈及的规模化难题：谁来监督老师？",
        "记得我们讨论一个规模化创业项目——每年新开 30 家儿童俱乐部时，"
        "一位投资人问我：「第 30 家门店的教学质量如何能与第 1 家保持一致？」"
        "坦率地说，他问到了关键问题。在教育领域，规模扩张很少受资本、"
        "场地或需求所限，真正的瓶颈在于质量控制。",
    ),
    (
        "The Prototype Paradox: What to Do When AI-Built Apps Outgrow the People Who Made Them",
        "原型悖论：当 AI 构建的应用超出其创造者的掌控时该怎么办",
        "设想周五下午，一家中型制造企业的规划团队里，一位供应链规划员"
        "厌倦了手工导出三份数据、清理格式再粘贴到跟踪表中。她打开 AI "
        "编程助手，描述了自己想要的工具。两小时后，她就有了一个小型"
        "网页应用：能自动拉取数据、标记延迟的采购订单，并建议哪些订单"
        "需要加急。它运行良好。周一，她把应用展示给两位同事。",
    ),
]


def main():
    for en, zh_title, zh_summary in FIXES:
        for path, val in ((T_JSON, zh_title), (S_JSON, zh_summary)):
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            if d.get(en) != val:
                d[en] = val
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
                print("[fix_2100] 已更新覆盖表:", os.path.basename(path), "|", en[:50])

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        for en, zh_title, zh_summary in FIXES:
            if it.get("title") == en:
                it["title_zh"] = zh_title
                it["summary_zh"] = zh_summary
                it["translated"] = True
                hit += 1
                print("[fix_2100] 已回写:", en[:60])
    if hit:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[fix_2100] 已回写 news.json，命中条目:", hit)
    else:
        print("[fix_2100] 未命中条目，未改动数据")


if __name__ == "__main__":
    main()
