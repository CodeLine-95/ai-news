"""11 点巡检：人工定稿整点抓取新增的 1 条 NLLB 硬伤译文。

沿用既往巡检做法：英文原标题为键写入 data/titles_override.json 与
data/summaries_override.json，同时回填 data/news.json，再重生摘要报告。
"""
import json
import os
import shutil
import sys

import report

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_OVR = os.path.join(BASE, "data", "titles_override.json")
S_OVR = os.path.join(BASE, "data", "summaries_override.json")
STAMP = "1100patrol1125"

FIXES = {
    "Anthropic is trying to kill traditional desktop apps with Claude-generated desktop apps": (
        "Anthropic 想用 Claude 生成的桌面应用取代传统桌面应用",
        "Anthropic PBC 几乎每天都会宣布某项新能力、功能或模型，今天也不例外。此次该公司推出新能力：只需一条提示词，即可用 Claude 创建适用于 Windows 与 Mac 电脑的功能完备的桌面应用程序。",
    ),
}


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main():
    for path in (DATA, T_OVR, S_OVR):
        shutil.copy2(path, path + ".bak." + STAMP)

    data = load(DATA)
    titles = load(T_OVR)
    summaries = load(S_OVR)
    applied = 0
    for it in data["items"]:
        en = (it.get("title") or "").strip()
        fix = FIXES.get(en)
        if not fix:
            continue
        zh_title, zh_summary = fix
        titles[en] = zh_title
        summaries[en] = zh_summary
        it["title_zh"] = zh_title
        it["summary_zh"] = zh_summary
        it["translated"] = True
        it["method"] = "manual"
        applied += 1
        print("定稿: %s -> %s" % (en[:55], zh_title[:45]), flush=True)

    save(DATA, data)
    save(T_OVR, titles)
    save(S_OVR, summaries)
    print("本轮定稿 %d 条，覆盖表 %d/%d 条" % (applied, len(titles), len(summaries)), flush=True)
    if applied != len(FIXES):
        print("警告：并非全部目标条目都命中", file=sys.stderr, flush=True)
    report.main()
    print("报告已重生", flush=True)


if __name__ == "__main__":
    main()
