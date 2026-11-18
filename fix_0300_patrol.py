# -*- coding: utf-8 -*-
"""03:00 例行巡检：调度新抓取 1 条（Google DeepMind "Genie 4 is now available"）
源站未提供摘要（summary 为空），属源数据缺失而非漏译。本脚本补齐原文摘要与
中文译文，并按历史巡检惯例固化覆盖三层，防止下一轮被空源数据覆盖：

1) data/news.json 内条目直接回填（立即生效）
2) data/titles_override.json / data/summaries_override.json（持久卷 JSON 层）
3) 再运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）

信息来源：DeepMind 官方 Genie 4 模型卡与博客、Google 官方博客。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = [
    {
        "match": "Genie 4 is now available",
        "title_zh": "Genie 4 现已开放",
        "summary": (
            "Google DeepMind has made Genie 4, its new world model for real-time "
            "interactive simulation, available as a research preview to trusted "
            "testers, rolling out to Google AI Ultra subscribers in Project Genie "
            "and early access partners in the Gemini API and Google AI Studio. "
            "Genie 4 is natively multimodal, generating audio—music, ambient sounds, "
            "and interactive dialogue—alongside the world, and lets users steer "
            "scenes in real time with natural language."
        ),
        "summary_zh": (
            "Google DeepMind 已将新一代世界模型 Genie 4 以研究预览形式向受信任测试者开放，"
            "并陆续面向 Project Genie 中的 Google AI Ultra 订阅者，以及 Gemini API 与 "
            "Google AI Studio 的早期访问伙伴推出。Genie 4 原生支持多模态，可在生成世界的"
            "同时同步生成音频（音乐、环境音与互动对话），用户还可用自然语言实时操控场景；"
            "相比 Genie 3，其在照片级真实感、流畅运动与实时操控上均有显著提升。"
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
        hit["summary"] = fx["summary"]
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
