# -*- coding: utf-8 -*-
"""2026-11-25 00:00 例行巡检：定稿本轮新增 5 条 NLLB 机翻硬伤。

本轮整点调度新增 5 条（total 2741 -> 2746），全部为 NLLB 原始机翻，硬伤包括：
1) Amazon/Decart：标题语序错乱（「的投注，这是……中的。」），品牌名与 Nvidia 对比语义不清；
2) Applied Systems/Tailwind：品牌名 Applied Systems 误作「应用系统」、Tailwind 误作「尾风」，
   carrier（保险公司）与 agency（代理机构）语义错位，operational/financial/trading workflows 漏译；
3) theCUBE/NetApp INSIGHT：theCUBE 误作「CUBE」、isolated pilots 误作「孤立的飞行员」、
   real-time 语境缺失，尾句 NetApp Inc. 孤立残留；
4) MIT Tech Review：agentic AI 误作泛化的「人工智能」、450% 语序错乱、
   hyperscale training clouds 长难句语义错位、结论句漏掉；
5) Ars Technica：Jensen Huang 人名中英混用、丑闻语义失真（affair/ subordinate 处理粗糙）、
   haemorrhage value 误作「流血价值」、董事会施压主体不清。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "Amazon’s Decart acquisition is a bet on using software to narrow the gap with Nvidia in the AI chip race",
        "title_zh": "亚马逊收购 Decart，押注用软件缩小与英伟达在 AI 芯片竞赛中的差距",
        "summary_zh": (
            "亚马逊据报以 75 亿美元收购 Decart，这是其提升自研 Trainium 芯片效率、"
            "在 AI 芯片竞赛中追赶英伟达的举措之一。"
        ),
    },
    {
        "title": "Applied Systems Acquires Tailwind for AI Insurance Document Automation",
        "title_zh": "Applied Systems 收购 Tailwind，推进 AI 保险文档自动化",
        "summary_zh": (
            "Applied Systems 于 2026 年 11 月 24 日宣布收购保险文档与数据检索服务商 Tailwind，"
            "用于将保险公司的文档自动导入其管理系统，并把 AI 自动化扩展到代理机构的运营、"
            "财务与交易工作流。此次收购弥补了保险公司所持文档与代理机构在管理系统中所需数据之间的缺口。"
        ),
    },
    {
        "title": "Three insights you may have missed from theCUBE’s coverage of NetApp INSIGHT",
        "title_zh": "theCUBE 对 NetApp INSIGHT 大会报道中，你可能错过的三点洞察",
        "summary_zh": (
            "随着企业把人工智能从孤立的试点推向生产环境，智能数据基础设施正成为优先事项。"
            "这一转变对原本支撑传统应用的存储系统提出了新要求，尤其是在组织开始于混合云与"
            "多云环境中引入 AI 工作负载之际。NetApp Inc. 在 INSIGHT 大会上强调了这一趋势。"
        ),
    },
    {
        "title": "Raising the stakes for enterprise networks with AI modernization",
        "title_zh": "AI 现代化推高企业网络的赌注",
        "summary_zh": (
            "企业网络正承受巨大压力。随着企业争相部署人工智能，这项技术迅速成为网络带宽需求的最大来源，"
            "而智能体 AI 又进一步加重了负担。据估算，AI 智能体执行的任务所产生的网络流量，"
            "比人工完成同样任务高出约 450%。随着 AI 推理从超大规模训练云——即原始模型摄取海量数据并"
            "完成学习的大型集中式数据中心——转向实时、对延迟敏感的应用，对本地或近本地基础设施的需求"
            "日益增长。其结果是，已准备好支撑 AI 的企业网络与尚未准备好的网络之间的差距正在拉大。"
            "近期一项研究显示，仅约一半的企业认为其现有网络能够应对 AI 的带宽与延迟需求。"
        ),
    },
    {
        "title": "How Trump and Silicon Valley forced Nvidia to take Jensen Huang back",
        "title_zh": "特朗普与硅谷如何迫使英伟达重新请回黄仁勋",
        "summary_zh": (
            "周一上午，黄仁勋走进英伟达位于圣克拉拉的总部，受到列队在上方走廊的员工的热情掌声欢迎。"
            "当一位同事扑上去拥抱他时，黄仁勋难掩激动。就在不到两周前，他因一起涉及客户及疑似中国间谍的"
            "丑闻、以及另一起据报与下属的恋情而辞职；如今这位英伟达首席执行官戏剧性复职，连公司最高层"
            "高管都感到意外。英伟达董事会的这一突然反转，是由特朗普总统推动的——在上周目睹这家曾是"
            "美国市值最高的公司以及更广泛的科技板块市值大幅缩水后，他在周末向董事会施压。"
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
        key = (it.get("title") or "").strip()
        fx = by_title.get(key)
        if not fx:
            continue
        it["title_zh"] = fx["title_zh"]
        it["summary_zh"] = fx["summary_zh"]
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), key[:60])

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
