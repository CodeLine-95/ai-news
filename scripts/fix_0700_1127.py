# -*- coding: utf-8 -*-
"""07:00 巡检：定稿 7 条 NLLB 机翻硬伤（历史存量条目）。

问题分布：
  1. TechCrunch 英伟达芯片条目标题标点错乱（「。,，詹森！」）；
  2-4. Unite.AI / SiliconANGLE 三条 Sentra 融资新闻把公司名误译为「集团」，
       并把 Capital One / Standard Investments / Munich Re 译成「资本一/标准/慕尼黑重」；
  5. Applied Compute 条目摘要金额重复（「3.25 亿美元的资金 3.5 亿美元的资金」）；
  6. 中期选举条目「受到试验」「早期的线路」等机翻腔；
  7. MIT 文本检测器条目摘要长句机翻腔。

把这些人工定稿合并进 data/ 的 JSON 覆盖表，随后运行
python3.11 scripts/regen_overrides.py 同步到代码层 manual_overrides.py，
再由 server 的启动回填逻辑写回 news.json 并重建报告。

用 news.json 里的英文原标题做键，避免手写弯引号/破折号造成键不匹配。
"""
import json
import os
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

FIXES = [
    {
        "prefix": "Export-banned Nvidia chips",
        "title": "出口受限的英伟达芯片，撑起了中国最强的 AI 模型——詹森，要当心了！",
        "summary": "新研究显示，中国最先进的 AI 模型是在遭禁的英伟达芯片上训练出来的。",
    },
    {
        "prefix": "Sentra raises $150M to control",
        "title": "Sentra 融资 1.5 亿美元，管控 AI 智能体可访问的企业数据范围",
        "summary": (
            "数据安全初创公司 Sentra Inc. 今日宣布完成 1.5 亿美元新融资，用于扩展其平台，"
            "管控 AI 智能体在企业数据存储中能够访问的内容。Sentra 提供数据安全软件，"
            "称其业务在过去一年增长超过 300%。"
        ),
    },
    {
        "prefix": "Sentra Raises $150M Series C",
        "title": "Sentra 完成 1.5 亿美元 C 轮融资，扩展智能体数据安全平台",
        "summary": (
            "Sentra 于 2026 年 11 月 4 日宣布，Capital One Ventures 领投了这家智能体数据安全"
            "公司的 1.5 亿美元战略投资。本轮 C 轮融资将用于扩展 Sentra 的企业数据治理平台"
            "（覆盖员工、应用与 AI 智能体访问的数据），并加强其市场推广。Capital One Ventures "
            "与现有投资方 Bessemer Venture Partners、Zeev Ventures、Standard Investments、"
            "Munich Re Ventures 和 Key1 Capital 一同加入。"
        ),
    },
    {
        "prefix": "Sentra Raises $150M to Secure",
        "title": "Sentra 融资 1.5 亿美元，为 AI 智能体保护企业数据安全",
        "summary": (
            "Sentra 获得由 Capital One Ventures 领投的 1.5 亿美元战略投资，用于扩展其数据安全"
            "平台——随着企业让 AI 智能体接触更多商业信息，这类平台愈发重要。该投资于 11 月 4 日"
            "宣布，Capital One Ventures 与现有投资方 Bessemer Venture Partners、Zeev Ventures、"
            "Standard Investments、Munich Re Ventures 和 Key1 Capital 共同参与。"
            "Capital One 的一名代表将进入 Sentra 董事会。"
        ),
    },
    {
        "prefix": "AI cloud startup Applied Compute",
        "title": "AI 云初创公司 Applied Compute 达成关键营收里程碑后融资 3.5 亿美元",
        "summary": (
            "快速增长的人工智能基础设施提供商 Applied Compute Inc. 完成 3.5 亿美元融资，"
            "估值达 32.5 亿美元。该初创公司周一宣布了这笔交易。知名天使投资人 Elad Gil 领投，"
            "英伟达、Shopify Ventures、HubSpot Ventures 等十余家机构跟投。"
        ),
    },
    {
        "prefix": "Midterm elections will put AI",
        "title": "中期选举将让 AI 与数据中心接受考验，但大型科技公司可能最终仍会胜出",
        "summary": (
            "现在判断中期选举后企业供应商中最终的赢家与输家或许为时过早，但初步判断是："
            "大型科技公司胜出，而芯片制造商、新云服务商等数据中心供应方失利。"
            "又或者，所有人都是输家？"
        ),
    },
    {
        "prefix": "Helping AI text detectors",
        "title": "帮助 AI 文本检测器跟上不断变化的形势",
        "summary": (
            "如果老师怀疑学生的学期论文出自大语言模型（LLM）之手，可以使用 AI 生成文本检测"
            "工具来印证怀疑。但老师不应完全信任检测结果。麻省理工学院与康奈尔大学的研究人员"
            "指出，这类检测工具本身也是 AI 模型，可能被伪装成人写文本的 AI 生成内容欺骗；"
            "随着写作习惯自然变化或新 LLM 出现，检测器也可能无法识别 AI 文本。在新论文中，"
            "研究人员展示了一种特殊训练技术，能让 AI 检测器更准确、更能抵御欺骗，"
            "即使人类与 AI 的写作方式持续变化。"
        ),
    },
]


def merge(path, updates):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    shutil.copyfile(path, path + ".bak.0700patrol1127")
    before = len(data)
    data.update(updates)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("[fix] %s: %d -> %d" % (os.path.basename(path), before, len(data)))


def main():
    with open(NEWS, "r", encoding="utf-8") as f:
        items = json.load(f)["items"]
    titles, summaries = {}, {}
    for fix in FIXES:
        matches = [x for x in items if (x.get("title") or "").startswith(fix["prefix"])]
        if len(matches) != 1:
            raise SystemExit("[fix] 标题匹配异常 %r: %d 条" % (fix["prefix"], len(matches)))
        key = matches[0]["title"]
        titles[key] = fix["title"]
        summaries[key] = fix["summary"]
        print("[fix] 定稿:", fix["prefix"], "->", fix["title"])
    merge(T_JSON, titles)
    merge(S_JSON, summaries)


if __name__ == "__main__":
    main()
