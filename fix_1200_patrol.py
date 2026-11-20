# -*- coding: utf-8 -*-
"""12:00 巡检修复：本轮新增 1 条 + 历史遗留 2 条 NLLB 机翻硬伤，人工定稿。

硬伤：
- Bonta/NVIDIA 条目（本轮新增）："Records"（调查记录/档案）误译为「唱片」，
  "investigative subpoena" 误译为「调查召唤」（应为调查传票），
  "misled investors and the public about the risk" 语义拧巴。
- Ripple-65B 条目："agentic coding" 误译为「机器人编码」（应为「智能体编程」），
  句末重复残句；"完全 Apache 2.0 开放的美国模型" 表述生硬。
- Ricursive AI 条目：标题整段英文未译（title_zh 仍是英文）。

覆盖三层：data/news.json 回填 + JSON 覆盖表 + manual_overrides.py（regen）。
运行后需 curl -X POST /api/refresh 让在线生效并重生成报告。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = {
    "Bonta Demands NVIDIA Records On China Transfers And Disclosures": {
        "title_zh": "邦塔要求 NVIDIA 提交对华芯片转移与信息披露的相关记录",
        "summary_zh": (
            "加利福尼亚州总检察长 Rob Bonta 于 2026 年 11 月 19 日向 NVIDIA 发出调查传票，"
            "要求其提供先进芯片或机密信息是否流入中国、以及该公司是否就相关风险误导投资者与公众等信息。"
            "加州方面将依据答复评估其是否可能违反加州法律。加州司法部正在调查 NVIDIA 与时任首席执行官黄仁勋（Jensen Huang）的行为。"
        ),
    },
    "Ripple-65B Preview delivers strong agentic coding results as a fully Apache 2.0 open US model": {
        "title_zh": "Ripple-65B 预览版展现出强劲的智能体编程能力，是完全采用 Apache 2.0 许可的美国开放模型",
        "summary_zh": (
            "Ricursive Intelligence 正在发布 Ripple-65B 预览版——一款 650 亿参数的开放权重语言模型。"
            "该公司称，该模型在 TerminalBench 2.1 编程基准上取得美国开源模型中的最高分，总研发成本为 3200 万美元。"
            "不过在其他基准上，Ripple 仍落后于同样新发布的西方开放模型 Inkling 2 Small。"
        ),
    },
    "Ricursive AI Releases Ripple-65B Preview: A 65B Dense Open-Weight Model Scoring 80.5 on Terminal-Bench 2.1": {
        "title_zh": "Ricursive AI 发布 Ripple-65B 预览版：一款在 Terminal-Bench 2.1 上得分 80.5 的 650 亿参数稠密开放权重模型",
        "summary_zh": (
            "Ricursive Intelligence 刚刚发布 Ripple-65B 预览版。这是 Ricursive 推出的一款 650 亿参数稠密开放权重模型，"
            "从零开始针对智能体编程进行预训练，是其 AI 芯片设计平台背后专有模型的通用版本。"
            "官方宣称其在 Terminal-Bench 2.1 上得分 80.52，是美国开放权重模型中自报的最高分；"
            "它在该测试中击败的每一个 MoE 竞品，总参数量都在 5010 亿至 9750 亿之间。"
        ),
    },
}


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
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
    print("title overrides:", len(tov), "summary overrides:", len(sov))


if __name__ == "__main__":
    main()
