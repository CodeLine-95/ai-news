# -*- coding: utf-8 -*-
"""2026-11-03 02:00 巡检：修复 7 条新增资讯的译文缺陷。

根因（已定位到代码级，不是随机噪声）：

1) `_align_numbers` 把「November」的中文月份「11 月」当成「中文侧多余数字」
   回填成「1 月」——英文月份是单词（November），不产生数字 token，
   中文却是「11 月」的纯数字，两侧数字集合永远对不齐；
   而英文品牌名 ON1 里的数字 1 恰好与 11 的数字集合 {1} 相似度达 1.0，
   于是「11 月」被「1」覆盖。同一机制已污染存量条目（2026-10-21 一条）。

   修复方向（见 translate.py）：把「N 月」标记为月份位置，与已有的
   「万/亿」量级词一样排除出「多余数字」候选池——月份本就无法与英文
   单词对齐，不该参与回填。

2) NLLB 对新出现的实体名还原不足：
   - Photo RAW → 「照片 RAW」（应为产品名 Photo RAW）
   - ON1 → 被整词吞掉
   - LifeVal → 「生命 Val」
   - seed funding → 英文残留未译
   - Culling Assistant → 「AI 除助手」（实为「AI 挑图助手」）
   - Silicon Valley → 「谷地址」
   - TechCrunch Founder Summit → 「TechCrunch 创始人峰会」被拆译
   - agentic → 「代理分析」（应为「智能体分析」）
   - 42AI 的 $62.5M → 「6250 万美元」（缺千分位）且伴随「行为世界模型种子资金」语序错乱

3) MIT Tech Review 摘要中间的「DOWNLOAD THE REPORT」是站点 CTA 噪声，
   夹在正文中间，尾部分类器清不掉。

本脚本做两件事：
  A. 用人工定稿覆盖受影响条目（标题 + 摘要），写回 news.json 与 JSON 覆盖表；
  B. 给 translate.py 补确定性规则与月份对齐逻辑（由 main 步骤执行），
     让同类缺陷在后续每小时的自动抓取中自愈，而不是每轮靠人工兜底。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    # ON1 被整词吞掉 + Photo RAW 被译成「照片 RAW」+ "With" 被吞
    "ON1 Brings Photo RAW 2027 to Mac and Windows With Local AI Tools":
        "ON1 发布 Photo RAW 2027，为 Mac 与 Windows 带来本地 AI 工具",
    # 整句是目录式汇总，无需逐词直译
    "The latest AI news we announced in October 2026":
        "我们在 2026 年 10 月公布的最新 AI 资讯",
    # 「行为世界模型」译法可保留，补「6,250」千分位
    "42AI Launches a Behavioral World Model to Predict Human Decisions":
        "42AI 推出行为世界模型，用于预测人类决策",
    # 职位 COO 被并入「联合创始人」语序，译作「首席运营官兼联合创始人」更准确
    "Sarah Webb, COO and Co-Founder of LawVu – Interview Series":
        "Sarah Webb：LawVu 首席运营官兼联合创始人",
    # $62.5M 被译成「6250 万美元」+ 语序倒装
    "42AI Secures $62.5M in Seed Funding for Behavioral World Model":
        "42AI 获 6,250 万美元种子轮融资，打造行为世界模型",
    # agentic analytics 被译成「代理分析」，AI 语境应为「智能体分析」
    "Raising the quality of insights in agentic analytics":
        "提升智能体分析中洞察的质量",
    # LifeVal 品牌名被拆成「生命 Val」
    "LifeVal":
        "LifeVal：衡量 AI 助力日常任务的基准",
    # TechCrunch 创始人峰会被拆译 + "Silicon Valley" 译成「谷地址」
    "2 days till TechCrunch Founder Summit: Boston founders don’t need a Silicon Valley address to build something big":
        "TechCrunch 创始人峰会倒计时 2 天：波士顿创始人不靠硅谷地址也能做大",}

SUMMARY_FIX = {
    "ON1 Brings Photo RAW 2027 to Mac and Windows With Local AI Tools":
        "ON1 于 2026 年 11 月 2 日发布面向 Mac 与 Windows 的 Photo RAW 2027，"
        "新增 RAW 处理引擎、改进版 NoNoise AI 模型，以及仅在 MAX 版本中提供的 AI 挑图助手。"
        "Photo RAW 2027 与 Photo RAW MAX 2027 均以独立应用形式运行，"
        "共享核心编辑、AI 与整理工具。此次发布是 Photo RAW 2026 完成 10 次免费更新之后的又一次升级。",
    "The latest AI news we announced in October 2026":
        "以下是 Google 在 2026 年 10 月公布的最新 AI 资讯汇总。",
    "42AI Launches a Behavioral World Model to Predict Human Decisions":
        "大多数 AI 系统是为解读信息或生成答案而构建的，42AI 提出的却是另一个问题："
        "当情况变化时，一个具体的人会如何反应？这家公司已走出隐身模式，"
        "推出所谓的「行为世界模型」，把人类行为定位为企业 AI 中一类独立的预测问题。"
        "这家特拉维夫公司表示，迄今已累计融资 6,250 万美元，并将首先在金融行业落地。",
    "Sarah Webb, COO and Co-Founder of LawVu – Interview Series":
        "Sarah Webb 是 LawVu 的首席运营官兼联合创始人，具备工程与软件管理背景，"
        "曾任职于 LOVEFiLM 和 Amazon。她于 2015 年加入 LawVu 担任首席技术官，"
        "2020 年升任首席运营官，横跨技术、运营、安全与治理等领域。"
        "她的工作重点是帮助法律团队打通数据与工作流，"
        "同时在 AI 创新与企业风险之间取得平衡。",
    "42AI Secures $62.5M in Seed Funding for Behavioral World Model":
        "TechCrunch 于 2026 年 11 月 2 日报道，以色列初创公司 42AI 已走出隐身模式，"
        "获得 6,250 万美元种子轮融资，并推出一款在金融经纪商场景中运行的行为世界模型。"
        "创始人告诉 TechCrunch，该系统能估算个人客户在环境变化下的行为概率。",
    "Raising the quality of insights in agentic analytics":
        "短短几年间，生成式 AI 已改变企业分析的面貌，尤其是让整个组织的用户都能用上分析工具。"
        "智能体 AI 承诺做得更多：通过自动化整个工作流，并基于智能体洞察采取行动。"
        "但问题在于：当前智能体生成的洞察质量仍有很大提升空间。"
        "在本报告调研的组织中，智能体生成的洞察里不足一半真正带来了业务改进。"
        "多数受访者虽称赞其智能体描述性洞察的质量，"
        "但对处方性洞察（即据以采取行动的那些洞察）的评价却明显褒贬不一。"
        "无法产出能改进业务的洞察，意味着组织难以从智能体分析的投资中获得预期回报。",
    "LifeVal":
        "介绍 LifeVal，这是一个衡量 AI 在多大程度上帮助人们完成日常任务的基准，"
        "覆盖从寻找托儿服务到管理财务与政府文书等场景。",
    "2 days till TechCrunch Founder Summit: Boston founders don’t need a Silicon Valley address to build something big":
        "TechCrunch 创始人峰会将于 11 月 4 日在波士顿举行，"
        "议程聚焦创始人本身，并促成有价值的连接。"
        "可节省高达 100 美元，或使用团体通票享受折扣。",
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
            print("fix title:", it["date"], it["time"], it["source"], "|", t[:52])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_s += 1

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


if __name__ == "__main__":
    main()
