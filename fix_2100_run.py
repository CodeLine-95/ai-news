# -*- coding: utf-8 -*-
"""21:00 例行巡检：人工定稿 8 条 NLLB 机翻硬伤。

本轮 21:00 整点调度新增 8 条（2312→2320），均有不同程度机翻缺陷：

1) 'Canva adds an AI 'off' button'
   off button→「开按」（应为「关闭」开关）；摘要「交换机关」等生硬。
2) 'DarioHealth Expands AI Care Distribution Through WebMD Health Services'
   「6500 万人的生命」(65 million lives)；multi-condition→「多条件」；
   标题语序崩坏。
3) 'From Intent to Autonomous Action: Governing AI Agents in the Enterprise'
   recommending→「推行动」；operational authority→「运营权威」。
4) 'MegaRobo Raises Nearly $200M to Expand AI for Science Globally'
   Oman→「奥曼」；Sultanate of Oman→「苏尔坦王国」(应为苏丹国)；
   CMB International→「CMB 国际」(应为招银国际)；AI for Science→「AI 为了科学」。
5) 'Isomorphic Labs and MSD Partner on AI Oncology Drug Discovery'
   oncology→「瘤学」(应为肿瘤)；small-molecule→「小型分子」；
   work against a target→「与目标作斗争」。
6) 'Sovereignty is the AI story everyone mentions and few have planned for ahead of 2027'
   profitably→「如何利地」(漏「盈」)；froth→「泡」(应为泡沫)；
   standing up AI factories→「站起来的人工智能工厂」。
7) 'Enterprises fear AI success more than failure, because success means lock-in they can't escape'
   lock-in→漏译（「无法逃脱」缺宾语「锁定」）。
8) 'Visualizing Information Entropy in Language Models'
   information entropy→「信息入侵」(应为信息熵)；cross-entropy loss→「交叉化损失」。

NLLB 同引擎重译会重复同类错误，故人工定稿写入两层 JSON 覆盖表，
regen_overrides.py 固化到代码层，并直接回填 news.json 使 API/报告立即生效。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

CANVA = "Canva adds an AI \u2018off\u2019 button"
DARIO = "DarioHealth Expands AI Care Distribution Through WebMD Health Services"
AGENTS = "From Intent to Autonomous Action: Governing AI Agents in the Enterprise"
MEGAROBO = "MegaRobo Raises Nearly $200M to Expand AI for Science Globally"
ISOMORPHIC = "Isomorphic Labs and MSD Partner on AI Oncology Drug Discovery"
SOVEREIGNTY = "Sovereignty is the AI story everyone mentions and few have planned for ahead of 2027"
LOCKIN = "Enterprises fear AI success more than failure, because success means lock-in they can\u2019t escape"
ENTROPY = "Visualizing Information Entropy in Language Models"

TITLE_FIX = {
    CANVA: "Canva 新增 AI\u300c关闭\u300d开关",
    DARIO: "DarioHealth 通过 WebMD Health Services 扩大 AI 护理服务分发",
    AGENTS: "从意图到自主行动：企业中的 AI 智能体治理",
    MEGAROBO: "MegaRobo 融资近 2 亿美元，在全球扩展 AI for Science 业务",
    ISOMORPHIC: "Isomorphic Labs 与 MSD 合作开展 AI 肿瘤药物研发",
    SOVEREIGNTY: "主权是人人都在谈、却少有人为 2027 年之前做好规划的 AI 议题",
    LOCKIN: "企业更怕 AI 成功而非失败，因为成功意味着陷入无法摆脱的锁定",
    ENTROPY: "可视化语言模型中的信息熵",
}

SUMMARY_FIX = {
    CANVA: (
        "Canva 现已允许用户关闭其生成式 AI 功能。通过这一变化，用户可以禁用该平面设计平台的"
        "一系列 AI 工具，例如 AI 照片扩展功能 Magic Expand，也可以关闭用 Canva 聊天机器人"
        "生成图像的能力。不过这个开关并不会关闭 Canva 上所有由 AI 驱动的功能——背景移除工具"
        "和 Magic Grab（可选中图片中的对象并移动到别处）仍然可用。Canva 表示：\u300c当生成式 AI "
        "开关关闭时，这两项功能仍可用，因为它们只处理设计中已有的内容。\u300d"
    ),
    DARIO: (
        "DarioHealth 于 2026 年 11 月 19 日宣布与 WebMD Health Services 达成合作，将其 AI 驱动的"
        "多病症护理平台分发至后者覆盖 3500 多家雇主、健康计划、医疗系统和公共部门机构的健康"
        "服务网络。WebMD Health Services 称其网络覆盖 6500 万人。这一数字代表的是潜在分发范围，"
        "而非已承诺加入 DarioHealth 项目的人数。"
    ),
    AGENTS: (
        "像\u300c恢复服务\u300d这样的指令看似简单，但当 AI 智能体必须决定授权什么时就不那么简单了。"
        "重启应用、修改配置、调配基础设施都可能服务于这一目标，但各自的后果截然不同。"
        "随着智能体从推荐行动转向执行行动，组织需要在业务意图与运营权限之间建立明确的关联。"
    ),
    MEGAROBO: (
        "MegaRobo Technologies 于 2026 年 11 月 19 日宣布，已筹集近 2 亿美元新融资，用于在国际上"
        "扩展其 AI for Science（AI 驱动科学）业务，并建设连接 AI 与实验室仪器、机器人及其他物理"
        "系统的基础设施。阿曼主权财富基金 Oman Investment Authority（阿曼投资局）参与本轮，"
        "招银国际（CMB International）作为新投资者加入。"
    ),
    ISOMORPHIC: (
        "Isomorphic Labs 于 2026 年 11 月 19 日宣布与 MSD 达成战略研究合作，共同发现小分子肿瘤"
        "药物候选物，将其 AI 药物设计引擎与该药企精选的专有数据集及研发专长相结合。MSD 是 "
        "Merck & Co., Inc.（默克）在美国和加拿大以外使用的商号。双方将针对一个他们称为具有"
        "重要战略意义的肿瘤靶点展开研究。"
    ),
    SOVEREIGNTY: (
        "随着企业越过\u300c建起 AI 工厂\u300d的阶段、开始思考如何盈利运营，AI 基础设施经济学正进入"
        "一个更清醒的阶段。如今，能否持久、是否有真实需求、是否具备长期价值，成为区分能长期"
        "存在的供应商与泡沫的标准。"
    ),
    LOCKIN: (
        "超算领域凭借科学模拟建立了声誉，而如今占据同一批数据中心的 AI 基础设施提出了一个更"
        "棘手的问题：当模型把数据转化为收入时，对数据及其所产生智能的控制权，就成为很少有"
        "公司公开讨论的董事会级议题。"
    ),
    ENTROPY: (
        "在本文中，你将了解信息熵与交叉熵损失如何把经典信息论同大语言模型\u300c预测下一个词\u300d的"
        "训练方式联系起来。"
    ),
}


def detect_indent(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for ln in lines[1:]:
        stripped = ln.lstrip(" ")
        if stripped and stripped.strip() != "}":
            return len(ln) - len(stripped)
    return 2


def main():
    for path, fixes, label in (
        (T_JSON, TITLE_FIX, "标题"),
        (S_JSON, SUMMARY_FIX, "摘要"),
    ):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        ind = detect_indent(path)
        n = 0
        for k, v in fixes.items():
            if d.get(k) != v:
                d[k] = v
                n += 1
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=ind)
        print("[fix_2100_run] %s覆盖表写入 %d 条，共 %d 条" % (label, n, len(d)))

    ind = detect_indent(DATA)
    with open(DATA, "r", encoding="utf-8") as f:
        data = json.load(f)
    fixed = 0
    for it in data.get("items", []):
        en = (it.get("title") or "").strip()
        if en in TITLE_FIX and it.get("title_zh") != TITLE_FIX[en]:
            it["title_zh"] = TITLE_FIX[en]
            it["translated"] = True
            it["method"] = "nllb+manual"
            fixed += 1
        if en in SUMMARY_FIX and it.get("summary_zh") != SUMMARY_FIX[en]:
            it["summary_zh"] = SUMMARY_FIX[en]
            it["method"] = "nllb+manual"
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=ind)
    print("[fix_2100_run] 回填 news.json 条目 %d" % fixed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
