# -*- coding: utf-8 -*-
"""03:00 例行巡检：人工定稿今日(2026-11-22)5 条 NLLB 机翻硬伤。

按项目惯例写入三层：manual_overrides.py 代码层 + data/*_override.json 持久卷 + data/news.json 即时回填。
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))

FIXES = [
    {
        "en_title": "Is selling an AI version of your face to this microdrama startup the future of Hollywood?",
        "title_zh": "把你的脸的 AI 版本卖给这家微短剧创业公司，是好莱坞的未来吗？",
        "summary_zh": (
            "一名演员已将自己的面部授权给一家微短剧创业公司——这在中国已是流行趋势。"
            "专家质疑，若这一做法在好莱坞也成为风潮，长期来看会带来怎样的后果。"
        ),
    },
    {
        "en_title": "Silicon Valley's growing obsession with AI doomsday is turning parts of the tech industry toward cult-like devotion",
        "title_zh": "硅谷对 AI 末日的日益痴迷，正让科技行业的部分角落走向邪教式的狂热",
        "summary_zh": (
            "佛蒙特州一座名为 Maple 的佛教寺院希望确立自己作为硅谷精神权威的地位，"
            "同时创造自己的 AI 之神。据《纽约客》报道，领袖 Soryu Forall 的团体记录成员每一次呼吸，"
            "用以按他的形象训练一个 AI。前成员讲述了操纵与精神崩溃的经历。"
        ),
    },
    {
        "en_title": "Nvidia researchers argue huge AI context windows are a dead end",
        "title_zh": "英伟达研究人员认为，超大的 AI 上下文窗口是一条死胡同",
        "summary_zh": (
            "英伟达研究人员认为，语言模型往往并不需要完整的上下文窗口——它速度慢、成本高且容易出错——"
            "并提出一种替代方案。在测试中，定期摘要与针对性关键词搜索通常能以极低的成本达到与全上下文相当的效果。"
            "团队甚至提出了一类新模型：用简短笔记代替长上下文来工作。"
        ),
    },
    {
        "en_title": "Here are the top AI agents that can live in your text messages",
        "title_zh": "以下是可以「住进」你短信里的顶级 AI 智能体",
        "summary_zh": (
            "我们整理了一份最值得关注的 AI 智能体清单，它们可以运行在你的短信应用中，"
            "从通用助手到专为家庭、旅行和工作设计的智能体不一而足。"
        ),
    },
    {
        "en_title": "Inference now drives two-thirds of AI workloads, changing where chips get deployed",
        "title_zh": "推理现已成为三分之二的 AI 工作负载，正在改变芯片的部署位置",
        "summary_zh": (
            "AI 支出正从大型训练集群转向规模更小、建设更快的站点，模块化数据中心正成为推理工作负载的天然归宿。"
            "如今，电力、散热与内存供应对 token 生成地点的影响，已不亚于原始芯片性能。"
            "以推理为核心的芯片厂商希望抓住这一转变。Positron AI Inc."
        ),
    },
]


def upsert_py(path, dict_name, pairs):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    marker = f"{dict_name} = {{"
    start = src.index(marker) + len(marker)
    m = re.search(r"\n\}\n", src[start:])
    end = start + m.start() + 1
    block = src[start:end]
    for key, value in pairs:
        pat = re.compile(r"(\s*)" + re.escape(repr(key)) + r"\s*:\s*.*?(?=,\n|\n\})", re.S)
        if pat.search(block):
            block = pat.sub(lambda mm: f"{mm.group(1)}{key!r}: {value!r}", block, count=1)
        else:
            block = block.rstrip() + f"\n    {key!r}: {value!r},\n"
    src = src[:start] + block + src[end:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)


def main():
    py_path = os.path.join(BASE, "manual_overrides.py")
    upsert_py(py_path, "TITLE_OVERRIDES", [(f["en_title"], f["title_zh"]) for f in FIXES])
    upsert_py(py_path, "SUMMARY_OVERRIDES", [(f["en_title"], f["summary_zh"]) for f in FIXES])
    print("已写入 manual_overrides.py")

    for fname, field in [("titles_override.json", "title_zh"), ("summaries_override.json", "summary_zh")]:
        p = os.path.join(BASE, "data", fname)
        d = json.load(open(p, encoding="utf-8"))
        for f in FIXES:
            d[f["en_title"]] = f[field]
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print(f"已写入 {fname}")

    p = os.path.join(BASE, "data", "news.json")
    d = json.load(open(p, encoding="utf-8"))
    items = d.get("items", d) if isinstance(d, dict) else d
    by_title = {f["en_title"]: f for f in FIXES}
    hit = 0
    for it in items:
        f = by_title.get((it.get("title") or "").strip())
        if f:
            it["title_zh"] = f["title_zh"]
            it["summary_zh"] = f["summary_zh"]
            it["translated"] = True
            it["method"] = "manual"
            hit += 1
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f"news.json 回填 {hit} 条")


if __name__ == "__main__":
    main()
