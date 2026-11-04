"""就地回填：对存量译文重新应用术语还原规则（不调用模型重译）。

适用于巡检中发现译文质量问题的场景：只需对已有译文重跑 _restore_terms，
即可套用新补充的术语/品牌规则，无需重新跑 NLLB 推理（快 1~2 个数量级）。

用法：
    python3 backfill_terms.py            # 全量回填
    python3 backfill_terms.py --dry      # 只看会改哪些条目，不落盘
"""
import argparse
import json
import os
import sys

import translate
import report

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只预览不写盘")
    args = ap.parse_args()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    changed = 0
    details = []

    for it in items:
        if it.get("lang") != "en":
            continue
        en_title = it.get("title") or ""
        en_summary = it.get("summary") or ""

        old_t = it.get("title_zh") or ""
        old_s = it.get("summary_zh") or ""
        # 用英文原文作为锚点重跑还原规则
        new_t = translate._restore_terms(old_t, en_title)
        new_s = translate._restore_terms(old_s, en_summary)

        if new_t != old_t or new_s != old_s:
            changed += 1
            details.append((it.get("source"), old_t, new_t, old_s, new_s))
            it["title_zh"] = new_t
            it["summary_zh"] = new_s

    print(f"回填完成：{changed}/{len(items)} 条译文被修正", flush=True)
    for src, ot, nt, os_, ns in details:
        print(f"[{src}]")
        if ot != nt:
            print(f"  标题: {ot}")
            print(f"    -> {nt}")
        if os_ != ns:
            print(f"  摘要: {os_[:100]}")
            print(f"    -> {ns[:100]}")

    if args.dry:
        print("(dry 模式，未写盘)")
        return 0

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    report.main()
    print("报告已重新生成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
