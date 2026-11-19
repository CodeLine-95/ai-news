# -*- coding: utf-8 -*-
"""2026-11-20 04:00 巡检：整点调度新增 10 条，NLLB 机翻硬伤人工定稿 8 条。

问题类型：英文标题残留未译（pgEdge / vCluster）、inference 误译为「结论」、
racks 误译为「架子」、contextuality 误译为「背景」、frontier lab 误译为
「边境实验室」、contextualized 误译为「文本化」、两党误译为「双党家」。

按历史惯例固化三层：data/news.json 回填 + titles/summaries_override.json
（持久卷 JSON 层）+ scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = [
    {
        "match": "Emerson to Link AspenTech Inmation with Databricks",
        "title_zh": "埃默森将 AspenTech Inmation 与 Databricks 连接，赋能工业 AI",
        "summary_zh": (
            "埃默森于 2026 年 11 月 19 日宣布与 Databricks 合作，将情境化的工业运营数据引入 "
            "Databricks Data + AI 平台，使工业企业能够利用工厂信息进行分析、AI 应用与智能体。"
            "原生访问 AspenTech Inmation OT Data Fabric 是实现这一点的关键机制。"
        ),
    },
    {
        "match": "pgEdge Adds Jev to Triage PostgreSQL Alerts",
        "title_zh": "pgEdge 在 AI DBA 工作台中引入 Jev 以分流 PostgreSQL 告警",
        "summary_zh": (
            "pgEdge 在其工作台测试版中加入 TypeSafe AI 模型 Jev，用于分拣 PostgreSQL 告警。"
            "厂商数据显示其在速度与成本上有提升，但准确性尚未得到验证。"
        ),
    },
    {
        "match": "vCluster Adds Self-Service Private Clouds",
        "title_zh": "vCluster 为专用 AI 硬件推出自助式私有云",
        "summary_zh": (
            "vCluster Platform v5.0 让 AI 云客户可自助访问专用服务器，以及经服务商批准的 "
            "Kubernetes、Slurm 和推理环境。"
        ),
    },
    {
        "match": "AI inference servers shrink to fit the air-cooled racks",
        "title_zh": "AI 推理服务器缩小体积，适配企业现有风冷机架",
        "summary_zh": (
            "对希望在自有硬件上运行 AI 的企业而言，高能效推理芯片正成为入门门槛。"
            "随着 AI 从模型构建转向日常运行，昂贵的 GPU 机架及其所需的液冷让许多企业仍选择租用算力。"
        ),
    },
    {
        "match": "Google Quantum AI Demonstrates Contextuality Across 105 Qubits",
        "title_zh": "Google Quantum AI 在 105 个量子比特上演示情境性",
        "summary_zh": (
            "Google Quantum AI 于 2026 年 11 月 19 日宣布，登上《科学》杂志封面的研究在其超导处理器上"
            "实现了规模化的测量情境性验证，其中一项协调游戏的胜率达 98.3%，超过 88.9% 的经典极限。"
            "情境性意味着测量结果并非预设值，而取决于同时进行哪些其他相容测量。"
        ),
    },
    {
        "match": "Whitesides, Moran and Beyer Lead New Bipartisan House AI Caucus",
        "title_zh": "怀特赛德斯、莫兰与比耶尔领导新一届众议院两党 AI 小组",
        "summary_zh": (
            "莫兰办公室宣布，众议员乔治·怀特赛德斯、纳塔尼尔·莫兰与唐·比耶尔于 2026 年 11 月 19 日"
            "发起成立两党众议院人工智能安全与创新小组，另有 23 名创始成员加入。该小组将制定并支持"
            "旨在应对严重 AI 风险的立法，同时支持美国在 AI 领域的持续领先地位。莫兰为得克萨斯州共和党人，"
            "与加利福尼亚州民主党人怀特赛德斯、弗吉尼亚州民主党人比耶尔共同担任联合主席。"
        ),
    },
    {
        "match": "D-Matrix bets stacked DRAM can solve inference",
        "title_zh": "D-Matrix 押注堆叠式 DRAM 解决推理的内存带宽难题",
        "summary_zh": (
            "随着 AI 工作负载转向推理，内存带宽决定了硬件是快速生成 token 还是闲置等待。"
            "D-Matrix 公司为此推出第二代芯片 Raptor，将 3D DRAM 堆叠在计算逻辑之下。"
        ),
    },
    {
        "match": "Anthropic’s IPO could deliver $156 billion to charity",
        "title_zh": "Anthropic 上市或为慈善事业带来 1560 亿美元",
        "summary_zh": (
            "按 95 美元的股价计算，这家前沿实验室的公益基金会、员工捐赠及公司配捐合计可达 1560 亿美元。"
        ),
    },
]


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}
    changed = 0
    for fx in FIXES:
        hit = next((i for i in items if fx["match"].lower() in (i.get("title") or "").lower()), None)
        if not hit:
            print("MISS:", fx["match"])
            continue
        en = hit["title"]
        hit["title_zh"] = fx["title_zh"]
        hit["summary_zh"] = fx["summary_zh"]
        hit["translated"] = True
        hit["method"] = "nllb+manual"
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
        changed += 1
        print("fixed:", hit.get("date"), hit.get("time"), en[:70])
    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print("changed:", changed, "/", len(FIXES))


if __name__ == "__main__":
    main()
