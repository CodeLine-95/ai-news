# -*- coding: utf-8 -*-
"""19:00 例行巡检：人工定稿本轮 6 条 NLLB 机翻硬伤条目。

本轮 19:00 整点抓取 +6 条（Unite.AI 5 条 / The Decoder 1 条），
NLLB 逐词硬伤包括：Anthropic 误译为「人类」、scale 误译为「测量」、
Archer（公司名）误译为「箭头」、Cedars-Sinai 音译崩坏、
CFO 场景语义走样、Hermes 名称音译不准等。
写入人工定稿标题 + 摘要覆盖表，并回写 data/news.json。
随后 /api/refresh 触发的 update_cycle 应用覆盖表并同步内存/报告。
不加载翻译模型，纯字典写入，不与后台调度器抢内存。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "en": "Alibaba Cloud Adds Third Johor Data Center for Local AI Workloads",
        "title_zh": "阿里云在柔佛增设第三个数据中心，承载本地 AI 工作负载",
        "summary_zh": (
            "阿里云于 2026 年 11 月 19 日宣布，其在马来西亚柔佛（Johor）公有云区域的"
            "第三个数据中心已投入使用，使其在马来西亚的布局增至六个。"
            "此次扩容增加了云与 AI 工作负载的本地算力，服务于需要将数据留在马来西亚境内的机构。"
            "柔佛于 2026 年 6 月成为阿里云在马来西亚的第二个云区域，与吉隆坡的三个数据中心形成互补。"
        ),
    },
    {
        "en": "Regular Tech Bros Are Worried About Honeypots",
        "title_zh": "普通科技男也开始担心「诱饵陷阱」",
        "summary_zh": (
            "黄仁勋丑闻成为新晋富裕且手握权力的科技从业者 dating 焦虑的最新导火索——"
            "他们开始担心自己是否被当成了「诱饵对象」（honeypot）。"
        ),
    },
    {
        "en": "MAS Sets Out Know-Your-Agent Protocol and SG Digital Ledger Plans",
        "title_zh": "新加坡金管局提出「了解你的智能体」协议与 SG 数字账本计划",
        "summary_zh": (
            "新加坡金融管理局（MAS）于 2026 年 11 月 19 日表示，将协助制定面向金融服务的"
            "「了解你的智能体」（know-your-agent）协议，并把其 SGD 测试网重新定位为"
            " SG 数字账本（SG Digital Ledger）——一个运营级结算基础设施，"
            "作为扩展智能体交易与代币化金融计划的一部分。"
            "董事总经理 Chia Der Jiun 在新加坡金融科技节上公布了这些计划。"
        ),
    },
    {
        "en": "Nference Plans Federated AI Research Platform with Cedars-Sinai",
        "title_zh": "Nference 计划与 Cedars-Sinai 共建联邦式 AI 研究平台",
        "summary_zh": (
            "nference 于 2026 年 11 月 20 日宣布与 Cedars-Sinai（雪松西奈）达成长期合作，"
            "将共建一个安全平台，用于分析来自多个患者护理领域的去标识化临床数据。"
            "计划中的研究基础涵盖超过 500 万名患者十余年的记录，可长期追踪其护理过程。"
            "该平台尚待开发，其研究与 AI 功能被描述为预期能力。"
        ),
    },
    {
        "en": "Before You Scale AI Agents, Ask What They Don’t Know",
        "title_zh": "在扩展 AI 智能体之前，先问问它们不知道什么",
        "summary_zh": (
            "试想这样一个场景：一位 CFO 正准备与一家大型机构投资者会面。"
            "为协助准备，投资者关系（IR）团队让一个 AI 工具调取一些背景资料——"
            "上次与该机构会面的日期、其表达的优先事项、持股数量等。"
            "该工具信心十足地声称这位投资者持有 250 万股。"
            "无人提出质疑，CFO 继续全速推进这场重要会面的准备。"
        ),
    },
    {
        "en": "Archer Raises $10M to Expand AI Tools for Candidates and Recruiters",
        "title_zh": "Archer 融资 1000 万美元，扩展面向求职者与招聘方的 AI 工具",
        "summary_zh": (
            "hackajob 旗下的 Archer 于 2026 年 11 月 20 日宣布完成 1000 万美元融资，"
            "由 Volition Capital 领投、AVP 参投，用于扩展面向求职者与招聘团队的 AI 产品。"
            "该公司正应对一个受 AI 生成简历、虚假候选人和小众技能需求影响的招聘市场。"
        ),
    },
    {
        "en": "Anthropic-Anchored AI Campus Draws 595 Objections or Delay Requests",
        "title_zh": "以 Anthropic 为锚的 AI 园区引来 595 项反对或延期请求",
        "summary_zh": (
            "路透社 2026 年 11 月 20 日报道，代表开发商 Zerra DC 提交的一份文件中，"
            "针对其在昆士兰州拟建的 Western Downs 数字公园，共有近 600 份公众意见："
            "595 份反对这座以 Anthropic 为锚的 AI 园区，或要求在满足特定环境要求前推迟建设，"
            "2 份支持，1 份中立。反对者主要提及用水、电力需求与价格、噪音、"
            "施工交通造成的道路损坏以及住房压力。"
        ),
    },
    {
        "en": "UK Departments Issue First Cross-Sector AI Guidance for Social Care",
        "title_zh": "英国多部门发布首份社会照护领域跨行业 AI 指南",
        "summary_zh": (
            "英国卫生和社会照护部与教育部于 2026 年 11 月 20 日宣布联合发布全国性指南，"
            "涵盖儿童与成人社会照护中人工智能（AI）的使用。"
            "他们称这是同类首份跨行业指南，并援引一项当地试点，称其行政时间减少了 63%。"
        ),
    },
    {
        "en": "Hermes Agent's Collective Wisdom feature turns one employee's AI trick into the whole team's skill",
        "title_zh": "Hermes 智能体的「集体智慧」功能，把一名员工的 AI 技巧变成整个团队的技能",
        "summary_zh": (
            "企业很快就能在 Microsoft Teams 内部直接运行来自 Nous Research 的开源 Hermes 智能体。"
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
                print("[fix_1900] %s覆盖表写入: %s" % (label, fx["en"][:45]))
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
                it["method"] = "nllb+manual"
                hit += 1
                print("[fix_1900] 回写数据: %s" % en[:45])
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("[fix_1900] 完成，回写条目 %d" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
