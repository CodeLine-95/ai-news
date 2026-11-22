# -*- coding: utf-8 -*-
"""2026-11-22 18:00 巡检：本轮新增 1 条 NLLB 机翻硬伤人工定稿。

The Decoder —— GPT-6.2 Astra / Sol 评测：
  - 标题「更快地达到了这一点」硬伤，get to the point faster 应为「更快切入要点」。
  - 摘要「人类的 Claude 模型」错译 Anthropic's Claude（NLLB 把 Anthropic 误译为「人类的」）。
  - 「得分远远」为截断硬伤，需补全为透明度指数领先对比。

三层覆盖：news.json 回填 + JSON 覆盖表 + (regen) manual_overrides.py。
"""
import json
import os
import report

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
N_JSON = os.path.join(BASE, "data", "news.json")

# (id, 定稿中文标题, 定稿中文摘要 或 None 表示沿用原摘要)
FIXES = [
    ("6ec6e37a9f0be91f0cca1925f8bc3acc",
     "GPT-6.2 Astra 与 Sol 回答更快切入要点，但透明度得分低于 Claude",
     "Artificial Analysis 的一项评测显示，OpenAI 新推出的 GPT-6.2 Astra 与 Sol 回答比前代短 34% 至 40%，更直接切入要点，使用的标题和破折号也更少；但两款模型承认不确定性的倾向大幅下降——Astra 该项得分从 96 跌至 24，Sol 从 98 跌至 51。与 Anthropic 的 Claude Fable 5.2 和 Opus 5.5 相比，Astra 与 Sol 在结构和透明度上均落后：Anthropic 两款模型透明度指数为 81 和 90，明显高于 Astra（41）与 Sol（57）；Opus 5.5 信息量指数达 90，为四款模型最高。该指数涵盖承认不确定性、真实性、声明假设、标注细微差别与谄媚（反向计分）五项特质。需强调的是，性格分数反映的是沟通风格差异，透明度较低并不等于答案错误率更高。"),
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
        if zh_s is not None:
            summaries[en] = zh_s
        it["title_zh"] = zh_t
        if zh_s is not None:
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
