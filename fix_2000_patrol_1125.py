# -*- coding: utf-8 -*-
"""20:00 例行巡检：定稿本轮 4 条新增资讯的 NLLB 生硬/漏译译文。

写入 JSON 覆盖表 + 回填 news.json，再运行 scripts/regen_overrides.py
同步代码层 manual_overrides.py（部署端持久卷不会随发布更新 JSON 表）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

FIXES = {
    "PrismML shrinks a 54 GB language model to 5.9 GB by reducing every weight to just three possible values": (
        "PrismML 通过将每个权重压缩为仅三种可能取值，把 54 GB 语言模型缩小到 5.9 GB",
        "初创公司 PrismML 发布了 Ternary Bonsai 2.5 27B，这是其极致压缩语言模型的升级版本。"
        "通过将每个权重缩减为仅三种可能取值（三值量化），原本 54 GB 的模型体积被压缩到 5.9 GB。",
    ),
    "AI Agents Are Becoming a Commodity. Your Company DNA Can Be Your Competitive Advantage": (
        "AI 智能体正在沦为同质化商品，你的公司 DNA 才是竞争优势",
        "设想两家银行都用 AI 智能体处理客户咨询。一家银行以灵活著称——免除手续费，"
        "并在客户遭遇财务困境时展现同理心；另一家则以透明与一致为傲，对所有人适用同样清晰的规则。"
        "当客户对透支手续费提出异议时，除非这些智能体经过训练、能够体现各自银行的服务理念，"
        "否则它们给出的回答可能同样是千篇一律的。",
    ),
    "Airplane Turbulence Is Extremely Hard to Predict, but Maybe Not for Long": (
        "飞机颠簸极难预测，但这种情况或许不会持续太久",
        "这道被称为「经典物理学中最后剩下的难题之一」的问题正迎来助力：数 TB 的众包数据，"
        "以及运用机器学习与 AI 的新方法，正在推动其取得突破。",
    ),
    "EpochGeo Deal Gives BlackSky AI Tools for Fusing Defense Data": (
        "EpochGeo 收购交易让 BlackSky 获得融合国防数据的 AI 工具",
        "BlackSky Technology 于 2026 年 11 月 24 日宣布收购 EpochGeo，为其实时天基情报业务"
        "增添能够融合多源数据的人工智能与机器学习（AI/ML）工具。EpochGeo 研发时空 AI/ML 技术，"
        "可跨位置与时间维度分析信息，同时提供数据管理工具和面向任务的多源分析能力。",
    ),
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    titles = load(T_JSON)
    summaries = load(S_JSON)
    for key, (title_zh, summary_zh) in FIXES.items():
        titles[key] = title_zh
        summaries[key] = summary_zh
    save(T_JSON, titles)
    save(S_JSON, summaries)

    news = load(NEWS)
    fixed = 0
    for it in news["items"]:
        fix = FIXES.get(it.get("title"))
        if not fix:
            continue
        it["title_zh"], it["summary_zh"] = fix
        it["translated"] = True
        it["method"] = "manual"
        fixed += 1
    save(NEWS, news)
    print("定稿条目数:", fixed)


if __name__ == "__main__":
    main()
