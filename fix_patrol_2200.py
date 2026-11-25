# -*- coding: utf-8 -*-
"""22:00 例行巡检：5 条新增资讯的 NLLB 直译硬伤人工定稿。

本轮机器译文出现「人类研究」（Anthropic study）、「浪漫关系」
（affair，实为黄仁勋与 Megaspeed 高管的恋情）、「间机构」等语义错误，
直接回填人工定稿，并同步写入 JSON 覆盖表；
随后由 scripts/regen_overrides.py 固化到代码层 manual_overrides.py，
保证线上部署后不会被模型译文再次覆盖。

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
    (
        "8b12331aa040ab2654008fb8d23013a7",
        "AI agents now control part of Deepmind's compute for Gemini experiments, but recursive self-improvement remains distant",
        "AI 智能体已掌控 DeepMind 部分算力用于 Gemini 实验，但递归式自我改进仍很遥远",
        "Google DeepMind 让 AI 智能体自主为即将推出的 Gemini 模型开展实验。研究负责人 Koray Kavukcuoglu 表示，实验室距离递归式自我改进仍很遥远。为便于监督，DeepMind 刻意不训练智能体的内部思维链，以便对其进行审查。Kavukcuoglu 衡量 AGI 的标准是日常用户的信任，而非基准测试成绩。",
    ),
    (
        "7e3bae2ad55db8fab1a90c1f9a0314f2",
        "Anthropic study shows the hardest part of adopting AI at work has little to do with learning the tools",
        "Anthropic 研究显示：工作中采用 AI，最大难点与学习工具关系不大",
        "Anthropic 研究了美国 58 家公司的近 300 个 AI 部署案例，结果不容乐观：近五分之一仍未带来业务价值，受制于繁重的审查工作负担、内部瓶颈和员工抵触。研究人员指出，最大的障碍源自过时的公司结构。",
    ),
    (
        "fb3c9c10b4ff0e9ea2adc783cc16fca7",
        "Back-to-back cyber incidents at US financial investigators and spy agencies follow a string of federal hacks and outages",
        "美国金融调查机构与情报机构接连发生网络事件，此前联邦政府已遭遇一系列黑客攻击与系统中断",
        "美国金融犯罪执法网络（FinCEN）在发现未经授权的访问后，出于预防考虑将系统下线。数小时前，有报道称中央情报局（CIA）、国家地理空间情报局（NGA）和国家情报总监办公室（ODNI）也遭遇另一起数据泄露，调查人员怀疑攻击者使用了 AI 防御工具 Artex。两起事件都发生在美国公众神经已然紧绷之际。",
    ),
    (
        "4621f767e4cf4e2625086690a9e1b4c9",
        "The questions Jensen Huang and Nvidia will still have to answer about Megaspeed",
        "黄仁勋与 NVIDIA 围绕 Megaspeed 仍需回答的问题",
        "黄仁勋回归出任 NVIDIA CEO，并未减轻公司面临的审查。NVIDIA 仍在接受多项调查：有指控称其先进 GPU 被客户、新加坡数据中心运营商 Megaspeed 违反美国出口管制走私至中国。调查人员关注的是 NVIDIA 对芯片最终去向究竟知情多少，以及黄仁勋与 Megaspeed 高管 Alice Huang 的恋情是否让公司有理由怀疑 Megaspeed 的保证。美国司法部长 Todd Blanche 表示 NVIDIA 并非调查目标，但加州总检察长与国会仍在推进调查，美国证监会（SEC）也在调查。",
    ),
    (
        "16ad7d5346f9ec0a4dee02a0ccf8f33e",
        "The Simulation Gap: Why Physical AI Still Needs Real-World Data",
        "仿真鸿沟：为何物理 AI 仍需要真实世界数据",
        "仿真、数字孪生和合成数据可以降低训练机器人的时间、成本与风险，这推动了跨任务、跨行业运行的机器人基础模型研究。业内许多人如今认为，只要有足够的仿真，就不再需要多少真实世界数据。我并不这么确信，尤其是当物理 AI 从受控研究环境走向实际运营之时。",
    ),
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
