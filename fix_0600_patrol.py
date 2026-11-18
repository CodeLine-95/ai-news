# -*- coding: utf-8 -*-
"""06:00 例行巡检：人工定稿 10 条 NLLB 机翻硬伤 + 补全 1 条空摘要。

本轮（05:03–05:57）新增 11 条，问题包括：
- 品牌/公司名误译：Synaptiq→赛纳普蒂克、Kulicke & Soffa→库利克和索法、
  Palo Alto Networks→帕洛阿尔托网络、Anduril→安德鲁尔/安杜里尔、Applied Compute→应用计算
- 术语错：tumor contouring→瘤划线、organ-at-risk→危险器官轮、CT contouring→CT 轮时间、
  bonding→结合、Jensen out→詹森退役、intrigue→阴谋
- 语义崩坏："与速度放射治疗规划""美国变得更弱""奇怪的阴谋"
- Google DeepMind「Introducing Gemini 4 Neon」源摘要为空，按同批发布信息补全

固化覆盖三层：
1) data/news.json 内条目直接回填
2) data/titles_override.json / data/summaries_override.json（JSON 层）
3) 再运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = [
    {
        "match": "Synaptiq Combines AI Tumor and Organ Contouring to Speed Radiotherapy Planning",
        "title_zh": "Synaptiq 融合 AI 肿瘤与危及器官勾画，加速放射治疗规划",
        "summary_zh": (
            "Synaptiq 正通过其 Mediq RT 平台，将 AI 辅助的肿瘤勾画与危及器官（organ-at-risk）"
            "勾画整合到统一的放射治疗规划工作流程中。这家罗马尼亚医疗科技公司表示，临床评估"
            "显示 CT 勾画时间平均减少 92.6%，其中已包含临床医生审核与修正 AI 结果所花的时间。"
        ),
    },
    {
        "match": "America’s AI Chip War Is Heating Up in the Dumbest Possible Ways",
        "title_zh": "美国的 AI 芯片战争正以最愚蠢的方式升温",
        "summary_zh": (
            "特朗普政府宣布计划收紧中国获取 AI 芯片的渠道。显然，「世纪作弊丑闻」正是他们"
            "此前所缺少的动机。"
        ),
    },
    {
        "match": "Kulicke & Soffa Ships Panel-Level Bonding Systems for AI Packages",
        "title_zh": "库力索法出货面向 AI 封装的面板级键合系统",
        "summary_zh": (
            "库力索法（Kulicke & Soffa）于 2026 年 11 月 18 日宣布，已向台湾两家主要客户交付"
            " APTURA WSX 面板级键合系统，将其无助焊剂热压（FTC）工艺从晶圆生产扩展到面向人工"
            "智能（AI）与高性能计算（HPC）的更大尺寸封装。此举将 K&S 现有的 FTC 工艺从细间距"
            "晶圆上芯片（chip-on-wafer）生产，拓展到更大尺寸的面板上芯片（chip-on-panel）流程。"
        ),
    },
    {
        "match": "Palo Alto Networks Reaches $4.5B Agreement for Applied Compute",
        "title_zh": "Palo Alto Networks 达成 45 亿美元收购 Applied Compute 的协议",
        "summary_zh": (
            "Palo Alto Networks 于 2026 年 11 月 18 日宣布，已达成最终协议，以全股票交易方式"
            "收购 Applied Compute，交易价值 45 亿美元（可作调整）。Applied Compute 的平台让"
            "企业能够适配并运行开放权重 AI 模型。该交易仍需满足包括监管批准在内的常规交割条件，"
            "Palo Alto Networks 预计将于其 2027 财年第三季度完成交易。"
        ),
    },
    {
        "match": "Palmer Luckey thinks China is ‘thrilled to have Jensen out,’ so he wants the ousted Nvidia CEO reinstated",
        "title_zh": "帕尔默·卢基认为中国「乐见黄仁勋下台」，因此希望这位被罢免的英伟达 CEO 复职",
        "summary_zh": (
            "Anduril 首席执行官帕尔默·卢基在谈到被罢免的英伟达领导人黄仁勋时表示："
            "「把他赶下台会让美国变得更弱。」"
        ),
    },
    {
        "match": "Palmer Luckey warns AI-powered cyberattacks are outpacing defenses: ‘It’s time to start running’",
        "title_zh": "帕尔默·卢基警告 AI 驱动的网络攻击已超越防御能力：「是时候开始奔跑了」",
        "summary_zh": (
            "这家 Anduril 联合创始人表示，过时的技术正使系统容易受到新一波 AI 驱动攻击的侵害。"
        ),
    },
    {
        "match": "Introducing Gemini 4 Neon",
        "title_zh": "Gemini 4 Neon 登场",
        "summary_zh": (
            "Google DeepMind 发布 Gemini 4 Neon。这是面向软件开发、知识工作与科学任务的新一代"
            "前沿模型，支持文本、图像、视频、音频与 PDF 文件输入，并具备百万 token 的上下文窗口。"
            "该模型已通过 Gemini API 与 Google AI Studio 开放使用。"
        ),
    },
    {
        "match": "Google Launches Gemini 4 Neon for Coding, Knowledge Work and Science",
        "title_zh": "Google 推出面向编程、知识工作与科学的 Gemini 4 Neon",
        "summary_zh": (
            "2026 年 11 月 18 日，Google 在其 Gemini API 发布说明中宣布 Gemini 4 Neon 正式可用，"
            "推出面向软件工程、知识工作与科学的付费模型：每百万输入 token 3 美元、每百万输出 "
            "token 15 美元。稳定的 gemini-4-neon 端点可通过 generateContent 与 Interactions API "
            "调用，也可通过 Google AI Studio 中的 Google AI Pro 与 Ultra 套餐使用。"
        ),
    },
    {
        "match": "Recent spate of outages attributed to technical issues amid accelerated AI bug discovery",
        "title_zh": "近期一连串故障归因于技术问题，AI 加速漏洞发现引发关注",
        "summary_zh": (
            "美国当局认为，近期联邦机构与顶尖科技公司发生的故障并非由网络攻击造成。受影响"
            "的组织包括美国联邦航空管理局、联合航空、Apple 与微软。四者均表示，其系统中断源于"
            "技术问题而非黑客攻击。专家指出，人工智能模型正加速漏洞发现，使此类技术问题的"
            "暴露与修复节奏加快。"
        ),
    },
    {
        "match": "Nvidia created a weird bit of intrigue by not filing a routine SEC report",
        "title_zh": "英伟达未提交例行 SEC 报告，引发一番离奇揣测",
        "summary_zh": (
            "一位华尔街分析师厘清了英伟达这则令人意外的公告的来龙去脉：该公司将延迟数周才提交"
            "正式的季度业绩文件（10-Q）。"
        ),
    },
]


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    for fx in FIXES:
        hit = None
        for it in items:
            if fx["match"].lower() in (it.get("title") or "").lower():
                hit = it
                break
        if not hit:
            print("MISS:", fx["match"])
            continue
        en = hit["title"]
        hit["title_zh"] = fx["title_zh"]
        hit["summary_zh"] = fx["summary_zh"]
        hit["translated"] = True
        hit["method"] = "nllb+manual"
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
        changed += 1
        print("fixed:", hit.get("date"), hit.get("time"), en[:70])

    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("changed:", changed, "/", len(FIXES))


if __name__ == "__main__":
    main()
