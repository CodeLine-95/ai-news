"""10 点巡检：人工定稿 09:30 / 09:41 入库的两条 NLLB 硬伤译文。

沿用既往巡检做法：英文原标题为键写入 data/titles_override.json 与
data/summaries_override.json，同时回填 data/news.json，再重生摘要报告。
服务后续 cycle 与重启时会自动应用覆盖表，定稿不会被模型译文覆盖。
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
STAMP = "1000patrol1125"

FIXES = {
    "Epochal launches with $100M to help developers train predictive AI models": (
        "Epochal 携 1 亿美元资金成立，助力开发者训练预测式 AI 模型",
        "AI 工具初创公司 Epochal AI Inc. 今日正式成立，并获得 1 亿美元资金。资金由首席执行官张果栋（Guodong Zhang）提供；他是一名机器学习研究员，此前曾联合创立 xAI。今年早些时候，他与另外两位 xAI 联合创始人 Zihang Dai、Manuel Kroiss 共同创办了 Epochal。",
    ),
    "Staff at Anthropic and Open AI sound alarm on advanced models too powerful to release": (
        "Anthropic 与 OpenAI 员工警告：先进模型过于强大，不宜发布",
        "据 Axios 今日援引二十多位知情人士报道，Anthropic 与 OpenAI 的前沿 AI 员工正就部分先进模型与高管产生分歧：这些模型的推理能力已强到被认为会对人类构成危险，公司内部因此陷入僵持。",
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
