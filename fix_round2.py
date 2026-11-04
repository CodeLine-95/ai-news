"""确定性重清洗：把新的术语规则与人工覆盖表应用到存量译文。

背景：
    离线翻译模型（NLLB-200）在品牌名、术语固定搭配上会稳定产生同��类偏差
    （Block→区块、PageBreak→页面破解、XSS Bugs→XSS 错误、forward pass→前进传递 等）。
    这些偏差每次重译都会复现，靠"再翻一遍"无法根治，必须靠确定性规则修复。

本脚本做三件事（全部不占用模型，无 OOM 风险）：
    1) 对全部英文条目的标题/摘要跑一遍 _clean_zh + _restore_terms，
       让新增的 TERM_FIXES / BRAND_TERMS / GLOSSARY 规则生效；
    2) 应用人工标题覆盖表 titles_override.json（人工核对结果优先）；
    3) 重生成摘要报告。

注意：运行前请先停止 server.py，避免与后台调度器争写 data/news.json。
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

# 摘要尾部残留的「由某某」署名（与 maintain.py 保持一致）
BYLINE_ZH_RE = __import__("re").compile(
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

    # ---- 1) 确定性重清洗：让新增术语规则作用于存量译文 ----
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
        s = BYLINE_ZH_RE.sub("", s).strip()
        if t != it.get("title_zh") or s != it.get("summary_zh"):
            cleaned += 1
            it["title_zh"] = t
            it["summary_zh"] = s

    # ---- 2) 人工标题覆盖（人工结果优先）----
    applied = 0
    for it in items:
        manual = overrides.get(it.get("title") or "")
        if manual and it.get("title_zh") != manual:
            it["title_zh"] = manual
            it["translated"] = True
            applied += 1

    # ---- 3) 人工摘要覆盖（整段语义崩坏时由人工重写）----
    sum_overrides = {}
    if os.path.exists(SUMMARY_OVERRIDE_FILE):
        with open(SUMMARY_OVERRIDE_FILE, "r", encoding="utf-8") as f:
            sum_overrides = json.load(f)
    sum_applied = 0
    for it in items:
        manual = sum_overrides.get(it.get("title") or "")
        if manual and it.get("summary_zh") != manual:
            it["summary_zh"] = manual
            it["translated"] = True
            sum_applied += 1

    data["items"] = items
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print("[fix_round2] 重清洗 %d 条，应用人工标题覆盖 %d 条（覆盖表 %d 条），"
          "人工摘要覆盖 %d 条（覆盖表 %d 条）"
          % (cleaned, applied, len(overrides), sum_applied, len(sum_overrides)),
          flush=True)

    report.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
