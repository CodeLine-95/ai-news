# -*- coding: utf-8 -*-
"""06:00 例行巡检：对整点调度新增 1 条 NLLB 机翻硬伤人工定稿。

问题：
  OpenAI's chief scientist has thoughts on how to limit AI development
  - 标题「OpenAI 的首席科学家有想法如何限制人工智能开发」为直译腔，
    "has thoughts on how to" 应译为「谈如何…」；AI 沿用通用译法「AI」。
  - 摘要「为了设定 AI 开发的速度限制，你需要同意如何测量速度。」
    "agree on how to measure speed" 应译为「就如何衡量速度达成一致」。

写入三层：JSON 标题表 / JSON 摘要表 / news.json；按 id 定位，避免引号不匹配。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

FINAL = {
    "772a602107cad2ee0d2e7ec2299ca0b5": (
        "OpenAI 首席科学家谈如何限制 AI 发展",
        "要为 AI 发展设定速度上限，各方需先就如何衡量速度达成一致。",
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
    print("[fix_patrol_0600_1123] 定稿 %d 条" % hit)
    print("[fix_patrol_0600_1123] 覆盖表: 标题 %d / 摘要 %d" % (len(t), len(s)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
