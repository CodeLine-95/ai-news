# -*- coding: utf-8 -*-
"""2026-11-03 11:00 巡检：定向人工定稿本轮新增的 2 条低质量译文。

11:00 轮抓取新增 2 条（343 → 344），自动译文存在明显缺陷：

条目 1 —— Zyphra ZHA（09:09）
  标题：「齐弗拉 AI 介绍了齐弗拉等级注意力（ZHA）：向真实次次级注意力的一条道路」
  问题：
    a) Zyphra 是公司名，被音译成「齐弗拉」，中文读者无法定位该公司；
    b) "hierarchical attention"（层次化注意力）→「等级注意力」；
    c) "subquadratic"（次二次复杂度）→「次次级」，完全不成词；
    d) "A Path to" 直译成「向…的一条道路」，中文不成句。
  摘要问题：
    e) "sparse attention"（稀疏注意力）→「稀有注意力」；
    f) "dense attention"（稠密注意力）→「密集关注」；
    g) "distilled into frozen pretrained models"（蒸馏到冻结的预训练模型）
       →「蒸成…冷预训练模型」；
    h) "context"（上下文）→「语境」，与站内 1M context 写法不一致；
    i) "Retrofits…" / "Speedups come from…" 两个小句的主语未译，中英混排；
    j) 句中大量半角逗号（「推理，智能体编程和…」「7 个推理，编码和检索基准」），
       与站内全角标点风格不一致；
    k) 尾句「在 7 个推理，编码和检索基准上的密集关注数点内」语义崩坏
       （原文 "Within a few points of dense attention on 7 … benchmarks"）。

条目 2 —— Dan Driscoll 加入 OpenAI（10:49）
  标题：「前陆军秘书丹·迪斯科尔加入 OpenAI 作为高级顾问」
  问题：Secretary of the Army 官方译名为「陆军部长」，
        「陆军秘书」是字面硬译，会低估该职位的分量；
        「加入 OpenAI 作为高级顾问」语序生硬。
  摘要问题：「网络安全」出现两次，第二次原文是 "cyber security"，
        译法与前半句 "national security" 混用；「说明先进的 AI 如何
        加强国家和网络安全」把 "advise … on how" 的语法关系拆散了。

处理方式：
  1) 根因修复写入 translate.py 的 TERM_FIXES（齐弗拉/Zyphra、
     稀有注意力/稀疏注意力、等级注意力/层次化注意力、密集关注/稠密注意力、
     次次级/次二次、冷预训练/冻结的预训练、蒸成/蒸馏到、语境/上下文、
     陆军秘书/陆军部长、Retrofits/Speedups 主语补全）；
  2) 本脚本对这两条做「语义层」人工定稿——术语规则解决不了整句语序
     与尾句崩坏，必须逐句重写。

处理顺序与 server.py 的调度周期完全一致（这一点很关键）：
    人工定稿 → 术语确定性重清洗 → 应用人工标题覆盖 → 应用人工摘要覆盖
    → 重新生成报告
早期版本的脚本只做了「重清洗」，漏掉最后两步的覆盖表回填，导致
既有条目被术语规则改坏（如「英特尔」被还原成「Intel」、「委员会会面」
被折叠成「委员会面」）。server 里覆盖表在最后应用，优先级最高，
因此必须复刻同样的顺序。

用法：
    python3.11 fix_1100_zha_driscoll.py
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
sys.path.insert(0, BASE)

import server  # noqa: E402  复用 server 的清洗/覆盖函数，保证顺序一致

# ---------- 人工定稿译文 ----------

TITLE_FIX = {
    # Zyphra：标题用中文习惯的「发布」结构；
    # 「A Path to True Subquadratic Attention」译作「迈向真正次二次注意力的路径」。
    "Zyphra AI Introduces Zyphra Hierarchical Attention (ZHA): A Path to True Subquadratic Attention":
        "Zyphra 发布 Zyphra 层次化注意力（ZHA）：迈向真正次二次注意力的路径",
    # Driscoll：「Secretary of the Army」译「陆军部长」；
    # 「加入 OpenAI 作为高级顾问」语序生硬，改为「出任 OpenAI 高级顾问」。
    "Former Army Secretary Dan Driscoll Joins OpenAI as Senior Counselor":
        "前陆军部长丹·迪斯科尔出任 OpenAI 高级顾问",
}

SUMMARY_FIX = {
    "Zyphra AI Introduces Zyphra Hierarchical Attention (ZHA): A Path to True Subquadratic Attention":
        (
            "Zyphra 发布了 Zyphra 层次化注意力（ZHA），这是一种围绕树形结构索引器"
            "构建的稀疏注意力方法。ZHA 针对稀疏注意力的一个已知短板：负责挑选 token "
            "的索引器仍需扫描全部上下文。Zyphra 的技术论文显示，ZHA 可被蒸馏到约 40 亿 "
            "token 的冻结预训练模型中。在 Qwen3.6-35B-A3B 上，它在推理、智能体编程与 "
            "256K 上下文检索基准上表现接近稠密注意力。速览：规模方面，该方法为 "
            "Qwen3.6-35B-A3B 增加了 81,920 个可训练参数（约 0.00024%），已在最高 256K "
            "上下文下测试。运行方式：在 32K 上下文下进行 40 亿 token 的 KL 预热后，即可"
            "回溯改造冻结的预训练模型；加速比来自建模的 H100 BF16 屋顶线，尚未发布优化内核，"
            "另测试了 FP4 路由器变体。性能：在 7 项推理、编程与检索基准上，与稠密注意力"
            "相差仅数分。"
        ),
    "Former Army Secretary Dan Driscoll Joins OpenAI as Senior Counselor":
        (
            "OpenAI 于 2026 年 11 月 2 日宣布，前陆军部长丹·迪斯科尔将出任国家安全"
            "现代化高级顾问，这是新设职位，聚焦国家安全、网络安全以及与美国盟友的协作。"
            "迪斯科尔将就先进 AI 如何强化国家安全与网络安全，向 OpenAI 高层领导团队与"
            "外部合作伙伴提供建议。"
        ),
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    # 第 1 步：人工定稿
    hit_t = hit_s = 0
    for it in items:
        t = it.get("title", "")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_t += 1
            print("fix title:", it["date"], it["time"], it["source"])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_s += 1
            print("fix summary:", it["date"], it["time"], it["source"])

    # 第 2~4 步：与 server.py 调度周期完全一致的顺序
    server.apply_term_cleanup(items)
    server.apply_title_overrides(items)
    server.apply_summary_overrides(items)

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
    if hit_t != len(TITLE_FIX) or hit_s != len(SUMMARY_FIX):
        raise SystemExit("覆盖未全部命中，请检查英文原标题是否一致")

    # 重新生成报告
    import report
    report.main()


if __name__ == "__main__":
    main()
