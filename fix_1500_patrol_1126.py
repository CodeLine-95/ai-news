# -*- coding: utf-8 -*-
"""15:00 例行巡检：定稿 15:00 轮次新增 2 条的 NLLB 机翻腔。

- 14:17 Unite.AI《DeepL Launches Aure V2 with End-to-End Speech Translation》：
  "DeepL" 被音译成「深度 L」，"speech translation" 被译成「演讲翻译」，
  定稿还原品牌并改用行业术语「语音翻译」。
- 14:45 InfoQ AI《Recap of Microsoft Ignite 2026: Copilot as the Work OS
  and Agent Governance》："Recap" 被译成「重复」，"Ignite" 被译成「启动」，
  "Work OS" 未译且句子成分错乱，定稿按技术会议语境重译。

按项目既有模式回填 news.json + JSON 覆盖表，再由
scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "DeepL Launches Aure V2 with End-to-End Speech Translation": (
        "DeepL 推出 Aure V2，实现端到端语音翻译",
        "2026 年 11 月 26 日，DeepL 在东京举办的首届 Unmute 峰会上推出 Aure v2，相比初代 Aure，其中位翻译延迟降低 50%。该模型已在 DeepL Voice 在线会议版、DeepL Voice 面对面交谈版以及语音版 DeepL API 中全面上线。不同于将音频依次经过转录、文本翻译和语音生成三个独立环节的传统流程，Aure v2 采用单一架构直接实现语音到语音的翻译。",
    ),
    "Recap of Microsoft Ignite 2026: Copilot as the Work OS and Agent Governance": (
        "Microsoft Ignite 2026 回顾：Copilot 成为「工作操作系统」，强化智能体治理",
        "在 Ignite 2026 大会上，微软将 Copilot 定位为「工作操作系统」（Work OS），并在 Azure、Foundry、Entra 和 Defender 全链条扩展智能体身份、治理与成本控制能力。亮点包括 Cobalt 200 虚拟机、Azure HorizonDB、Foundry 中的持续改进闭环、Microsoft IQ、独立的 Azure AI Gateway 以及 Windows Server 2028。",
    ),
}


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    for it in items:
        en = it.get("title") or ""
        if en not in FIX:
            continue
        title_zh, summary_zh = FIX[en]
        if it.get("title_zh") != title_zh:
            it["title_zh"] = title_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] title:", en[:60], "->", title_zh)
        if it.get("summary_zh") != summary_zh:
            it["summary_zh"] = summary_zh
            changed += 1
            print("[fix]  summary:", en[:60])
        tov[en] = title_zh
        sov[en] = summary_zh

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 变更 %d 处 | 覆盖表 标题 %d 条 / 摘要 %d 条"
          % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
