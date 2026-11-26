# -*- coding: utf-8 -*-
"""08:00 巡检：定稿本轮新增 2 条译文（NLLB 漏译专名/语义偏差）。

把人工定稿合并进 data/ 的 JSON 覆盖表；随后运行
python3.11 scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLES = {
    "Quoting Scott Aaronson":
        "引用斯科特·亚伦森（Scott Aaronson）的观点",
    "S&P Global Ratings Puts NVIDIA’s AA Ratings on CreditWatch":
        "标普全球评级将英伟达（NVIDIA）AA 评级列入信用观察名单",
}

SUMMARIES = {
    "Quoting Scott Aaronson":
        "现在显而易见，我们迎来的将不是针对这个或那个复杂性问题的一次性解答，"
        "而是一片全新的数学真理大陆——此前我们只能透过迷雾隐约窥见它。"
        "想象一下列文虎克首次把显微镜对准池水，或伽利略首次把望远镜对准星空。"
        "这或许能让你体会到，我们如今对复杂性理论宇宙、乃至其之外整个数学真理宇宙的"
        "分辨能力有了怎样的提升。",
    "S&P Global Ratings Puts NVIDIA’s AA Ratings on CreditWatch":
        "标普全球评级（S&P Global Ratings）于 2026 年 11 月 25 日将英伟达（NVIDIA）的 "
        "AA 发行人信用评级与 AA 高级无担保债务评级列入信用观察名单（CreditWatch），"
        "理由是对董事会独立性、高管监督与继任规划的担忧。该机构表示，若进一步尽职调查"
        "发现治理缺陷依然存在，可能在 90 天内下调英伟达评级。评级本身获得确认，"
        "信用观察名单意味着评级面临潜在下调的复查。",
}


def merge(path, updates):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    shutil.copyfile(path, path + ".bak.0800patrol1126")
    before = len(data)
    data.update(updates)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("[fix] %s: %d -> %d" % (os.path.basename(path), before, len(data)))


if __name__ == "__main__":
    merge(T_JSON, TITLES)
    merge(S_JSON, SUMMARIES)
