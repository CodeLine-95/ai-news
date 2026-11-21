# -*- coding: utf-8 -*-
"""18:00 巡检：定稿 1 条本轮新增译文缺陷（The Decoder, 17:17）。

问题条目：
  'Bytedance argues most AI training phases are unnecessary and backs it up
   with a competitive open model'
  缺陷：NLLB 把品牌 Bytedance 音译成「拜登斯」（应为「字节跳动」）；把
  training phases / training data / training steps 中的 training 误译为
  「培训」（AI 语境应为「训练」）。

本脚本把人工定稿结果写回 data/ 覆盖表（JSON 层，线上持久卷即时生效）与
news.json；随后由 scripts/regen_overrides.py 同步到 manual_overrides.py
（代码层，随 git 发布生效）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    (
        "Bytedance argues most AI training phases are unnecessary and backs it up with a competitive open model",
        "字节跳动认为大多数 AI 训练阶段并无必要，并以一款有竞争力的开放模型予以佐证",
        "字节跳动与数所美国大学推出 Axion 1.0——一款 AI 智能体，仅经历三个训练阶段"
        "便在基准测试中对标 OpenAI 与 Anthropic 的顶级商业模型。研究者将这些提升归因于"
        "精心策划的训练数据，而非不断增加的训练步骤。该模型、数据与代码均已免费开放。",
    ),
]


def main():
    for en, zh_title, zh_summary in FIXES:
        for path, val in ((T_JSON, zh_title), (S_JSON, zh_summary)):
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            if d.get(en) != val:
                d[en] = val
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
                print("[fix_1800_new] 已更新覆盖表:", os.path.basename(path), "|", en[:50])

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        for en, zh_title, zh_summary in FIXES:
            if it.get("title") == en:
                it["title_zh"] = zh_title
                it["summary_zh"] = zh_summary
                it["translated"] = True
                hit += 1
                print("[fix_1800_new] 已回写:", en[:60])
    if hit:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[fix_1800_new] 已回写 news.json，命中条目:", hit)
    else:
        print("[fix_1800_new] 未命中条目，未改动数据")


if __name__ == "__main__":
    main()
