# -*- coding: utf-8 -*-
"""05:00 巡检补修：4 条历史机翻硬伤（Spotify / Thinking Machines Lab 音译崩坏）。

- Spotify → 「斯波地夫」（标题+摘要残留）
- Thinking Machines Lab → 「思考机/思考机器实验室」「智能机器释放」（标题+摘要）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "52588916": (
        "Spotify 向所有艺术家开放艺人资料保护功能",
        "2026 年 11 月 17 日，Spotify 向所有艺术家开放 Artist Profile Protection（艺人资料保护），"
        "扩大了可选控制功能，允许艺术家审查以其名义发布的作品，并在这些作品影响其个人资料、"
        "统计数据或听众数时将其下架。",
    ),
    "34711bc4": (
        "Spotify 新工具旨在阻止深度伪造内容被归到真实艺人名下",
        "此次更新之前，Billboard 上月报道称，索尼音乐已要求数字平台下架超过 26 万首深度伪造歌曲，"
        "这一数字几乎是该公司 3 月公布数量的两倍。",
    ),
    "dea179e2": (
        "Thinking Machines 发布 Inkling 2 Small：5940 亿总参数、170 亿激活参数的 MoE 模型",
        "Thinking Machines Lab 发布了 Inkling 2 Small，这是其第二代 Inkling 系列的首款模型。"
        "Inkling 2 Small 是一个稀疏专家混合（MoE）模型，总参数量 5940 亿、激活参数 170 亿，"
        "支持文本与图像输入，并支持可变的计算预算。",
    ),
    "fcb5909c": (
        "Thinking Machines Lab 发布 Inkling 2 Small，权重即将开放",
        "Thinking Machines Lab 于 2026 年 11 月 5 日推出 Inkling 2 Small，"
        "使其第二代模型可通过 Tinker 使用。这个稀疏专家混合（MoE）系统拥有 5940 亿总参数和"
        "170 亿激活参数，面向文本与图像任务，权重将在稍后开放。",
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    changed = 0
    for it in items:
        iid = it.get("id", "")
        key = next((k for k in FIX if iid.startswith(k)), None)
        if not key:
            continue
        title_zh, summary_zh = FIX[key]
        en = (it.get("title") or "").strip()
        it["title_zh"] = title_zh
        it["summary_zh"] = summary_zh
        it["method"] = "nllb+manual"
        titles[en] = title_zh
        summaries[en] = summary_zh
        changed += 1
        print("legacy fixed:", iid[:8], en[:55])
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)
    print("[fix_0500_legacy] 回填 %d 条" % changed)


if __name__ == "__main__":
    main()
