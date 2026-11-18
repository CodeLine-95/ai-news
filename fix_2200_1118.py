# -*- coding: utf-8 -*-
"""22:00 巡检修复：本轮新增 9 条中有 7 条 NLLB 机翻缺陷，人工定稿。

覆盖三层：
1) data/news.json 内条目直接回填（立即生效）
2) data/titles_override.json / data/summaries_override.json（持久卷 JSON 层）
3) 生成代码层片段，追加进 manual_overrides.py（随发布生效）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = {
    "KPMG's \"Project Exponential\" put AI agents alongside a real audit team and found the bots dug deeper on individual questions": {
        "title_zh": "毕马威「指数级项目」让 AI 智能体与真实审计团队并肩工作，发现机器人对单个问题挖掘更深",
        "summary_zh": "据英国审计业务负责人 Cath Burnet 介绍，毕马威（KPMG）在一家英国上市公司的常规审计中部署了 100 多个 AI 智能体，与审计团队并肩工作；在某些情况下，这些智能体提出了比审计团队「更好的问题」。英国会计监管机构 FRC 认为这种做法存在风险：AI 智能体分析的数据量远超传统抽样方法，可能暴露出一些发现，进而被当作高利润咨询业务的推销切入点，损害审计师的独立性。",
    },
    "Pentera Opens Early Access to Agentic Web App and API Pentesting": {
        "title_zh": "Pentera 开放智能体式 Web 应用与 API 渗透测试产品的早期体验",
        "summary_zh": "Pentera 已将其智能体式 Web 应用与 API 渗透测试产品 Pentera Apps 推进至早期可用阶段。2026 年 11 月 18 日的公告称，已有 60 多家客户在测试版中试用。Pentera 报告的测试版发现包括：未付款的电商结账流程、通过失效的访问控制与多因素认证绕过实现的账户接管，以及通过未经认证的 API 中的 SQL 注入提取客户数据。",
    },
    "Ofqual Plans A Level Assessment Changes Over AI Misuse Risks": {
        "title_zh": "因 AI 滥用风险，英国资格与考试监管办公室 Ofqual 计划调整 A-Level 评估",
        "summary_zh": "首席监管官 Ian Bauckham 爵士在 2026 年 11 月 18 日发布的一封致部分颁证机构负责人的信中表示，Ofqual 将提议对部分 A-Level 科目的非考试评估作出调整，并要求针对可穿戴技术滥用采取更有力的措施。该干预适用于英格兰地区。即将提出的方案将涵盖 A-Level 历史以及三项 A-Level 英语资格。",
    },
    "Checkers & Rally’s Renews Hi Auto AI Drive-Thru Ordering Deal": {
        "title_zh": "Checkers & Rally's 续签 Hi Auto 的 AI 免下车点餐合作协议",
        "summary_zh": "Hi Auto 于 2026 年 11 月 18 日宣布，快餐连锁 Checkers & Rally's 已将其 AI 免下车（drive-thru）点餐合作延长至 2030 年。该公司计划在 2027 年第一季度末前，将部署规模从 267 家免下车餐厅扩大到 360 多家。该计划意味着 Hi Auto 在这两个品牌中的覆盖规模增长 38%，并延续了自 2023 年开始的合作关系。",
    },
    "SEC probes Nvidia over undisclosed chip sales tied to China": {
        "title_zh": "美国证券交易委员会就与中国相关的未披露芯片销售对英伟达展开调查",
        "summary_zh": "美国证券交易委员会（SEC）已对英伟达（Nvidia）启动民事调查。",
    },
    "Starburst Introduces Enterprise Context Layer for AI Agents": {
        "title_zh": "Starburst 推出面向 AI 智能体的企业上下文层",
        "summary_zh": "Starburst Data 于 2026 年 11 月 18 日在 Launch Point 2026 大会上推出其企业上下文层（Enterprise Context Layer），发布 Context Studio 与 AI 就绪数据产品（AI-ready Data Products），旨在让 AI 智能体在访问分布式企业数据的同时，获得受治理的业务语义。Starburst 表示，其 AI 数据助手 AIDA 的最新进展扩展了智能体可回答的问题、可访问的数据以及可支持的工作流，客户自己的智能体也能使用同一套受治理的上下文。",
    },
    "KPMG Brings AI Agents Into U.S. Audits With Clara Intelligence": {
        "title_zh": "毕马威借助 Clara Intelligence 将 AI 智能体引入美国审计业务",
        "summary_zh": "毕马威（KPMG）将受治理的 AI 智能体引入美国审计工作流，随着 Clara 智能能力扩展，审计师仍保留复核与最终判断权。",
    },
}

def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en in FIXES:
            fx = FIXES[en]
            it["title_zh"] = fx["title_zh"]
            it["summary_zh"] = fx["summary_zh"]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it["date"], it["time"], en[:55])

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}
    for en, fx in FIXES.items():
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    with open(os.path.join(BASE, "manual_overrides_2200.snippet"), "w", encoding="utf-8") as f:
        f.write("# TITLE\n")
        for en, fx in FIXES.items():
            f.write("    %r: %r,\n" % (en, fx["title_zh"]))
        f.write("# SUMMARY\n")
        for en, fx in FIXES.items():
            f.write("    %r: %r,\n" % (en, fx["summary_zh"]))
    print("changed:", changed)

if __name__ == "__main__":
    main()
