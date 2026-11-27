# -*- coding: utf-8 -*-
"""23 点巡检：定稿 5 条 NLLB 机翻硬伤并写回覆盖表。

问题条目（含 22 点批次遗留 1 条 + 23 点整点新增 4 条）：

  1) 'Aditya Infotech Completes KGraph Stake Deal for AI Surveillance'
     缺陷：Stake Deal 误译为「股票交易」（实为股权入股）；₹45.39 crore
     误译为「45.39 亿卢比」（1 crore = 1000 万，实为 4.539 亿卢比）。
  2) 'SAP plans to cut at least 10,000 jobs as it pivots to AI'
     缺陷：「就业位」不顺；「据博社报道」漏字（应为彭博社）；
     「并援引熟悉此事的人」主语错乱（原文是 Bloomberg 援引知情人士）。
  3) 'Meta Brings Code Review Auto-Approval More Mainstream with PyTorch GreenLight'
     缺陷：标题中英混杂且语序颠倒；pull requests 译成「提取请求」
     （应为拉取请求/PR）；auto-land 译成「自动降落」（应为自动合并）。
  4) 'Android’s DIY widgets are a bit of vibe-coding fun'
     缺陷：vibe-coding 译成「编码音调/振动编码」（应为氛围编程）；
     stop 译成「停车位」（应为公交站点）；多处语句生硬。
  5) 'Edge AI in 2027: Running Models Offline Becomes a Competitive Advantage'
     缺陷：标题把 Offline 译成「在线」（反义）；Edge AI 漏译；
     discipline 译成「学科」（应为约束下的功力）。

本脚本把人工定稿结果写回数据与覆盖表，随后运行
    python3.11 scripts/regen_overrides.py
同步到代码层覆盖表，使后续轮次不再被模型译文覆盖。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    (
        "Aditya Infotech Completes KGraph Stake Deal for AI Surveillance",
        "Aditya Infotech 完成对 KGraph 的 AI 监控股权收购",
        "Aditya Infotech Limited 在 2026 年 11 月 27 日提交给证券交易所的文件中表示，"
        "已以 4.539 亿卢比（₹45.39 crore）现金完成对 KGraph AI Solutions Private Limited "
        "30% 股权的收购（按完全稀释口径）。KGraph 将成为其联营公司，其 BLUE 视频分析"
        "技术计划整合进 CP PLUS 监控产品。",
    ),
    (
        "SAP plans to cut at least 10,000 jobs as it pivots to AI",
        "SAP 战略转向 AI，计划至少裁员 1 万人",
        "据彭博社援引知情人士报道，SAP 正准备在一场大规模的 AI 重组中裁减至少 1 万个岗位。",
    ),
    (
        "Meta Brings Code Review Auto-Approval More Mainstream with PyTorch GreenLight",
        "PyTorch GreenLight 让代码审查自动审批走向主流，Meta 推动落地",
        "PyTorch 现已允许 AI 审查员批准来自其自身维护者的拉取请求（PR）。GreenLight 是 "
        "RADAR 的开源版本；RADAR 是 Meta 内部使用的系统，可在完成安全检查、风险评分"
        "与大模型审查后自动合并低风险改动。OpenAI、Anthropic 和 Sonar 也介绍了类似的"
        "自动审批方式，同时对高风险改动保留人工审核。",
    ),
    (
        "Android’s DIY widgets are a bit of vibe-coding fun",
        "安卓的 DIY 小组件：玩一把「氛围编程」的乐趣",
        "小组件，由你做主。图片：Allison Johnson / The Verge 除了打理我的日历，我还希望 AI "
        "帮我做一件事：提醒我别错过公交车。我需要一个小组件，告诉我家附近站点的实时到站"
        "信息。在手机屏幕上点开正确的应用、选择站点，这套操作慢下来足以让我错过一班车。"
        "我需要的是一眼可见的信息，本指望安卓的「氛围编程」（vibe-coding）小组件功能能"
        "帮上忙。结果让我失望，但我倒是兴致勃勃地做了些别的小组件。谷歌在春季 I/O 大会上"
        "就宣布了用 AI 创建自定义小组件的能力。",
    ),
    (
        "Edge AI in 2027: Running Models Offline Becomes a Competitive Advantage",
        "2027 年边缘 AI：离线运行模型成为竞争优势",
        "设备不会因为模型需要更多 token 就获得更大的电池；运行另一个应用时也不会多出"
        "第二个内存池；网络断开时，客户仍期待产品照常工作。边缘 AI 就生活在这些物理限制"
        "之中。到 2027 年，这种在约束下的功力将成为卖点。最有说服力的演示，将展示设备在"
        "发热、断网、理想测试条件消失之后，还剩下多少真正可用的能力。",
    ),
]


def main():
    for en, zh_title, zh_summary in FIXES:
        for path, val in ((T_JSON, zh_title), (S_JSON, zh_summary)):
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            if d.get(en) != val:
                d[en] = val
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
                print("[fix_2300] 已更新覆盖表:", os.path.basename(path), "|", en[:50])

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        for en, zh_title, zh_summary in FIXES:
            if it.get("title") == en:
                it["title_zh"] = zh_title
                it["summary_zh"] = zh_summary
                it["translated"] = True
                hit += 1
                print("[fix_2300] 已回写:", en[:60])
    if hit:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[fix_2300] 已回写 news.json，命中条目:", hit)
    else:
        print("[fix_2300] 未命中条目，未改动数据")


if __name__ == "__main__":
    main()
