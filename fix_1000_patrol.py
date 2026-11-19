# -*- coding: utf-8 -*-
"""10:00 例行巡检：调度重启首轮新增 2 条，抽查发现 2 处 NLLB 机翻硬伤，人工定稿。

硬伤清单：
1) Google's AI Controls... 标题译成「控制有主要地区重新思考搜索」语义崩坏，
   摘要「未来学校控制器」「区块」为错译；
2) Fathom（AI 治理组织）标题音译成「富通」，摘要前后「Fathom/费托姆」不一致。

覆盖三层（与历史巡检一致）：
1) data/news.json 内条目直接回填（立即生效）
2) data/titles_override.json / data/summaries_override.json（持久卷 JSON 层）
3) 再运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = [
    {
        "match": "Fathom Urges Rapid Implementation",
        "title_zh": "AI 治理组织 Fathom 敦促加州快速落实 AI 监管计划",
        "summary_zh": (
            "人工智能治理组织 Fathom 于 2026 年 11 月 18 日表示，加州州长加文·纽森"
            "（Gavin Newsom）新出台的前沿 AI 路线图反映了其多项建议，并敦促加州尽快"
            "针对灾难性风险实施强制性的独立评估。Fathom 提出并倡导了独立验证组织（IVO）"
            "模式——由外部评估机构对 AI 模型与系统进行风险评估。"
        ),
    },
    {
        "match": "Google’s AI Controls Have Major Districts Rethinking Search",
        "title_zh": "Google 的 AI 管控措施促使多个主要学区重新考虑搜索引擎",
        "summary_zh": (
            "据《纽约时报》2026 年 11 月 18 日报道（由 The Verge 转载），纽约市、洛杉矶"
            "和芝加哥的学区官员正在考虑替换 Google 搜索，因为 Google 即将面向学校推出的"
            "管控措施会把搜索访问与其 AI 功能绑定。这项定于 2027 年生效的调整将两项设置"
            "关联在一起：学区一旦关闭由 Gemini 驱动的功能，搜索也会一并关闭。"
        ),
    },
]


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
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
