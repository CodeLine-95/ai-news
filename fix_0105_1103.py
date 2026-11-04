# -*- coding: utf-8 -*-
"""2026-11-03 01:05 重启首轮新增 3 条的人工定稿。

NLLB 直译缺陷：
1. "eager and compiled execution" → 「快速和编译的执行」：
   eager execution 是 PyTorch 的即时执行模式，与「快速」不是一回事；
   "Bring Native PyTorch Support to Google TPUs" 译法尚可但生硬。
2. "What Should Enterprises Own in Their AI Stack?" → 「AI 堆」：
   stack 在此指「技术栈」，不是「堆」；且摘要第一句把原文缺失的句号
   补成了「人工智 能对话的重点问题」，整段语序崩坏。
3. "Anthropic Details..." → 「人类细节修改的 IPO 申请」：
   Anthropic 被译成「人类」；"amended" 是「修订版」不是「修改的」；
   $895.4 billion → 「8954 亿美元」应为「8,954 亿美元」；
   Anthropic, PBC 的 PBC 被丢掉只剩「PBC 披露了」。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    "Google and Meta Open-source TorchTPU to Bring Native PyTorch Support to Google TPUs":
        "Google 与 Meta 开源 TorchTPU，为 Google TPU 带来原生 PyTorch 支持",
    "What Should Enterprises Own in Their AI Stack?":
        "企业该在自己的 AI 技术栈中掌握什么？",
    "Anthropic Details Long-Term Compute Commitments in Amended IPO Filing":
        "Anthropic 在修订版 IPO 文件中披露长期算力采购承诺",
}

SUMMARY_FIX = {
    "Google and Meta Open-source TorchTPU to Bring Native PyTorch Support to Google TPUs":
        "TorchTPU 是 Google 与 Meta 合作开发的开源项目，为 Google TPU 提供原生 PyTorch 后端。"
        "它让 PyTorch 工作负载几乎无需修改代码即可在 TPU 硬件上运行，"
        "并支持即时执行与编译执行、分布式计算以及针对特定硬件的优化。",
    "What Should Enterprises Own in Their AI Stack?":
        "AI 转型的下一个阶段，关键在于企业能从 AI 的每一次决策中学到什么，"
        "以及这份学习成果的归属权归谁。围绕 AI 的讨论一直聚焦于一个问题："
        "这些模型能做什么？它们被基准测试、被试点、被惊叹——"
        "在实验阶段，这确实是正确的问题。但对今天的位置而言，它已不是。"
        "企业的技术栈中，究竟哪些部分应当由自己拥有？",
    "Anthropic Details Long-Term Compute Commitments in Amended IPO Filing":
        "Anthropic, PBC 在 2026 年 11 月 2 日提交的修订版 Form S-1 文件中披露，"
        "其采购承诺与租赁协议规模约合 8,954 亿美元，并称其中绝大部分与算力和基础设施相关。"
        "这份初步招股说明书还补充了 2026 年第三季度的业绩数据，"
        "该公司正在筹备 A 类普通股的首次公开发行。",
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    hit = 0
    for it in items:
        t = it.get("title", "")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit += 1
            print("fixed:", it["date"], it["time"], it["source"], "|", t[:50])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"

    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    for name, fix in (("titles_override.json", TITLE_FIX),
                      ("summaries_override.json", SUMMARY_FIX)):
        path = os.path.join(DATA, name)
        cur = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                cur = json.load(f)
        cur.update(fix)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=2)

    print("fixed items:", hit, "/ expected", len(TITLE_FIX))


if __name__ == "__main__":
    main()
