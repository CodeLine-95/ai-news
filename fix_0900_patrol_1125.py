"""09 点巡检：人工定稿 08:12 新增的 Sonnenfeld 评论英伟达条目。

沿用既往巡检做法：英文原标题为键写入 data/titles_override.json 与
data/summaries_override.json，同时回填 data/news.json，再重生摘要报告。
服务重启时 apply_manual_overrides_on_startup() 会再次确保定稿生效。
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
STAMP = "0900patrol1125"

FIXES = {
    "Yale’s Sonnenfeld: Nvidia is a ‘detriment’ to U.S. industrial might — not a champion": (
        "耶鲁学者索恩菲尔德：英伟达有损美国工业实力，而非产业冠军",
        "耶鲁大学杰弗里·索恩菲尔德警告称，市场周一欢呼的黄仁勋在白宫支持下回归英伟达、出任 CEO 兼董事，可能最终被证明是一个重大错误：日益增多的诉讼可能让董事们承担「历史性」个人责任；同时也引发疑问——美国是否在庆祝一家曾帮助把先进芯片交到对手手中的公司。",
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
