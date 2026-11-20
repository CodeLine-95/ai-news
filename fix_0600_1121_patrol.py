# -*- coding: utf-8 -*-
"""2026-11-21 06:00 巡检：定稿本轮新增 5 条 NLLB 机翻硬伤 + 3 条历史遗留硬伤。

本轮 06:00 整点抓取 2521 -> 2527（+6），其中 5 条存在明显机翻缺陷：
- Anthropic -> 「人类」/「安特洛皮克」；IPO closed -> 「关闭扩大」；
- models of chaos -> 「模特」；Riemann -> 「里曼」（应为黎曼）；
- record emissions -> 「记录排放」；中英混杂未译（Meta reconsiders）。
另含 3 条 05:00 轮未进覆盖表的历史硬伤：
- Gemini Mac：标题语句不通（「在工作中继续工作时，在背景下」）；
- Trump tax：语义反转（原文是对转移数据中心征重税，译文成了威胁把数据中心迁出去）；
- Körber：摘要末句「美国和德国之间均分开」表述生硬。

覆盖三层：news.json 回填 + JSON 覆盖表 + manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    # ---- 本轮 06:00 新增 5 条 ----
    "5652e6a0a79ec65e344ab58d5d73802e": (
        "AI 数据中心排放创纪录，Meta 重新考虑 2030 年净零目标",
        "Meta 高管正在重新审视公司最初提出的 2030 年实现净零排放的目标。"
        "Meta 最新可持续发展报告披露这一变化时，公司报告的温室气体排放量增幅创下纪录，"
        "超过了任何一家竞相新建 AI 数据中心的科技巨头。"
        "据 Meta 数据中心副总裁 Rachel Peterson 与净零及可持续发展全球负责人 Blair Swedeen"
        "在报告序言中所称，公司 2026 年可持续发展报告表示「我们的长期目标没有改变，但运营环境已经改变」。",
    ),
    "de143fdc6f9691c6bb49bf8a39f3a378": (
        "Anthropic 完成规模扩大后的 935 亿美元 IPO 与 260 亿美元私募配售",
        "Anthropic 于 2026 年 11 月 20 日宣布，完成 11.27 亿股 A 类股首次公开募股，"
        "发行价每股 83 美元，其中包括承销商全额行使增购 1.47 亿股的期权。"
        "在扣除承销折扣、佣金及其他发行费用前，该 IPO 募集总金额约 935 亿美元。",
    ),
    "2d1867977bbcb1f45df5fc1f1c7b803b": (
        "MIT 框架将混沌系统的 AI 模型约束在物理边界内",
        "麻省理工学院研究人员开发出一种机器学习框架，可保证混沌系统 AI 模型的轨迹有界，"
        "解决长时间模拟中模型可能漂移至物理上不可能数值的问题。"
        "MIT 于 2026 年 11 月 20 日宣布了这项成果。"
        "研究生 Sunbochen Tang 与教授 Navid Azizan、Themistoklis Sapsis 的研究"
        "涉及天气、气候、湍流及其他非线性过程的模型。",
    ),
    "6d1392db34e733fa05aef870c2e0aaa4": (
        "Anthropic 研究人员声称用 Claude 证明了黎曼猜想",
        "Anthropic PBC 一名研究人员声称借助 Claude 证明了黎曼猜想——这被广泛认为是数学中最重要的未解难题。"
        "Levent Alpöge 今日在其个人网站上宣布了这一发现。Anthropic 尚未就此发布官方公告。",
    ),
    "6b6a52faaa4c9ee55864b84ca6db4d57": (
        "据路透社报道，美国证监会执法人员正审查 NVIDIA 会计问题",
        "据路透社 2026 年 11 月 20 日报道，两名知情人士透露，美国证券交易委员会执法人员"
        "正在审查 NVIDIA 可能存在的会计问题。据 LSEG 数据，消息传出后 NVIDIA 股价下跌约 13%，"
        "此前已下跌逾 6%。《华尔街日报》于 2026 年 11 月 17 日报道了这项调查的存在，"
        "但称无法确定调查重点。",
    ),
    # ---- 历史遗留 3 条硬伤 ----
    "c36079881022286cba4323bcea52b323": (
        "Google 的 Gemini 现已可在 Mac 上运行应用，并在后台完成桌面任务，用户可继续工作",
        "Google 正把「计算机使用」能力带到 Mac 版 Gemini，让 AI 在一个隔离的后台窗口中"
        "操作桌面应用、本地文件和网站，并提供实时预览，用户可同时继续自己的工作。",
    ),
    "b44ab066f64c7bf4520fbd30393b9555": (
        "特朗普威胁对将 AI 数据中心迁至美国境外的公司征收「巨额税收」",
        "唐纳德·特朗普总统承诺，将对在美国境外建设数据中心的公司征收「巨额税收」，"
        "与此同时，全美各州和城市正限制新建数据中心的申请。"
        "特朗普在与中国国家主席习近平和俄罗斯总统普京会晤后于周五的新闻发布会上表示："
        "「我们不会允许我们的公司在境外建设数据中心。他们任由芯片和其他一切发生这种事，"
        "这对我们的国家极具破坏性。这正是我们开始落后的地方。」",
    ),
    "88cd462fac560b447719435a31f69e8c": (
        "Körber 调查发现：随着商业决策愈发艰难，AI 的应用正在上升",
        "企业正让 AI 在决策中发挥更大作用，但这并不意味着领导者觉得决策更容易了。"
        "在 Körber 发布的一项调查中，76% 的高级决策者表示决策变得更复杂，"
        "同样比例的人表示允许 AI 发挥更大作用。"
        "这些答案描述的是同时发生的两个趋势，并不能证明其中之一是另一者的原因。"
        "该调查覆盖 2000 名高管，美国与德国各占一半。",
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    changed = 0
    for it in items:
        iid = it.get("id")
        if iid not in FIX:
            continue
        title_zh, summary_zh = FIX[iid]
        en = (it.get("title") or "").strip()
        it["title_zh"] = title_zh
        it["summary_zh"] = summary_zh
        it["translated"] = True
        it["method"] = "nllb+manual"
        titles[en] = title_zh
        summaries[en] = summary_zh
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_0600_1121_patrol] news.json 回填 %d 条" % changed)
    print("[fix_0600_1121_patrol] 覆盖表 %d 标题 / %d 摘要" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
