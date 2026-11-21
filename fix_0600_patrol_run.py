# -*- coding: utf-8 -*-
"""06:00 例行巡检：人工定稿 4 条 NLLB 机翻硬伤。

本轮（2026-11-22 06:00 整点调度）自动新增 4 条，其中专有名词被错误音译、
语义崩坏：
  - Signal（通讯软件）→「信号」
  - Lean / Mathlib（定理证明器与数学库）→「利恩 / 马思利布」
  - Riemann（黎曼）→「里曼」
  - Levent Alpöge（人名）→「莱恩 Alpöge」
  - "A tale of two Nvidias"→「一个两个 Nvidia 故事」

固化覆盖三层：
1) data/news.json 内条目直接回填
2) data/titles_override.json / data/summaries_override.json（JSON 层）
3) 再运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = [
    {
        "match": "Sovereignty starts with data, not chips",
        "title_zh": "斯图加特 AI 工厂负责人：主权始于数据，而非芯片",
        "summary_zh": (
            "一座主权 AI 工厂的价值，取决于真正能用它做事的企业。在全欧洲，由公共资金支持的 "
            "AI 工厂正争相为初创企业和小型制造商提供超级计算机级 GPU，同时避免把它们推入"
            "供应商锁定或松散的数据处理。"
        ),
    },
    {
        "match": "Signal restricts mobile screenshots",
        "title_zh": "Signal 限制移动端截图，因其直面 AI 监控这一「生存威胁」",
        "summary_zh": "Signal 正在限制用户在 Android 与 iOS 应用中截取屏幕的能力。",
    },
    {
        "match": "Lean and Mathlib Communities Certify Claude-Assisted Riemann Proof",
        "title_zh": "Lean 与 Mathlib 社区认证 Claude 辅助完成的黎曼猜想证明",
        "summary_zh": (
            "Lean 与 Mathlib 社区于 2026 年 11 月 21 日确认：经过一整天的编译、命题匹配与证明内核"
            "校验，Levent Alpöge 的 1700 万行 Lean 代码库正确表述并证明了黎曼猜想。双方的联合声明"
            "获得 Lean FRO 与 Mathlib 倡议组织背书。此次认证源自 Alpöge 于 2026 年 11 月 20 日"
            "宣布的成果——他表示自己是在与 Claude 协作的过程中发现并形式化了这一证明。"
        ),
    },
    {
        "match": "A tale of two Nvidias",
        "title_zh": "两个英伟达的故事",
        "summary_zh": (
            "关于英伟达，我们看到了两幅截然不同的图景——公司最新发布的财报，与那些高声呼吁"
            "黄仁勋（Jensen Huang）回归的科技高管。"
        ),
    },
]


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    for fx in FIXES:
        hit = None
        for it in items:
            if fx["match"].lower() in (it.get("title") or "").lower():
                hit = it
                break
        if not hit:
            print("MISS:", fx["match"])
            continue
        en = hit["title"]
        hit["title_zh"] = fx["title_zh"]
        hit["summary_zh"] = fx["summary_zh"]
        hit["translated"] = True
        hit["method"] = "nllb+manual"
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
        changed += 1
        print("fixed:", hit.get("date"), hit.get("time"), en[:70])

    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("changed:", changed, "/", len(FIXES))


if __name__ == "__main__":
    main()
