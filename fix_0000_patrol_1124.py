# -*- coding: utf-8 -*-
"""2026-11-24 00:00 例行巡检：定稿本轮新增 6 条 NLLB 机翻硬伤。

沙箱休眠恢复后调度线程补抓 22:58-23:50 共 6 条，均为 nllb 机翻，主要问题：
1) InfoQ Netflix：QConSF2026 重复、"运输"(ship) 应为「交付/发布」、
   GraphRAG 上下文被漏掉；
2) Unite.AI Maxon Plus：品牌名 Maxon Plus 误作「马克森+」、Cinema 4D 误作
   「4D 电影院」、ZBrush 保留；
3) TechCrunch Trump：U.S. Attorney General 误作「美国检察长」（应为司法部长）、
   "辩护黄的回归" 语义残缺；
4) The Decoder Z.ai：loop transformer 误作「循环变压器」（应为循环 Transformer）、
   品牌 Z.ai 音译为「扎伊」、"Generalized Coding" 未译、尾部 "The article Z." 截断；
5) Unite.AI Focus：整体尚可，IP O prospectus 补「招股书」使语义完整；
6) SiliconANGLE Nvidia：effective immediately 误置为「即将生效」，应为「立即生效」。

覆盖三层：news.json 回填 + JSON 覆盖表 + （随后 regen）代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

# 用稳定 id 定位回填，覆盖表 key 使用数据中的真实英文标题
FIX = {
    "f5ee0ddf9988d07f9b5ab1b56130f4bd": (
        "Netflix 亮相 QConSF 2026：为 AI 编码智能体改造 SDLC",
        "在 2026 年旧金山 QCon 大会上，Netflix 商务团队的 Mark Khuzam 介绍了他们如何改造软件开发生命周期（SDLC），让 AI 编码智能体与工程师能够协同交付。团队为人和智能体编写了 45 份架构决策记录，新增了一个只发布「已验证阻塞项」的评审智能体，并通过单个 MCP 工具为每个领域提供 GraphRAG 上下文。",
    ),
    "c0f8bce3a8783a71aa758d4849b3ac3e": (
        "Maxon Plus 将 AI 3D 模型生成带入 Cinema 4D 与 ZBrush",
        "Maxon Plus 在艺术家既有的工作流程中，加入 AI 辅助的 3D 建模、纹理制作与基于浏览器的资产审查能力。",
    ),
    "910818793cbec448fe05314c5be0a431": (
        "特朗普支持黄仁勋回归英伟达，称美方没有其不当行为的证据",
        "特朗普总统援引美国司法部长的意见为黄仁勋的回归辩护，同时敦促英伟达继续推进出口管制调查。",
    ),
    "d61a651e8b31b27efae1bbe9435b0a90": (
        "Z.ai 携全新 750B 旗舰模型跟进 OpenAI，踏入循环 Transformer 领域",
        "Z.ai 正将其旗舰模型 GLM-5.4 迁移到循环架构：28 层网络各运行两次，公司称这使得这一 7500 亿参数模型可媲美 2 万亿至 3 万亿参数规模的模型。目前基准分数仅来自一个较小的 30B 测试模型，Z.ai 将 GLM-5.4 定位为「通用编码（Generalized Coding）」的开端——在这种范式下，代码还能生成视频、游戏与 CAD 模型。",
    ),
    "883505832db2cc25f7b9fd8b60683dcf": (
        "先管好你的 AI 智能体，再担心 AI 末日",
        "企业可能在使用智能体 AI 取得进展的同时，就已对它失去控制。这正是「AI 智能体泛滥」的问题——智能体工具在组织内部不受控制地扩散。围绕 AI 风险的讨论常常滑向极端场景。Anthropic 的 IPO 招股书就给出了一些相当惊人的例子，从抗拒关机、勒索人类用户，到「对人类构成生存性风险」。",
    ),
    "34de9cb47e66f098cda94d9111c8aa0b": (
        "英伟达改变决定，重新任命黄仁勋为 CEO",
        "人工智能芯片巨头英伟达公司今日宣布，在辞职近两周后，黄仁勋已立即恢复首席执行官、总裁兼董事职务。",
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    changed = added_t = added_s = 0
    for it in items:
        iid = it.get("id")
        if iid not in FIX:
            continue
        title_zh, summary_zh = FIX[iid]
        en = (it.get("title") or "").strip()
        it["title_zh"] = title_zh
        it["summary_zh"] = summary_zh
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])
        if titles.get(en) != title_zh:
            titles[en] = title_zh
            added_t += 1
        if summaries.get(en) != summary_zh:
            summaries[en] = summary_zh
            added_s += 1

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_0000_1124] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_0000_1124] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
