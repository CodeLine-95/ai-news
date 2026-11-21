# -*- coding: utf-8 -*-
"""2026-11-20 23:00 巡检：定稿本轮新增 8 条 NLLB 机翻硬伤。

本轮 23:00（服务 22:59 沙箱恢复后首轮）抓取新增 8 条（2471→2479）：
1) TechCrunch《The fallout from Nvidia's Jensen Huang scandal continues》——
   「NvidiaJensen Huang」中英粘连、标题生硬；摘要「被推卸」错译 ouster。
2) The Decoder《Nvidia bets at least $500 million ...》——
   「纳维迪亚」错译 Nvidia、「传播流程」错译 diffusion、「token 代码」生硬。
3) Marktechpost《NVIDIA AI Releases Nemotron-Labs-Sigma ...》——
   「连续传播语言模型」错译 diffusion、「代码文本」错译 denoises、
   「几步蒸」截断、「NVIDIAs6」「DPM 步骤」等硬伤。
4) Unite.AI《Why Sovereign AI Is Worth Building ...》——
   标题「破碎的原因」生硬；摘要「COOBrad」粘连、「过度接触」错译 overreach。
5) The Verge《The week everything fell apart》——
   标题「都崩了」偏口语；摘要「停电」错译 outage、「ICloud」大小写错误。
6) TechCrunch《Six AI-powered gadgets ...》——
   摘要「注册记者」错译 notetakers。
7) Unite.AI《Miro vs. Notion ...》——
   标题品牌「视角与概念」完全误译；摘要「一堵墙满意的想法」语义崩坏。
8) Unite.AI《AI in 2027: Memory Will Become ...》——
   摘要「失去了世界线索」「内存才是有用的」语义崩坏。

覆盖三层：news.json 回填 + JSON 覆盖表 + manual_overrides.py（regen）。
运行后需 curl -X POST /api/refresh 让在线生效并重生成报告。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

T1 = "The fallout from Nvidia’s Jensen Huang scandal continues"
T2 = "Nvidia bets at least $500 million on Inception's diffusion models to strengthen its open-source Nemotron lineup"
T3 = "NVIDIA AI Releases Nemotron-Labs-Sigma, a Continuous Diffusion Language Model with 14 checkpoints at 3B/8B"
T4 = "Why Sovereign AI Is Worth Building, and Where It Breaks"
T5 = "The week everything fell apart"
T6 = "Six AI-powered gadgets that could make your home office smarter"
T7 = "Miro vs. Notion: Which Is Better for Team Collaboration?"
T8 = "AI in 2027: Memory Will Become the Next Test of Machine Intelligence"

TITLE_FIX = {
    T1: "英伟达黄仁勋丑闻的余波仍在持续",
    T2: "英伟达向 Inception 的扩散模型押注至少 5 亿美元，强化其开源 Nemotron 产品线",
    T3: "NVIDIA AI 发布 Nemotron-Labs-Sigma：连续扩散语言模型，提供 3B/8B 共 14 个检查点",
    T4: "主权 AI 为何值得建设，以及它会在哪里失效",
    T5: "一切分崩离析的一周",
    T6: "六款可让家庭办公室更智能的 AI 设备",
    T7: "Miro 与 Notion：哪个更适合团队协作？",
    T8: "2027 年 AI：记忆将成为机器智能的下一场考验",
}

SUMMARY_FIX = {
    T1: (
        "在应对首席执行官黄仁勋被解职一事的余波之际，英伟达本周发布了最新财报，"
        "业绩保持稳健增长，并承诺好日子将继续下去。"
    ),
    T2: (
        "据 The Information 报道，英伟达接近以至少 5 亿美元收购 AI 初创公司 Inception。"
        "该公司成立仅两年，基于扩散过程构建语言模型——这是有别于 ChatGPT 等模型逐词生成方式的另一条技术路线。"
        "该交易将增强英伟达自身的开源模型，并助推其机器人业务布局。"
    ),
    T4: (
        "2025 年 5 月 13 日，曼哈顿一名联邦法官在《纽约时报》与 OpenAI 的版权纠纷中签署了一项证据开示命令，"
        "要求 OpenAI「保存并隔离所有本会被删除的输出日志数据」。这意味着用户已要求删除的聊天记录也在保留范围内，"
        "涵盖 ChatGPT 免费版、Plus、Pro 和团队账户，以及未签署零数据保留协议的 API 客户。"
        "OpenAI 对此提出抗辩，其首席运营官 Brad Lightcap 称该命令「越权」。"
    ),
    T5: (
        "Outlook 发生了持续数天的服务中断。美国 25 年来第二次实施全国范围的航班停飞。"
        "银行似乎突然无法运转。就连 iCloud 也无法保持在线。本周，科技世界仿佛彻底崩塌，"
        "而且感觉这可能只是更大事件的开端。在本期 The Vergecast 节目中，Nilay 和 David 回顾了本周的诸多事故，"
        "试图解释每一起事件的来龙去脉——实际通常远比阴谋论所渲染的要温和——"
        "以及为什么这些小问题叠加起来仍值得担忧。"
    ),
    T6: (
        "从语音记录工具到网络摄像头，这里有六款可以升级你工作空间的 AI 设备。"
    ),
    T7: (
        "一个团队可能带着满墙的想法离开一场研讨会，却仍然没有留下任何可用的决策记录。"
        "Miro 与 Notion 在协作流程的不同阶段发挥作用。Miro 是我们进行可视化思考和促进协作的首选；"
        "Notion 则是我们推荐的、用于在会后让决策、文档和进行中的计划持续发挥作用的工具。"
        "两者都收录在我们评选的最佳 AI 协作工具指南中。"
    ),
    T8: (
        "一位助理记得玛雅负责这个项目，随后玛雅把它交给了别人。第二天，助理却自信地又给她安排了一项任务。"
        "它记住了一个事实，却跟丢了事态的变化。这个小失误折射出机器智能面临的更大问题："
        "只有当系统能够判断哪些信息仍然适用、哪些值得检索、哪些应当修改或遗忘时，记忆才真正有用。"
    ),
}

# 长摘要用定点替换，保留 TL;DR 事实结构
SUMMARY_PATCH = {
    T3: [
        ("连续传播语言模型", "连续扩散语言模型"),
        ("在 16D 嵌入空间中代码文本", "在 16 维嵌入空间中对文本去噪"),
        ("这使得几步蒸和 Trajectory 引导", "这使得少步蒸馏和轨迹引导"),
        ("NVIDIAs6 任务套件", "NVIDIA 六项任务套件"),
        ("平均值为 71.16 次", "平均得分为 71.16 分"),
        ("256 个 DPM 步骤", "256 步 DDPM"),
        ("最好：91.96 次", "最佳成绩为 91.96 分"),
        ("最差：17.00 次", "最差成绩为 17.00 分"),
    ],
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        touched = False
        if en in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[en]
            touched = True
        if en in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[en]
            touched = True
        if en in SUMMARY_PATCH:
            s = it.get("summary_zh") or ""
            for old, new in SUMMARY_PATCH[en]:
                s = s.replace(old, new)
            it["summary_zh"] = s
            touched = True
        if touched:
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), en[:55])
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    added_t = added_s = 0
    for k, v in TITLE_FIX.items():
        if titles.get(k) != v:
            titles[k] = v
            added_t += 1
    for k, v in SUMMARY_FIX.items():
        if summaries.get(k) != v:
            summaries[k] = v
            added_s += 1
    for en, patches in SUMMARY_PATCH.items():
        s = summaries.get(en)
        if s:
            for old, new in patches:
                s = s.replace(old, new)
            summaries[en] = s
            added_s += 1
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_2300] news.json 回填 %d 条；标题定稿 %d 条 / 摘要定稿 %d 条" %
          (changed, added_t, added_s))
    print("[fix_2300] 覆盖表 %d 条 / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
