# -*- coding: utf-8 -*-
"""2026-11-24 16:00 例行巡检：定稿本轮新增 1 条 NLLB 机翻硬伤。

16:00 整点调度新增 1 条（Unite.AI，2694→2695）：
《ATOM Signs ¥4.5B in Loan Facilities for GPU Cluster, Humanoid Output》
（15:27）——标题把 "Humanoid Output" 误译为「人体输出」，"¥4.5B"
未换算为「45 亿日元」；摘要把银行名按音译写成「苏米托莫三 / 米苏比西 UFJ」，
且 "borrowing limits" 误译为「借款限制」。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
运行后重新生成报告，并通过发布/重启让线上生效。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE = "ATOM Signs ¥4.5B in Loan Facilities for GPU Cluster, Humanoid Output"

TITLE_ZH = "ATOM 签署 45 亿日元贷款额度，用于建设 GPU 集群与推进人形机器人量产"

SUMMARY_ZH = (
    "2026 年 11 月 24 日，ATOM 宣布与瑞穗银行（Mizuho Bank）、三井住友银行"
    "（Sumitomo Mitsui Banking Corp.）和三菱日联银行（Mitsubishi UFJ Bank）"
    "达成协议，获得总额 45 亿日元的贷款额度，用于建设本地部署的 GPU 集群，"
    "并为人形机器人量产做好准备。其中三井住友银行提供 20 亿日元，瑞穗银行提供"
    " 15 亿日元，三菱日联银行提供 10 亿日元。"
)


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    changed = 0
    for it in items:
        if (it.get("title") or "").strip() != TITLE:
            continue
        it["title_zh"] = TITLE_ZH
        it["summary_zh"] = SUMMARY_ZH
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), TITLE)

    titles[TITLE] = TITLE_ZH
    summaries[TITLE] = SUMMARY_ZH

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1600_1124] news.json 回填 %d 条；覆盖表 %d / %d 条"
          % (changed, len(titles), len(summaries)))
    return 0 if changed == 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
