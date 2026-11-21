# -*- coding: utf-8 -*-
"""22:00 例行巡检：人工定稿 2 条 NLLB 机翻硬伤。

本轮 22:00 整点调度新增 2 条：

1) 'Anthropic Shares Drop 8.5% in Second Session During AI Selloff'
   title: 人类股票→Anthropic 股价；第二次会议→第二个交易日；语序崩坏。
   summary: 首次开业时开业价/关闭价（debut 误译为开业）；
            "回报了最初的大部分前进"（gave back much of initial advance）。
2) 'OpenAI shares new prompting tips for GPT-6.2 Astra and Sol to fix brief
    answers and unnecessary questions'
   title: 简短的答案和不必要的问题→回答过短、追问过多。
   summary: 低质量的响应→降低响应质量；尾部截断重复标题。

写入两层 JSON 覆盖表 + 回填 news.json；再跑 regen_overrides.py 固化代码层。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

ANTHROPIC = "Anthropic Shares Drop 8.5% in Second Session During AI Selloff"
PROMPTING = ("OpenAI shares new prompting tips for GPT-6.2 Astra and Sol to "
             "fix brief answers and unnecessary questions")
CHESS = "Chess.com\u2019s next move is a new hub for classic games, from mahjong to sudoku"
GOVERNANCE = "AI Governance in 2027: Accountability Moves Into the Workflow"

TITLE_FIX = {
    ANTHROPIC: "AI 抛售潮中 Anthropic 股价第二个交易日下跌 8.5%",
    PROMPTING: "OpenAI 分享新提示技巧：修复 GPT-6.2 Astra 与 Sol 回答过短、追问过多的问题",
    CHESS: "Chess.com 下一步推出经典游戏新平台：从麻将到数独",
    GOVERNANCE: "2027 年 AI 治理：问责机制进入工作流",
}

SUMMARY_FIX = {
    ANTHROPIC: (
        "CNBC 于 2026 年 11 月 21 日报道，Anthropic 股价在 2026 年 11 月 20 日的"
        "第二个交易日收于 88.91 美元，下跌 8.5%，此前纳斯达克综合指数单周下跌 10%，"
        "创下自 2020 年新冠疫情初期市场动荡以来最糟的一周。这一收盘价使这家 Claude "
        "开发商的完全稀释市值达到 1.6 万亿美元，仅落后于六家美国公司。纳斯达克官方"
        "历史报价显示，Anthropic 在 2026 年 11 月 19 日上市首日开盘 111.50 美元、"
        "收盘 97.17 美元，较发行价上涨 17%。次日股价在 83.05 至 92.56 美元之间交易，"
        "回吐了首日的大部分涨幅。"
    ),
    PROMPTING: (
        "OpenAI 发布了针对 GPT-6.2 Astra 与 Sol 的新提示模板，旨在修正模型的常见"
        "行为问题，例如回答过于简短、不必要的后续追问，以及编码时过度测试。API 也"
        "在调整：编辑对话历史可能丢弃推理内容，从而降低响应质量。"
    ),
    CHESS: (
        "Chess.com 的下一步将远远超出国际象棋。继今年早些时候推出无赌博扑克网站 Gambit 后，"
        "该公司现新增 10 款游戏：双陆棋、跳棋、围棋、红心大战、麻将、将棋、数独、纸牌、"
        "象棋，以及一款名为 Word 的 Scrabble 替代品。它们都属于 Chess.com 全新的「经典游戏」"
        "平台，将于周六以公开测试形式在网页端及 iOS、Android 新应用上线。联合创始人称，"
        "常有人向他们提到自己周三晚上办麻将局，或在芝加哥一家酒吧和几个人一起下围棋，"
        "却缺少一个类似 Chess.com 的线上平台。"
    ),
    GOVERNANCE: (
        "一个人收到一项自己无法理解的自动化决策，于是申请复核。组织内部某项政策指定了一位"
        "负责任的负责人，但支持团队找不到任何有权更改结果的人。治理停留在纸面上，当事人"
        "依旧陷入困境。到 2027 年，这一落差将越来越难以辩解。"
    ),
}


def detect_indent(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for ln in lines[1:]:
        stripped = ln.lstrip(" ")
        if stripped and stripped.strip() != "}":
            return len(ln) - len(stripped)
    return 2


def main():
    for path, fixes, label in (
        (T_JSON, TITLE_FIX, "标题"),
        (S_JSON, SUMMARY_FIX, "摘要"),
    ):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        ind = detect_indent(path)
        n = 0
        for k, v in fixes.items():
            if d.get(k) != v:
                d[k] = v
                n += 1
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=ind)
        print("[fix_2200] %s覆盖表写入 %d 条，共 %d 条" % (label, n, len(d)))

    ind = detect_indent(DATA)
    with open(DATA, "r", encoding="utf-8") as f:
        data = json.load(f)
    fixed = 0
    for it in data.get("items", []):
        en = (it.get("title") or "").strip()
        if en in TITLE_FIX and it.get("title_zh") != TITLE_FIX[en]:
            it["title_zh"] = TITLE_FIX[en]
            it["translated"] = True
            it["method"] = "nllb+manual"
            fixed += 1
        if en in SUMMARY_FIX and it.get("summary_zh") != SUMMARY_FIX[en]:
            it["summary_zh"] = SUMMARY_FIX[en]
            it["method"] = "nllb+manual"
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=ind)
    print("[fix_2200] 回填 news.json 条目 %d" % fixed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
