# -*- coding: utf-8 -*-
"""2026-11-23 19:00 例行巡检：定稿本轮新增 3 条 NLLB 机翻硬伤。

1) Marktechpost《27 Cybersecurity Terms to Prepare You for the Age of AI》
   (18:40)：NLLB 把 terms 误译为「条款」（应为「术语」），全句不通。
2) Unite.AI《Türkiye Opens Humanoid Robot Call Covering 50% of Project
   Budgets》(18:25)：humanoid robot 误作「人类机器人」（应为「人形机器人」），
   Call 误作「呼叫」（此处为「项目征集」），grant 误作「补贴」（应为「资助」）。
3) Marktechpost《Architect Labs Unveils Frostbite, an Interaction Net CPU
   Designed by AI》(18:05)：公司名 Architect Labs 被误译为「建筑师实验室」
   （应保留原名），interaction nets 误作「互动网」（应为「交互网络」），
   pre-silicon 误作「预试验」（应为「流片前/硅前」），GDS 数字乱译。
4) Wired《States Sue SpaceX Over Grok Deepfakes》(19:00，重启后补抓)：
   States（各州）被误译为「索赔」，全句语序颠倒为「索赔 SpaceX 超越 Grok
   州的深度伪造 s」，完全不可读。按原文定稿。
5) Wired《Meta Muse can now do your Black Friday shopping at Walmart》
   (19:00，重启后补抓)：误译为「在沃尔玛购买你的黑色星期五购物」，
   「代用户购物」语义尽失。按原文定稿。

覆盖三层：news.json 回填 + JSON 覆盖表（regen 时复用）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_FIX = {
    "27 Cybersecurity Terms to Prepare You for the Age of AI":
        "迎接 AI 时代需要掌握的 27 个网络安全术语",
    "Türkiye Opens Humanoid Robot Call Covering 50% of Project Budgets":
        "土耳其启动人形机器人项目征集，覆盖项目预算的 50%",
    "Architect Labs Unveils Frostbite, an Interaction Net CPU Designed by AI":
        "Architect Labs 发布 Frostbite：一款由 AI 设计的交互网络 CPU",
    "States Sue SpaceX Over Grok Deepfakes":
        "美国多州就 Grok 深度伪造内容起诉 SpaceX",
    "Meta Muse can now do your Black Friday shopping at Walmart":
        "Meta Muse 现在可帮你在沃尔玛完成黑色星期五购物",
}

SUMMARY_FIX = {
    "27 Cybersecurity Terms to Prepare You for the Age of AI": (
        "人工智能如今同时站在安全攻防双方，相关词汇也随之改变。IBM《2026 年数据泄露成本报告》"
        "发现，每 4 次恶意泄露中就有 1 次由 AI 驱动，同比增长 56%，这些泄露平均造成 600 万美元"
        "损失，比 499 万美元的全球平均值高出约 100 万美元。攻击者如今瞄准模型本身、基于模型输出"
        "行动的智能体，以及信任 AI 产出结果的人。参考清单也在快速更新：OWASP 于 2026 年 8 月 4 日"
        "发布《LLM 应用 Top 10（2026）》，并于 2025 年 12 月首次发布《智能体应用 Top 10》；"
        "MITRE ATLAS 则像 ATT&CK 针对 IT 系统那样，梳理针对 AI 系统的攻击者战术。以下 27 个术语"
        "分为 4 部分：针对模型的攻击、智能体风险、AI 驱动的人身攻击，以及应对它们的防御措施。"
    ),
    "Türkiye Opens Humanoid Robot Call Covering 50% of Project Budgets": (
        "土耳其工业和技术部长穆罕默德·法蒂赫·卡奇尔（Mehmet Fatih Kacır）宣布，土耳其于 2026 年"
        "11 月 23 日开放面向工业用途的人形机器人开发项目申请，向企业提供覆盖项目预算 50% 的资助。"
        "这项「工业应用人形机器人开发」项目征集的申请截止日期为 2026 年 12 月 31 日。"
    ),
    "Architect Labs Unveils Frostbite, an Interaction Net CPU Designed by AI": (
        "Architect Labs 推出 Frostbite——一款采用围绕交互网络（interaction nets）构建的全新指令集、"
        "由 AI 设计的 CPU。该公司表示，其 AI 智能体完成了从交互网络理论到最终 GDS（版图数据）的"
        "全流程设计。在流片前（pre-silicon）测试中，其每瓦性能达到现代顺序执行 CPU 内核的 4.59 倍。"
        "核心数据：面积方面，1 个 quad（2×2 tile）加 4 个 L3 节点在 7nm 工艺下占 0.792 平方毫米；"
        "无参数量（因为它是 CPU）；目前仅有流片前版本；最终 GDS 在 7nm 下于 500MHz 收敛；"
        "计划推出基于 FPGA 的体验平台。性能方面：每瓦性能 4.59 倍（25 个负载几何平均）、"
        "单位面积性能 8.77 倍（对比单核顺序执行内核），conv2d 负载最高达每瓦 23.12 倍。"
        "Frostbite 是 Architect Labs 的一款 CPU，以硬件交互网络方式执行程序，程序用类 Rust 语言 "
        "Vine 编写，并编译为名为 Ivy 的中间表示（IR）。"
    ),
    "States Sue SpaceX Over Grok Deepfakes": (
        "俄勒冈州和弗吉尼亚州的总检察长正在起诉埃隆·马斯克旗下的多家公司，指控这些公司"
        "针对涉及真人（包括儿童）的性化图像设置了薄弱的防护措施。"
    ),
    "Meta Muse can now do your Black Friday shopping at Walmart": (
        "沃尔玛现在将允许 Meta 的 Muse 智能体代表用户在网站上购物，代为寻找并购买黑色星期"
        "五折扣商品。据沃尔玛介绍，这家零售巨头正上线其上月公布的 Agent Gateway（智能体"
        "网关）的实装版本，可在不共享用户购买记录的前提下帮助 AI 智能体找到相关商品。"
        "Muse 可通过沃尔玛的「Agent Profiles」（智能体档案）完成购买——该档案在用户的"
        "沃尔玛账户中为智能体活动提供专属空间，用户可据此设置消费上限、审批购买，并查看"
        "Muse 所购全部商品的记录。"
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en not in TITLE_FIX:
            continue
        it["title_zh"] = TITLE_FIX[en]
        it["summary_zh"] = SUMMARY_FIX[en]
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    added_t = added_s = 0
    for k, v in TITLE_FIX.items():
        if titles.get(k) != v:
            titles[k] = v
            added_t += 1
    for k, v in SUMMARY_FIX.items():
        if summaries.get(k) != v:
            summaries[k] = v
            added_s += 1
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1900_1123] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_1900_1123] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
