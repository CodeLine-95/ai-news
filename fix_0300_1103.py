# -*- coding: utf-8 -*-
"""2026-11-03 03:00 巡检：修复 02:41 / 02:56 周期新增 2 条。

NLLB 直译缺陷：

A) Anthropic 条（The Verge, 02:56）
   1) 标题语义崩坏：「clamps down on Claude's AI video game clones」
      被译成「Claude 的人工智能视频游戏克隆人群受到人类的压力」——
      clamps down on（收紧管制）被拆成「克隆人群受到人类的压力」。
   2) 摘要「Retro gaming」译成「逆转游戏」（应为「复古游戏」）。
   3)「decompilations, recompilations, and ports」译成
      「化解译，重组和端口覆盖」——decompile/recompile/port 全线错译，
      且三个词被强行合并成一句。
   4) 末句引号内「原创游戏，一种类型的游戏和游戏」语义混乱
      （games in a genre / games from the user's own designs and assets）。
   注：GLOSSARY 只能修复「英文原样残留在中文里」的情况，NLLB 把
   clamps down on 直接翻成了中文，故本条必须人工定稿。

B) Deep Principle 条（Marktechpost, 02:41）
   1) 专名丢失：Hydrogen-1.0 → 「化-1.0」，Deep Principle → 「深度原则」，
      FrontierScience-Research → 「边界科学研究」，Z.ai → 「Z.ais」，
      GPQA-Diamond → 「GpQA-Diamond」。
   2)「post-training」→ 「后期培训」（应为「后训练」）。
   3)「ships under the MIT License」→ 「权重在 MIT 许可下运输」
      （ship 在此为「发布」，非「运输」）。
   4)「1M-token context」→ 「1M 代码语境」（应为「1M token 上下文」）。
   5)「Beats GPT-6-Astra」→ 「打败 GPT-6-Astra」（应为「击败」）。
   6) 末段性能数字语序崩坏：「GPT-6-Astra（自我报告）的 38.3%对边界
      科学研究和 33.3%…」——数字与基准名对不上。

注：专名遮蔽层已在 translate.py 中修复根因（本轮新增代码），
本脚本负责把这两条已入库条目的译文定稿，并沉淀到覆盖表，
使其在后续仅代码部署时依然生效。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    "Anthropic clamps down on Claude’s AI video game clones":
        "Anthropic 收紧对 Claude AI 视频游戏克隆的限制",
    "Deep Principle Releases Hydrogen-1.0: A 753B Open-Weight Model for Scientific Discovery":
        "Deep Principle 发布 Hydrogen-1.0：面向科学发现的 753B 开放权重模型",
}

SUMMARY_FIX = {
    "Anthropic clamps down on Claude’s AI video game clones":
        "据 Tom's Hardware 报道，Anthropic 已更新 Claude Code 的系统提示，"
        "以防止该 AI 工具被用于重制已有的电子游戏。"
        "复古游戏（Retro gaming）领域眼下正被 AI 生成的反编译、重编译与移植作品大量冲击，"
        "但 Anthropic 仍允许人们使用 Claude Code 制作游戏，只是不希望人们用它来直接克隆原作。"
        "上周，X 平台上一位用户发布了一张截图，据称显示 Claude Code 的系统提示中新增了两句话："
        "“请构建原创游戏、某一类型的游戏，以及基于用户自有设计与素材的游戏。”",
    "Deep Principle Releases Hydrogen-1.0: A 753B Open-Weight Model for Scientific Discovery":
        "Deep Principle 发布了 Hydrogen-1.0，这是一个面向化学、材料科学与生命科学的开放权重科学模型。"
        "它以 Z.ai 的 GLM-5.3 为基座，在领域数据、实验室记录与智能体发现轨迹之上完成后训练。"
        "对开发者而言，它提供开放权重，并报告了在 FrontierScience-Research 上击败 GPT-6-Astra 的成绩。"
        "权重以 MIT 许可证发布。"
        "TL;DR 规模：753B 参数（MoE，基于 GLM-5.3，约 40B 激活），1M token 上下文，128K 最大输出。"
        "运行方式：8 张 GPU 搭配 SGLang（已测试）；NVIDIA B200/B300 采用 NVFP4，"
        "AMD MI350X/MI355X 采用 MXFP4。"
        "性能：在 FrontierScience-Research 上击败 GPT-6-Astra；在 GPQA-Diamond 上大致与 Kimi-K3 相当。"
        "最佳：FrontierScience-Research 上取得 38.3%，对比 GPT-6-Astra 的 33.3%（均为自报数据）。"
        "最差：在 NMR 结构解析上落后 GPT-6-Astra（最大思考模式）3.33 分。"
        "Hydrogen-1.0 是什么？",
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    hit_t = hit_s = 0
    for it in items:
        t = it.get("title", "")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_t += 1
            print("fix title:", it["date"], it["time"], it["source"], "|", t[:50])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_s += 1
            print("fix summary:", it["date"], it["time"], it["source"])

    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    for name, fix in (("titles_override.json", TITLE_FIX),
                      ("summaries_override.json", SUMMARY_FIX)):
        path = os.path.join(DATA, name)
        cur = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                cur = json.load(f)
        cur.update(fix)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=2)

    print("fixed titles:", hit_t, "/", len(TITLE_FIX))
    print("fixed summaries:", hit_s, "/", len(SUMMARY_FIX))


if __name__ == "__main__":
    main()
