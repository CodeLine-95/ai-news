# -*- coding: utf-8 -*-
"""2026-11-21 02:00 巡检：人工定稿 4 条新入库的 NLLB 机翻硬伤。

本轮整点调度新增 8 条，抽查发现以下 4 条标题/摘要存在专名误译或语义崩坏，
同引擎重译会重复相同错误，故人工定稿：

1) Marktechpost《RadixArk Ships DaisyRose-27B...》
   标题「据 DaisyRose-27B 称…训练用强化学习，只有 Radi」语义崩坏且截断；
   摘要「终端台」「染色扩展」「代码背景」等术语机械直译。
2) The Decoder《BoodleBox Joins Montana's AI Procurement Program》
   标题/摘要「布德尔 Box」「博德博克斯」专名音译崩坏。
3) The Decoder《Databricks Brings PostgreSQL 19 to Lakebase and Neon》
   标题「数据片…湖基和尼安」= Databricks / Lakebase / Neon 全误译。
4) Marktechpost《Brizy AI 1.9.5...》
   标题/摘要「布里齐」专名音译，「个人部分」应为「单个区块」。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

T1 = "RadixArk Ships DaisyRose-27B, a 27B Agentic Coding Model Trained With Reinforcement Learning Only"
T2 = "BoodleBox Joins Montana’s AI Procurement Program"
T3 = "Databricks Brings PostgreSQL 19 to Lakebase and Neon"
T4 = "Brizy AI 1.9.5 Generates Website Images and Lets Users Rework Individual Sections"

TITLE_FIX = {
    T1: "RadixArk 发布 DaisyRose-27B：一款仅用强化学习训练的 27B 智能体编程模型",
    T2: "BoodleBox 加入蒙大拿州 AI 采购计划",
    T3: "Databricks 将 PostgreSQL 19 引入 Lakebase 与 Neon",
    T4: "Brizy AI 1.9.5 生成网站图像，让用户重新编辑单个区块",
}

SUMMARY_FIX = {
    T1: (
        "本周，RadixArk 发布了其首个开放权重模型 DaisyRose-27B。"
        "DaisyRose-27B 是 RadixArk 的智能体编程模型，基于 Qwen3.8-27B 通过强化学习（RL）进行后训练。"
        "模型卡页面称其仅使用 RL，未采用监督微调（SFT）或蒸馏，并以 Apache 2.0 许可发布，"
        "可作为基础模型的直接替代品。主要结果：Terminal Bench 4.1 的 pass@1 从 5.6 提升至 12.0。"
        "可通过 GPULeaderboard.com 的 Chrome 扩展查看部署选项与规格。"
        "规格速览：27.8B 稠密参数（0.46B 视觉编码器、0.42B MTP 头），262,144 token 上下文，"
        "单张 GPU 即可运行；BF16 约 52 GB、FP8 约 29 GB、NVFP4 约 23 GB（仅 Blackwell 支持）。"
        "目标平台包括 H200、B200、GB300、RTX PRO 6000、RTX 5090、DGX Spark，也提供 GGUF 版本。"
        "性能方面，在全部 7 项公布的基准测试中均击败其 Qwen3.8-27B 基础模型。"
    ),
    T2: (
        "BoodleBox 表示，蒙大拿州已批准其成为该州「AI 产品与服务主采购计划」的供应商。"
        "该入选为符合条件的机构、学院和大学提供了一条采购这款协作式 AI 工作空间的途径。"
        "但这并不意味着这些机构已经下单、部署该产品，或同意在全州范围内使用。"
    ),
    T3: (
        "Databricks 已将 PostgreSQL 19 引入 Lakebase 和 Neon，"
        "让团队能够在托管基础设施上试用这一开源数据库的新维护、查询规划与复制工具。"
        "Databricks 称，PostgreSQL 项目发布新版本的当天，这两项服务就已提供支持。"
        "PostgreSQL 官方公告显示，社区版发布于 2026 年 11 月 19 日。"
    ),
    T4: (
        "Brizy 发布了其 AI 网站构建器的 1.9.5 版本，"
        "在 AI 生成工作流中以生成的图像取代 Unsplash 库存照片。"
        "该更新还改变了构建器组装页面的方式：Brizy 表示现在可根据提示生成单个区块，"
        "而不必依赖页面设计的现成模板块。这些改动让用户能在不丢弃已有可用草稿的情况下，"
        "仅修改网站的某一部分。"
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        touched = False
        if en in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[en]
            touched = True
        if en in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[en]
            touched = True
        if touched:
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

    print("[fix_1121_0200] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_1121_0200] 覆盖表 %d 条 / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
