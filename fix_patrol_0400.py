# -*- coding: utf-8 -*-
"""04 点例行巡检：对本轮新增 2 条 NLLB 机翻硬伤人工定稿。

问题：
  1) Employee Health Benefits End at Foundation Future Industries
     - 「Foundation Future Industries」被误译为「基金会未来行业」（公司名，应保留英文）
     - terminated retroactively 被误译为「推迟到 2026 年 10 月」（应为「追溯至…终止」）
     - missed payrolls 被误译为「错过了工资表」（应为「未能按时发薪」）
  2) Nonprofits Build Capacity for Potential Giving After Anthropic's IPO
     - 「捐赠承诺（pledges）」漏译「捐赠」义
     - debut valuation 语句崩坏（「报告将 Anthropic 首次估值达到…」）
  3) Decoding Policies in a Serving Engine（refresh 后新抓到）
     - Decoding Policies 误译为「解码政策」（应为「解码策略」）
     - Sampling Filters 误译为「采样过器」、Beam Search 误译为「光束搜索」、
       Per-Token Work 误译为「每代码工作」

写入三层：JSON 标题表 / JSON 摘要表 / news.json；按 id 定位，避免引号不匹配。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

# id -> (定稿中文标题, 定稿中文摘要)
FINAL = {
    "74897f15acdd14fa0aa37d0c270933a5": (
        "Foundation Future Industries 终止员工健康福利",
        "CNBC 于 2026 年 11 月 22 日援引获取的内部备忘录报道称，人形机器人初创公司 Foundation Future Industries 告知员工，因其未能按时发薪并寻求紧急融资，通过管理员 Rippling 提供的健康福利已被追溯至 2026 年 10 月终止。致员工的邮件称，他们将获得 2026 年 11 月的 COBRA 医保覆盖；Foundation 承诺报销保费，并正在启用新的福利供应商。",
    ),
    "55d0ebaa9b5477153277094826f3c4d0": (
        "Anthropic IPO 后，非营利组织为潜在捐赠扩充能力",
        "美联社于 2026 年 11 月 22 日报道称，在这家 AI 公司 IPO 之后，非营利组织正为接收 Anthropic 员工与创始人的潜在捐赠做准备。按 IPO 价格计算，联合创始人承诺的股份价值 1120 亿美元，但许多员工要到 2027 年春季才能出售或赠与多数股份，因此非营利组织在扩大能力的同时，并不指望立即收到捐款。报道称 Anthropic 上市首日估值创纪录地达到 1.5 万亿美元。",
    ),
    "a27c7fa03de7a9df87510e14dcff6c05": (
        "服务引擎中的解码策略",
        "本文概述分为六个部分：使用 vLLM 运行解码策略、采样过滤器与逐词元处理、多输出与束搜索、停止条件与请求生命周期、结构化输出，以及批处理与运行时成本。在使用 vLLM 运行解码策略部分，vLLM 将模型执行与词元选择分离开来。",
    ),
}


def main():
    t = json.load(open(T_JSON, encoding="utf-8"))
    s = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(NEWS, encoding="utf-8"))
    items = news.get("items", [])

    hit = 0
    for iid, (zh_t, zh_s) in FINAL.items():
        target = next((it for it in items if it.get("id") == iid), None)
        if not target:
            print("  [警告] news.json 未匹配 id:", iid)
            continue
        en = (target.get("title") or "").strip()
        t[en] = zh_t
        s[en] = zh_s
        target["title_zh"] = zh_t
        target["summary_zh"] = zh_s
        target["translated"] = True
        target["method"] = "manual"
        target.pop("needs_retranslate", None)
        target.pop("retranslate_attempts", None)
        hit += 1
        print("  定稿:", en)

    json.dump(t, open(T_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(s, open(S_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(news, open(NEWS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[fix_patrol_0400] 定稿 %d 条" % hit)
    print("[fix_patrol_0400] 覆盖表: 标题 %d / 摘要 %d" % (len(t), len(s)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
