# -*- coding: utf-8 -*-
"""07:00 例行巡检：人工定稿 12 条 NLLB 机翻硬伤。

本轮（06:00–07:00）整点调度新增 12 条，机翻硬伤包括：
- 品牌/公司名误译：Palo Alto Networks→帕洛阿尔托网络、Applied Compute→应用计算、
  Gresham House Ventures→格雷 esham House Ventures、Clairic→明确模型、WIRED→无线电
- 术语错：Class C Issuance→C 级 C 发行、IPO→首次公开投资、Delaware→德拉华州
- 语义崩坏："It's Got This"→"得到了这个"、"to expand internationally"→"以国际上扩大"

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
        "match": "China Trip Will Lead to Progress on AI",
        "title_zh": "即便其本国官员也不认为特朗普访华能在 AI 议题上取得进展",
        "summary_zh": (
            "官员表示，英伟达（Nvidia）丑闻的余波让围绕人工智能的任何谈判都变得困难。"
        ),
    },
    {
        "match": "Meta Agrees to Pause Class C Issuance",
        "title_zh": "Meta 同意在 AI 融资诉讼期间暂停发行 C 类股",
        "summary_zh": (
            "Meta Platforms 于 2026 年 11 月 18 日同意，根据法院批准的和解令，在特拉华州"
            "围绕股票计划的投资者诉讼的审前和庭审阶段不发行 C 类股。这些无投票权股票"
            "旨在为 Meta 的人工智能扩张提供资金，同时不削弱马克·扎克伯格的投票控制权。"
            "庭审定于 2027 年 4 月 19 日至 23 日在威尔明顿举行。"
        ),
    },
    {
        "match": "Tomorrow.io Research Shows Better Starting Data",
        "title_zh": "Tomorrow.io 研究显示，更优的初始数据可提升 AI 天气预报准确度",
        "summary_zh": (
            "Tomorrow.io 主张在预报模型运行之前就改进 AI 天气预报。其最新研究报告称，"
            "对当前大气状况做出更精准的估算，就能改善微软 Aurora 1.5 和 Google DeepMind "
            "的 WeatherNext 2 的预测结果，而无需改动这些预报模型本身。"
        ),
    },
    {
        "match": "Disseqt AI Raises $8M",
        "title_zh": "Disseqt AI 融资 800 万美元，将 AI 治理与保障业务推向国际",
        "summary_zh": (
            "NovaUCD 于 2026 年 11 月 18 日宣布，总部位于都柏林的企业 AI 智能体治理与"
            "保障平台 Disseqt AI 已融资 800 万美元（730 万欧元）以拓展国际市场。"
            "Gresham House Ventures 领投，Sure Valley Ventures、Delta Partners 和 "
            "Enterprise Ireland 参投。Disseqt 将把资金用于国际客户拓展、扩大伦敦业务"
            "规模，以及招聘销售、运营和技术人才。"
        ),
    },
    {
        "match": "Anthropic reportedly prices IPO at $83 a share, above projected range",
        "title_zh": "据报道，Anthropic 将 IPO 定价为每股 83 美元，高于预期区间",
        "summary_zh": (
            "据报道，这场备受期待的 IPO 按完全稀释后估值将该公司估值达 1.5 万亿美元。"
        ),
    },
    {
        "match": "Palo Alto Networks bets $4.5B on AI startup Applied Compute",
        "title_zh": "Palo Alto Networks 斥资 45 亿美元押注 AI 初创公司 Applied Compute，季度业绩超预期",
        "summary_zh": (
            "网络安全公司 Palo Alto Networks Inc. 今日宣布，已同意以全股票交易方式收购"
            " AI 模型训练与推理初创公司 Applied Compute Inc.，交易价值 45 亿美元。"
            "该消息与其远超华尔街预期的第一财季营收和收益一同公布。"
        ),
    },
    {
        "match": "Does Nvidia Got This?",
        "title_zh": "英伟达搞得定吗？临时 CEO Colette Kress 称一切尽在掌控",
        "summary_zh": (
            "《连线》（WIRED）统计了英伟达临时首席执行官向众人保证公司一切尽在掌控的次数。"
        ),
    },
    {
        "match": "Construction Summit Canada 2026",
        "title_zh": "2026 年加拿大建筑 AI 与数据转型峰会揭示了企业 AI 的哪些趋势",
        "summary_zh": (
            "声明：AMG World 为 Unite.AI 参加多伦多峰会提供了支持。本文的观察与结论均为"
            "我们自己的。建筑业或许并非人们寻找人工智能发展方向时首先想到的领域，而这"
            "恰恰使其成为检验这项技术的绝佳试验场。"
        ),
    },
    {
        "match": "Cloudflare Releases Open-Weight Clairic Models",
        "title_zh": "Cloudflare 发布用于数据提取的开放权重 Clairic 模型",
        "summary_zh": (
            "Cloudflare 于 2026 年 11 月 18 日宣布，其升级后的 270 亿参数 Clairic 与全新的"
            " 90 亿参数 Clairic-flash 已在 Hugging Face 上以开放权重形式提供，并作为托管"
            "的 Workers AI 端点上线。两者均旨在将非结构化文本、图像和 PDF 转换为结构化"
            "取值、估算与预测。Clairic 的模型卡注明其基座为 Qwen3.8-27B，Clairic-flash "
            "则采用 Qwen3.5-9B。"
        ),
    },
    {
        "match": "Reported $83 IPO Price Exceeds Preliminary Range",
        "title_zh": "报道称 Anthropic 的 83 美元 IPO 定价超出初步区间",
        "summary_zh": (
            "TechCrunch 于 2026 年 11 月 18 日报道，Anthropic 已将其首次公开募股（IPO）"
            "定价为每股 83 美元，高于 70–78 美元的初步区间，早于这家 Claude 开发商"
            "预期的纳斯达克上市。据报道的价格使 Anthropic 按完全稀释后估值达到 1.5 万亿美元。"
        ),
    },
    {
        "match": "AWS Adds Quality, Speed and Cost Rankings",
        "title_zh": "AWS 为 SageMaker JumpStart 新增质量、速度与成本排名",
        "summary_zh": (
            "亚马逊云科技（AWS）于 2026 年 11 月 18 日推出 Amazon SageMaker JumpStart "
            "模型排行榜，让 SageMaker Studio 用户能够在一个统一视图中查看 70 多个模型的"
            "基准测试结果、响应性能和预估实例定价。"
        ),
    },
    {
        "match": "Satya Nadella predicts AI agents will reshuffle",
        "title_zh": "萨蒂亚·纳德拉预测，AI 智能体将重塑互联网经济格局",
        "summary_zh": (
            "微软 CEO 表示，AI 智能体可能颠覆以广告为驱动的商业模式，迫使亚马逊等公司"
            "重新思考如何争夺客户。"
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
