# -*- coding: utf-8 -*-
"""2026-11-23 00:00 巡检：整点调度新增 1 条（23:15 The Decoder），NLLB 硬伤人工定稿。

  * The Decoder《AI coding agents ace isolated tests but complete fewer than one in ten
    tasks in a simulated workplace》——
    标题漏译 "ace isolated tests"（在隔离测试中表现出色）；摘要里 "project boards"
    译成「项目董事会」（应为「项目看板」）、"incomplete handoffs" 译成「不完整的交付」、
    "close open tickets" 译成「关闭开放门票」（应为「关闭待办工单」）、
    "fall far short" 译成「都很短暂」（应为「远未达标」）。

三层覆盖：news.json 回填 + JSON 覆盖表 + (regen) manual_overrides.py。
"""
import json
import os
import report

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
N_JSON = os.path.join(BASE, "data", "news.json")

FIXES = [
    (
        "7b00cb497c405b42c29702fce793a28f",
        "AI 编码智能体轻松通过隔离测试，但在模拟工作场所完成的任务不到十分之一",
        "一项新的贴近现实的测试将 AI 编码智能体置于模拟的开发者岗位：有同事、项目看板和残缺的交接文档，"
        "它们必须自主持续开发软件，并在混乱的日常工作流程中可靠地关闭待办工单。即便是 Opus 5.5 和 Astra "
        "也远未达标——能完整解决的任务不到十分之一。这些模型能迅速完成清晰、独立的任务，"
        "但一旦作为自主开发者持续工作就会失去条理。",
    ),
]


def main():
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(N_JSON, encoding="utf-8"))
    by_id = {it["id"]: it for it in news["items"]}

    ok = 0
    for iid, zh_t, zh_s in FIXES:
        it = by_id.get(iid)
        if not it:
            print("[WARN] id 未找到:", iid)
            continue
        en = (it.get("title") or "").strip()
        titles[en] = zh_t
        summaries[en] = zh_s
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
