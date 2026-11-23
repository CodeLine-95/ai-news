# -*- coding: utf-8 -*-
"""2026-11-23 20:00 例行巡检：定稿本轮新增 4 条 NLLB 机翻硬伤。

本轮 20:00 整点抓取新增 4 条（均来自 Unite.AI），逐条核对原文后人工定稿：
1) Why Generative Try-On Fails on Fit, and What Fixes It (19:51)：
   NLLB 把 try-on 误译为「试试」、fit 误译为「适应」，语义尽失。按原文定稿。
2) 3Shape Links AI Dental Visualizations to Henry Schein One Records (19:34)：
   Records 误译为「唱片」（此处为「病历」），Henry Schein One 公司名被拆分。按原文定稿。
3) Walmart Enables Muse Shopping Through Its Agent Gateway (19:16)：
   Agent Gateway 误译为「智能体门户端」，Agent Profile 语境生硬。按原文定稿。
4) Z.ai’s GLM-5.4 Uses Iterative Depth Without Adding Parameters (19:10)：
   Iterative Depth 误译为「不变深度」（应为「迭代深度」），末尾误加句号。按原文定稿。

覆盖三层：news.json 回填 + JSON 覆盖表（regen 时复用）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_FIX = {
    "Why Generative Try-On Fails on Fit, and What Fixes It":
        "生成式虚拟试穿为何解决不了「合身」，以及如何真正解决",
    "3Shape Links AI Dental Visualizations to Henry Schein One Records":
        "3Shape 将 AI 牙科可视化接入 Henry Schein One 患者病历",
    "Walmart Enables Muse Shopping Through Its Agent Gateway":
        "沃尔玛通过其智能体网关（Agent Gateway）支持 Muse 购物",
    "Z.ai’s GLM-5.4 Uses Iterative Depth Without Adding Parameters":
        "Z.ai 发布 GLM-5.4：不增加参数，用迭代深度提升推理",
}

SUMMARY_FIX = {
    "Why Generative Try-On Fails on Fit, and What Fixes It": (
        "10 月 1 日，OpenAI 在 ChatGPT 的服装搜索结果中加入「试穿」（Try On）按钮：上传自拍、"
        "等待几秒，就能看到自己穿上刚浏览的外套。这是一个流畅的演示，很可能成为数百万人的网购"
        "标配，但它完全忽略了购物者真正会搞错的一件事——该买什么尺码。这个盲点并非下季度路线图"
        "上待补齐的功能，而是内生于生成式图像模型的工作方式：图像里没有判断合身所需的数学信息。"
        "Coresight Research 估计，2025 年美国服装网购退货率达 23.4%，近 70% 的退货源于尺码与合身"
        "问题。真正的解决方案需要三类数据协同：真实身体数据、结构化的服装规格（平铺尺寸、面料弹性"
        "与垂坠感），以及来自「留下还是退回」的成交结果闭环。文章来自服装尺码推荐与虚拟试穿公司 "
        "Garu 联合创始人 Glen Pegado，他指出：虚拟试穿仍有价值，但图像应反映数据推荐的尺码，而非"
        "扩散模型凭空想象的垂坠效果。"
    ),
    "3Shape Links AI Dental Visualizations to Henry Schein One Records": (
        "3Shape 于 2026 年 11 月 23 日宣布，与 Henry Schein One 达成的新集成将其 Unite 软件与 "
        "Dentrix、Ascend by Dentrix 及 Dentally 连接，把牙科扫描、治疗数据和 AI 辅助诊断可视化"
        "带入患者病历。该集成由两家公司共同开发，已在北美、英国、澳大利亚及部分欧洲市场即时上线。"
    ),
    "Walmart Enables Muse Shopping Through Its Agent Gateway": (
        "The Verge 于 2026 年 11 月 23 日报道，沃尔玛的智能体网关（Agent Gateway）已上线并支持 "
        "Meta 的 Muse，允许该 AI 智能体通过客户可控的智能体档案（Agent Profiles）查找并购买沃尔玛"
        "商品，包括黑色星期五优惠。沃尔玛的 Agent Gateway 页面也将 Muse 购物列为当前可用功能。"
        "设置流程包括：告诉 Muse 要找什么、关联沃尔玛账户、创建智能体档案，并在结账前选择购物"
        "控制选项。"
    ),
    "Z.ai’s GLM-5.4 Uses Iterative Depth Without Adding Parameters": (
        "Z.ai 于 2026 年 11 月 23 日推出 GLM-5.4——一个 7500 亿参数模型，通过重复使用层来加深"
        "推理，而不增加参数量。该公司称其智能水平可与 2 万亿至 3 万亿参数的模型相媲美。GLM-5.4 是 "
        "Z.ai 基于 Loop Transformer（循环 Transformer）打造的首款旗舰模型，面向大规模软件工程、"
        "网络安全、3D 建模与物理控制等推理密集任务。其核心做法是从 GLM-5 基础模型中取出 28 层，"
        "以共享权重运行两轮迭代，在不新增参数的前提下获得更大的计算深度；Z.ai 还通过逐 token 门控、"
        "混合 KV 缓存与稀疏注意力索引复用控制稳定性和部署成本。测试显示，30B 规模下循环版本在数学、"
        "科学推理和长上下文任务上提升最明显，平均输出缩短 10–14%，高峰吞吐达 70–80 token/秒。"
        "主要局限是推理循环可能过长。GLM-5.4 已通过 Z.ai Chat、GLM Coding Plan 与 ZCode 提供，"
        "API 即将上线，完成安全加固后将开源权重。"
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en not in TITLE_FIX:
            continue
        it["title_zh"] = TITLE_FIX[en]
        it["summary_zh"] = SUMMARY_FIX[en]
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])
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
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_2000_1123] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_2000_1123] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
