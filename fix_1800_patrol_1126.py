# -*- coding: utf-8 -*-
"""18:00 例行巡检：定稿 7 条新增条目的 NLLB 机翻腔。

18:00 整点抓取净新增 7 条（Unite.AI 6 条 + The Verge 1 条），
NLLB 机翻出现专名直译与语义误译：
- WaterSense -> 「水 Sense」；Oder mouth -> 「口头」（应为河口）
- LINE Taiwan -> 「台湾线路」
- Dragos -> 「龙虎」；seeded prompts -> 「种植的提示」
- Hon Hai -> 「海」/「荣海」；Beihai AI Center -> 「贝海」
- promptable OCR -> 「即时的 OCR」；abstention -> 「禁忌」
- oracles -> 「神言」（应为预言机）；Beam Foundation -> 「梁基金会」
- state AGs -> 「州总裁」；Chapter 11 -> 「导航第 11 章」

按项目既有模式回填 news.json + JSON 覆盖表，再由
scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "WaterSense Raises €5.75M in Pre-Seed and Grants for AI Water Monitoring": (
        "WaterSense 获 575 万欧元种子前轮融资与补助，用于 AI 水质监测",
        "WaterSense 于 2026 年 11 月 26 日宣布，已通过种子前轮投资与补助合计筹集 575 万欧元，用于扩展覆盖欧洲的 AI 辅助水质监测，包括从源头到河口持续监测奥得河（Oder River）的计划。该种子前轮由 b2venture 与 Movens Capital 联合领投，vastpoint 参投。公告还单独提到波兰国家研究与发展中心提供的 350 万欧元，用于进一步开发传感器并集成卫星数据。相关工作将新增对铵离子、硝酸盐、正磷酸盐、氟化物、铅和大肠杆菌的测量，把分析从单个监测站扩展到整个水体与水道。",
    ),
    "LINE Taiwan Unveils Three-Part AI Agent Strategy for Businesses": (
        "LINE 台湾发布面向企业的三部分 AI 智能体战略",
        "在 2026 年 11 月 26 日举行的 LINE BIZ CONVERGE 2026 上，LINE 台湾表示将推进涵盖消费者助手、品牌服务与商家运营的三部分 AI 智能体战略，依托超过 360 万个官方账号，让客户互动从回答问题走向完成任务。该战略把消费者触达、品牌履约与商家决策串联起来。",
    ),
    "Dragos Identifies MiniMax in AI Prompt Privacy Investigation": (
        "Dragos 在 AI 提示词隐私调查中确认 MiniMax 涉案",
        "路透社 2026 年 11 月 26 日报道，Dragos 首席研究官 HD Moore 在对近 200 万条植入式 AI 提示词展开的更广泛调查中，确认此前未具名的中国 AI 开发商为 MiniMax。研究人员发现，即使用户要求不存储或保留数据，私人网页链接仍会在随后被打开。路透社称，公开指认以及莫斯科地区的相关发现均为首次报道。",
    ),
    "Hon Hai Unveils Integrated Chemotherapy Automation System": (
        "鸿海推出一体化化疗自动化系统",
        "鸿海科技集团于 2026 年 11 月 26 日宣布，其与台北荣民总医院共同推出一套自动化系统，打通化疗药物配置、院内药品运输与护理任务。双方还在台北启用了北海 AI 中心（Beihai AI Center）。该系统把多家公司的设备与软件整合为统一的临床工作流。",
    ),
    "BharatGen Launches Patram 1.5 with Promptable OCR and Abstention": (
        "BharatGen 发布 Patram 1.5，支持可提示 OCR 与拒答能力",
        "BharatGen 于 2026 年 11 月 25 日推出 Patram 1.5——一个面向文档智能的 78 亿参数开放权重视觉语言模型。其两项核心新增能力是可通过提示控制的 OCR，以及「弃权」（abstention）：在证据缺失或相互矛盾、输入难以辨认或问题含义模糊时，模型会保留答案而不作答。文本优先的提取流程可以把赋予文档意义的信息扁平化。",
    ),
    "Cournot Raises $5M Strategic Funding to Make AI Reasoning Verifiable": (
        "Cournot 获 500 万美元战略融资，致力于让 AI 推理可验证",
        "Cournot Protocol 在 2026 年 11 月 26 日的公告中称，已获得由 Paper Ventures 与 Beam Foundation 联合领投的 500 万美元战略融资。这笔资金将用于为链上应用与 AI 智能体构建可验证的智能层。Cournot 公开宣称的使命，是拓展预言机（oracle）超越结构化数据的能力：用 AI 解读真实世界事件，同时保留记录，使由此得出的判断可被复核。",
    ),
    "42 state AGs are trying to stop Character.AI from selling users’ chats": (
        "42 位州总检察长试图阻止 Character.AI 出售用户聊天记录",
        "由 42 位州总检察长组成的联盟正试图阻止 Character.AI 在第 11 章破产程序中出售用户数据。在大量近乎相同的新闻稿中，各位总检察长指控该公司计划拍卖「超过 2100 万个美国账户的私人聊天记录，其中逾 210 万个账户属于未成年人，且对被出售对话的当事人没有任何保护措施」。Character.AI 于 10 月申请破产，此前多年间深陷丑闻与法律挑战，其中包括来自迪士尼的诉讼。",
    ),
}


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    matched = set()
    for it in items:
        en = it.get("title") or ""
        if en not in FIX:
            continue
        matched.add(en)
        title_zh, summary_zh = FIX[en]
        if it.get("title_zh") != title_zh:
            it["title_zh"] = title_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] title:", en[:60], "->", title_zh)
        if it.get("summary_zh") != summary_zh:
            it["summary_zh"] = summary_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] summary:", en[:60])
        tov[en] = title_zh
        sov[en] = summary_zh

    missing = set(FIX) - matched
    if missing:
        print("[warn] 未匹配到条目:", missing)

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 变更 %d 处 | 覆盖表 标题 %d 条 / 摘要 %d 条"
          % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
