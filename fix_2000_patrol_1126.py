# -*- coding: utf-8 -*-
"""20:00 例行巡检：定稿本轮新增条目的 NLLB 机翻误译。

20:00 整点抓取净新增 3 条（The Decoder / Microsoft ARTEX、The Decoder /
Nvidia 出口管制、ML Mastery / 1-Bit LLM），外加上一轮遗留的 InfoQ 演讲条。
重点误译：
- honeypots 被译成「蜜蜂」，faked success signals 被译成「假设成功信号」
- Nvidia 通知戴尔 / 超微停止发货这一核心信息被整句漏译
- BitNet 被译成「比特网」，H100 GPU 粘连、LLM-as-a-judge 出现双横线

按项目既有模式回填 news.json + JSON 覆盖表，再由
scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "Microsoft details how state-backed hackers use the ARTEX AI framework to automate cyberattacks": (
        "微软披露国家背景黑客如何利用 ARTEX AI 框架自动化网络攻击",
        "微软公布了 ARTEX 的技术架构。这一 AI 框架自 2026 年 7 月以来被广泛使用，可通过专用智能体发起网络攻击，几乎无需人工参与。来自中国和朝鲜的国家背景组织以及犯罪团伙已在使用该框架。微软建议使用蜜罐、伪造成功信号等欺骗手段作为防御，但面对具备学习与适应能力的智能体，这些手段能维持多久仍是未知数。",
    ),
    "Nvidia halts server shipments to Malaysia, Singapore, Thailand, and Indonesia after tighter US export controls": (
        "美国收紧出口管制后，英伟达（NVIDIA）暂停向马来西亚、新加坡、泰国和印尼发运服务器",
        "英伟达已通知戴尔、超微（Supermicro）等合作伙伴，停止向马来西亚、新加坡、泰国和印度尼西亚发运服务器。在美国针对中国云计算访问出台新的出口管制后，经销商已开始为数千颗 B300 芯片寻找买家，一位云服务商高管形容市场陷入「混乱」。东南亚数据中心的贷款和重大交易目前岌岌可危。",
    ),
    "Presentation: Finetuning Your Embedding Model for Better Search: Learning from Agentic Search at Dell": (
        "演讲：微调嵌入模型以提升搜索效果——来自戴尔智能体搜索的实践",
        "Rachel Shalom 介绍了戴尔如何通过微调开源嵌入模型，解决内部术语导致的企业 RAG 检索失败问题。她讨论了难负样本的数据准备、在 H100 GPU 上进行分布式 InfoNCE 损失训练、自动化超参数调优，以及采用 LLM-as-a-judge 进行生产环境评估。",
    ),
    "Running 1-Bit LLMs Locally: A Practical Guide to BitNet Inference": (
        "在本地运行 1-Bit 大模型：BitNet 推理实用指南",
        "在开始运行之前，了解微软的实测数据会有所帮助。",
    ),
}


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    matched = set()
    for it in items:
        en = it.get("title") or ""
        if en not in FIX:
            continue
        matched.add(en)
        title_zh, summary_zh = FIX[en]
        if it.get("title_zh") != title_zh:
            it["title_zh"] = title_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] title:", en[:60], "->", title_zh)
        if it.get("summary_zh") != summary_zh:
            it["summary_zh"] = summary_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] summary:", en[:60])
        tov[en] = title_zh
        sov[en] = summary_zh

    missing = set(FIX) - matched
    if missing:
        print("[warn] 未匹配到条目:", missing)

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 变更 %d 处 | 覆盖表 标题 %d 条 / 摘要 %d 条"
          % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
