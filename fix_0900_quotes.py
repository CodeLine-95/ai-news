# -*- coding: utf-8 -*-
"""2026-11-03 09:00 巡检：修复 1 条历史条目未闭合的引号。

条目标题：Why Engineers Should Brave Capitol Hill（2026-10-22 21:00）

原文的引号是嵌套结构（外层单引号包住整句，内层单引号包住引语）：
    'My first reaction was, 'Wow, I get to visit Congress,' ' says Jathar
中文按「外层『内层』」的习惯翻译成「『』」，但外层的「没有收尾：
    「我的第一反应是，『哇，我要去参观国会了，』Jathar 说道。…
读者看到的是一个悬空的左引号，句子读起来断裂。

这是上一轮人工定稿时遗留的排版缺陷（模型直译的引号错位未被
人工发现）。本脚本补上外层收尾引号，并把该条的中英引号层级
一并校验。

同时给 validate_run.py 增加「引号配对」门禁，避免同类缺陷再次漏检。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

KEY = "Why Engineers Should Brave Capitol Hill"

OLD_FRAG = "『哇，我要去参观国会了，』Jathar 说道。"
NEW_FRAG = "『哇，我要去参观国会了，』」Jathar 说道。"


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    fixed = 0
    for it in items:
        if it.get("title") != KEY:
            continue
        s = it.get("summary_zh") or ""
        if OLD_FRAG in s and NEW_FRAG not in s:
            it["summary_zh"] = s.replace(OLD_FRAG, NEW_FRAG)
            it["method"] = "nllb+manual"
            fixed += 1
            print("fix quotes:", it["date"], it["time"], it["source"])
        # 校验配对
        t = it["summary_zh"] or ""
        for a, b in (("「", "」"), ("『", "』")):
            assert t.count(a) == t.count(b), "引号仍不配对: %s %s" % (a, t.count(a))

    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    # 同步覆盖表（JSON 层 + 代码层），避免下一轮调度被模型译文覆盖回缺陷版本
    for name in ("summaries_override.json",):
        path = os.path.join(DATA, name)
        cur = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                cur = json.load(f)
        if KEY in cur and OLD_FRAG in cur[KEY]:
            cur[KEY] = cur[KEY].replace(OLD_FRAG, NEW_FRAG)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cur, f, ensure_ascii=False, indent=2)
            print("updated", name)

    print("fixed:", fixed)


if __name__ == "__main__":
    main()
