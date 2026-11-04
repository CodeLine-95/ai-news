"""恢复被定向重译覆盖的人工修正标题。

背景：
    retranslate_terms.py 会重译命中错误译名的条目，这会把人工核对过的标题
    译文覆盖回模型译文（如「Gemini 4 Argon 面向机器人技术」被覆盖成
    「Gemini 4机器人技术的语」）。

本脚本把人工标题作为「权威版本」重新写回，并作为固定项沉淀到
    titles_override.json，后续任何重译流程都会先读取该表再写回，
    确保人工修正不被覆盖。

注意：
    权威表以 data/titles_override.json 为唯一数据源（由人工逐条核对维护）。
    本脚本不再内置硬编码副本，避免两边不一致导致覆盖表被回退。

注意：运行前请先停止 server.py，避免争写 data/news.json。
"""
import json
import os
import sys

import report

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
OVERRIDE_FILE = os.path.join(BASE, "data", "titles_override.json")


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 加载人工覆盖表（唯一数据源）
    overrides = {}
    if os.path.exists(OVERRIDE_FILE):
        try:
            with open(OVERRIDE_FILE, "r", encoding="utf-8") as f:
                overrides = json.load(f)
        except Exception:
            overrides = {}

    items = data.get("items", [])
    applied = 0
    for it in items:
        en = (it.get("title") or "").strip()
        manual = overrides.get(en)
        if manual and (it.get("title_zh") or "") != manual:
            it["title_zh"] = manual
            it["translated"] = True
            applied += 1
            print("恢复人工标题: %s -> %s" % (en[:45], manual), flush=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("已应用人工标题 = %d，覆盖表共 %d 条" % (applied, len(overrides)), flush=True)
    report.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
