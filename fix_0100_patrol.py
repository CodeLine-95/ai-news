# -*- coding: utf-8 -*-
"""01 点巡检：本轮 8 条 NLLB 机翻硬伤人工定稿。

- 英文标题 -> 中文标题 写入 titles_override.json
- 英文标题 -> 中文摘要 写入 summaries_override.json
- 按 id 精确回填 data/news.json 的 title_zh / summary_zh，method 标记 manual
- 重生成 Markdown 摘要报告

纯确定性处理，不加载翻译模型，避免与后台调度争内存。
"""
import json
import os
import report

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
N_JSON = os.path.join(BASE, "data", "news.json")

# (id, 英文原标题, 定稿中文标题, 定稿中文摘要)
FIXES = [
    ("70a98d5b450946ecca79e5ecbff3f8f6",
     "Sarvarth Misra, Co-Founder and CEO of Leah – Interview Series",
     "Leah 联合创始人兼 CEO Sarvarth Misra 访谈",
     "Sarvarth Misra 是 Leah（前身为 ContractPodAi）的联合创始人兼首席执行官。他早年从事公司与商业律师工作，期间在查找信息、协调文件与跟踪义务上耗费的大量时间，促使他为法律团队打造技术工具。此后他的工作从合同生命周期管理，扩展到协调企业工作流程的智能体系统，专注于将领域专业知识和受控执行与人类判断相结合。"),
    ("3beff62fefd827a294c5d91bcac8f3fb",
     "At Nasdaq opening bell, Anthropic CEO recommits to pacing AI development",
     "纳斯达克开盘钟响，Anthropic CEO 重申审慎把控 AI 发展节奏",
     "在纳斯达克敲钟仪式上的演讲中，Dario Amodei 重申了 Anthropic 审慎把控人工智能发展节奏的承诺，并表示无论面临商业还是政治压力，这一立场都不会改变。"),
    ("89961a77fdb69fa3fbbf5b2006cb920e",
     "AI is Finding Vulnerabilities at Warp Speed. Fixing Them is a Whole Other Story.",
     "AI 正以极快速度发现漏洞，但修复它们完全是另一回事",
     "网络安全领域出现了一个新问题，讽刺的是，它恰恰源于我们以空前速度发现问题的能力。前沿 AI 模型在发现和利用软件漏洞方面已变得极为擅长，这意味着过去可能潜伏多年的缺陷，如今正以几个月前几乎无法想象的速度被暴露出来。"),
    ("4fdcd73045ae8fa066d9aab4b8cab0ec",
     "Agentic AI pushes the neocloud race beyond GPU counts toward global platforms",
     "智能体 AI 推动新兴云竞赛从比拼 GPU 数量转向全球平台布局",
     "新兴云（neocloud）热潮正进入洗牌阶段，而全球云服务的可及性，正成为区分两类供应商的分水岭：一类是面向企业 AI 需求构建的供应商，另一类则只是出租成排图形处理器（GPU）的算力房东。"),
    ("199a52476287594b130531c085a42e70",
     "Koch Tests HappyRobot AI Agents for Recruiting and HR Support",
     "科氏工业测试 HappyRobot AI 智能体，用于招聘与人力资源支持",
     "科氏工业（Koch）于 2026 年 11 月 19 日宣布，正测试 HappyRobot 的 AI 智能体，用于候选人初筛和员工人力资源支持。此前双方在威奇托展开了一场为期两天的工作坊，并产出了两个可用原型。此次合作回应了人力资源团队反复面临的需求：员工经常需要了解薪资、福利和政策方面的解答，而招聘人员则要花费大量时间进行初步的候选人沟通。"),
    ("ae37b430d53fa8bc58c985195482213f",
     "China-based AI robotics biotech firm MegaRobo raises $200M to accelerate scientific discovery",
     "中国 AI 机器人生物技术公司 MegaRobo 融资 2 亿美元，加速科学发现",
     "中国生物科技机器人公司 MegaRobo（镁伽）今日宣布完成 2 亿美元新融资，将用于投资核心技术，并扩展其自动化生命科学基础设施，以应对日益复杂的物理系统。"),
    ("cb3d520ce0121093d95bf5ff6eae9f24",
     "Mathias Ingvarsson, Founder and CEO of Holyvolt – Interview Series",
     "Holyvolt 创始人兼 CEO Mathias Ingvarsson 访谈",
     "Mathias Ingvarsson 是电池技术公司 Holyvolt 的创始人兼首席执行官，他于 2022 年创立该公司，探索电池技术的全新路径。他的职业经历涵盖 Tempur-Pedic 的国际业务扩张，以及横跨多个行业的创业项目。在 Holyvolt，他专注于将科学专业知识、实验数据与制造能力相连接，以加速电池材料的研发，其中包括收购 Wildcat Discovery Technologies。"),
    ("e73ee03b16d6d0e284fa4ab009db8481",
     "Anthropic hits NASDAQ exchanges at $110, $27 above IPO price",
     "Anthropic 登陆纳斯达克，报 110 美元，较 IPO 发行价高出 27 美元",
     "Anthropic 的 IPO 发行价定为 83 美元，对应募集超过 800 亿美元新资本。其股票在纳斯达克交易所开盘报 110 美元，较发行价高出 27 美元。"),
]


def main():
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(N_JSON, encoding="utf-8"))
    by_id = {it["id"]: it for it in news["items"]}

    ok = 0
    for iid, en, zh_t, zh_s in FIXES:
        titles[en] = zh_t
        summaries[en] = zh_s
        it = by_id.get(iid)
        if not it:
            print("[WARN] id 未找到:", iid)
            continue
        it["title_zh"] = zh_t
        it["summary_zh"] = zh_s
        it["method"] = "manual"
        it["translated"] = True
        ok += 1
        print("[FIX]", iid[:8], "->", zh_t)

    json.dump(titles, open(T_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(summaries, open(S_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(news, open(N_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("[OK] 定稿 %d 条；覆盖表 标题=%d 摘要=%d；news.json=%d 条"
          % (ok, len(titles), len(summaries), len(news["items"])))

    report.main()
    print("[OK] 报告已重生成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
