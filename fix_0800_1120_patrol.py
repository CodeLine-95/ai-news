# -*- coding: utf-8 -*-
"""08:00 例行巡检（2026-11-20）：人工定稿本轮 NLLB 机翻硬伤（8 条），回填 news.json 并写入三层覆盖表。

键为英文原标题的关键词片段（规避弯引号精确匹配问题），写入时以数据中的真实英文标题为键。
写入 JSON 覆盖表后由 scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

# 英文原标题关键词 -> (定稿中文标题, 定稿中文摘要)
FIX = {
    "Lumivero Opens SharpCloud": (
        "Lumivero 推出 SharpCloud POLI 测试版，用于项目组合决策",
        "SharpCloud POLI 测试版利用投资组合数据回答问题、模拟变更，同时让项目经理保持掌控与认可。",
    ),
    "Anthropic IPO Draws Protests": (
        "Anthropic IPO 引发围绕 AI 安全与医疗保健的抗议",
        "由于 Anthropic 进入公开市场，ACT UP NY 与 Ban RSI 于 2026 年 11 月 19 日在纽约和旧金山分别举行示威。抗议活动质疑 AI 在医疗保健与递归自我改进（RSI）方面的应用，另一项独立行动则要求金融机构对 AI 投资及退休储蓄的使用进行压力测试。",
    ),
    "computer use capabilities to Gemini": (
        "Google 为 Gemini 的 Mac 应用新增电脑操作能力",
        "Google 今日发布 Gemini Mac 客户端新版本，可与用户电脑上的其他应用交互。该功能推出时即在美国上线，需要 Google AI 订阅，从而为消费者 Google 账户提供更广泛的 AI 工具。",
    ),
    "Form & Function Launches Lever": (
        "Form & Function 推出 Lever，为 AI 助手提供共享业务上下文",
        "咨询公司 Form & Function 推出 AI 平台 Lever，旨在为专业服务公司提供跨孤立系统的统一运营视图。该产品于 11 月 12 日发布，将运营数据与各公司的业务定义相结合，使管理者可通过对话界面查询人员配置、收入预测和项目盈利能力等问题。值得一提的是，它并非又一款回答财务问题的聊天机器人。",
    ),
    "Tanium AgentSight": (
        "Tanium AgentSight 将影子 AI 纳入终端资产清单",
        "Tanium 的 AgentSight 发布，让安全团队掌握员工设备上安装的 AI 工具情况，而智能体活动追踪与更广泛执法功能仍在路线图上。",
    ),
    "AWS Lets AgentCore": (
        "AWS 允许 AgentCore 智能体通过 AWS 账单购买 Marketplace 产品",
        "Amazon Web Services 于 2026 年 11 月 19 日宣布，Amazon Bedrock AgentCore 支付现可通过支持 x402 的 AWS Marketplace 卖家、使用 AWS 账单结算购买。AI 智能体可以美元购买软件、API、数据和内容，相关费用记入智能体开发者的 AWS 账单。",
    ),
    "SRE-1 model finds root causes": (
        "Resolve AI 的 SRE-1 模型可定位生产告警根因，AI 智能体开始值班待命",
        "事件修复公司 Resolve AI Inc. 宣布推出 SRE-1——一个专为定位生产告警根因训练的新模型，以及 Primary On-call 新服务，让 AI 智能体在人类工程师之前响应告警。",
    ),
    "Anthropic Raises $81.34B": (
        "Anthropic 在 IPO 中募资 813.4 亿美元；股价首日收盘上涨 17%",
        "根据纳斯达克官方市场记录，Anthropic 的 A 类股票于 2026 年 11 月 19 日以 97.17 美元完成纳斯达克首日交易，较 83 美元的 IPO 发行价上涨 17.07%。开盘价 111.50 美元，盘中交易区间为 92.72 至 115.10 美元。",
    ),
}


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    for it in items:
        en = it.get("title") or ""
        key = next((k for k in FIX if k in en), None)
        if not key:
            continue
        title_zh, summary_zh = FIX[key]
        if it.get("title_zh") != title_zh:
            it["title_zh"] = title_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] title:", en[:50], "->", title_zh)
        if it.get("summary_zh") != summary_zh:
            it["summary_zh"] = summary_zh
            print("[fix]  summary:", en[:50])
        tov[en] = title_zh
        sov[en] = summary_zh

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 标题变更:", changed, "| 覆盖表 标题:", len(tov), "摘要:", len(sov))


if __name__ == "__main__":
    main()
