# -*- coding: utf-8 -*-
"""2026-11-23 14:00 例行巡检：定稿本轮新增 3 条 NLLB 机翻硬伤。

1) Unite.AI《Li Ming Took Part in Major Megaspeed Decisions, WSJ Reports》(13:32)
   NLLB 把 Megaspeed（公司名）译成「大规模」，WSJ 报道误译为「WSJ 报告」，
   且摘要把 WSJ / CNBC / ABC 三家媒体归属完全错乱，人名 Jay Clayton 重复。
2) Unite.AI《LlamaIndex Releases OCRia-Nano-1 Open Weights ...》(13:17)
   标题语序生硬，摘要「文件解析管道」「日常报告，合同」等标点与用词需润色。
3) Unite.AI《KT Expands K-Water Partnership ...》(13:14)
   「水场」应为「水务站点」，Daejeon 应补中文名「大田」。

覆盖三层：news.json 回填 + JSON 覆盖表 + manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_FIX = {
    "Li Ming Took Part in Major Megaspeed Decisions, WSJ Reports":
        "据《华尔街日报》报道，李明参与了 Megaspeed 的重大决策",
    "LlamaIndex Releases OCRia-Nano-1 Open Weights for CPU Document Parsing":
        "LlamaIndex 开放 OCRia-Nano-1 权重，支持 CPU 文档解析",
    "KT Expands K-Water Partnership to Test Physical AI at Water Sites":
        "KT 扩大与 K-Water 的合作，在水务站点测试物理 AI",
}

SUMMARY_FIX = {
    "Li Ming Took Part in Major Megaspeed Decisions, WSJ Reports": (
        "《华尔街日报》援引知情人士于 2026 年 11 月 21 日报道称，爱丽丝·黄（Alice Huang）的关联人"
        "李明（Li Ming）「深度参与」了 Megaspeed 的活动并参与重大决策；该报道由 CNBC 于 2026 年 "
        "11 月 23 日转载。国家情报总监杰伊·克莱顿（Jay Clayton）于 2026 年 11 月 22 日告诉 ABC，"
        "美国对黄及其前公司的调查仍在进行。他将案件关注点与英伟达先进芯片的需求联系起来。"
    ),
    "LlamaIndex Releases OCRia-Nano-1 Open Weights for CPU Document Parsing": (
        "LlamaIndex 于 2026 年 11 月 23 日开放 OCRia-nano-1 的权重，推出一套可在本地 CPU 上运行的"
        "810 万参数文档解析流水线。这套由七个模型组成的系统面向大批量文档摄取，以及智能体处理"
        "日常报告、合同、发票和常规扫描件。LlamaIndex 称，在单核上平均每页耗时 426 毫秒，"
        "90% 的页面可在 862 毫秒内完成。"
    ),
    "KT Expands K-Water Partnership to Test Physical AI at Water Sites": (
        "KT 于 2026 年 11 月 23 日宣布，已与韩国水资源公司（Korea Water Resources Corporation，"
        "K-water）签署谅解备忘录，共同开发并测试用于水管理的物理 AI，将双方的数字化平台工作"
        "拓展到现场应用与试验。签署仪式在位于大田（Daejeon）的 K-water 总部举行。"
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en not in TITLE_FIX:
            continue
        it["title_zh"] = TITLE_FIX[en]
        it["summary_zh"] = SUMMARY_FIX[en]
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    added_t = added_s = 0
    for k, v in TITLE_FIX.items():
        if titles.get(k) != v:
            titles[k] = v
            added_t += 1
    for k, v in SUMMARY_FIX.items():
        if summaries.get(k) != v:
            summaries[k] = v
            added_s += 1
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1400_1123] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_1400_1123] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
