# -*- coding: utf-8 -*-
"""验证 15:00 巡检新增的根因修复规则是否真实生效（只译这 1 条，不写库）。"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import translate  # noqa: E402

TITLE = "OpenAI Introduces Pando: A Git Backend That Cuts Median Push Latency ~80%"

with open(os.path.join(BASE, "data", "news.json"), encoding="utf-8") as f:
    items = json.load(f)["items"]
target = [i for i in items if i.get("title") == TITLE][0]

print("[原文标题]", TITLE)
print("[原文摘要]", (target.get("summary") or "")[:160], "...\n")

zt, m1 = translate.translate_list([TITLE], beams=2)
zs, m2 = translate.translate_list_chunked([target.get("summary") or ""], beams=3)

print("[引擎]", m1, "/", m2)
print("\n[新标题]\n%s" % zt[0])
print("\n[新摘要]\n%s" % zs[0])

zh = zs[0] + " " + zt[0]
print("\n[缺陷复检]")
checks = {
    "一百字节(petabyte 错译)": "一百字节" in zh,
    "中位 push 残留": "中位 push" in zh,
    "非干部(非主干 错译)": "非干部" in zh,
    "商品硬件 错译": "商品硬件" in zh,
    "推进的推进器 错译": "推进的推进器" in zh,
    "化 10Gbps 残句": "化 10Gbps" in zh,
    "每次 OpenAI 自己的测试": "每次 OpenAI 自己的测试" in zh,
    "最糟糕的是 标签": "最糟糕的是" in zh,
    "TL;DR Scale 英文标签": "Scale：" in zh or "Scale:" in zh,
    "半角句号+大写": bool(__import__("re").search(r"[^\w\s]\.[A-Z]", zh)),
}
bad = 0
for k, v in checks.items():
    flag = "仍存在" if v else "已修复"
    if v:
        bad += 1
    print("   %-28s %s" % (k, flag))
print("\n未修复项:", bad)
