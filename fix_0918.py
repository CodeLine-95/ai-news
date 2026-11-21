# -*- coding: utf-8 -*-
"""0918 巡检：人工定稿 2 条 NLLB 机翻硬伤（新增条目）。"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
N_JSON = os.path.join(BASE, "data", "news.json")

TITLE_FIX = {
    "Oracle Says Funding for OpenAI Infrastructure Contract Is Secured":
        "Oracle 称 OpenAI 基础设施合同资金已落实",
    "Three insights you may have missed from theCUBE’s coverage of the Dell Technologies New York Symposium":
        "你可能错过的 theCUBE 对 Dell Technologies 纽约研讨会报道中的三点洞见",
}

SUMMARY_FIX = {
    "Oracle Says Funding for OpenAI Infrastructure Contract Is Secured":
        "Oracle 在 2026 年 11 月 20 日的声明中表示，其 OpenAI 基础设施合同所需的全部资金均已落实，"
        "并称自己是本轮投资周期中首个获得全额资金保障的超大规模云服务商。"
        "此前 Oracle 于 11 月上旬完成了其所谓的最后一轮融资。Oracle 投资者日披露的融资方案（包括供应商融资）均已到位。",
    "Three insights you may have missed from theCUBE’s coverage of the Dell Technologies New York Symposium":
        "AI 运营就绪不仅仅在于选对服务器、存储与算力。对金融机构而言，这些考量尤为关键——"
        "可靠性、监管合规义务，以及证明技术投资回报的需求，都会影响其部署决策。",
}


def main():
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(N_JSON, encoding="utf-8"))
    items = news["items"] if isinstance(news, dict) and "items" in news else news

    titles.update(TITLE_FIX)
    summaries.update(SUMMARY_FIX)
    json.dump(titles, open(T_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(summaries, open(S_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    hit = 0
    for x in items:
        en = x.get("title", "")
        if en in TITLE_FIX:
            x["title_zh"] = TITLE_FIX[en]
            x["summary_zh"] = SUMMARY_FIX[en]
            x["translated"] = True
            x["method"] = "manual_0918"
            hit += 1
    json.dump(news, open(N_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"[fix_0918] 覆盖表 标题{len(titles)}/摘要{len(summaries)}，回填条目 {hit} 条")


if __name__ == "__main__":
    main()
