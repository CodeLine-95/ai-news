# -*- coding: utf-8 -*-
"""20:00 例行巡检：人工定稿 8 条 NLLB 机翻硬伤。

本轮 20:00 启动抓取新增 8 条，均有不同程度机翻缺陷，逐条定稿：

1) 'Presentation: RIIIR: Rewrite It In *Idiomatic* Rust (with AI)'
   Idiomatic(*惯用的*)→「愚蠢」；Symposium(工具链名)→「研讨会」；摘要语义崩坏。
2) 'Gemini 4 Neon Delivers Small Intelligence Gain at Lower Cost Per Task'
   Neon(代号)→「虹彩」；Artificial Analysis(机构)→「人工分析」；Carbon→「碳」。
3) 'Google's latest AI model is faster...'
   fourth model→「第四款车型」；sibling→「同胞」；Gemini 4Neon 缺空格。
4) 'Modular Data Centers Feature in Mitsubishi Heavy–Sakura Internet MOU'
   Mitsubishi Heavy→「三比希重/密苏比希重」；标题语法崩坏。
5) 'IEA Scenario Links AI Growth to Doubling of Data Center Power Use'
   标题 dangling「链接」；terawatt-hours→「兆瓦时」(应为太瓦时)；Stated Policies→「定制」。
6) 'ChronoScale Plans 350 MW AI Data Center Campus with STN in Odessa'
   「只有第 65 兆瓦阶段已订购」语义崩；campus→「校园」；site→「网站」。
7) 'Nscale Activates Its First Vera Rubin NVL72 Racks for Global AI Cloud'
   rack-scale→「架构规模」；training and serving→「培训和服务」。
8) 'Why a Computer Scientist Thinks Superintelligence Won't Happen'
   human extinction→「轻松辩论」尚可，但 gambling with our lives→「与生活进行博」，
   head of alignment science 漏译；末句语义反。

NLLB 同引擎重译会重复同类错误，故人工定稿写入两层 JSON 覆盖表，
regen_overrides.py 固化到代码层，并直接回填 news.json 使 API/报告立即生效。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

RIIIR = "Presentation: RIIIR: Rewrite It In *Idiomatic* Rust (with AI)"
NEON_GAIN = "Gemini 4 Neon Delivers Small Intelligence Gain at Lower Cost Per Task"
GOOGLE_LATEST = "Google's latest AI model is faster, cheaper and smarter than its flagship predecessor from just weeks ago"
MITSUBISHI = "Modular Data Centers Feature in Mitsubishi Heavy–Sakura Internet MOU"
IEA = "IEA Scenario Links AI Growth to Doubling of Data Center Power Use"
CHRONO = "ChronoScale Plans 350 MW AI Data Center Campus with STN in Odessa"
NSCALE = "Nscale Activates Its First Vera Rubin NVL72 Racks for Global AI Cloud"
SUPERINT = "Why a Computer Scientist Thinks Superintelligence Won’t Happen"

TITLE_FIX = {
    RIIIR: "演讲：RIIIR——用 AI 以地道的 Rust 重写（Idiomatic Rust）",
    NEON_GAIN: "Gemini 4 Neon 以更低的单任务成本带来小幅智能提升",
    GOOGLE_LATEST: "Google 最新 AI 模型比数周前的旗舰前代更快、更便宜、更智能",
    MITSUBISHI: "三菱重工—Sakura Internet 谅解备忘录聚焦模块化数据中心",
    IEA: "国际能源署情景：AI 增长与数据中心用电量翻倍相关联",
    CHRONO: "ChronoScale 与 STN 计划在得州奥德萨建设 350 兆瓦 AI 数据中心园区",
    NSCALE: "Nscale 为其全球 AI 云启用首批 Vera Rubin NVL72 机架",
    SUPERINT: "为何一位计算机科学家认为超级智能不会发生",
}

SUMMARY_FIX = {
    RIIIR: (
        "Nicholas Matsakis 分享了为何 AI 使 Rust 成为现代生产系统的理想选择——"
        "借助编译器护栏（guardrails）跨越陡峭的采用门槛。"
        "他介绍了 Symposium（Rust 基金会开源的、面向智能体的工具链），"
        "并演示了智能体客户端协议（ACP）如何在多样的企业开发工作流中，"
        "标准化智能体与工具之间的可扩展性。"
    ),
    NEON_GAIN: (
        "Artificial Analysis 于 2026 年 11 月 18 日报告，Google 的 Gemini 4 Neon（xhigh）"
        "在其智能指数上得分 61，比 Gemini 4 Carbon（high）高 1 分。"
        "在标准、未折扣定价下，Neon 每项智能指数任务成本为 6.44 美元、平均约 21 分钟；"
        "Carbon 则为 7.76 美元、约 36 分钟。该评估将 Neon 总体排在第三位，"
        "仅次于 GPT-6.2 Astra（max）与 Claude Fable 5.2（max）。"
    ),
    GOOGLE_LATEST: (
        "Google DeepMind 发布了 Gemini 4 Neon，这是其七周内的第四款模型，"
        "速度几乎是同门 Carbon 的两倍，在大多数基准上胜过后者，且价格明显更低。"
    ),
    MITSUBISHI: (
        "三菱重工（Mitsubishi Heavy Industries）与 Sakura Internet 于 2026 年 11 月 18 日宣布，"
        "双方已签署谅解备忘录，将开发位于日本的主权 AI 与云基础设施，"
        "包括为加快建设而设计的模块化 AI 数据中心。"
        "拟议中的联盟将三菱重工的工业系统专长与 Sakura Internet 的本土云运营能力结合。"
        "该谅解备忘录涵盖在数字服务与数据中心建设领域探索战略联盟。"
    ),
    IEA: (
        "国际能源署（IEA）于 2026 年 11 月 19 日发布《世界能源展望 2026》。"
        "在报告的「既定政策情景」（Stated Policies Scenario）中，AI 相关投资"
        "有助于到 2030 年将全球数据中心用电量翻一番，达到 1,000 太瓦时（TWh）。"
        "这一发现把 AI 的电力足迹置于更广泛的系统规划问题之中。"
        "报告的情景显示，随着 AI 与数字服务扩张，到 2035 年数据中心容量将接近当前规模的三倍。"
    ),
    CHRONO: (
        "ChronoScale 于 2026 年 11 月 18 日宣布，已与 STN 签署最终协议，"
        "将在得克萨斯州奥德萨分三期开发一座 AI 数据中心园区，总容量 350 兆瓦，"
        "并配套高达 7.5 亿美元的融资方案。目前仅首期 65 兆瓦已下单。"
        "STN 是该园区的初始开发商，该场址拟用于承载一家未具名的领先前沿 AI 实验室的大规模部署。"
    ),
    NSCALE: (
        "Nscale 于 2026 年 11 月 18 日宣布，其首批 NVIDIA Vera Rubin NVL72 机架级 AI 系统已上线，"
        "标志着全球推广的开始，预计将在未来数月持续推进。"
        "戴尔 PowerEdge XE9812 系统为客户训练和部署大型模型增加了算力，"
        "包括需要多步骤推理的工作负载。"
    ),
    SUPERINT: (
        "今年夏天，当全球一家领先 AI 公司的员工开始随意讨论「自家产品是否会导致人类灭绝」时，"
        "许多人措手不及。事情始于 Anthropic 研究员 Jacob Coxon 宣布辞职，"
        "他警告称自己的雇主与 OpenAI 正「直奔自我改进的超级智能，拿我们的生命赌博」。"
        "Anthropic 对齐科学负责人 Evan Hubinger 回应：「Jacob 说得对——我们确实真诚地相信 AI 可能杀死全人类！」"
        "随后 Anthropic CEO Dario Amodei 告诉 CNN：「我同意 Jacob 的程度，远大于我不同意他的程度。」"
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
        print("[fix_2000_run] %s覆盖表写入 %d 条，共 %d 条" % (label, n, len(d)))

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
    print("[fix_2000_run] 回填 news.json 条目 %d" % fixed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
