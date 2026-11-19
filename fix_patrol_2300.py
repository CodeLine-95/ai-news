# -*- coding: utf-8 -*-
"""23点例行巡检：人工定稿 22:00/22:02 批次 6 条 NLLB 机翻硬伤。

以数据中实际英文标题作为覆盖表键（避免引号字符不匹配），
写入两层 JSON 覆盖表并回填 news.json，随后由 regen_overrides.py
固化到代码层，再由 /api/refresh 触发在线生效与报告重生成。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(BASE, "data")

# (标题匹配子串, 权威中文标题, 权威中文摘要)
FIXES = [
    (
        "Anthropic's $81.3 billion IPO",
        "利率上升与政治逆风冲击行业，Anthropic 813 亿美元 IPO 打破 SpaceX 纪录",
        "Anthropic 启动史上最大规模 IPO，取代 SpaceX 成为此前纪录保持者。早期投资者 Dustin Moskovitz 正公开与此划清界限，警告称自己早期的这笔投资可能是一桩「终结世界」的行为。",
    ),
    (
        "liquid-cooling sidecars get bolted on",
        "如今的数据中心并非为 AI 机架而建，液冷「侧挂」装置被加装上来",
        "随着买家发现交付硬件只是工作的一半，部署服务正成为 AI 基础设施真正的竞争战场。GPU 供应紧张、更新周期加快，新型云服务商和企业开始以 AI 工厂实际投产的速度来评判供应商。",
    ),
    (
        "Groundcover launches Agent Investigations",
        "Groundcover 推出 Agent Investigations：AI 智能体与工程师的共享工作空间",
        "可观测性公司 Groundcover Inc. 今日宣布推出 Agent Investigations——一个共享工作空间，让 Groundcover 的 AI 智能体、团队自有的编码智能体以及值班工程师协同处理生产事故。该产品旨在解决调查线索分散的问题，因为 AI 智能体在事故响应中扮演的角色正越来越重要。",
    ),
    (
        "Superhuman unveils personal AI assistant",
        "Superhuman 推出个人 AI 助理，将 Go 扩展至整个产品套件",
        "Superhuman Inc.（前身为 Grammarly）今日宣布扩展其主动式 AI 助理与多智能体平台 Go，并为整个产品套件带来功能更新。",
    ),
    (
        "Nodal Networks raises $11.3M",
        "Nodal Networks 融资 1130 万美元，破解全球航运瓶颈",
        "Nodal Networks Inc. 是一家构建 AI 决策网络以管理全球海运集装箱码头的企业，今日宣布已完成 1130 万美元种子轮融资，帮助港口与铁路枢纽缓解拥堵、提升货运量。全球货运网络每年运输逾 10 亿个集装箱。",
    ),
    (
        "Streamings and Savings: Black Friday Deals Come to GeForce",
        "节日串流与优惠：黑色星期五特惠登陆 GeForce NOW",
        "GeForce NOW 开启黑色星期五活动，为玩家提供更多畅玩理由。限时回归六个月会员订阅：Performance 或 Ultimate 会员前六个月可享七折优惠。大作畅玩，价格更实惠。更多 NVIDIA 节日优惠面向玩家、创作者与 AI 爱好者。客厅娱乐体验也升级了——运行 Vega OS 的 Amazon Fire TV Stick HD、Fire TV Stick 4K Select 及 Fire TV Stick 4K（2026 款）现已支持 GeForce NOW；今日稍晚还将推出 Amazon 专属优惠，参与国家的符合条件的 Performance 或 Ultimate 会员首月可享一折（减免 90%）折扣，用户可直接从 Amazon 购物车将主机级游戏体验带到电视上。Bethesda 粉丝还有更多惊喜：本周加入 GeForce NOW 的九款游戏中，有五款人气作品新增 GOG 支持。",
    ),
]


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main():
    news_p = os.path.join(D, "news.json")
    t_p = os.path.join(D, "titles_override.json")
    s_p = os.path.join(D, "summaries_override.json")
    news = load(news_p)
    items = news["items"]
    titles = load(t_p)
    summaries = load(s_p)

    by_title = {it.get("title", ""): it for it in items}
    done = 0
    for needle, zh_t, zh_s in FIXES:
        matches = [t for t in by_title if needle in t]
        if len(matches) != 1:
            print("[fix] 匹配异常 %r -> %d 条，跳过" % (needle, len(matches)))
            continue
        en = matches[0]
        it = by_title[en]
        titles[en] = zh_t
        summaries[en] = zh_s
        it["title_zh"] = zh_t
        it["summary_zh"] = zh_s
        it["translated"] = True
        done += 1
        print("[fix] 定稿: %s" % en[:70])

    save(t_p, titles)
    save(s_p, summaries)
    save(news_p, news)
    print("[fix] 完成 %d 条定稿；覆盖表标题 %d / 摘要 %d" % (done, len(titles), len(summaries)))


if __name__ == "__main__":
    main()
