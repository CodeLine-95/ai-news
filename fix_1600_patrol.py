# -*- coding: utf-8 -*-
"""16:00 巡检：定稿 2 条 Simon Willison 插件版本号标题的 NLLB 截断缺陷。

llm-gemini 0.37 / 0.36 被译成「Gemini 0.37 ll」「Gemini 0.36 ll」
（llm- 前缀丢失、ll 被挪到末尾）。这类版本标识符按原文保留，
写入 JSON 覆盖表后由当前调度周期自动回填，并同步重生代码层覆盖表。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")

FIX = {
    "llm-gemini 0.37": "llm-gemini 0.37",
    "llm-gemini 0.36": "llm-gemini 0.36",
}


def main():
    titles = json.load(open(T_JSON, encoding="utf-8"))
    added = 0
    for k, v in FIX.items():
        if titles.get(k) != v:
            titles[k] = v
            added += 1
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    print("[fix_1600] 标题覆盖表新增 %d 条，共 %d 条" % (added, len(titles)))


if __name__ == "__main__":
    raise SystemExit(main())
