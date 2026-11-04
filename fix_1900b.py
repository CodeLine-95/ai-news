# -*- coding: utf-8 -*-
"""2026-11-02 19:00 例行巡检：修复 19:00 轮次新增条目的译文缺陷。

问题条目（均为 2026-11-02 19:00 轮次新抓取）：
  1) 'OpenAI's Lehane Calls AI the Number-One Issue of the 2028 Election'
     （Unite.AI, 18:50）
     缺陷：标题「开放 AIs Lehane 称 AI 为…」、摘要「开通 AI 首席全球事务官…」
     —— OpenAI 被译成「开放 AI」/「开通 AI」（带空格形态未登记在品牌还原表），
     且所有格 's 处理成「AIs」，中文读起来是断裂的。

  2) 'Why AI Agents Need Evidence Before They Retry'
     （Unite.AI, 18:18）
     缺陷：标题「为什么 AI 智能体在退休之前需要证据？」—— retry（重试）
     被 NLLB 误译为「退休」（retire），语义与原文完全相反。
     摘要英文原文本身在源站就被黏连（小标题 + 正文之间无分隔），
     译文因此断裂为「如何防止丢失的响应变成重复行动授权一次退款的…」。

根因修复（translate.py）：
    BRAND_TERMS 的 "OpenAI" 补入带空格形态「开通 AI」「开放 AI」；
    新增 _fix_retry_confusion()：retry（重试）被译成「退休」时还原，
    仅在原文含 retry 且不含 retire 时生效，避免误伤真正的退休语境。

本脚本：只对这两条做人工定稿，不动其余 276 条存量译文。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

# 缺陷条目 1：品牌还原修复后引擎译文已自然正确，此处人工定稿以保证稳定
EN1 = "OpenAI’s Lehane Calls AI the Number-One Issue of the 2028 Election"
ZH1_TITLE = "OpenAI 的 Lehane 称 AI 是 2028 年大选的頭號議題"
ZH1_SUMMARY = (
    "OpenAI 首席全球事务官克里斯·莱汉（Chris Lehane）撰写了一份备忘录，"
    "主张人工智能将成为 2028 年总统大选的头号议题，并提出他认为"
    "候选人必须回答的五个问题，以构建人工智能议程。"
    "该备忘录于 2026 年 11 月 2 日公开。"
)

# 缺陷条目 2：源站英文摘要本身小标题与正文黏连，人工定稿补回语义分层
EN2 = "Why AI Agents Need Evidence Before They Retry"
ZH2_TITLE = "为什么 AI 智能体在重试之前需要证据"
ZH2_SUMMARY = (
    "如何避免一次丢失的响应变成重复操作？一个获得授权、只需执行一次退款"
    "的支持智能体发出请求，却中途丢失了连接。智能体没有收到成功确认，"
    "于是再次尝试发送退款。如果最初的请求其实已经成功，"
    "那么这次重试就可能导致第二笔退款。这纯属假设，"
    "但它揭示了一个仅靠提升模型准确率无法解决的问题。"
)


def put_override(path, key, value):
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    d[key] = value
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    n = 0
    for it in data.get("items", []):
        title = it.get("title")
        if title == EN1:
            it["title_zh"] = ZH1_TITLE
            it["summary_zh"] = ZH1_SUMMARY
            it["translated"] = True
            it["method"] = "nllb+manual"
            n += 1
        elif title == EN2:
            it["title_zh"] = ZH2_TITLE
            it["summary_zh"] = ZH2_SUMMARY
            it["translated"] = True
            it["method"] = "nllb+manual"
            n += 1

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 人工覆盖表也要写入，保证下一轮调度重跑时不会被引擎译文覆盖回去
    for en, t, s in ((EN1, ZH1_TITLE, ZH1_SUMMARY), (EN2, ZH2_TITLE, ZH2_SUMMARY)):
        put_override(T_JSON, en, t)
        put_override(S_JSON, en, s)
        print("[fix_1900b] 已写入覆盖表:", en[:42])

    print("[fix_1900b] 已回写 %d 条" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
