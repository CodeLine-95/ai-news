# -*- coding: utf-8 -*-
"""2026-11-02 20:00 例行巡检（第二批）：修复 20:11 轮次新增条目。

背景
----
巡检期间（20:11）调度器抓到了新条目，本地服务重启后立即跑了一轮，
因此本轮实际新增 2 条（20:00 整点 1 条 + 20:11 重启后 1 条）。

问题条目
--------
'When You Should—and Shouldn't—Use AI to Search the Web'（Wired, 20:00）

缺陷：
  标题「当你应该和不应该使用人工智能搜索网络时」——「AI」被展开成
  「人工智能」（站内一律保留 AI 品牌原形），且 em dash 的「和…和」
  结构丢失了「该做与不该做」的对照语气。
  摘要「但有时你会通过输入查询到一个好的老搜索引擎来获得更好的结果」——
  "typing your query into a good old search engine" 里 query 是「查询词」，
  模型把动词 into 译成了「到」，导致搜索引擎被当成宾语，
  整句读作「输入查询到一个搜索引擎」，语义完全跑偏。

根因修复（translate.py）
------------------------
TERM_FIXES 新增两条：
  1. ("通过输入查询到", "在搜索框中输入查询词后使用", ["typing your query into"])
  2. ("输入查询到", "输入查询词后使用", ["typing your query into"])
  修复 "typing X into Y" 的宾语关系断裂。

本脚本：对该条做人工定稿（保证线上稳定），并写入覆盖表，
避免下一轮调度重跑时又被引擎译文覆盖回去。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

EN = "When You Should—and Shouldn’t—Use AI to Search the Web"
ZH_TITLE = "何时该用、何时不该用 AI 搜索网页"
ZH_SUMMARY = (
    "聊天机器人在从网上检索你想要的信息这件事上往往相当擅长。"
    "但有时候，把查询词敲进一个老牌搜索引擎里，反而能得到更好的结果。"
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
        if it.get("title") == EN:
            it["title_zh"] = ZH_TITLE
            it["summary_zh"] = ZH_SUMMARY
            it["translated"] = True
            it["method"] = "nllb+manual"
            n += 1

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    put_override(T_JSON, EN, ZH_TITLE)
    put_override(S_JSON, EN, ZH_SUMMARY)
    print("[fix_2000d] 已写入覆盖表:", EN[:50])
    print("[fix_2000d] 已回写 %d 条" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
