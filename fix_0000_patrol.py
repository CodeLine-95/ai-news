# -*- coding: utf-8 -*-
"""00 点巡检：本轮 8 条 NLLB 机翻硬伤人工定稿。

- 英文标题 -> 中文标题 写入 titles_override.json
- 英文标题 -> 中文摘要 写入 summaries_override.json
- 按 id 精确回填 data/news.json 的 title_zh / summary_zh，method 标记 manual
- 重生成 Markdown 摘要报告

纯确定性处理，不加载翻译模型，避免与后台调度争内存。
"""
import json
import os
import report

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
N_JSON = os.path.join(BASE, "data", "news.json")

# (id, 英文原标题, 定稿中文标题, 定稿中文摘要)
FIXES = [
    ("68c0133a64535dc324a5023931398693",
     "Yes, the EU AI Act Covers Agentic AI—Here’s How",
     "是的，欧盟《AI 法案》涵盖智能体 AI——具体如此",
     "当下有一种很强的论调，认为智能体 AI 和 AI 智能体落入某种监管空白——欧盟《AI 法案》无力对此加以治理。我们在挪威知名媒体（Morgenbladet 和 Dagensnæringsliv）上读到这种说法，奥斯陆大学的顶尖学者也反复提及。我们认为这些论断存在两个根本缺陷……而且它们基于恐惧，而非事实。首先，智能体 AI 受欧盟《AI 法案》监管。"),
    ("17b4240c4cd31e3309bac01afdccdcc9",
     "Meet Shepherd, the Meta-Agent Keeping Rogue AI In Check",
     "认识 Shepherd：约束失控 AI 的元智能体",
     "AI 智能体正在互联网上失控肆虐，它们被赋予完成特定任务的指令，却常常以不受欢迎或意想不到的方式行事。这些失控事件从删光整个收件箱，到入侵网站，甚至发起网络攻击，不一而足。就像人类员工需要管理者一样，东北大学助理教授 Weiyan Shi 认为 AI 智能体也需要监督。她说：『它们可能长时间运行。然而，运行时间越长，就越可能出错，并可能采取一些危险、不安全的行动。我们认为应该有一个中间层。』这个中间层以元智能体的形式出现，负责监督行为、提供质量控制，并在适当的时候将问题上报给人类。"),
    ("6dbad1140452d6c75064b058b62821bc",
     "Anthropic’s IPO puts AI’s circular financing boom to the test",
     "Anthropic 上市，检验 AI 循环融资热潮",
     "随着公司上市，Anthropic 面临巨额算力承诺，但其最大的基础设施合作伙伴（包括 Amazon 和 Google）即便在 Anthropic 失去领先地位后，也可能继续从 AI 中获利。"),
    ("b7a38d4ee1358e7d8f1099e706136ce8",
     "Abridge Details Controls for AI-Generated Physical-Exam Notes",
     "Abridge 详解 AI 生成体检记录的管控功能",
     "Abridge 于 2026 年 11 月 19 日发布临床指南，说明临床医生如何结合检查模板、风格设置、常用偏好和提示词编辑，将就诊对话转化为结构化的体检记录。儿科医生兼 Abridge 临床成功总监 Casey Hribar 撰文，围绕一名捂着头部一侧的两岁患儿的就诊经历展开。"),
    ("0a3a49e408c2b8b0a4111e6fb8338833",
     "LangChain Launches LangSmith Tool Gateway to Govern Agent Tool Calls",
     "LangChain 推出 LangSmith Tool Gateway，治理智能体工具调用",
     "LangChain 于 2026 年 11 月 19 日推出公开测试版 LangSmith Tool Gateway，为企业提供一种托管方式，控制 AI 智能体可以调用哪些工具、使用谁的凭证，以及如何记录每项操作。Tool Gateway 通过 LangSmith 智能体平台上的共享控制层，将智能体请求路由到 MCP 工具服务器。它集中管理原本需要为每个智能体单独构建的身份验证、访问规则和调用记录。"),
    ("f944fd980cbd40de87978ac722ec5cd1",
     "Oliver Wyman to Acquire Synpulse for AI and Technology Consulting",
     "Oliver Wyman 收购 Synpulse，强化 AI 与技术咨询业务",
     "Marsh 旗下企业 Oliver Wyman 于 2026 年 11 月 19 日宣布，已同意收购 Synpulse——一家为金融机构提供服务的全球技术咨询与 AI 平台公司。该交易将增加约 1200 名员工，预计于 2027 年初完成，尚需监管批准并满足惯常交割条件。此次合并将把 Oliver Wyman 的战略咨询业务与 Synpulse 的技术咨询及实施能力结合起来。"),
    ("3ba874076974ccdd443daffd0484b5eb",
     "AI’s next build-out: Inference racks that resize themselves for every new model",
     "AI 下一轮建设：可为每个新模型自动调整规格的推理机架",
     "内存池化正迅速成为 AI 推理经济学中最锋利的工具之一，各家公司竞相从每块图形处理单元（GPU）中榨取更多产出。目前大多数 AI 服务器仍采用固定的 GPU 与内存配比，且这一配比在机器整个生命周期内保持不变。"),
    ("38c66bd23a6ee65546c53d950226544c",
     "ChatGPT can transcribe as you speak now with Live Dictation",
     "ChatGPT 上线实时听写，可边说边转写",
     "现在，ChatGPT 可通过实时听写（Live Dictation）功能更快地接收来自麦克风的音频提示，边说边转写，而无需等到录音结束。该功能现已在网页、桌面应用以及 iOS 和 Android 应用上向所有 ChatGPT 套餐全球推出。在 ChatGPT 中使用听写时，你可以点按音频波形查看 AI 正在生成的实时文字转录，完成后再在提示框中编辑。ChatGPT 的听写功能正变得更快、更可靠。借助实时听写，你的语音会在说话过程中转化为文字，从而减少等待转写完成的时间。"),
]


def main():
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(N_JSON, encoding="utf-8"))
    by_id = {it["id"]: it for it in news["items"]}

    ok = 0
    for iid, en, zh_t, zh_s in FIXES:
        titles[en] = zh_t
        summaries[en] = zh_s
        it = by_id.get(iid)
        if not it:
            print("[WARN] id 未找到:", iid)
            continue
        it["title_zh"] = zh_t
        it["summary_zh"] = zh_s
        it["method"] = "manual"
        it["translated"] = True
        ok += 1
        print("[FIX]", iid[:8], "->", zh_t)

    json.dump(titles, open(T_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(summaries, open(S_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(news, open(N_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[OK] 定稿 %d 条；覆盖表 标题=%d 摘要=%d；news.json=%d 条"
          % (ok, len(titles), len(summaries), len(news["items"])))

    report.main()
    print("[OK] 报告已重生成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
