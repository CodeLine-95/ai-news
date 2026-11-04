"""对术语修复表命中的历史条目做定向重译（窄口径版）。

与 retranslate_terms.py 的差别：
    判据只针对「明确的产品名错误译名」，不再使用宽口径的候选词，
    避免把正常中文（如「低碳」「深思熟虑」）误判为需要重译。

注意：运行前请先停止 server.py，避免争写 data/news.json。
"""
import json
import os
import sys

import translate
import report

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
OVERRIDE_FILE = os.path.join(BASE, "data", "titles_override.json")

# 明确的产品名错误译名（窄口径，不含正常中文词）
BAD_TITLE = [
    "Gemini 4碳", "Gemini4碳", "深思", "云飞", "双子球", "阿贡", "安安",
    "人类学", "大赦国际", "安特罗皮克", "尼维迪亚", "杰米尼",
    "克劳德", "困惑度", "数据砖块", "副驾驶", "文学硕士", "法学士",
]
BAD_SUMMARY = [
    "Gemini 4碳", "Gemini4碳", "Gemini 4安安", "安安", "深思发表", "Google深思",
    "深思熟悉", "云飞", "双子球", "阿贡", "抗重力",
    "10万代币", "10万令牌", "人类学", "大赦国际", "文学硕士", "法学士",
]


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    overrides = {}
    if os.path.exists(OVERRIDE_FILE):
        with open(OVERRIDE_FILE, "r", encoding="utf-8") as f:
            overrides = json.load(f)

    items = data.get("items", [])
    targets = []
    for it in items:
        t = it.get("title_zh") or ""
        s = it.get("summary_zh") or ""
        if any(b in t for b in BAD_TITLE) or any(b in s for b in BAD_SUMMARY):
            targets.append(it)

    print("命中待重译 = %d" % len(targets), flush=True)
    if not targets:
        report.main()
        return 0

    print("翻译引擎加载中 ...", flush=True)
    translate.translate_list(["warmup"])

    for it in targets:
        en_title = it.get("title") or ""
        en_sum = it.get("summary") or ""
        zh_t, m1 = translate.translate_list([en_title], beams=2)
        zh_s, m2 = translate.translate_list_chunked([en_sum], beams=1)
        if zh_t[0] and zh_t[0] != en_title:
            it["title_zh"] = zh_t[0]
            it["translated"] = True
        if zh_s[0]:
            it["summary_zh"] = zh_s[0]
        it["method"] = m1 if m1 != "none" else m2
        print("重译: %s -> %s" % (en_title[:45], (it.get("title_zh") or "")[:45]), flush=True)

    # 人工标题优先于模型译文
    applied = 0
    for it in items:
        en = (it.get("title") or "").strip()
        manual = overrides.get(en)
        if manual and (it.get("title_zh") or "") != manual:
            it["title_zh"] = manual
            it["translated"] = True
            applied += 1
    if applied:
        print("恢复人工标题 = %d" % applied, flush=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    report.main()
    print("retranslate_terms done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
