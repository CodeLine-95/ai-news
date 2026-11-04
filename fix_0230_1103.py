# -*- coding: utf-8 -*-
"""2026-11-03 02:30 巡检：修复 02:00 周期新增 6 条的译文缺陷。

02:00 整点自动抓取新增 6 条，NLLB 直译暴露三类系统性缺陷：

1) 品牌/地名还原不足
   - Larridin（AI 支出衡量创业公司）被音译成「拉里丁」
   - Brave（浏览器厂商）被意译成「勇敢」——正文里出现「勇敢软件」
     「勇敢指数」，中文读者完全无法定位公司
   - Effingham County 被译成「埃芬汉姆」（既有规则只覆盖「埃菲金汉」）
   - Georgia 被译成「乔治亚州」——既有规则只覆盖「格鲁齐亚」，漏了这一个变体
   - Stony Brook（斯通尼布鲁克大学）被译成「斯通尼布鲁克」尚可，但
     「Stony Brook Study」在标题里被拆成「斯通尼布鲁克研究」

2) 领域术语误译（严重事实错误）
   - discharge summary（出院小结，医疗文书）被直译成「排放总结」，
     语义完全相反，属医疗领域专业性错误

3) 语气/结构塌陷
   - 「won't stop the AI copying boom」被译成「不会阻止 AI 复制繁荣」，
     「boom」（热潮）译成「繁荣」后整句语义崩坏
   - 「chasm」（网名）被译成「化」，只剩一个字

同时对上一轮遗留的 1 条（Ebix/Intentyx）补齐摘要定稿：
原摘要结尾「检测智能体行为偏离经营目的或安全界限时。」是断句残缺
（以「时」结尾后无下文），需重写。

修复策略与上一轮一致：
  A. 人工定稿覆盖受影响条目的标题与摘要；
  B. 在 translate.py 补确定性术语规则，使同类缺陷在后续每小时的
     自动抓取中自愈，不依赖逐条人工兜底。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    # Larridin 品牌名保留；Series A 是「A 轮」而非「A 系列」
    "Larridin Raises $30 Million Series A to Measure AI Spending and Workforce Impact":
        "Larridin 获 3,000 万美元 A 轮融资，衡量 AI 支出与人力影响",
    # 标题结构：主干 + 副标，用「：」比「，」更贴合原文
    "Microsoft and Lumen Expand Co-Selling for Enterprise AI Networks":
        "Microsoft 与 Lumen 扩大企业 AI 网络的联合销售",
    # 「won't stop the AI copying boom」——boom 是「热潮」不是「繁荣」
    "Claude’s new rules against game cloning won’t stop the AI copying boom":
        "Claude 新增游戏克隆限制，但挡不住 AI 仿制热潮",
    # Georgia 州 + Effingham County 地名规范；pitches 是「对外推介」
    "OpenAI pitches data center power plants as a way to protect nearby areas":
        "OpenAI 推介数据中心自建电厂，以保护周边地区",
    # discharge summary = 出院小结（医疗文书），不是「排放总结」
    "Physicians Preferred AI Discharge Summaries in 95% of Cases in Stony Brook Study":
        "斯通尼布鲁克研究：95% 病例中医生更偏好 AI 出院小结",
    # Brave 是公司名，必须保留英文；不能译成「勇敢」
    "The New York Times sues Brave web browser for AI scraping and bypassing paywalls":
        "《纽约时报》起诉 Brave 浏览器：涉 AI 抓取与绕过付费墙",
}

SUMMARY_FIX = {
    "Larridin Raises $30 Million Series A to Measure AI Spending and Workforce Impact":
        "Larridin 完成由 Pelion Ventures 领投的 3,000 万美元 A 轮融资，"
        "累计融资达 4,700 万美元。该公司衡量 AI 支出如何转化为员工与软件智能体"
        "实际承担的工作，面向希望更清晰验证 AI 投资回报的企业。"
        "现有投资者 Andreessen Horowitz 与 Gradient Ventures 参与本轮，"
        "新投资者还包括 GFT、W23、Thayer、DG Daiwa Ventures、"
        "Alumni Ventures 与 Cougar Capital。",
    "Microsoft and Lumen Expand Co-Selling for Enterprise AI Networks":
        "Microsoft 与 Lumen Technologies 于 2026 年 11 月 2 日宣布扩大联合销售合作，"
        "重点是打通企业 AI 工作负载所依赖的数据、应用与基础设施，"
        "并通过 Azure 与 Microsoft Marketplace 扩大 Lumen 网络能力的可及性。",
    "Claude’s new rules against game cloning won’t stop the AI copying boom":
        "上周 Anthropic 推出了一套新的系统提示，用于阻止其 Claude 模型"
        "重新创建特定已有电子游戏。这一举措或许能让 Anthropic 规避部分责任，"
        "但恐怕难以遏制近几个月涌现的大规模 AI 辅助游戏移植与仿制浪潮。"
        "一位网名为「chasm」的社交媒体用户兼 AI 反编译爱好者，"
        "是最早注意到该提示变更的人之一，他表示大约在 10 月 27 日前后，"
        "Claude Code 的提示词中被加进了一条新规则。",
    "OpenAI pitches data center power plants as a way to protect nearby areas":
        "OpenAI 在周一发布的一份声明中表示，将在佐治亚州埃芬汉县一座即将建成的数据中心"
        "试点「电网守护者计划」，承诺在极端天气或紧急状况下释放出最多 1,000 兆瓦电力，"
        "足以为约 70 万户家庭提供空调用电。"
        "这一声明发布之际，美国各地针对数据中心的反对声浪正不断扩散——"
        "这些项目体量巨大，已陆续动工建设，而当地居民的意见往往极少被听取。",
    "Physicians Preferred AI Discharge Summaries in 95% of Cases in Stony Brook Study":
        "在斯通尼布鲁克大学的一项研究中，医生评审者在所评估的 95% 住院病例里，"
        "更偏好 AI 生成的出院小结，而非人工撰写的同类文书。"
        "这项回顾性分析聚焦 60 例内科住院案例，住院时长为 7 至 21 天；"
        "此类病例治疗周期长、临床记录量大，"
        "因而向门诊环节的交接工作尤为繁重。",
    "The New York Times sues Brave web browser for AI scraping and bypassing paywalls":
        "据路透社报道，《纽约时报》与其他多家出版机构已起诉 Brave 浏览器的"
        "运营方，指其涉嫌非法抓取内容用于训练 AI，并允许用户绕过付费墙。"
        "据运营《纽约日报》《芝加哥论坛报》与《奥兰多哨兵报》的公司提交的诉状，"
        "Brave Software 已通过向 AI 公司付费提供「来自 Brave Index 的实时在线内容」"
        "等方式，将其抓取索引商业化。",
    # 上一轮遗留：原摘要以「时」结尾，句子残缺
    "Ebix and Intentyx Launch SMARE to Track AI Agent Behavior":
        "Ebix 于 2026 年 11 月 2 日宣布与网络安全公司 Intentyx 建立设计与交付合作，"
        "面向受监管行业推出智能体 AI 安全与治理方案。"
        "该方案以 SMARE（Synthetic Mind Aware Risk Engine）为核心，"
        "这是 Intentyx 的行为安全与治理平台，用于发现企业 AI 智能体、明确责任归属，"
        "并检测智能体行为偏离既定业务目的或安全边界的情况。",
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
