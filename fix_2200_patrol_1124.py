# -*- coding: utf-8 -*-
"""2026-11-24 22:00 例行巡检：定稿本轮新增 11 条 NLLB 机翻硬伤。

本轮整点调度新增 11 条（total 2720 -> 2731），全部为 NLLB 原始机翻，硬伤包括：
1) Waystar 收入周期/revenue-cycle 误作「收入周期人工智能」，Gemini for healthcare 语义不顺；
2) Avicena 的 $100M+ 被削成「1 亿美元」（漏 +），Series C、microLED optical interconnect 译法生硬；
3) Ambarella（安霸）/Sigma Connectivity 被音译错乱，industrialize 误作「工业化边缘 AI」；
4) Automation Anywhere 被直译为「自动化任何地方」，half a billion 硬伤译成「近 50 亿次」（应为 5 亿）；
5) Nuro 的 Lucid Gravity 被误译为「Lucid 重力机器人」，robotaxi/driverless 语义错位；
6) Roscosmos 条 2.4 metric tons 漏单位（「超过 2.4 的货物」），Progress MS-36 语序错乱；
7) 10Web 条 working commercial websites 误作「运营商业网站」，来源列表需准确；
8) Verra（SiliconANGLE）forget institutional amnesia 被误译为「忘记机构失忆」（语义反了）；
9) Dante Security 的 human owners 误作「人类拥有者」，应为「人类负责人」；
10) Verra（Unite.AI）institutional memory 误作「机构内存」，traceable sources 误作「可追踪的来源」；
11) Zipher 种子轮+A 轮 音译错乱（「齐弗」），valuation 语义失真。

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
        "title": "Waystar Plans Revenue-Cycle AI Integration with Gemini for Healthcare",
        "title_zh": "Waystar 计划将收入周期 AI 分析与 Google Cloud 医疗版 Gemini 集成",
        "summary_zh": (
            "Waystar 于 2026 年 11 月 24 日宣布，将把其 AI 驱动的收入周期分析与保险资格核验工具，"
            "与 Google Cloud 面向医疗行业的 Gemini 集成。此举将让医疗服务提供方通过自然语言交互"
            "来查询付款表现、发起资格核验，而无需在多个独立系统之间切换。"
        ),
    },
    {
        "title": "Avicena Raises $100M+ Series C to Commercialize microLED Optical Links",
        "title_zh": "Avicena 完成逾 1 亿美元 C 轮融资，推进 microLED 光互连商业化",
        "summary_zh": (
            "Avicena 于 2026 年 11 月 24 日宣布，已募集超过 1 亿美元的 C 轮融资，用于将面向 AI "
            "基础设施的 microLED 光互连平台 LightBundle 推向商业化。InterVest 领投本轮，Kevin "
            "Pope 将接替 Marco Chisari 出任首席执行官。本轮吸引了新老投资者参与。"
        ),
    },
    {
        "title": "Ambarella Teams With Sigma Connectivity to Industrialize Edge AI",
        "title_zh": "安霸（Ambarella）与 Sigma Connectivity 合作推进边缘 AI 量产",
        "summary_zh": (
            "安霸（Ambarella）与 Sigma Connectivity 于 2026 年 11 月 24 日宣布战略合作，帮助制造"
            "商将计算机视觉与边缘 AI 原型转化为可量产的产品。安霸将提供低功耗 AI 芯片与软件工具，"
            "Sigma Connectivity 负责量产所需的工程与验证工作。此次合作面向原始设备制造商（OEM）"
            "以及为联网设备增添 AI 功能的企业。"
        ),
    },
    {
        "title": "Automation Anywhere Closes Boost.ai Deal to Automate Customer Service",
        "title_zh": "Automation Anywhere 完成收购 Boost.ai，强化客户服务自动化",
        "summary_zh": (
            "Automation Anywhere 于 2026 年 11 月 24 日宣布完成对 Boost.ai 的收购，将面向受监管"
            "行业的对话式与语音 AI 纳入其服务逾 4000 家客户的智能体自动化平台。合并后的方案旨在"
            "把客户请求从对话一路推进到跨企业系统的实际完成。该公司称其每年执行近 5 亿次 AI "
            "智能体与自动化任务。"
        ),
    },
    {
        "title": "Nuro Begins Driverless Lucid Gravity Robotaxi Tests in Bay Area",
        "title_zh": "Nuro 在湾区启动 Lucid Gravity 无人驾驶 Robotaxi 测试",
        "summary_zh": (
            "Nuro、Lucid 与 Uber 在 2026 年 11 月 24 日的 Nuro 公告中表示，Lucid Gravity Robotaxi "
            "已在旧金山湾区启动完全无人驾驶的公开道路测试，标志着三方联合项目在筹备载客服务之际，"
            "超越了此前的有人监督试验阶段。测试正在帕洛阿尔托、山景城、洛斯阿尔托斯和桑尼维尔"
            "进行，并计划于 2027 年扩展至更多湾区城市。"
        ),
    },
    {
        "title": "Roscosmos Launches Teledroid Humanoid Robot on Progress MS-36",
        "title_zh": "俄罗斯国家航天集团搭乘进步 MS-36 发射 Teledroid 类人机器人",
        "summary_zh": (
            "俄罗斯国家航天集团（Roscosmos）于 2026 年 11 月 24 日向国际空间站发射进步 MS-36"
            "（Progress MS-36）货运飞船，搭载一台用于 Teledroid 实验的类人机器人。联盟 2.1b 火箭"
            "于莫斯科时间 13:17 从拜科努尔升空，运送超过 2.4 吨货物。飞船进入预定轨道，与火箭第"
            "三级分离，并按计划展开天线与太阳能电池板。"
        ),
    },
    {
        "title": "10Web turns social media profiles into working commercial websites",
        "title_zh": "10Web 将社交媒体主页变成可运营的商业网站",
        "summary_zh": (
            "AI 网站构建工具 10Web Inc. 正在推出一项新功能，据称可自动将 Instagram、TikTok、"
            "Etsy、Google 商家资料等 30 多个来源的内容转化为可用的网站和在线商店。"
        ),
    },
    {
        "title": "Verra raises $5M to help consulting firms forget their institutional amnesia",
        "title_zh": "Verra 融资 500 万美元，帮咨询公司摆脱「机构失忆」",
        "summary_zh": (
            "为咨询公司构建机构记忆层的 AI 初创公司 Verra 今日表示，已完成 500 万美元种子轮融资，"
            "帮助这些公司克服知识遗忘，让沉淀数十年的知识为每一位员工所用。"
        ),
    },
    {
        "title": "Dante Security Raises $10 Million to Give Enterprise AI Agents Human Owners",
        "title_zh": "Dante Security 融资 1000 万美元，为企业 AI 智能体指定人类负责人",
        "summary_zh": (
            "由 NFX 领投的这轮种子融资支持一个企业平台，该平台将 AI 智能体的活动与具名的人类"
            "负责人关联，帮助安全团队审查智能体的行为。"
        ),
    },
    {
        "title": "Verra Raises $5 Million to Build AI-Powered Institutional Memory for Consulting Firms",
        "title_zh": "Verra 融资 500 万美元，为咨询公司打造 AI 驱动的机构记忆",
        "summary_zh": (
            "Verra 的种子融资支持一个 AI 平台，帮助咨询团队复用既往工作，并以可追溯的来源起草"
            "新的交付物。"
        ),
    },
    {
        "title": "Zipher Raises $53M Across Seed and Series A Rounds to Automate Data Workloads",
        "title_zh": "Zipher 在种子轮与 A 轮共融资 5300 万美元，实现数据工作负载自动化",
        "summary_zh": (
            "Zipher 已在种子轮与 A 轮融资中累计筹集 5300 万美元，用于自动化企业数据负载在云端的"
            "运行方式。该公司称 TLV Partners、Maor Investments 和 Glilot Capital 参与了这些轮次，"
            "但未披露各轮金额与估值。资金将用于研发和扩大销售，包括扩建美国企业销售团队并拓展"
            "美国以外市场。"
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
