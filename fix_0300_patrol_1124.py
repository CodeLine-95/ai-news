# -*- coding: utf-8 -*-
"""2026-11-24 03:00 例行巡检：定稿本轮新增 10 条 NLLB 机翻硬伤。

服务于 02:59:32 自动重启后执行首轮抓取，补抓 02:00-02:47 共 10 条，
均为 nllb 机翻，主要问题：
1) SiliconANGLE AWS Strands：decisive 误作「更具决心」（应为决策力）、
   Amazon Web Services 音译「Amazon 网页服务」；
2) TechCrunch Jensen：句式崩坏「黄出台有关与嫌疑中国间的情形」；
3) Unite.AI Mercedes-Benz：品牌截断「梅赛德斯-奔」、20–30% 乱码成 20%%；
4) Unite.AI Anthropic EFS：frontier 误作「边境」（应为前沿）、
   zero data retention 误作「零保留」、句式崩坏；
5) The Verge Grok：起诉对象语序颠倒、porn deepfakes 误作「色情深度事件」、
   Jay Jones 音译「杰伊·斯」、「更多利的市场机会」残句；
6) Unite.AI Gemini API：file slicing 误作「文件剪辑」、
   native Office 误作「本地办公室」、spreadsheet 误作「电子表」；
7) Unite.AI AWS Decider：sandboxes 误作动词「Sandboxes 更多的编码智能体」、
   unattended coding sessions 误作「不受监督的编码会议」、
   without generating prose 误作「不需要生成散文」；
8) The Decoder OpenAI：核心能力阈值句「以惊人的精确的门出现」语义崩坏；
9) Unite.AI P3 State：Main Sequence 误作「主要序列/主机序列」、
   P3 State 误作「P3 州」、A$9.5M 误作「$9.5M」；
10) The Decoder xAI：compute 误作「计算」（应为算力）、
    rent-over-build 误作「租建设」（应为租而非建）、SpaceXSI 还原。

覆盖三层：news.json 回填 + JSON 覆盖表 + （随后 regen）代码层 manual_overrides.py。
覆盖表 key 直接从 item['title'] 读取，避免智能引号/短横线手工录入偏差。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "5f55e50decad95b9c567cde5f95c29df": (
        "AWS 通过最新 Strands 更新让 AI 智能体更具决策力与安全性",
        "亚马逊云科技（AWS）正通过对其开源自主智能体构建工具包 Strands Agents 的重大更新，解决 AI 智能体开发者面临的两大难题。",
    ),
    "4eec8977b6a96a50e0b875b574f57529": (
        "黄仁勋恢复英伟达 CEO 职务后，下周将在参议院作证",
        "此次公开听证会是在两党呼吁黄仁勋就与一名疑似中国间谍的往来事件作证之后举行的。",
    ),
    "90034cb094976a2de026e12f41b57446": (
        "梅赛德斯-奔驰采用 Atlas AI 智能体进行工厂电气故障诊断",
        "根据这家汽车制造商与 Arena Physica 于 2026 年 11 月 23 日宣布的全球协议，AI 智能体将帮助梅赛德斯-奔驰技术人员诊断和修复生产线上的电气与电子（E/E）故障。Arena Physica 报告称，在初步测试中，无论是新手还是经验丰富的技术人员，使用 Atlas 后诊断和修复问题的速度都提升了 20%–30%。",
    ),
    "f27629d7830ef03e772f94b1d018678b": (
        "Anthropic 推出零数据留存的企业前沿安全防护公测版",
        "Anthropic 于 2026 年 11 月 23 日在与 100 多家客户共同开发后，开放了企业前沿安全防护（EFS）公测版。该系统将零数据留存与跨多个请求的滥用模式自动监测相结合，同时将密封的安全数据保存在客户自有的云存储中。Bridgewater、Salesforce 和 Stripe 参与了私测评估。",
    ),
    "7b4f2fa9d495656290ef518988620b03": (
        "俄勒冈州和弗吉尼亚州就 Grok 的色情深度伪造内容起诉 SpaceX",
        "在周一分别提起的两起类似诉讼中，俄勒冈州检察长丹·雷菲尔德（Dan Rayfield）与弗吉尼亚州检察长杰伊·琼斯（Jay Jones）指控 SpaceX 违反州消费者保护法，无视行业标准的安全保障，并虚假宣传其 X 社交媒体平台和 Grok AI 功能的安全性。在弗吉尼亚州提交的诉状中，马斯克被指蓄意无视外界对 AI 生成的性化深度伪造内容日益加剧的担忧，反而「看到了更多利润的市场机会」，并将 Grok 周围薄弱的安全措施形容为「不是失败，而是一项功能」。",
    ),
    "7c453e14e795ae3ab9b70eb955c5652c": (
        "Google 为 Gemini API 增加文件切片与原生 Office 文档支持",
        "Google 于 2026 年 11 月 23 日在 Gemini API 中推出原生文件切片控制，并新增对 Microsoft Office 和 OpenDocument 文件的原生上传支持。开发者可以请求指定页面、电子表格区域或媒体片段，仅对 Gemini 实际检查的内容计费。此次更新面向那些需要从长报告中提取图表、从工作簿中提取单张工作表，或从录音中提取简短片段的智能体。",
    ),
    "69ae5495a7998967b4ee34199a04a5a8": (
        "AWS 发布 Strands Decider V2，并为更多编码智能体提供沙箱支持",
        "亚马逊云科技于 2026 年 11 月 23 日发布了五款开放权重的 Strands Decider v2 模型，并在其开源 Strands Box 沙箱中新增对 Claude Code、Codex 和 Kiro CLI 的原生支持，旨在降低常规智能体决策的推理成本，并提升无人值守编码会话的安全性。Decider 可直接处理重复性选择，无需生成冗长文字。",
    ),
    "98b64aa39b49b829b8bee9c2ea265310": (
        "OpenAI 警告称即将推出的 AI 系统可能超越安全检查，并敦促竞争对手就共同限制达成一致",
        "OpenAI 首席科学家雅库布·帕霍茨基（Jakub Pachocki）首次公布了整个 GPT 系列的内部困惑度分数，数据延伸至当前一代之外的一款未发布模型。该指标显示，核心能力会在出人意料地精确的阈值上涌现。帕霍茨基正推动将困惑度确立为全行业通用的进展指标，并在对 AI 行为的控制力削弱之前建立共同限制。",
    ),
    "76f7feb761968c4cd4077ca54d089d5c": (
        "Main Sequence 领投澳大利亚 AI 初创公司 P3 State 的 950 万澳元融资",
        "澳大利亚基础 AI 初创公司 P3 State 宣布完成 950 万澳元（650 万美元）融资，由 Main Sequence 领投，美国深科技投资机构 DCVC 参投。该公司新闻索引显示帖子日期为 2026 年 11 月 23 日，而新闻稿本身的澳大利亚日期为 2026 年 11 月 24 日。这笔资金将用于扩充 P3 State 在澳大利亚的研究与工程团队，并推进其核心技术走向公开发布。",
    ),
    "477cc9a19ab03c3570c554514bffcded": (
        "Anthropic 对算力的旺盛需求正推动 xAI 转向「租而非建」策略",
        "据《纽约时报》报道，自 5 月以来，SpaceXAI 一直向 Anthropic、Google 等竞争对手出租算力，同时缩减自身 AI 项目。Anthropic 每月支付约 31 亿美元，Google 支付约 8 亿美元。在 6 月 IPO 之后，SpaceXAI 解散了 60 人的 Grok Imagine 团队，并进行了其他裁员。",
    ),
    # 历史遗留：2026-11-23 22:00 源站把 xAI 拼作 SpaceXSI，译文沿用致门禁告警，
    # 按 KNOWN_BAD 规则还原为 SpaceXAI。
    "0f9e3fb7c1a379e2199819f2ebe61b33": (
        "Innovaccer 借助 SpaceXAI 的 Grok Voice 模型扩展 Gravity Voice AI 智能体",
        "医疗保健人工智能公司 Innovaccer Inc. 今日宣布，已通过 Grok Voice 扩展其 Gravity Voice AI 智能体。Grok Voice 是埃隆·马斯克旗下人工智能公司 SpaceXAI（原 xAI）推出的语音到语音模型。",
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

    print("[fix_0300_1124] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_0300_1124] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0 if changed == len(FIX) else 1


if __name__ == "__main__":
    raise SystemExit(main())
