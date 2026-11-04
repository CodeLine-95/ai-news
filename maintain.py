"""例行维护：剥离英文摘要尾部署名 -> 定点重译 -> 重清洗 -> 重生成报告。

背景：
    InfoQ 等源的 RSS description 以 "By <作者名>" 结尾，这是署名不是正文。
    离线模型会把这类署名译成「由Renato Losio」这种半中半英的悬空结尾，
    读起来像半句话。这里在抓取层剥离署名（fetcher._BYLINE_RE），
    本脚本负责把存量条目里的署名剥离掉并定点重译受影响条目。
"""
import json
import os
import re

import translate
import fetcher
import report

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
OVERRIDE_FILE = os.path.join(BASE, "data", "titles_override.json")

BYLINE_ZH_RE = re.compile(
    r"由[A-Za-z][A-Za-z.\- ]*(?:，\s*[A-Za-z][A-Za-z.\- ]*)*$"
)


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", [])

    overrides = {}
    if os.path.exists(OVERRIDE_FILE):
        with open(OVERRIDE_FILE, "r", encoding="utf-8") as f:
            overrides = json.load(f)

    # ---- 1) 剥离英文原文里的尾部署名 ----
    touched = []
    for it in items:
        if it.get("lang") != "en":
            continue
        en = it.get("summary") or ""
        new_en = fetcher._strip_tail_noise(en, it.get("title"))
        if new_en != en and len(new_en) >= 20:
            it["summary"] = new_en
            touched.append(it)

    # ---- 2) 定点重译受影响的条目（标题 + 摘要）----
    if touched:
        titles = [it.get("title") or "" for it in touched]
        summaries = [it.get("summary") or "" for it in touched]
        zh_titles, m1 = translate.translate_list(titles)
        zh_sums, m2 = translate.translate_list_chunked(summaries)
        for i, it in enumerate(touched):
            if zh_titles[i]:
                it["title_zh"] = zh_titles[i]
            if zh_sums[i]:
                it["summary_zh"] = zh_sums[i]
            it["translated"] = True
            it["method"] = m1 if m1 != "none" else m2
        print("[maintain] 剥离署名并重译 %d 条（%s / %s）" % (
            len(touched), m1, m2))
    else:
        print("[maintain] 无需剥离署名")

    # ---- 3) 全量确定性重清洗（不依赖模型）----
    cleaned = 0
    for it in items:
        if it.get("lang") != "en":
            continue
        t = translate._clean_zh(it.get("title_zh") or "")
        s = translate._clean_zh(it.get("summary_zh") or "")
        if it.get("title"):
            t = translate._restore_terms(t, it["title"])
        if it.get("summary"):
            s = translate._restore_terms(s, it["summary"])
        # 译文尾部残留的「由某某」署名一并去掉
        s = BYLINE_ZH_RE.sub("", s).strip()
        if t != it.get("title_zh") or s != it.get("summary_zh"):
            cleaned += 1
            it["title_zh"] = t
            it["summary_zh"] = s

    # ---- 4) 人工标题覆盖（人工结果优先，模型重译不会冲掉）----
    applied = 0
    for it in items:
        manual = overrides.get(it.get("title") or "")
        if manual and it.get("title_zh") != manual:
            it["title_zh"] = manual
            it["translated"] = True
            applied += 1
    if applied:
        print("[maintain] 应用人工标题覆盖 %d 条" % applied)

    data["items"] = items
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("[maintain] 重清洗 %d 条，已写库" % cleaned)

    report.main()


if __name__ == "__main__":
    main()
