# -*- coding: utf-8 -*-
"""14:00 例行巡检：人工定稿当日新增的 2 条含品牌音译缺陷的译文。

问题条目：
  1) 'SemiAnalysis Launches GDPx Benchmark Spanning 11 Agentic Domains'
     （Unite.AI, 13:35）
     模型把研究机构名 SemiAnalysis 意译成「半分析」，读者会误以为
     是一篇讲「半分析」的文章，而非机构名。

  2) 'Ceva NeuPro NPU Family Reaches Production in Mobilint REGULUS Edge AI SoC'
     （Unite.AI, 13:18）
     同一句里三处品牌名失真 + 两处半导体术语误译：
       - Ceva      -> 「塞瓦」（音译，品牌丢失）
       - Mobilint  -> 「莫比林特」（音译，品牌丢失）
       - fabless   -> 「无形」半导体公司（应为「无晶圆厂」）
       - edge AI   -> 「尖端 AI」（应为「边缘 AI」）
       - system-on-chip -> 「系统-on-chip」（中英混排，应为「系统级芯片」）
     标题的「NPU 家庭在……中生产」也不通：family 指产品家族，
     应为「NPU 家族量产落地」。

根因修复：已在 translate.py 的 BRAND_TERMS 补入 SemiAnalysis / Ceva /
Mobilint 三条品牌还原规则，在 TERM_FIXES 补入 fabless / edge AI /
system-on-chip 三条术语修复规则，使后续轮次自动生效。

处理：写入人工定稿标题 + 摘要覆盖，并回写数据。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

# --- 条目 1：SemiAnalysis 发布 GDPx 基准 ---
EN_1 = "SemiAnalysis Launches GDPx Benchmark Spanning 11 Agentic Domains"
ZH_1_TITLE = "SemiAnalysis 发布 GDPx 基准，覆盖 11 个智能体领域"
ZH_1_SUMMARY = (
    "2026 年 11 月 2 日，SemiAnalysis 发布了 GDPx——一项衡量通用智能体能力、"
    "涵盖 11 个专业领域的基准，公告由 Max Kan、Andrew Megalaa 与 Dylan Patel 撰写。"
    "Anthropic 的 Claude Opus 5.5 以 12.0% 的分数位列首版排行榜榜首。"
    "GDPx 官网列出 1.0 版本共 206 项任务，由 14 家专业数据合作方构建，"
    "排行榜共收录 13 个模型，其中 Claude Opus 5.5 以平均 51 美元的成本位列第一。"
)

# --- 条目 2：Ceva NeuPro NPU 家族量产落地 ---
EN_2 = (
    "Ceva NeuPro NPU Family Reaches Production in Mobilint "
    "REGULUS Edge AI SoC"
)
ZH_2_TITLE = "Ceva NeuPro NPU 家族在 Mobilint REGULUS 边缘 AI SoC 中量产"
ZH_2_SUMMARY = (
    "Ceva 于 2026 年 11 月 2 日宣布，Mobilint 已将 Ceva 的 SensPro AI DSP "
    "与 NeuPro-Nano NPU 部署至 REGULUS——Mobilint 的边缘 AI 系统级芯片，"
    "这是 Ceva 所称的 NeuPro NPU 家族首次量产落地。"
    "Mobilint 是一家成立于 2019 年、总部位于首尔的无晶圆厂 AI 半导体公司，"
    "专注于为边缘与端侧 AI 应用提供 NPU 与 AI SoC。"
)

FIXES = [
    (EN_1, ZH_1_TITLE, ZH_1_SUMMARY),
    (EN_2, ZH_2_TITLE, ZH_2_SUMMARY),
]


def main():
    for path, key, val in (
        (T_JSON, EN_1, ZH_1_TITLE),
        (S_JSON, EN_1, ZH_1_SUMMARY),
        (T_JSON, EN_2, ZH_2_TITLE),
        (S_JSON, EN_2, ZH_2_SUMMARY),
    ):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get(key) != val:
            d[key] = val
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print("[fix_1400] 已更新覆盖表:", os.path.basename(path), "->", key[:52])

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        for en, zh_t, zh_s in FIXES:
            if it.get("title") == en:
                it["title_zh"] = zh_t
                it["summary_zh"] = zh_s
                it["translated"] = True
                hit += 1
                print("[fix_1400] 已回写:", en[:60])
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix_1400] 已回写数据 %d 条" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
