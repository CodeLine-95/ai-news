# -*- coding: utf-8 -*-
"""2026-11-21 07:00 巡检：定稿本轮新增 3 条 NLLB 机翻硬伤。

07:00 整点抓取（服务 07:00 重启后首轮）2528 -> 2531（+3），3 条均为 Unite.AI，
存在明显机翻缺陷：
- AWS HyperPod：Routes 误译为「路线」（应为路由）、endpoint「终点」（应为端点）、
  「近距离」误译 proximity、「发射」误译 launch、重复「推出了」；
- Cognition AI：$2B-Plus 误译为「2 亿美元」（应为 20 亿美元以上）、
  $75B 标题误译为「75 亿」（应为 750 亿）、Cognition 品牌被译成「认知人工智能」、
  Bloomberg 误译为「博新闻」；
- CrowdStrike/Zscaler：CrowdStrike 音译为「克劳德斯特莱克」、Bloomberg「博社」
  （应为彭博社）、extended trading「扩展交易」（应为盘后交易）、shares「股份」（应为股价）。

覆盖三层：news.json 回填 + JSON 覆盖表 + manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "1d6fce669f14c7cd13ad85d0a96caf50": (
        "AWS 通过一个端点跨区域路由 HyperPod 推理请求",
        "AWS 于 2026 年 11 月 20 日推出 Amazon SageMaker HyperPod 全球推理网关"
        "（Global Inference Gateway），为客户提供一个统一管理端点，"
        "可向单个 AWS 区域或多个区域中已注册的 HyperPod 集群发起推理请求。"
        "该服务依据容量、队列长度、远近和错误信号来选择集群，"
        "并在某个集群不可用时自动故障转移。此次上线在现有的 SageMaker HyperPod "
        "推理网关之上增加了第二层路由。",
    ),
    "245091b119d2b16260a9c9b0b83187ba": (
        "Cognition AI 拟融资逾 20 亿美元，估值达 750 亿美元",
        "据彭博社 2026 年 11 月 20 日援引知情人士报道（路透社转载），"
        "Cognition AI 正在商谈新一轮融资，估值达 750 亿美元，"
        "并考虑募集 20 亿美元或更多资金。谈判仍在进行，细节可能生变。"
        "报道描述的是潜在融资，而非已完成的投资。"
        "Cognition 方面未立即回应路透社的置评请求。",
    ),
    "b29df9971a55bdcc3db43b4d7ec892dc": (
        "据报道 CrowdStrike 正洽谈收购 AI 安全合作伙伴 Zscaler",
        "据彭博社 2026 年 11 月 20 日援引知情人士报道（CNBC 转载），"
        "CrowdStrike 正就收购 Zscaler 进行持续谈判。消息传出后，"
        "Zscaler 股价在盘后交易中上涨 18%，CrowdStrike 股价则下跌逾 8%。"
        "目前尚未宣布任何收购协议。CrowdStrike 拒绝就该报道置评，"
        "Zscaler 也未立即回应置评请求。",
    ),
    # ---- 历史遗留 3 条 CrowdStrike 音译/语义硬伤（11-04）----
    "f4da1e57d329e64517908244361298c4": (
        "CrowdStrike 拟以约 4.95 亿美元收购网络安全初创公司 Fiddler AI 与 Dreadnode",
        "CrowdStrike Holdings Inc. 今日披露了收购 Fiddler AI Inc. 与 Dreadnode Inc. 的计划，"
        "这两家初创公司专注于保护人工智能智能体。该公司在宣布这些交易的同时，"
        "还更新了其 Falcon Guardian 产品。《华尔街日报》报道称，"
        "CrowdStrike 将为这两笔收购花费 4.95 亿美元。",
    ),
    "8917472723632c48eb8ca1cf78bfce97": (
        "CrowdStrike 为 Falcon Guardian 新增 AI 终止开关，应对失控智能体",
        "CrowdStrike 于 2026 年 11 月 3 日宣布为 Falcon Guardian 推出 AI 终止开关"
        "（AI Kill Switch），为安全团队提供一种由人工掌控的方式来中断失控的 AI 智能体。"
        "该功能随产品上线即可使用，并通过相连的 AI 网关拒绝智能体访问 AI 模型。"
        "此次上线针对的是那些能够串联任务、并在端点、云环境和 SaaS 应用中"
        "以系统级权限运行的智能体。",
    ),
    "606d854f4c59b72686798208696b79a8": (
        "CrowdStrike 计划收购 Fiddler 与 Dreadnode 以强化 AI 安全",
        "CrowdStrike 于 2026 年 11 月 3 日宣布，拟收购 Fiddler，"
        "其技术将成为 Falcon Observe，用于评估和解释 AI 智能体的行为。"
        "另一份公告则详述了收购 Dreadnode 的计划，将在系统投入生产之前"
        "把自动化 AI 安全测试加入 Falcon 平台。"
        "两项公告均发布于 Fal.Con EU 2026，描述的均为拟议中的收购。",
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    changed = 0
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
        titles[en] = title_zh
        summaries[en] = summary_zh
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_0700_1121] news.json 回填 %d 条" % changed)
    print("[fix_0700_1121] 覆盖表 %d 标题 / %d 摘要" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
