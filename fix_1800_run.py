# -*- coding: utf-8 -*-
"""18:00 例行巡检：人工定稿两条 NLLB 机翻硬伤。

条目 1（本轮 16:00 新增，Unite.AI）：
  'Wilgot Raises $3 Million Seed Round...'
  缺陷：「种子轮回」应为「种子轮」；「威尔哥」应为品牌名 Wilgot；
  摘要「理解和推」「工业基金会」「不断调整」断句崩坏。

条目 2（今日 07:59，Simon Willison）：
  'llm-gemini 0.38'
  缺陷：型号代号 Hydrogen/Argon/Carbon/Neon 被误译为「气/碳/尼昂」，
  「1/4 的价格」被译成「4/4」，语义反转；标题被拆成「Gemini 0.38 ll」。

NLLB 同引擎重译会重复同类错误，故人工定稿写入两层 JSON 覆盖表，
regen_overrides.py 固化到代码层，并直接回填 news.json 使 API/报告立即生效。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

WILGOT = "Wilgot Raises $3 Million Seed Round to Improve Product Visibility in AI Shopping"
GEMINI = "llm-gemini 0.38"

TITLE_FIX = {
    WILGOT: "Wilgot 融资 300 万美元种子轮，提升产品在 AI 购物中的可见性",
    GEMINI: "llm-gemini 0.38 发布：Google 推出 Gemini 4 Neon 及定价解析",
}

SUMMARY_FIX = {
    WILGOT: (
        "Wilgot 已完成 300 万美元种子轮融资，帮助零售商让自家产品更容易被 "
        "AI 购物助手找到、理解并推荐。这家斯德哥尔摩初创公司正在构建其所谓的"
        "「智能体产品优化」（Agentic Product Optimization，简称 APO）软件："
        "把客户知识转化为更丰富的产品信息，并随着购物行为变化持续调整内容。"
        "本轮由 Industrifonden 领投，Wilgot 称其金额相当于 3000 万瑞典克朗。"
    ),
    GEMINI: (
        "发布：llm-gemini 0.38。今天 Google 推出了 Gemini 4 Neon。我最近写过 "
        "Gemini 4 系列的定价有多令人困惑——Neon 某种程度上让情况更糟。此前 "
        "Gemini 4 阵容是 Hydrogen、Argon 和 Carbon——Argon 与 Carbon 同价，"
        "Hydrogen 目前是它们的 3/4，但等到 12 月 1 日另外两款初始折扣到期、"
        "价格翻倍后，Hydrogen 会降到它们的 1/4。Neon 的发布公告干脆假装 Argon "
        "不存在。以下是他们解释模型阵容的新图：现在的阵容从贵到便宜依次是 "
        "Carbon、Neon、Hydrogen。但 Carbon 目前是半价，所以眼下 Neon（输入每百万 "
        "3 美元、输出每百万 15 美元）反而是三者中最贵的——其次是 Carbon（2/10 "
        "美元），再次是 Hydrogen（1.50/7.50 美元）。我想等 12 月 1 日 Carbon "
        "翻倍到 4/20 美元时，这一切会更合理些。"
    ),
}


def detect_indent(path):
    """沿用文件既有缩进，避免整文件重排产生无谓 diff。"""
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
        print("[fix_1800_run] %s覆盖表写入 %d 条，共 %d 条" % (label, n, len(d)))

    ind = detect_indent(DATA)
    with open(DATA, "r", encoding="utf-8") as f:
        data = json.load(f)
    fixed = 0
    for it in data.get("items", []):
        en = (it.get("title") or "").strip()
        if en in TITLE_FIX and it.get("title_zh") != TITLE_FIX[en]:
            it["title_zh"] = TITLE_FIX[en]
            it["translated"] = True
            it["method"] = "manual"
            fixed += 1
        if en in SUMMARY_FIX and it.get("summary_zh") != SUMMARY_FIX[en]:
            it["summary_zh"] = SUMMARY_FIX[en]
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=ind)
    print("[fix_1800_run] 回填 news.json 条目 %d" % fixed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
