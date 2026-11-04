# -*- coding: utf-8 -*-
"""2026-11-03 09:00 巡检：人工定稿本轮抓取中译文质量差的条目。

本轮 09:00 抓取新增 4 条，巡检发现 4 类译文缺陷（均已回写 translate.py
作为根因规则，见 TERM_FIXES 2026-11-03 09:00 段）：

1) 品牌名被当普通词意译
   - "Brave"（浏览器厂商）→ 「勇敢」，标题整句变成「勇敢面临两家出版商诉讼」，
     中文读者无法定位公司。
   - "The Letter Company" → 标题里整段品牌丢失，只剩「公司发布了…」；
     摘要里变成「字母公司」「字母团队」「信显示」「每封信」。
   - "Y Combinator" → 「Y 组合者」，机构名彻底丢失。
   根因规则已加（品牌还原 + TERM_FIXES），但标题丢失整段品牌、
   摘要语序崩坏，规则无法整句修复，故人工定稿兜底。

2) 通用术语直译失真
   - "pull request" → 「带动请求」（已有规则只覆盖「拉动请求」）
   - "git repository" → 「吉特库」（Git 是专名，不该音译）
   - "fine-tuned" → 「精细调节」（应为「微调」）
   - "implied enterprise value" → 「企业价值意味着」（应为「隐含企业价值」）

3) 引号配对崩坏
   - Garry Tan 一条的英文原文本身引号不成对（"cyber psychosis” ），
     模型沿用了错位引号，中文变成
     「他患有“网络精神病，有时几乎睡不着……播客”构建者“的新集中」，
     三个引号段互相嵌套错位，完全无法阅读。

4) 长摘要被截断在半句
   - Letterpress-1 一条的摘要结尾停在「最糟糕」后被腰斩，
     且开头「这是一个用于增长工程的编码智能体，利用和 IDE 的编码智能体」
     是把 "a coding agent, harness and IDE" 拆坏的病句。

以下为人工逐条重写的中文译文。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    # 原文："Brave Faces Two Publisher Lawsuits Over AI Use of News Content"
    # 直译「勇敢面临两家出版商诉讼，涉及人工智能使用新闻内容」——
    # "Brave" 是浏览器厂商名（隐私浏览器 Brave），
    # 被 NLLB 当普通英文形容词意译成「勇敢」，标题主语完全错位。
    "Brave Faces Two Publisher Lawsuits Over AI Use of News Content":
        "Brave 面临两家出版商诉讼，指其将新闻内容用于 AI",
    # 原文："The Letter Company Releases Letterpress-1: A Coding Agent Built for Growth Engineering"
    # 直译「公司发布了 Letterpress-1：一个用于增长工程的编码智能体」——
    # "The Letter Company" 整段品牌词被丢掉，只剩「公司」，
    # 中文读者无从知道是哪家公司发布的。
    "The Letter Company Releases Letterpress-1: A Coding Agent Built for Growth Engineering":
        "The Letter Company 发布 Letterpress-1：为增长工程打造的编码智能体",
    # 原文："Y Combinator's Garry Tan uses AI agents so much, he spends up to $200K a year on tokens"
    # 直译「Y 组合者加里·坦使用 AI 智能体如此多，他每年花费多达 20 万美元购买 token」——
    # "Y Combinator" 是美国顶级加速器机构名，被意译成「Y 组合者」；
    # 且「如此多」是 "so much" 的逐词直译，中文不成句。
    "Y Combinator’s Garry Tan uses AI agents so much, he spends up to $200K a year on tokens":
        "Y Combinator 的加里·坦使用 AI 智能体如此频繁，每年在 token 上花费高达 20 万美元",
    # 原文："Marvell Agrees to Acquire Lumentum in All-Stock AI Connectivity Deal"
    # 直译「马维尔同意收购 Lumentum 在全股人工智能连接交易中」——
    # "Marvell" 被音译成「马维尔」（并购语境下应保留英文原名，
    # 与摘要里的 "Marvell Technology" 统一），且介词短语堆在句尾，
    # 中文语序需要调整。
    "Marvell Agrees to Acquire Lumentum in All-Stock AI Connectivity Deal":
        "Marvell 同意以全股票交易收购 Lumentum，布局 AI 互联",
}

SUMMARY_FIX = {
    # 原文摘要："The New York Times Company filed a federal complaint against
    # Brave Software ... through Brave's search index, AI services and browser."
    # 直译把 Brave 的三处品牌名分别译成「勇敢」/「勇敢的搜索索引」/「勇敢人」，
    # 且媒体名「New York Daily News / Chicago Tribune / Orlando Sentinel」
    # 被译成「纽约日报/芝加哥论坛/奥兰多卫报」，读者无法定位。
    "Brave Faces Two Publisher Lawsuits Over AI Use of News Content":
        "2026 年 11 月 2 日，《纽约时报》公司向 Brave Software 提起联邦诉讼，"
        "指其通过 Brave 搜索索引、AI 服务与浏览器，未经授权复制并分发其新闻内容。"
        "同日，《纽约日报》《芝加哥论坛报》与《奥兰多哨兵报》的出版方"
        "在纽约南区联邦地区法院另行对 Brave 提起诉讼。",
    # 原文摘要含 "a coding agent, harness and IDE"（被拆成病句
    # 「编码智能体，利用和 IDE 的编码智能体」）、"git repository"（吉特库）、
    # "fine-tuned small models"（精细调节的小模型）、"pull request"（带动请求）、
    # "per Letter"（每封信）、"Letter shows"（信显示），
    # 且整段被腰斩在「最糟糕」，语义不完整。人工整段重写。
    "The Letter Company Releases Letterpress-1: A Coding Agent Built for Growth Engineering":
        "The Letter Company 发布了 Letterpress-1 的 beta 版本，"
        "这是一款面向增长工程的编码智能体，配套编排框架与 IDE。"
        "Letterpress-1 编码智能体先读取一个网站及其市场，再判断应该构建什么；"
        "它在沙箱中完成改动，并发起带实时预览的拉取请求。"
        "速览：规模——Letter 团队称其结合了前沿模型与微调后的小模型，"
        "具体名称与参数量均未公开。"
        "运行方式：运行在 Letter 的托管平台上，对接你的 Git 仓库，无需本地 GPU；"
        "按 Letter 的说法，5 分钟内即可完成配置。"
        "性能：没有公开基准，Letter 给出 1 组自报数据，"
        "即与 Codex 并排对比的一次页面构建。"
        "优点：通过 1 个注册表，以 MCP、REST 和 CLI 三种方式对外暴露 760 个工具。"
        "缺点：没有可量化的评测；入门方案为每月 100 美元，超额用量按标价的 5 倍计费。"
        "Letterpress-1 是什么？它是 The Letter Company 推出的一款增长工程智能体。",
    # 原文摘要的引号本身不成对（"cyber psychosis” ），模型沿用错位引号后，
    # 中文出现三个互相嵌套错位的引号段，完全无法阅读。
    # 另 "The Builders"（播客名）被译成「构建者」并与引号缠绕。
    "Y Combinator’s Garry Tan uses AI agents so much, he spends up to $200K a year on tokens":
        "Y Combinator 的加里·坦（Garry Tan）开玩笑承认自己患上了「网络精神病」，"
        "有时几乎无法入睡，因为他实在太兴奋能与自己的 AI 智能体协作。"
        "在 Walter Isaacson 的播客《Builders》新一期中，坦为这份热情标上了价。",
    # 原文摘要："...an all-stock transaction with an implied enterprise value of
    # $115 billion..." 直译成「其企业价值意味着 1150 亿美元」——
    # "implied" 被漏译，且「企业价值意味着」是病句；
    # 财务并购语境的标准说法是「隐含企业价值」。
    "Marvell Agrees to Acquire Lumentum in All-Stock AI Connectivity Deal":
        "2026 年 11 月 2 日，Marvell Technology 与 Lumentum 在联合公告中表示，"
        "双方已就 Marvell 以全股票交易收购 Lumentum 达成最终协议，"
        "交易隐含企业价值 1150 亿美元，将电气与光学技术整合用于 AI 互联。"
        "交割时，每股 Lumentum 普通股将转换为 4.500 股 Marvell 普通股，"
        "不足一股的部分以现金支付。",
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    hit_t = hit_s = 0
    for it in items:
        t = it.get("title", "")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_t += 1
            print("fix title:", it["date"], it["time"], it["source"], "|", t[:56])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_s += 1
            print("fix summary:", it["date"], it["time"], it["source"])

    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    for name, fix in (("titles_override.json", TITLE_FIX),
                      ("summaries_override.json", SUMMARY_FIX)):
        path = os.path.join(DATA, name)
        cur = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                cur = json.load(f)
        cur.update(fix)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=2)

    print("fixed titles:", hit_t, "/", len(TITLE_FIX))
    print("fixed summaries:", hit_s, "/", len(SUMMARY_FIX))
    if hit_t != len(TITLE_FIX) or hit_s != len(SUMMARY_FIX):
        raise SystemExit("覆盖未全部命中，请检查英文原标题是否一致")


if __name__ == "__main__":
    main()
