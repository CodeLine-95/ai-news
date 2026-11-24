# -*- coding: utf-8 -*-
"""2026-11-24 21:00 例行巡检：定稿本轮新增 10 条 NLLB 机翻硬伤。

本轮整点调度新增 11 条（total 2709 -> 2720），其中 10 条为 NLLB 原始机翻，硬伤包括：
1) Zipher 被误译为「齐弗」，put ... in charge of 被误译为「用于将...负责」；
2) humanoid concierge 被误译为「人体容器」，Six Seven 被误译为「六七」；
3) FrenchFry / Tavia 被拆译错乱（「法国 Fry」「塔维亚」）；
4) Matters.AI 被误译为「材料。AI」，pre-Series A 被误译为「预测系列」；
5) TU Darmstadt 被误译为「德意志大学达姆斯塔德大学」，on the fly 被误译为「空中」；
6) zero-day 被误译为「零天 / 0 天内」，root access 被误译为「根源访问」；
7) Exein 条「发射处理了继固件扫描后的分析」语义失真；
8) THB 113 billion 被误译为「1130 亿泰币」（应为泰铢），末尾截断文本不译入；
9) $0.7 billion 被误译为「17 亿美元」（数值硬伤，应为约 7 亿美元），800G transceiver 被误译为「接收器」；
10) CNCF 条标题漏译主体 CNCF。

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
        "title": "Zipher lands $53M to put AI agents, not data engineers, in charge of data workloads",
        "title_zh": "Zipher 融资 5300 万美元，用 AI 智能体而非数据工程师管理数据工作负载",
        "summary_zh": (
            "数据基础设施初创公司 Zipher Technologies Ltd. 今日宣布，已为一座由 AI 智能体（而非数据"
            "工程师）决定企业数据工作负载如何运行的平台融资 5300 万美元。Zipher 成立于 2024 年，"
            "负责接管企业数据工作负载的日常运营，从资源分配到框架选择与调度。"
        ),
    },
    {
        "title": "YYForce Launches Six Seven Humanoid Concierge for Novotel Singapore",
        "title_zh": "YYForce 为新加坡诺富特酒店推出人形礼宾机器人「Six Seven」",
        "summary_zh": (
            "YYForce 于 2026 年 11 月 24 日宣布推出 Six Seven——一款为酒店礼宾服务打造的人形机器人，"
            "计划部署于新加坡史蒂文斯路诺富特酒店（Novotel Singapore on Stevens）。酒店团队将其命名"
            "为 Six Seven（即 67）。在大堂内，Six Seven 旨在通过自然对话应答问题，并借助 YYForce "
            "的 Workforce OS 软件获取酒店及周边环境的实时信息。"
        ),
    },
    {
        "title": "FrenchFry Targets Nasdaq Listing Through Tavia SPAC Deal",
        "title_zh": "FrenchFry 拟通过与 Tavia 的 SPAC 交易登陆纳斯达克",
        "summary_zh": (
            "FrenchFry Acquisitions LLC 与上市特殊目的收购公司（SPAC）Tavia Acquisition Corp. "
            "于 2026 年 11 月 24 日宣布达成最终合并协议，对 FrenchFry 的企业估值达 5 亿美元，并为其"
            "铺就登陆纳斯达克之路。FrenchFry 的股东将获得 4500 万股 FrenchFry Holdings 普通股"
            "（每股作价 10 美元），外加 5000 万美元的可转换本票。"
        ),
    },
    {
        "title": "Matters.AI Raises $12M Pre-Series A Led by Tanglin Venture Partners",
        "title_zh": "数据安全初创公司 Matters.AI 完成 1200 万美元 Pre-A 轮融资，Tanglin Venture Partners 领投",
        "summary_zh": (
            "联合创始人兼首席执行官 Keshava Murthy 于 2026 年 11 月 24 日宣布，数据安全初创公司 "
            "Matters.AI 完成由 Tanglin Venture Partners 领投的 1200 万美元 Pre-A 轮融资，累计融资额"
            "达 1825 万美元。IIFL Capital Services Limited、Piper Serica、Foster Ventures 与 "
            "Tetration Ventures 参与本轮，早期投资方 Kalaari Capital 和 Endiya Partners 继续跟投。"
        ),
    },
    {
        "title": 'German researchers call for computer science to reinvent itself as "Computer and AI Science"',
        "title_zh": "德国研究人员呼吁计算机科学重塑为「计算机与 AI 科学」",
        "summary_zh": (
            "在一份立场文件中，达姆施塔特工业大学（TU Darmstadt）的研究人员呼吁将计算机科学重新定义"
            "为「计算机与 AI 科学」。他们最大的担忧是运行时即时生成的代码，认为这颠覆了当今的安全性"
            "与正确性保障。"
        ),
    },
    {
        "title": "Amazon says hackers' AI agents found and exploited 0-day with little human input",
        "title_zh": "亚马逊称黑客的 AI 智能体几乎无需人工干预即发现并利用零日漏洞",
        "summary_zh": (
            "亚马逊表示，AI 智能体近日发现并利用了一个零日漏洞，除一条「获取某东亚大学服务器 root "
            "权限」的简单指令外，全程无人监督。这些智能体运行在开源 AI 渗透测试框架 Cairn 上。黑客"
            "用简体中文提供提示，并将模型设置为中国标准时区，给智能体一份 IP 地址清单和「获取 shell "
            "访问权限」的目标。很快，智能体在一台目标服务器上运行的开源医学影像 AI 应用中发现了零日"
            "漏洞，随后加以利用并完全控制了系统。亚马逊称：「这些发现表明，智能体驱动的攻击行动已然"
            "发生，防守方应为这些工具带来的速度与持续性做好准备。」"
        ),
    },
    {
        "title": "Exein Launches Ray AI Agent to Prioritize Firmware Security Fixes",
        "title_zh": "Exein 推出 Ray AI 智能体，为固件安全修复排定优先级",
        "summary_zh": (
            "Exein 于 2026 年 11 月 24 日推出 Ray——一款嵌入其 Exein Analyzer 固件安全平台的对话式 AI "
            "智能体。该测试版对现有 Analyzer 客户免费开放，旨在帮助团队为漏洞及其他扫描结果排定优先级、"
            "决定调查方向并确定修复步骤。此次发布针对的是固件扫描之后的分析环节。"
        ),
    },
    {
        "title": "B.Grimm and NTT Pursue 400 MW AI Data Center Opportunity in Thailand",
        "title_zh": "B.Grimm 与 NTT 探索泰国 400 兆瓦 AI 数据中心机会",
        "summary_zh": (
            "B.Grimm 于 2026 年 11 月 24 日宣布，旗下 B.Grimm Power 与 NTT Global Data Center 签署"
            "谅解备忘录，探索在泰国推进一个 400 兆瓦数据中心项目，涵盖数字基础设施、AI 生态系统与能源"
            "基础设施，投资额约 1130 亿泰铢。该备忘录仅为探索这一机会的协议，并非确认工程已经动工。"
        ),
    },
    {
        "title": "Applied Optoelectronics Signs Four-Year AI Optics Supply Agreement",
        "title_zh": "应用光电（AOI）签署为期四年的 AI 光模块供应协议",
        "summary_zh": (
            "应用光电（Applied Optoelectronics）于 2026 年 11 月 24 日宣布，与一家未具名的现有 Tier-1 "
            "超大规模数据中心客户签署为期四年的供应协议，涉及约 22 亿美元的 800G 光模块与激光二极管最低"
            "采购量，用于 AI 基础设施。协议自 2026 年 12 月持续至 2030 年 12 月。客户承诺 2027 年采购"
            "约 15 亿美元的 800G 光模块，并在 2028 至 2029 年间采购约 7 亿美元的激光二极管，未来或按需"
            "增加其他产品。AOI 将承担一次性 200 万美元支出以加快产品认证，客户在协议下未作出资本承诺。"
        ),
    },
    {
        "title": "CNCF Research Shows Virtual Machines Remain Central as AI Workloads Evolve",
        "title_zh": "CNCF 研究显示：随着 AI 工作负载演进，虚拟机仍是核心",
        "summary_zh": (
            "云原生计算基金会（CNCF）与 Linux 基金会研究的最新调查发现，虚拟机平均承载 53% 的生产应用，"
            "而新兴的 AI 与智能体工作负载正为虚拟化带来新增需求，尤其是在需要更强执行隔离的场景。"
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
