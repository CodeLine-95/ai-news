# -*- coding: utf-8 -*-
"""21:00 巡检第二轮修复（新增 2 条的译文缺陷）：

1. Clarivate（知识产权数据公司）被模型当普通动词直译成「澄清器」，
   中文完全认不出是哪家公司 —— 已在 translate.py 加品牌规则，
   本脚本人工定稿标题与摘要。
2. 「AI Latency vs. Throughput」标题里AI 被展开成「人工智能」，
   且「延迟与人工智能吞吐量」搭配不通 —— 定稿为
   「AI 延迟与吞吐量：TTFT、每秒 Token 及其他指标详解」。
3. Clarivate 那条摘要「带到 Microsoft Copilot 通过 IPOne」语序断裂，
   重新组织为通顺中文。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
    db = json.load(f)
items = db["items"] if isinstance(db, dict) else db

TITLE_FIX = {
    "Clarivate Connects CompuMark Trademark Data to Microsoft Copilot":
        "Clarivate 将 CompuMark 商标数据接入 Microsoft Copilot",
    "AI Latency vs. Throughput: TTFT, Tokens per Second, and Other Metrics Explained":
        "AI 延迟与吞吐量：TTFT、每秒 Token 及其他指标详解",
}

SUMMARY_FIX = {
    "Clarivate Connects CompuMark Trademark Data to Microsoft Copilot":
        "2026 年 11 月 2 日，Clarivate 宣布将旗下 CompuMark 的商标数据与洞察，"
        "通过公司的知识产权决策智能平台 IPOne 接入 Microsoft Copilot，"
        "让知识产权专业人士能在 Copilot 的工作流中用自然语言直接调用商标情报。",
    "AI Latency vs. Throughput: TTFT, Tokens per Second, and Other Metrics Explained":
        "人工智能延迟衡量的是请求或 token 需耗时多久，吞吐量衡量的则是服务系统"
        "每单位时间能完成多少工作。本文指南解释了实践中真正起决定作用的机制、"
        "需要权衡的取舍，以及如何评估与控制这两项指标。",
}

for it in items:
    t = it.get("title", "")
    if t in TITLE_FIX:
        it["title_zh"] = TITLE_FIX[t]
        it["translated"] = True
        it["method"] = "nllb+manual"
        print("title fixed:", it["date"], it["time"], it["source"])
    if t in SUMMARY_FIX:
        it["summary_zh"] = SUMMARY_FIX[t]
        it["translated"] = True
        it["method"] = "nllb+manual"
        print("summary fixed:", it["date"], it["time"], it["source"])

ov_path = os.path.join(DATA, "summaries_override.json")
with open(ov_path, encoding="utf-8") as f:
    ov = json.load(f)
for it in items:
    if it.get("method") == "nllb+manual" and it.get("title"):
        ov[it["title"]] = it.get("summary_zh") or ""
with open(ov_path, "w", encoding="utf-8") as f:
    json.dump(ov, f, ensure_ascii=False, indent=2)

with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)
print("done")
