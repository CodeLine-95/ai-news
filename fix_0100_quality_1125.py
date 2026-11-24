# -*- coding: utf-8 -*-
"""2026-11-25 01:00 巡检质量修复：历史低质量译文定点回填。

修复对象为质量门禁提示的存量条目：TSMC 投资金额误作「50000 亿美元」、
Anthropic 误作「人类」、产品名 Daybreak/Yonkers/PR 被意译、半角标点贴中文、
以及两条摘要截断。均按英文原文人工定稿并写入三层覆盖表。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "Taiwan’s chipmaking giant TSMC to invest $1B in Anthropic, OpenAI",
        "title_zh": "中国台湾芯片制造巨头台积电将向 Anthropic 与 OpenAI 投资 10 亿美元",
        "summary_zh": (
            "顶级芯片制造商台积电（TSMC）准备向 Anthropic 与 OpenAI 投资 10 亿美元。"
            "这将让这家中国台湾芯片制造商直接持有头部 AI 开发商的股权，"
            "尽管其自身代工业务已从 AI 数据中心建设中获利丰厚。据路透社报道，"
            "台积电董事会批准的方案包括向面向大型投资者预留的 OpenAI 优先股投资 5 亿美元，"
            "以及按预期 IPO 价格购买 Anthropic 普通股的另一笔 5 亿美元投资。"
            "《华尔街日报》报道称，此类投资可能向市场传递信心，因为 AI 交易已显现紧张迹象。"
            "不过分析师同时警告，投资者、供应商与客户之间的循环融资，"
            "会使评估 AI 硬件与服务的真实市场需求变得困难。"
        ),
    },
    {
        "title": "Welcome to elite impunity, Jensen Huang",
        "title_zh": "欢迎来到精英免责的世界，黄仁勋",
        "summary_zh": (
            "「大而不能倒」续集。图片：The Verge；Getty Images。我想我得向黄仁勋致以热烈祝贺。"
            "黄仁勋再次出任英伟达 CEO，这让除特朗普总统与万斯（J.D. Vance）副总统"
            "（正是他们促成了此事）之外的所有人几乎都感到意外。现在，我们这些对"
            "「自由市场」有些基本认知的人，或许会觉得美国总统对一家美国大公司施压令人反感。"
            "但我们的亿万富翁科技大佬们对「自由市场」的在意程度，"
            "与他们对「言论自由」的在意程度一样——也就是说，根本不在乎。"
        ),
    },
    {
        "title": "States sue SpaceX to stop Grok from generating child sex images, revenge porn",
        "title_zh": "多州起诉 SpaceX，要求阻止 Grok 生成儿童性图像与报复性色情内容",
        "summary_zh": (
            "周一，弗吉尼亚州和俄勒冈州成为首批起诉 SpaceX 的州，指控 Grok 持续未经遏止地"
            "将主要为妇女和儿童的真实照片性化。SpaceX 于 2 月收购 xAI，如今必须应对"
            "Grok「spicy mode」争议性上线带来的持续清算——马斯克曾大力宣传这一模型功能，"
            "但很快发现它生成了大量非自愿亲密影像（NCII）与儿童性虐待影像（CSAM）。"
            "最初的防护措施极为松懈，Grok 有时甚至会在用户未提出要求的情况下生成裸体图像。"
            "尽管 X Safety 与 xAI（现更名为 SpaceX AI）起初保持沉默，"
            "马斯克旗下公司最终道歉，并声称已实施额外防护措施、重新设计政策以屏蔽有害输出。"
        ),
    },
    {
        "title": "Binding of Isaac developer removes AI music from Repentance Plus",
        "title_zh": "《以撒的结合》开发者从《Repentance Plus》中移除 AI 音乐",
        "summary_zh": (
            "《以撒的结合：Repentance Plus》过去几天在 Steam 上遭到差评轰炸，"
            "起因是玩家发现游戏中某个段落使用了 AI 音乐。Reddit 用户 ShweetsStuff 发现了"
            "《侠盗猎车手》（GTA）主题段落中使用的歌曲——多个音频文件带有 Suno 元数据，"
            "指向 Suno 网站上的曲目。游戏创作者埃德蒙·麦克米伦（Edmund McMillen）随后在 X 上道歉，"
            "称自己「完全不知道」游戏中的 GTA 恶搞桥段用了生成式 AI 音乐。"
            "更富戏剧性的是，Valve 要求开发者披露在开发过程中使用生成式 AI 的方式与时机，"
            "发行商 Nicalis 公司也因此面临追问。"
        ),
    },
    {
        "title": "Explore the Codex Security Plugin",
        "title_zh": "探索 Codex 安全插件",
        "summary_zh": (
            "观看 Codex 安全插件的演示，了解从入门到查看录制结果的完整工作流程。"
        ),
    },
    {
        "title": "See PR scans in action",
        "title_zh": "PR 扫描实战演示",
        "summary_zh": (
            "观看 PR 扫描教程，了解演示者如何在拉取请求工作流中审阅扫描结果。"
        ),
    },
    {
        "title": "Get started with Daybreak Blue",
        "title_zh": "开始使用 Daybreak Blue",
        "summary_zh": (
            "观看 Daybreak Blue 的上手教程，详细了解配置体验与入门步骤。"
        ),
    },
    {
        "title": "Deploying Daybreak Red",
        "title_zh": "部署 Daybreak Red",
        "summary_zh": (
            "了解借助 Daybreak Red 开展受监督安全调查的参考架构，"
            "包括安全控制、部署配置与监控。"
        ),
    },
    {
        "title": "The Silent Consensus",
        "title_zh": "沉默的共识",
        "summary_zh": (
            "OpenAI 战略未来负责人迪恩·鲍尔（Dean Ball）探讨能力更强的 AI 将如何重塑社会，"
            "以及人们如何保留对自身机构的掌控。"
        ),
    },
    {
        "title": "Research Reports",
        "title_zh": "研究报告",
        "summary_zh": "点击对应图像即可访问相应研究报告。",
    },
    {
        "title": "Yonkers Rises",
        "title_zh": "Yonkers 崛起",
        "summary_zh": (
            "工具：Yonkers Rises。我意识到自己并不知道 Yonkers 在哪里，于是先在 Google 地图上查找，"
            "接着为了在脑中记住它的位置与形状（同时试用 Claude Fable 5.2 的 3D 建模与动画能力），"
            "用 Fable 5 生成了这座城市的三维可视化模型。"
        ),
    },
    {
        "title": "Google Unveils TPU 8i Max and TPU 8tx: A Dual-Chip TPU and a Confidential TPU",
        "title_zh": "Google 发布 TPU 8i Max 与 TPU 8tx：双芯片 TPU 与机密 TPU",
        "summary_zh": (
            "Google 在第八代 TPU 产品线中新增两套系统：TPU 8i Max 面向超大上下文窗口与机架密度，"
            "TPU 8tx 面向安全的机密推理。8i Max 是由两颗 TPU 8i 芯片构成的双芯片封装，"
            "二者均与 4 月发布的 TPU 8t 和 TPU 8i 一同供货。规格速览：8i Max 为单封装 2 颗 8i 芯片；"
            "8tx 为 TPU 8t 芯片加第五代 AMD EPYC 主机，均运行于 Google Cloud TPU 系统。"
            "性能上，8i Max 的算力、SRAM 与 HBM 带宽均为 TPU 8i 的两倍，"
            "8tx 相比 TPU 8t 最多可将延迟降低一半。优势在于在现有机架占用内提供双倍芯片；"
            "不足是两套系统均未公布绝对规格、基准测试、价格或可用区域。"
            "这两款是新的系统配置，而非新芯片。"
        ),
    },
]


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    by_title = {fx["title"].strip(): fx for fx in FIXES}
    changed = 0
    for it in items:
        fx = by_title.get((it.get("title") or "").strip())
        if fx:
            it["title_zh"] = fx["title_zh"]
            it["summary_zh"] = fx["summary_zh"]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), it.get("title", "")[:55])

    for fx in FIXES:
        titles[fx["title"]] = fx["title_zh"]
        summaries[fx["title"]] = fx["summary_zh"]

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("回填条目:", changed)
    assert changed == len(FIXES), "定稿条目数不符：%d != %d" % (changed, len(FIXES))


if __name__ == "__main__":
    main()
