# -*- coding: utf-8 -*-
"""05:00 例行巡检：对整点调度新增 1 条 NLLB 机翻硬伤人工定稿。

问题：
  Bessent Declines to Back Huang's Return Amid Nvidia Investigations
  - 标题「在 Nvidia 调查中，Bessent 拒绝回归黄。」语义崩坏：
    "back Huang's return" 意为「支持黄仁勋回归（CEO）」，
    NLLB 误译为「拒绝回归黄」；Huang 指 Jensen Huang（黄仁勋），
    不应只译「黄」；amid 是「在…之际」而非「调查中」。
  - 摘要「唐纳德特朗普」缺间隔号、「黄应该恢复工作」应为「黄仁勋应复职」、
    "where the buck stops" 是「责任归属/最终由谁承担责任」，
    NLLB 误译为「资金停留在哪里」。

写入三层：JSON 标题表 / JSON 摘要表 / news.json；按 id 定位，避免引号不匹配。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

FINAL = {
    "121776a6999925efe152e3bdba6c4660": (
        "英伟达调查之际，贝森特拒绝支持黄仁勋回归",
        "美国财政部长斯科特·贝森特（Scott Bessent）在 2026 年 11 月 22 日播出的 CBS 新闻采访中表示，特朗普政府仍未从英伟达方面获得有关向中国销售先进 AI 芯片问题的答复，并拒绝在出口管制失职责任被厘清之前支持黄仁勋（Jensen Huang）回归首席执行官一职。当被问及特朗普总统关于黄仁勋应当复职的立场时，贝森特表示，官员们首先需要看清「最终责任由谁承担」。",
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
        print("  定稿:", en)

    json.dump(t, open(T_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(s, open(S_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(news, open(NEWS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[fix_patrol_0500_1123] 定稿 %d 条" % hit)
    print("[fix_patrol_0500_1123] 覆盖表: 标题 %d / 摘要 %d" % (len(t), len(s)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
