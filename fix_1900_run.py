# -*- coding: utf-8 -*-
"""19:00 例行巡检：人工定稿 5 条 NLLB 机翻硬伤。

条目 1（本轮 18:45 新增，Marktechpost）：
  'Not If, But How: Responding to Security Incidents...'
  缺陷：标题「如果不是，但如何」语义崩坏；摘要「烟花人工智能」= Fireworks AI，
  「4 支支柱的游戏手册」为 playbook 误译。

条目 2（11-19 17:51，Unite.AI）：
  'Imagen Raises Over $100M...'  「放射能」应为「放射科医生」，Imagen 被译成「图像公司」。

条目 3（11-19 17:28，The Decoder）：
  'OCR models now digitize...'  标题「将 100 万页的数字化页面为低于 130 美元」语法崩坏。

条目 4（11-12 23:55，Unite.AI）：
  'Databricks Makes Genie App for Slack Generally Available'  Databricks→「数据」，一般可用→GA。

条目 5（11-18 23:58，Simon Willison）：
  'Quoting Daniel Stenberg'  curl→「卷轴」，Rust→「蚀」，语义全崩。

NLLB 同引擎重译会重复同类错误，故人工定稿写入两层 JSON 覆盖表，
regen_overrides.py 固化到代码层，并直接回填 news.json 使 API/报告立即生效。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

SEC = "Not If, But How: Responding to Security Incidents in the Age of AI Attackers"
IMAGEN = "Imagen Raises Over $100M in Growth Capital for Radiologists and AI"
OCR = "OCR models now digitize a million pages for under $130 as costs drop fivefold in 18 months"
DATABRICKS = "Databricks Makes Genie App for Slack Generally Available"
STENBERG = "Quoting Daniel Stenberg"

TITLE_FIX = {
    SEC: "不是是否发生，而是如何应对：AI 攻击者时代的安全事件响应",
    IMAGEN: "Imagen 筹集逾 1 亿美元增长资本，用于放射科医生与 AI",
    OCR: "随着成本 18 个月内下降五倍，OCR 模型数字化百万页的成本已低于 130 美元",
    DATABRICKS: "Databricks 宣布 Slack 版 Genie 应用正式可用（GA）",
    STENBERG: "引用 Daniel Stenberg 的话",
}

SUMMARY_FIX = {
    SEC: (
        "攻击者如今手握强大的 AI。AI 智能体能够以机器速度扫描、规划并实施入侵，"
        "而且每个月都在进步。结果是攻击变得更多、更频繁，并延伸至全球规模。"
        "在这样的环境下，越来越多的公司迟早都会遭遇安全事件，真正拉开差距的是它们如何响应。"
        "面对机器速度的威胁，需要一套现代化的行动手册，包含四大支柱：自动检测与遏制；"
        "快速且安全地进行沟通；彻底根除；持续缩小影响范围（blast radius）。"
        "本文通过 6 个月的事件数据展示了这一趋势，随后审视了若干公司，"
        "其中以 Fireworks AI 作为成熟、结构完善的响应典范。核心要点（TL;DR）——"
        "趋势：AI 驱动的攻击者正在全球范围内发动越来越频繁的攻击。"
        "证据：2026 年 5 月至 11 月间，多家 AI 平台披露了安全事件。"
        "第一支柱：自动检测与遏制。"
    ),
    IMAGEN: (
        "Imagen Technologies 于 2026 年 11 月 18 日宣布，公司在 2026 年内已筹集超过 1 亿美元的"
        "增长资本，并获得了最多 1.5 亿份额外影像研究数据的使用权，用于训练 AI 模型。"
        "这笔资金将用于放射科医生的招聘与留任，同时投资于面向其医生的临床资源、"
        "运营基础设施和技术。资金来自新老投资者。"
    ),
    OCR: (
        "借助免费可用的 AI 模型，从扫描的书籍和记录中提取文本的成本已经大幅下降。"
    ),
    DATABRICKS: (
        "Databricks 于 2026 年 11 月 12 日宣布其 Slack 版 Genie 应用正式可用（GA），"
        "使员工无需离开 Slack，即可提出具备权限感知的数据问题、分析文件、创建图表、"
        "安排分析并在所连接的工具中审批操作。用户可以直接给 Genie 发送消息，"
        "或在频道或群聊中 @提及 Genie。回复会留在相关的对话或线程中，引用来源，"
        "并允许用户在 Databricks 中打开该问答以获取更多上下文。"
    ),
    STENBERG: (
        "在这些智能体把 18.5 万行 C 代码转换为 34 万行 Rust 代码的这段时间里（我数过），"
        "我们向真正的 curl 项目合并了 300 多个提交。在这三周多的时间里，我们实际上改进了 curl——"
        "提交了 200 多个错误修复，而且这些修复是那些 Rust 重写版本一个都没有的。"
        "我们还修复了几个漏洞。在接下来的一个月里，我们又完成了 200 个提交，也许还多修了几个漏洞。"
        "这些克隆项目能跟上吗？"
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
        print("[fix_1900_run] %s覆盖表写入 %d 条，共 %d 条" % (label, n, len(d)))

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
    print("[fix_1900_run] 回填 news.json 条目 %d" % fixed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
