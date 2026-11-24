# -*- coding: utf-8 -*-
"""2026-11-25 05:00 例行巡检：定稿本轮 4 条新入库条目的 NLLB 机翻硬伤。

本轮后台抓取 4 条新条目（The Decoder / The Verge / Ars Technica / ML Mastery），
机翻存在明显硬伤：
1) The Decoder：Anthropic 误译为「人类化」，MacOS/Windows 大小写错乱；
2) The Verge：黄仁勋复职报道整句语义崩坏（「特朗普让他重新聘请了」），
   需按 11-24 已定稿的「黄仁勋/英伟达」译名体系统一；
3) Ars Technica：Riemann 误译为「里曼」，应为「黎曼猜想」，摘要长句需理顺；
4) ML Mastery：Speculative Decoding 标题正确但摘要术语需规范（草稿/目标模型）。

覆盖三层：news.json 回填 + 标题覆盖表 + 摘要覆盖表，以英文原标题为 key。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "Anthropic turns Claude Artifacts into standalone desktop apps for macOS and Windows": (
        "Anthropic 将 Claude Artifacts 打造为 macOS 与 Windows 独立桌面应用",
        "Anthropic 现支持将 Claude Artifacts 安装为 Mac 与 Windows 上的桌面应用，免费账户即可使用。"
        "用户可在对话中无需编写代码就创建一个应用，它还能添加菜单栏项目、发送通知并创建透明窗口。",
    ),
    "Jensen Huang reportedly tells Nvidia staff it’s ‘not true’ Trump got him rehired": (
        "据报道黄仁勋向英伟达员工表示：特朗普助其复职「并非事实」",
        "据彭博社、《纽约时报》以及 The Handbasket 的 Marisa Kabas 报道，"
        "英伟达 CEO 黄仁勋在重返公司后的首次全员大会上向员工致歉，"
        "同时试图撇清白宫与科技领袖帮助他复职的说法。"
        "会上黄仁勋称，特朗普总统直接介入其复职的说法「完全不实」——这一说法曾由特朗普本人公开宣扬。"
        "据 Kabas 称，他还表示：「别以为政治在公司里起了任何作用，我们是政治中立度最高的公司。」",
    ),
    "What's going on with the Riemann hypothesis?": (
        "黎曼猜想究竟怎么回事？",
        "上周有消息称，一位数学家借助 AI 帮助攻克了数学界最重大的未解难题之一——黎曼猜想的证明。"
        "此前已有多项重大数学突破或由大型语言模型系统促成、或完全由其完成，令整个数学界为之震动。"
        "现在对证明本身下定论还为时过早——数学家们仍在消化理解之中。"
        "不过我们可以谈谈这一证明是如何产生的，以及它反映了数学领域的何种现状。"
        "黎曼猜想提出于 19 世纪中叶，由（你或许会惊讶）伯恩哈德·黎曼创立。"
        "虽然难以简单描述该猜想的技术细节，但它对素数的分布有着重要意义。",
    ),
    "Speculative Decoding": (
        "投机解码",
        "概述 本文分为六个部分：• 草稿与验证 • 基于采样的投机解码 • 借助草稿模型的辅助生成 "
        "• 衡量接受率与加速比 • 其他生成草稿词元的方法 • 投机何时有效。"
        "草稿与验证：投机解码涉及两个模型——草稿模型（通常是运行更快的小型模型）"
        "与目标模型（通常是准确率更高的大型模型）。",
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    changed = added_t = added_s = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en not in FIX:
            continue
        title_zh, summary_zh = FIX[en]
        it["title_zh"] = title_zh
        it["summary_zh"] = summary_zh
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])
        if titles.get(en) != title_zh:
            titles[en] = title_zh
            added_t += 1
        if summaries.get(en) != summary_zh:
            summaries[en] = summary_zh
            added_s += 1

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_0500_1125] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_0500_1125] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0 if changed == len(FIX) else 1


if __name__ == "__main__":
    raise SystemExit(main())
