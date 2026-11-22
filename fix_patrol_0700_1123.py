# -*- coding: utf-8 -*-
"""07:00 例行巡检：对整点调度新增 1 条 NLLB 机翻硬伤人工定稿。

问题条目（InfoQ AI, 06:44）：
  QCon San Francisco 2026: The Harness Is the New Operating System
  - 标题「旧金山 2026 年 QCon：使用权是新操作系统」把术语 harness 误译为
    「使用权」；harness 在智能体语境下指包裹模型的「智能体框架/约束装置」，
    应保留术语并点明含义。
  - 摘要把 Mad Labs 意译成「疯狂实验室」（公司名应保留原文）、
    context 译成「文本」（应为「上下文」）、
    feedback loops 译成「反循环」（应为「反馈循环」）、
    「the harness around an AI model」译成「人工智能模型的运用」（应为
    「包裹在 AI 模型外层的 harness」）。

写入三层：JSON 标题表 / JSON 摘要表 / news.json；按 id 定位。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

FINAL = {
    "2a50ef21668613f72c79cb9aeeb013f4": (
        "QCon 旧金山 2026：Harness（智能体框架）才是新操作系统",
        "在 2026 年 QCon 旧金山大会上，Mad Labs 创始人兼首席执行官 Manju Rajashekhar 为大会开幕，"
        "提出观点：决定智能体能做什么、以及能做得多安全的，是包裹在 AI 模型外层的 harness（智能体框架），"
        "而非模型本身。这场主题演讲把 harness 的各个组成部分——上下文、工具、状态、权限与反馈循环——"
        "逐一对应到操作系统早已承担的职责上。",
    ),
    "96ead1957e2c6cf5f523b7e46c3bdc3e": (
        "重大科技故障还没到尽头",
        "过去一周左右，我们目睹了 FAA（美国联邦航空管理局）全国性停飞、持续数日令整家公司停摆的 "
        "Outlook 故障，以及摩根大通（JPMorgan Chase）的银行系统故障。但各方共识是：类似故障还会更多。"
        "美国国家情报总监杰伊·克莱顿（Jay Clayton）对 CNN 表示：「美国民众应当做好大规模投入升级系统的准备；"
        "应当做好投资网络安全的准备；还应当明白，每当技术、算力与应用发生阶跃式变革，路上难免会有颠簸。」",
    ),
}


def main():
    t = json.load(open(T_JSON, encoding="utf-8"))
    s = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(NEWS, encoding="utf-8"))
    items = news.get("items", [])

    hit = 0
    for iid, (zh_t, zh_s) in FINAL.items():
        target = next((it for it in items if it.get("id") == iid), None)
        if not target:
            print("  [警告] news.json 未匹配 id:", iid)
            continue
        en = (target.get("title") or "").strip()
        t[en] = zh_t
        s[en] = zh_s
        target["title_zh"] = zh_t
        target["summary_zh"] = zh_s
        target["translated"] = True
        target["method"] = "manual"
        target.pop("needs_retranslate", None)
        target.pop("retranslate_attempts", None)
        hit += 1
        print("  定稿:", en, "->", zh_t)

    json.dump(t, open(T_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(s, open(S_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(news, open(NEWS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[fix_patrol_0700_1123] 定稿 %d 条" % hit)
    print("[fix_patrol_0700_1123] 覆盖表: 标题 %d / 摘要 %d" % (len(t), len(s)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
