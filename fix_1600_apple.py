# -*- coding: utf-8 -*-
"""16:00 巡检：定稿 3 条译文缺陷条目并写回覆盖表。

问题条目（均为本轮新增，来源 Unite.AI / TechCrunch）：

  1) 'Apple Watch Audio Intelligence Enters Developer Beta Testing'
     （Unite.AI, 2026-11-03 15:38）
     缺陷：NLLB 把独立的 "Apple" 译成单字「果」，产出「果 Watch 音频智能
     进入开发者测试」；摘要里还有「果 Apple Watch 的音频智能功能」。

  2) 'Apple Watch’s AI features for rewinding and recapping conversations
      begin beta testing'（TechCrunch, 2026-11-03 15:20）
     缺陷：NLLB 把 "Apple Watch's" 拆成「果果的」，产出「果 Apple 的 AI 功能
     用于重复和重复对话开始 beta 测试」——品牌残字 + 重复品牌 + 动词
     "rewinding and recapping" 被译成「重复和重复」（实为「回放与回顾」）。

  3) 'Windward Acquires Azimut.ai to Add Visual Vessel Intelligence'
     （Unite.AI, 2026-11-03 15:16）
     缺陷：整句尾巴 "to Add Visual Vessel Intelligence" 原样留成英文未译；
     品牌 Windward 被意译成「风向」；摘要中 windward / azimut.ai /
     ami daniel 三个专名被整体小写。

根因修复已在 translate.py 完成：
  - _APPLE_BARE_RE 前瞻扩充 Apple 硬件产品线英文名（Watch/Vision/…）；
  - _fix_bare_apple 新增「果 Apple」去重与连续「果」合并（果果 -> Apple）；
  - _repair_stranded_en_clause：整段英文从句残留时单独送一次模型译成中文；
  - _fix_proper_noun_case：按英文原文恢复被模型整体小写的专有名词大小写；
  - BRAND_TERMS 补 Windward（风向 -> Windward）。

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
        "Apple Watch Audio Intelligence Enters Developer Beta Testing",
        "Apple Watch 音频智能进入开发者测试",
        "2026 年 11 月 2 日，TechCrunch 报道称，Apple Watch 的音频智能功能"
        "已在 iOS 27.3 测试版中向开发者开放，包括 Live Rewind（现场回放）与 "
        "Siri Recap（对话回顾）。在正式全面上线之前，官方还计划面向公众进行"
        "更大范围的公测。Apple 在 2026 年 9 月 9 日的 Apple Watch Series 12 "
        "发布会上首次引入这一功能包，并承诺在年内将这两项对话功能带入测试阶段。",
    ),
    (
        "Apple Watch’s AI features for rewinding and recapping conversations "
        "begin beta testing",
        "Apple Watch 的 AI 功能开始 beta 测试：回放与回顾对话",
        "现已开启 beta 测试：Apple 最新的音频智能功能能帮你记住对方说过的话，"
        "或为对话自动做笔记。",
    ),
    (
        "Windward Acquires Azimut.ai to Add Visual Vessel Intelligence",
        "Windward 收购 Azimut.ai，为海上平台增加视觉船舶智能",
        "2026 年 11 月 3 日，Windward 宣布收购 Azimut.ai，将基于摄像头的"
        "船舶识别能力加入其 Maritime AI 平台。首席执行官兼联合创始人 Ami Daniel "
        "称，这次收购是「我们构建专有视觉智能层的第一步」，旨在提升海上可见性。",
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
                print("[fix_1600_apple] 已更新覆盖表:", os.path.basename(path), "|", en[:50])

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
                print("[fix_1600_apple] 已回写:", en[:60])
    if hit:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[fix_1600_apple] 已回写 news.json，命中条目:", hit)
    else:
        print("[fix_1600_apple] 未命中条目，未改动数据")


if __name__ == "__main__":
    main()
