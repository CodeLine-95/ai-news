# -*- coding: utf-8 -*-
"""12:00 例行巡检：定稿本轮新增的 2 条 Marktechpost 机翻硬伤。

1) Tencent 被 NLLB 截成「讯」；"sparse KV cache" 错乱成「重复目标斯 parse KV」。
   按英文原文重述，保留 Tencent / DFly2 / DeepSeek 等专名。
2) nexos.ai 标题 "AI Adoption Platform" 被直译为「采用平台」，摘要机翻生硬。
   按英文原文重述，保留 SOC 2 / ISO 27001 / GDPR 等认证标识。

写入人工覆盖表（标题 + 摘要），并回写 data/news.json，
保证服务端重启 / 线上持久卷也能回填为定稿版本。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = [
    {
        "en": "Tencent Open-Sources DFly2: Speculative Decoding That Reuses the Target’s Sparse KV Cache",
        "title_zh": "腾讯开源 DFly2：复用目标模型稀疏 KV 缓存的投机解码",
        "summary_zh": (
            "腾讯开源了 DFly2——一款为原生稀疏大模型设计的投机解码草稿模型。"
            "DFly2 面向 DeepSeek-V4.1-Flash、GLM-5.3-Flash 以及腾讯自研 Hy4 flash 等模型。"
            "其核心特点是草稿模型不保留自己的 KV 缓存，这对长上下文与智能体服务至关重要，"
            "因为草稿显存会与并发量争夺资源。要点：规格方面，随 Hy4 flash 提供 0.85B 参数、"
            "5 层的草稿模型；运行方面，服务测试使用 NVIDIA H20 GPU 与 vLLM，每实例 TP8，"
            "Hy4 flash 的 vLLM 方案默认 8×H200；性能方面，在全部 3 个目标模型和通用基准上，"
            "草稿接受率均高于同配置的 DFlash 与 DSpark；最佳情形是在 DeepSeek-V4.1-Flash"
            "（SWE 64K）上吞吐最高提升 81%，且保持相同的单用户速度；最弱情形是在 Hy4 flash "
            "通用任务上，温度 0 时仅比 DSpark 高 3.9%。"
        ),
    },
    {
        "en": "nexos.ai AI Adoption Platform puts 200+ models behind one AI Gateway, with budget limits and governance built in",
        "title_zh": "nexos.ai AI 采用平台将 200 多个模型统一接入一个 AI 网关，内置预算限制与治理能力",
        "summary_zh": (
            "nexos.ai 是一站式企业 AI 采用平台，为每个团队提供全面的管控与治理。"
            "其核心 AI 网关将所有大模型请求路由至统一层，在此统一施加预算、策略与审计追踪。"
            "本文说明它如何管理用量、优化 AI 支出，并满足欧盟企业的合规要求。要点：治理方面，"
            "可集中设定谁使用哪些模型、配置预算与用量上限、管理权限；合规方面，通过 "
            "SOC 2 Type 2、ISO 27001、ISO 42001 认证，并完全符合 GDPR；成本控制方面，"
            "智能路由与大模型缓存可优化 AI 支出，成本追踪可将每笔开销归集到团队、项目或用户；"
            "欧洲托管方面，平台及多数可用模型均在欧洲托管，零数据留存、不用客户数据训练。"
        ),
    },
]


def main():
    db_path = os.path.join(DATA, "news.json")
    db = json.load(open(db_path, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    for fx in FIXES:
        en, zh_t, zh_s = fx["en"], fx["title_zh"], fx["summary_zh"]
        tov[en] = zh_t
        sov[en] = zh_s
        for it in items:
            if (it.get("title") or "").strip() != en:
                continue
            if it.get("title_zh") != zh_t:
                it["title_zh"] = zh_t
                changed += 1
            if it.get("summary_zh") != zh_s:
                it["summary_zh"] = zh_s
                changed += 1
            it["translated"] = True
            it["method"] = "nllb+manual"
            break

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(db_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[fix] 定稿 %d 处 | 标题覆盖 %d / 摘要覆盖 %d" % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
