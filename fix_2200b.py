# -*- coding: utf-8 -*-
"""2026-11-02 22:00 例行巡检修复（新增 5 条的译文缺陷）。

本轮 22:00 抓取新增 5 条英文资讯，NLLB 直译出现多处硬伤：

1. 「Stop counting tokens, start counting what ships」
   → 标题把 ships 当「货物」译成「开始计数什么货」；
     摘要「智能体越有用，就越多打电话」丢失 calls（调用次数）语义，
     末句「全面限制可以限制工作流提供价值」语义反了（原文说的是
     一刀切限制会束缚真正创造价值的工作流）。
2. 「Building a People-First, AI-Powered City」
   → 标题「以人工智能为主的人员首发的城市」是逐词硬拼，语义全乱；
     摘要「现在是人工智能的轮到」语序不通。
3. 「Emerald AI Becomes Full Member of EPRI's DCFlex Initiative」
   → 品牌名 Emerald 被译成「玉 AI」，EPRI's 变成「EPRIsDCFlex」；
     摘要里「黄金 AI 表示」「6 次人工智能数据中心灵活性示范」均不可用。
4. 「Signia Brings MaX and Active Mini IX to U.S. Government Services」
   → 品牌 Signia 被音译成「索尼亚」；摘要里人名职务串成一团，
     「活跃的员工」应为「现役军人」。
5. 「OpenAI is finally merging ChatGPT's chat and Work tabs」
   → 标题出现「ChatGPTs」「tabb」两个残留英文/拼写错误；
     摘要「从相同的分配池中获取使用」是逐字硬翻。

本脚本人工定稿这 5 条的标题与摘要，写回 data/news.json，
并同步进 titles_override.json / summaries_override.json，
最后由 scripts/regen_overrides.py 固化到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    "Stop counting tokens, start counting what ships":
        "别再数 token 了，开始数真正交付的成果",
    "Building a People-First, AI-Powered City":
        "打造以人为本的 AI 智慧城市",
    "Emerald AI Becomes Full Member of EPRI’s DCFlex Initiative":
        "Emerald AI 成为 EPRI DCFlex 计划的正式成员",
    "Signia Brings MaX and Active Mini IX to U.S. Government Services":
        "Signia 将 MaX 与 Active Mini IX 引入美国政府服务体系",
    "OpenAI is finally merging ChatGPT’s chat and Work tabs":
        "OpenAI 终于合并了 ChatGPT 的 Chat 与 Work 标签页",
}

SUMMARY_FIX = {
    "Stop counting tokens, start counting what ships":
        "当开发者交给 AI 智能体一个编码任务时，智能体做的远不止回答一次："
        "它会制定计划、生成代码、运行测试，再重复这一过程以纠正错误。"
        "单个任务的 token 消耗可能是普通聊天提问的 10 到 50 倍。"
        "智能体越有用，发起的调用次数就越多。在按 token 计费的模式下，"
        "创造价值最高的工作流往往也是成本最高的。财务压力已经显现："
        "据报道，Uber 在扩大 Claude Code 使用后，到 4 月就耗尽了 2026 全年的 AI 预算；"
        "GitHub Copilot 也从统一定价改为按积分计量。"
        "Gartner 预测，到 2028 年，AI 编码的 token 成本将超过开发人员的平均工资。"
        "自然的应对是在开发者上线智能体之前设置用量上限、席位数限制和审批流程，"
        "但一刀切的限制也会束缚真正在创造价值的工作流。",
    "Building a People-First, AI-Powered City":
        "纵观历史，新技术总是引发人们的恐惧，往往裹挟着「威胁社会」的争议登场。"
        "如今轮到 AI 了。这些担忧是合理的，也值得认真回应，"
        "但历史还告诉了我们一个更普遍的道理：技术变革固然会带来扰动，"
        "同时也会释放巨大的机会。这正是当下正在全球各地的城市上演的故事。",
    "Emerald AI Becomes Full Member of EPRI’s DCFlex Initiative":
        "Emerald AI 于 2026 年 11 月 2 日宣布，将以正式成员身份加入 EPRI 的 DCFlex 计划，"
        "延续双方的合作——此前双方已与 NVIDIA、公用事业公司、电网运营商及数据中心伙伴"
        "共同完成六次 AI 数据中心灵活性示范。Emerald AI 表示，"
        "与 EPRI 的合作可追溯至公司 2024 年 11 月成立之时，"
        "恰逢 DCFlex 在同年秋季推出。",
    "Signia Brings MaX and Active Mini IX to U.S. Government Services":
        "Signia 于 2026 年 11 月 2 日宣布，其 Pure Charge&Go MaX 与 Active Mini IX 助听器"
        "已可通过美国退伍军人事务部、国防部以及印第安人健康服务局获取，"
        "公司公告称。Signia 政府服务业务销售副总裁 Mike Irby 表示，"
        "MaX 的设计目标是帮助退伍军人和现役军人在嘈杂、难以预测的环境中"
        "跟随并参与对话。",
    "OpenAI is finally merging ChatGPT’s chat and Work tabs":
        "OpenAI 表示，此次调整之后，ChatGPT 与 Codex 将从同一个额度池中扣取用量。",
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    hit = 0
    for it in items:
        t = it.get("title", "")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit += 1
            print("title fixed:", it["date"], it["time"], it["source"])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"

    with open(os.path.join(DATA, "titles_override.json"), encoding="utf-8") as f:
        tov = json.load(f)
    tov.update(TITLE_FIX)
    with open(os.path.join(DATA, "titles_override.json"), "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)

    with open(os.path.join(DATA, "summaries_override.json"), encoding="utf-8") as f:
        sov = json.load(f)
    sov.update(SUMMARY_FIX)
    with open(os.path.join(DATA, "summaries_override.json"), "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)

    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("fixed items:", hit, "/ expected", len(TITLE_FIX))


if __name__ == "__main__":
    main()
