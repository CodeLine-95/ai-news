# -*- coding: utf-8 -*-
"""21:00 巡检修复：
1. 摘要「在...之外移动」→「偏离...」（NLLB 直译缺陷）
2. 报告摘要截断改为按句边界，避免词中间硬切
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
    db = json.load(f)
items = db["items"] if isinstance(db, dict) else db

changed = 0
for it in items:
    s = it.get("summary_zh") or ""
    if "之外移动" in s:
        it["summary_zh"] = s.replace(
            "在经营目的或安全界限之外移动", "偏离经营目的或安全界限")
        it["summary_zh"] = it["summary_zh"].replace(
            "之外移动时", "时")
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it["date"], it["time"], it["source"])

# 同步写入摘要覆盖表（JSON + 代码层 manual_overrides.py）
ov_path = os.path.join(DATA, "summaries_override.json")
with open(ov_path, encoding="utf-8") as f:
    ov = json.load(f)
for it in items:
    if it.get("method") == "nllb+manual" and it.get("title"):
        ov[it["title"]] = it.get("summary_zh") or ""
with open(ov_path, "w", encoding="utf-8") as f:
    json.dump(ov, f, ensure_ascii=False, indent=2)

with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)
print("changed:", changed)
