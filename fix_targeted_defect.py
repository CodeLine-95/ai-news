"""针对性修复：仅重译 summary_zh 为空或标题被截断的条目（用 NLLB 回填）。

与 retranslate.py（全量重译 1627 条，耗时久且与运行中的服务争写）不同，
本脚本只处理真正有缺陷的少量条目，适合巡检时快速修复。
"""
import json
import os
import sys
import time

import translate
import report

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")


def needs_fix(it):
    summ_zh = (it.get("summary_zh") or "").strip()
    title_zh = (it.get("title_zh") or "").strip()
    # 摘要为空（源无摘要或丢失）
    if not summ_zh:
        return True
    # 标题被截断（末位为单字且原英文明显更长，常见 "气" 截断为 "氢气"）
    if title_zh and len(title_zh) <= 2 and len(it.get("title", "")) > 6:
        return True
    return False


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", [])
    targets = [it for it in items if needs_fix(it)]
    print(f"需修复条目: {len(targets)} 条", flush=True)
    for it in targets:
        print("  缺陷:", it.get("id"), it.get("source"), repr(it.get("title")),
              "title_zh=", repr(it.get("title_zh")), "summary_zh=", repr(it.get("summary_zh"))[:40])

    if not targets:
        print("无需修复，跳过。")
        report.main()
        return

    print("引擎加载中 ...", flush=True)
    t0 = time.time()
    translate.translate_list(["warmup"])
    print(f"模型就绪 {time.time()-t0:.1f}s", flush=True)

    # 个别专有名词标题被 NLLB 截断（如 Hydrogen→气），直接给定忠实中文标题
    CLEAN_TITLE = {
        "454af483986caafd202a14635607b68e": "谷歌 DeepMind 推出 Gemini 4 Hydrogen",
    }
    for it in targets:
        en_title = it.get("title") or ""
        en_summ = (it.get("summary") or "").strip()
        zh_title, _ = translate.translate_list([en_title], beams=3)
        zh_title = (zh_title[0] if zh_title else en_title).strip()
        if it.get("id") in CLEAN_TITLE:
            zh_title = CLEAN_TITLE[it["id"]]
        # 源本就无英文摘要：保留空，报告层会标注「该来源未提供摘要」
        if en_summ:
            zh_summ, _ = translate.translate_list([en_summ], beams=3)
            zh_summ = (zh_summ[0] if zh_summ else en_summ).strip()
        else:
            zh_summ = ""
        it["title_zh"] = zh_title
        it["summary_zh"] = zh_summ
        it["translated"] = True
        it["method"] = "nllb"
        print(f"  已修复 {it.get('id')[:8]}: 标题={zh_title[:40]} | 摘要={'<空，源未提供>' if not zh_summ else zh_summ[:40]}", flush=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("已写回", DATA_FILE, flush=True)
    report.main()


if __name__ == "__main__":
    main()
