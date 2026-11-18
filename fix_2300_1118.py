# -*- coding: utf-8 -*-
"""23:00 巡检修复：本轮新增条目中有 9 条 NLLB 机翻缺陷，人工定稿。

覆盖三层：
1) data/news.json 内条目直接回填（立即生效）
2) data/titles_override.json / data/summaries_override.json（持久卷 JSON 层）
3) 再运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = {
    "Vero Security Raises $11M Seed to Expand AI Security Platform": {
        "title_zh": "Vero Security 完成 1100 万美元种子轮融资，扩展 AI 安全平台",
        "summary_zh": "Vero Security 于 2026 年 11 月 18 日宣布完成由 TLV Partners 领投的 1100 万美元种子轮融资，同时推出 AISecurityEngineering.org——一个面向「保护企业 AI 工具与智能体」这一新兴领域的开放社区。GTM Capital、Maple Capital 及多位天使投资人也参与本轮。",
    },
    "Supermicro Ships Petascale All-Flash Servers With PCIe Gen 6": {
        "title_zh": "Supermicro 出货搭载 PCIe Gen 6 的 PB 级全闪存服务器",
        "summary_zh": "Supermicro 于 2026 年 11 月 18 日宣布，其基于第六代 AMD EPYC 9006 处理器的全新全闪存存储家族首批系统已开始出货，主打机型是一款 Petascale 服务器，采用 PCIe Gen 6 连接，在 2U 机箱中提供高达 3.93 PB 的闪存容量。Supermicro 称，新服务器的顺序读取带宽较 PCIe Gen 5 最高提升 100%，这是其首批采用 PCIe Gen 6 的存储产品，面向高性能计算、AI 训练与推理。该 Petascale 服务器采用 AMD 的 SP7 平台，随着 AMD 推出 SP8 版本 CPU，后续还计划推出更多存储产品。",
    },
    "NVIDIA Expands RTX Spark to Compact Desktops for Always-On Local AI": {
        "title_zh": "NVIDIA 将 RTX Spark 扩展至紧凑型台式机，支持常驻本地 AI",
        "summary_zh": "NVIDIA 于 2026 年 11 月 18 日宣布，来自华硕（ASUS）、戴尔（Dell）和微星（MSI）的 RTX Spark 紧凑型台式机现已开售，为专用 Windows PC 带来本地 AI 智能体、图像与视频生成及模型微调能力，统一内存最高达 128GB。NVIDIA 点名华硕 ProArt GR1X 与微星 EdgeMesa N AI+ 系列属于这批新台式机，它们与此前已开售的 RTX Spark 笔记本形成互补。",
    },
    "Hugging Face now routes model requests through OpenRouter for the best price or speed": {
        "title_zh": "Hugging Face 现通过 OpenRouter 路由模型请求，以获得最优价格或速度",
        "summary_zh": "Hugging Face 现已通过 OpenRouter 路由语言模型请求，后者会自动选择最便宜或最快的供应商。「自带 API 密钥」（bring-your-own API keys）的语言模型调用方式正在退出。据 OpenRouter 称，新路由机制将容量错误减少了 46%。两家公司均面临数十亿美元的收购。",
    },
    "Sequel.io Raises $15M Series B to Expand AI Agents and Personalization": {
        "title_zh": "Sequel.io 完成 1500 万美元 B 轮融资，扩展 AI 智能体与个性化能力",
        "summary_zh": "Sequel.io 于 2026 年 11 月 18 日宣布完成超额认购的 1500 万美元 B 轮融资，由 Sorenson Capital 领投，累计融资额达 2600 万美元。公司将在 AI 智能体、底层数据基础设施、网站个性化及其视频驱动营销平台的集成方面加大投入。High Alpha、Album VC 与 Webflow Ventures 作为新投资人加入，Javelin Venture Partners、Struck Capital、Alumni Ventures 与 Social Leverage 继续跟投。",
    },
    "Mistral plays catch-up with Vibe Desktop as rivals already command full operating systems": {
        "title_zh": "竞争对手已掌控完整操作系统，Mistral 借 Vibe Desktop 奋起直追",
        "summary_zh": "Mistral 的 AI 智能体 Vibe 现拥有了自己的桌面应用。竞争对手已掌控完整的操作系统，Mistral 正借 Vibe Desktop 奋起追赶。",
    },
    "Disney Introduces Autonomous Star Wars Audio-Animatronics With AWS": {
        "title_zh": "迪士尼携手 AWS 推出自主式《星球大战》电子与动画人偶",
        "summary_zh": "迪士尼体验公司于 2026 年 11 月 18 日宣布，华特迪士尼幻想工程研发部门与 AWS 打造了一个由三个角色组成的《星球大战》电子与动画人偶（Audio-Animatronics）原型，可实时选择对白与动作。这三个安泽兰人（Anzellan）角色——Vilo Vele、Kado Bre'a 与 Jibu Bre'a——无需木偶师操控或固定表演循环即可运行。这些角色来自《星球大战》宇宙中的一个外星种族。",
    },
    "Downgrading From Claude Fable Barely Affected Dev Productivity During Ban": {
        "title_zh": "禁令期间从 Claude Fable 降级，对开发生产力影响甚微",
        "summary_zh": "要准确评估新 AI 模型是否较前代有所改进非常困难——甚至难以界定「生产力提升」究竟意味着什么，因为新版本可能在一个领域表现更好，却在另一个领域性能下降，这与传统软件和框架的情况如出一辙。有时这是人为主动选择的取舍，有时则是「附带损害」。而这还假设各方是在「公平竞技」。",
    },
    "AI\u2019s hidden energy tax: More than 80% of scale-up traffic is just memory moving around": {
        "title_zh": "AI 隐藏的能源税：超 80% 的扩容流量只是内存在搬移",
        "summary_zh": "随着推理任务超过训练，内存瓶颈正成为 AI 基础设施中代价最高的问题之一。GPU 空闲等待数据，而高带宽内存（HBM）却被固定绑定在无法共享的处理器上。光子学正成为一条潜在出路。迈威尔科技（Marvell Technology Inc.）",
    },
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en in FIXES:
            fx = FIXES[en]
            it["title_zh"] = fx["title_zh"]
            it["summary_zh"] = fx["summary_zh"]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), en[:60])

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}
    for en, fx in FIXES.items():
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("changed:", changed, "/", len(FIXES))


if __name__ == "__main__":
    main()
