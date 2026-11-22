# -*- coding: utf-8 -*-
"""2026-11-22 20:00 巡检：本轮新增 2 条，NLLB 硬伤人工定稿。

  1) Unite.AI《Anthropic Sought Limits on IPO Deal Teams and Work with Rivals》——
     标题/摘要把公司名 Anthropic 误译成「人类」「人类有限公司」，应保留公司名。
  2) The Decoder《... confirms Levent Alpöge's proof of the Riemann hypothesis ...》——
     Lean / Mathlib / Levent Alpöge / Riemann / Terence Tao 被音译成
     「利恩/马思利布/利文特·阿尔波格/里曼/特伦斯·陶」，应为专有名词原称
     （Riemann=黎曼猜想，Terence Tao=陶哲轩）。

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
        "4206f8c9340d90ff5e16effcc4952f55",
        "Anthropic 拟限制 IPO 交易团队规模及与竞争对手的合作",
        "2026 年 11 月 22 日，路透社报道称，Anthropic 在其 22 家 IPO 承销商中，将部分交易团队限定为 4 名高级银行家，并要求一些银行高管接受为期 6 个月的限制，不得与 AI 竞争对手合作，作为严格受控上市流程的一部分。多位接近此次发行的人士描述了被压缩的时间表、临时变更、财务预测迟交以及文件审批仓促等情况。",
    ),
    (
        "53be26b502b2bd54a199d12f8698da2b",
        "Lean 与 Mathlib 社区正式确认 Levent Alpöge 对黎曼猜想的证明正确",
        "Lean 与 Mathlib 社区已正式确认 Levent Alpöge 对黎曼猜想的证明正确。数十名独立验证者核验了这份长达 1700 万行的计算机代码。这一成果比预期提前数年到来：陶哲轩（Terence Tao）此前曾预测要到 2050 年左右才会出现，也未曾料到 AI 能独立解决它。",
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
