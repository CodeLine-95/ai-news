# -*- coding: utf-8 -*-
"""2026-11-03 05:00 巡检：修复 04:00 周期新抓取的 3 条 Unite.AI 条目译文缺陷。

A) 04:01 —— xAI Introduces Data Bot to Bring Shared Analytics Skills to Grok Bot
   1) 产品名 "Data Bot" / "Shared Bot" 被意译成「数据机器人」「共享机器人」，
      中文读者无法定位到具体产品（已在 translate.py 补 BRAND_TERMS）。
   2) unite.ai 原文把 SpaceXAI 误拼为 "SpaceXSI"（源站笔误，正文 7 处），
      模型照抄，译文出现「太空 XSI」（已在 translate.py 补 TERM_FIXES）。
   3) "a bottleneck for colleagues" 的 bottleneck 被截断成「瓶」，
      产出「同事们的瓶」。

B) 04:07 —— Oracle Files Concurrent Common Stock and Senior Notes Offerings
   1) "Senior Notes"（债券品种）被译成「资深笔记」，完全不成词。
   2) "prospectus supplement" 先被译成「高级证券备忘录补充文件」，
      随后二次劣化成「股票明信片补充」（明信片＝postcard）。
   3) "leaves the public offering price blank" → 「公开报价空白」，
      应为「公开发行价格留空」。

C) 04:36 —— Sierra Puts Ghostwriter at the Center of Agent Studio Workflows
   1) 公司名 Sierra 被音译成「塞拉拉」。
   2) 产品名 Ghostwriter 被直译成「幽灵作家」。
   3) 平台名 Agent Studio 被意译成「智能体工作室」。
   4) "journey editing"（智能体旅程编排）被按旅行义直译成
      「旅行编辑」「编辑行程」，语义完全跑偏。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    "xAI Introduces Data Bot to Bring Shared Analytics Skills to Grok Bot":
        "xAI 推出 Data Bot，为 Grok Bot 带来共享的分析能力",
    "Oracle Files Concurrent Common Stock and Senior Notes Offerings":
        "Oracle 提交普通股与优先票据同步发行文件",
    "Sierra Puts Ghostwriter at the Center of Agent Studio Workflows":
        "Sierra 将 Ghostwriter 置于 Agent Studio 工作流的核心位置",
}

SUMMARY_FIX = {
    "xAI Introduces Data Bot to Bring Shared Analytics Skills to Grok Bot":
        "xAI 于 2026 年 11 月 2 日推出 Data Bot，这是 Grok Bot 中的一种 Shared Bot，"
        "由 SpaceXAI 的数据科学团队打造，可借助团队共享的分析方法处理数据仓库查询"
        "与分析工作，并按用户分别格式化结果。"
        "SpaceXAI 数据科学团队表示，Data Bot 体积小巧，"
        "反而可能成为同事们的瓶颈——因为他们那些看似简单的问题，"
        "仍需专业知识才能解答。",
    "Oracle Files Concurrent Common Stock and Senior Notes Offerings":
        "Oracle 于 2026 年 11 月 2 日就优先票据向美国证券交易委员会"
        "提交了初步招股说明书补充文件，涵盖普通股与优先票据的同步发行，"
        "其中股票与债务部分的规模各为 100 亿美元。"
        "两份文件均为初步版本，且可能变更。"
        "普通股的招股说明书补充文件将公开发行价格留空。",
    "Sierra Puts Ghostwriter at the Center of Agent Studio Workflows":
        "Sierra 于 2026 年 11 月 2 日宣布，已围绕其用于构建智能体的 Ghostwriter "
        "重新设计了 Agent Studio，把调查、旅程编排与测试整合进同一个对话之中。"
        "证据、拟议的变更与测试结果始终留存在一起，"
        "团队可在任何内容正式上线之前先行审阅。"
        "此前，用户必须在 Agent Studio 的不同部分之间来回切换，"
        "才能编辑旅程、运行模拟并查看性能表现。",
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


if __name__ == "__main__":
    main()
