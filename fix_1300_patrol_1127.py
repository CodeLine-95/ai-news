# -*- coding: utf-8 -*-
"""13:00 例行巡检：定稿 1 条 NLLB 机翻硬伤（Sakana AI / Namazu Small）。

原标题中的 "a 30B Model Built on Nemotron 3 Nano" 被译成「一个 30B 型号在
Nemotron 3Nano Sak 上构建的模型」；摘要中 Sakana/NVIDIA 被截成 Sahanas、
NVIDIAs，"Nemotron 3 Nano" 被误译为「Nemotron 3 纳米」，基准结论也损失了
自报口径与最差项说明。按英文原文重述并写入人工覆盖表，保证服务端重启 /
线上持久卷也能回填为定稿版本。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = [
    {
        "en": "Sakana AI Releases Namazu Small, a 30B Model Built on Nemotron 3 Nano",
        "title_zh": "Sakana AI 发布 Namazu Small：基于 Nemotron 3 Nano 的 300 亿参数推理模型",
        "summary_zh": (
            "Sakana AI 宣布推出 Sakana Namazu Small——一款基于 NVIDIA Nemotron 3 Nano "
            "构建的 300 亿参数推理模型。这家位于日本的实验室从 Nemotron 3 Nano 的预训练底座出发，"
            "在内部完成了持续预训练与后训练。Sakana AI 团队称，该模型在 25 项基准测试的平均成绩上"
            "超过了 NVIDIA 的 120B 参数 Nemotron 3 Super。要点：规模方面，总参数 300 亿、"
            "激活参数 30 亿（Sakana 图表中标注为 30B-A3B）；上下文长度未披露；运行硬件未披露，"
            "Sakana 称其小到足以在自有环境中运行，Nemotron 3 Nano 底座面向 DGX Spark、H100 "
            "与 B200 GPU 设计；性能方面，25 项基准平均 60.1 分，领先 Nemotron 3 Super（56.2）"
            "与 Nano（50.2），成绩为自报；最佳成绩为 BrowseComp 73.5，约为 Nemotron 3 Super "
            "36.1 的两倍；最差为 SimpleQA Verified 6.8，低于 Nemotron 3 Nano（9.1）和 Super（18.1）。"
        ),
    },
]


def main():
    db_path = os.path.join(DATA, "news.json")
    db = json.load(open(db_path, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    for fx in FIXES:
        en, zh_t, zh_s = fx["en"], fx["title_zh"], fx["summary_zh"]
        tov[en] = zh_t
        sov[en] = zh_s
        for it in items:
            if (it.get("title") or "").strip() != en:
                continue
            if it.get("title_zh") != zh_t:
                it["title_zh"] = zh_t
                changed += 1
            if it.get("summary_zh") != zh_s:
                it["summary_zh"] = zh_s
                changed += 1
            it["translated"] = True
            it["method"] = "nllb+manual"
            break

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(db_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[fix] 定稿 %d 处 | 标题覆盖 %d / 摘要覆盖 %d" % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
