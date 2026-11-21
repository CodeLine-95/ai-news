# -*- coding: utf-8 -*-
"""2026-11-21 14:00 巡检：定稿本轮新增 1 条 NLLB 机翻硬伤。

1) Marktechpost《Baseten Releases Bison-1 and Groundhog-1 ...》(12:01)——
   NLLB 把 bison-1/groundhog-1 截成「-1」「土-1」，Hugging Face 译成
   「拥抱面」，weights→重量、inference→推断、ranks #1 of 19→「19 中排名第 1」
   均为硬伤。人工定稿标题+摘要。

覆盖三层：news.json 回填 + JSON 覆盖表 + manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

T = "Baseten Releases Bison-1 and Groundhog-1, Topping Decision Model Index"
T2 = "Baseten Extends Decision Models to 128K Context and Image Input"

TITLE_FIX = {
    T: "Baseten 发布 Bison-1 与 Groundhog-1，登顶决策模型指数",
    T2: "Baseten 将决策模型扩展至 128K 上下文与图像输入",
}

SUMMARY_FIX = {
    T: (
        "Baseten 发布了基于 Google Gemma 4 构建的两款开放权重决策模型 bison-1 与 groundhog-1。"
        "决策模型不生成文本，而是针对是/否、选择与评分类问题返回经过校准的概率。"
        "在 Artificial Analysis 决策指数 v2.1 中，Baseten 的 bison-1 得分 76，在 19 个模型中排名第 1。"
        "两款模型均将上下文从 16k 提升至 128k tokens，并支持图像输入；对于路由、分流与护栏流水线而言，"
        "这意味着一次调用即可纳入完整的策略与历史记录。简而言之，规模方面：bison-1 为 310 亿参数的稠密模型，"
        "groundhog-1 为 260 亿参数的混合专家（MoE）模型、约 40 亿参数激活，两者均支持 128k tokens（131,072）。"
        "运行方式：可通过 Baseten Model APIs 使用，权重以 BF16 格式在 Hugging Face 上开放；"
        "未列出推理 GPU 或量化版本。仅 BF16 权重一项，按估算约为 62 GB（bison-1）与 52 GB（groundhog-1）。"
    ),
    T2: (
        "Baseten 于 2026 年 11 月 20 日发布 bison-1 与 groundhog-1，这是两款基于 Google Gemma 4 后训练、"
        "对外开放权重的模型，用于针对预定义决策返回经过校准的概率。在 Artificial Analysis 决策指数 v2.1 中，"
        "bison-1 得分 76，在 19 个参评决策模型中位列第一。两款模型均可通过 Baseten Model APIs 使用，"
        "权重在 Hugging Face 上开放。"
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en not in TITLE_FIX:
            continue
        it["title_zh"] = TITLE_FIX[en]
        if en in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[en]
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:55])
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    added_t = added_s = 0
    for k, v in TITLE_FIX.items():
        if titles.get(k) != v:
            titles[k] = v
            added_t += 1
    for k, v in SUMMARY_FIX.items():
        if summaries.get(k) != v:
            summaries[k] = v
            added_s += 1
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1400] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_1400] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
