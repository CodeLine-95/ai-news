"""2026-11-26 06:00 例行巡检修复脚本（确定性，不加载模型）。

本轮问题条目：
  'AI infrastructure stocks continue their slide, but Anthropic closes higher'
  （SiliconANGLE 05:15）NLLB 把 Anthropic 误译成「人类」，标题语义跑偏；
  源站摘要还在「the day Nvidia Corp.」处截断，中文摘要随之语义崩坏。

处理：
    1) 把人工定稿合并进 data/titles_override.json 与
       data/summaries_override.json，使其在后续每轮调度中持续生效；
    2) 按 SiliconANGLE 原文首两段补全被截断的英文摘要，保证「查看原文」完整；
    3) 对全部英文条目跑确定性重清洗，并应用人工覆盖；
    4) 重生成 Markdown 摘要报告。

全程不加载翻译模型（纯确定性处理），不会与后台调度器抢内存。
运行前请先停止服务，避免与后台调度器争写 data/news.json。
"""
import json
import os
import sys

import report
import translate

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
OVERRIDE_FILE = os.path.join(BASE, "data", "titles_override.json")
SUMMARY_OVERRIDE_FILE = os.path.join(BASE, "data", "summaries_override.json")

sys.path.insert(0, os.path.join(BASE, "data"))
from titles_fix_0600 import TITLE_OVERRIDES          # noqa: E402
from summaries_fix_0600 import SUMMARY_OVERRIDES      # noqa: E402

# 源站摘要在「the day Nvidia Corp.」处截断，按 SiliconANGLE 原文首两段补全。
EN_SUMMARY_FIX = {
    "AI infrastructure stocks continue their slide, but Anthropic closes higher": (
        "Investors continued to offload artificial intelligence infrastructure stocks "
        "today, but Anthropic PBC recouped some of its losses from earlier this week. "
        "The AI selloff reportedly began in August. It accelerated on Nov. 17, the day "
        "Nvidia Corp. CEO Jensen Huang resigned over his affair with a former executive "
        "of Megaspeed, a cloud provider under investigation over alleged export control "
        "violations. Huang returned to the helm of the chipmaker this past Monday."
    ),
}


def _load(path, default):
    if not os.path.exists(path):
        return dict(default)
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return dict(default)


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    titles = _load(OVERRIDE_FILE, {})
    summaries = _load(SUMMARY_OVERRIDE_FILE, {})

    new_t = sum(1 for k in TITLE_OVERRIDES if k not in titles)
    titles.update(TITLE_OVERRIDES)
    new_s = sum(1 for k in SUMMARY_OVERRIDES if k not in summaries)
    summaries.update(SUMMARY_OVERRIDES)

    with open(OVERRIDE_FILE, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=1)
    with open(SUMMARY_OVERRIDE_FILE, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=1)

    items = data.get("items", [])
    cleaned = applied_t = applied_s = fixed_en = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if not en:
            continue

        if en in EN_SUMMARY_FIX and it.get("summary") != EN_SUMMARY_FIX[en]:
            it["summary"] = EN_SUMMARY_FIX[en]
            fixed_en += 1

        if it.get("lang") == "en":
            for field in ("title_zh", "summary_zh"):
                zh = it.get(field) or ""
                src = it.get("title") if field == "title_zh" else it.get("summary")
                if zh:
                    new_zh = translate._clean_zh(zh)
                    new_zh = translate._restore_terms(new_zh, src or "")
                    new_zh = translate._fix_cjk_latin_spacing(new_zh)
                    if new_zh != zh:
                        it[field] = new_zh
                        cleaned += 1

        if titles.get(en):
            v = translate._fix_cjk_latin_spacing(titles[en])
            if it.get("title_zh") != v:
                it["title_zh"] = v
                it["translated"] = True
                applied_t += 1
        if summaries.get(en):
            v = translate._fix_cjk_latin_spacing(summaries[en])
            if it.get("summary_zh") != v:
                it["summary_zh"] = v
                it["translated"] = True
                applied_s += 1

    data["items"] = items
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print("[fix_0600_1126] 覆盖表合并：标题 +%d 条（共 %d），摘要 +%d 条（共 %d）"
          % (new_t, len(titles), new_s, len(summaries)), flush=True)
    print("[fix_0600_1126] 英文摘要补全 %d 条，确定性重清洗 %d 条，人工标题 %d 处，人工摘要 %d 处"
          % (fixed_en, cleaned, applied_t, applied_s), flush=True)

    report.main()
    print("[fix_0600_1126] 报告已重生成", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
