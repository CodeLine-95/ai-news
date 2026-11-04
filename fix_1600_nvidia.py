# -*- coding: utf-8 -*-
"""16:00 巡检（第二批）：定稿 NVIDIA 城市 AI 两条的译文并写回覆盖表。

问题条目（均为本轮新增）：

  1) 'NVIDIA Expands City AI with Shared Infrastructure and Digital Twins'
     （Unite.AI, 2026-11-03 15:29）
     缺陷：英文并列项用逗号直译——「包括居民援助，交通管理，城市规划和
     工业运营」「共享计算基础设施，AI 智能体和数字双胞胎结合在一起」；
     且 "digital twins" 译成「数字双胞胎」，与站内人工定稿写法
     「数字孪生」不一致。

  2) 'Cities Worldwide Build and Scale AI Services With NVIDIA Physical
      and Agentic AI'（NVIDIA Blog, 2026-11-03 15:00）
     缺陷：
       - "Physical and agentic AI" 译成「物理和机器人人工智能」——
         agentic（具备智能体能力的）被译成「机器人」，语义完全跑偏；
       - "operational systems"（业务系统）译成「操作系统」，
         中文里「操作系统」特指 OS；
       - "GTC Berlin" 译成「GTC 柏林」，会议专名应保留英文原名；
       - 并列项仍用逗号；
       - "enormous amounts of data" 译成「大量的数据」，「的」字冗余。

根因修复已在 translate.py 的 TERM_FIXES 完成（physical and agentic /
shared computing infrastructure / digital twin / gtc berlin /
operational systems / 并列顿号 / 大量的数据），
本脚本只负责把人工定稿结果写回数据与覆盖表，使后续轮次不被模型译文覆盖。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    (
        "NVIDIA Expands City AI with Shared Infrastructure and Digital Twins",
        "NVIDIA 扩大了城市 AI，使用共享基础设施和数字孪生",
        "2026 年 11 月 3 日，NVIDIA 宣布，它及其合作伙伴正在扩大全球城市的"
        "物理和智能体人工智能服务，包括居民援助、交通管理、城市规划和工业运营。"
        "这些项目将共享计算基础设施、AI 智能体和数字孪生结合在一起，"
        "同时让地方政府控制敏感数据处理和使用。",
    ),
    (
        "Cities Worldwide Build and Scale AI Services With NVIDIA Physical "
        "and Agentic AI",
        "城市在全球范围内建立和扩展 AI 服务，使用 NVIDIA 物理和智能体 AI",
        "城市从摄像头、传感器和业务系统中产生大量数据，"
        "但将其转化为有用的行动，用于规划、维护和公共服务，仍然是一个挑战。"
        "物理和智能体人工智能提供了解决这一差距的新方法，"
        "从数字孪生的基础设施规划到视觉和服务智能体，"
        "同时让地方政府控制如何处理和使用敏感数据。"
        "基于 GTC Berlin 公布的倡议，NVIDIA 及其合作伙伴正在扩大物理人工智能和 "
        "AI 智能体到世界各地的城市。共享的计算基础设施为城市部门、"
        "邻近的市政和当地开发人员提供了共同的基础，可以建立在扩展服务的基础上，"
        "而每个组织都不需要收购和管理自己的资源。",
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
                print("[fix_1600_nvidia] 已更新覆盖表:", os.path.basename(path),
                      "|", en[:50])

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
                print("[fix_1600_nvidia] 已回写:", en[:60])
    if hit:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[fix_1600_nvidia] 已回写 news.json，命中条目:", hit)
    else:
        print("[fix_1600_nvidia] 未命中条目，未改动数据")


if __name__ == "__main__":
    main()
