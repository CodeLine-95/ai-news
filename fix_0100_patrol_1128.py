# -*- coding: utf-8 -*-
"""01 点巡检：定稿 4 条 NLLB 机翻硬伤并写回覆盖表。

本轮（2026-11-28 01:00）整点自动抓取新增 4 条，机翻存在明显缺陷：
  1) 'Three studies ... Yann LeCun's bet on JEPA world models ...'
     bet 译为「投注」生硬；training 误译为「培训」；人名前后不一致。
  2) 'Vikram Srivats, CCO & Head of Product Experience at WaveMaker'
     Product Experience 误译为「产品经验」（应为产品体验）；人名前后不一致；
     architectural 误译为「建筑的」。
  3) 'Hackers breached the US Air Force's flagship Cloud One platform'
     Cloud One 误译为「云一平台」（产品名应保留英文）。
  4) 'OpenAI is building "Athena" data platform to cut down on AI agent guesswork'
     Athena 误译为「雅典」（代号应保留英文并括注）；guesswork 译为「猜测」偏弱；
     Snowflake / Databricks 误译为「雪和数据」。

人工定稿后写回 data 与覆盖表，随后运行 scripts/regen_overrides.py 同步到代码层覆盖表。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    (
        "Three studies from Meta and AMI Labs back Yann LeCun's bet on JEPA world models over large language models",
        "Meta 与 AMI Labs 的三项研究为 Yann LeCun 押注 JEPA 世界模型而非大语言模型提供支撑",
        "Yann LeCun 正通过初创公司 AMI Labs 推进其语言模型替代方案。JEPA 架构旨在为机器提供一个捕捉"
        "因果关系的内部世界模型。三项新研究在机器人规划、更高效的训练与纠错方面取得进展，尽管这些"
        "模块仍需协同发展。",
    ),
    (
        "Vikram Srivats, CCO & Head of Product Experience at WaveMaker – Interview Series",
        "WaveMaker 首席商务官兼产品体验负责人 Vikram Srivats 访谈系列",
        "Vikram Srivats 现任 WaveMaker 首席商务官兼产品体验负责人。他的职业经历涵盖手持计算、无线技术、"
        "物联网与企业软件。他专注于将新兴技术转化为企业级可维护应用所需的架构与组织条件，尤其强调"
        "代码所有权、设计一致性与工程纪律。",
    ),
    (
        "Hackers breached the US Air Force's flagship Cloud One platform, report says",
        "报道称黑客入侵美国空军旗舰平台 Cloud One",
        "黑客攻破了美国空军的旗舰云平台。",
    ),
    (
        "OpenAI is building \"Athena\" data platform to cut down on AI agent guesswork",
        "OpenAI 正在打造「Athena」数据平台，减少 AI 智能体的臆测",
        "OpenAI 在 ChatGPT 工作版中的数据智能体仍不够准确。该公司正以「Athena」为代号构建语义层，"
        "为智能体提供业务指标的标准化定义。该工具也可能让 OpenAI 与 Snowflake、Databricks 直接竞争。",
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
                print("[fix_0100] 已更新覆盖表:", os.path.basename(path), "|", en[:50])

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
                print("[fix_0100] 已回写:", en[:60])
    if hit:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[fix_0100] 已回写 news.json，命中条目:", hit)
    else:
        print("[fix_0100] 未命中条目，未改动数据")


if __name__ == "__main__":
    main()
