# -*- coding: utf-8 -*-
"""2026-11-24 06:00 例行巡检：定稿本轮新增 8 条 NLLB 机翻硬伤。

06:00 整点调度抓取（进程 05:59 重启后首轮）新增 8 条，均为纯 nllb 机翻，
主要问题：
1) TechCrunch「reinstated at Nvidia」误作「被恢复到 Nvidia」；摘要缺主语；
2) Ars Technica「revenge porn」误作「报复色情」（应为「报复性色情内容」），
   Grok 误作「格洛克」、SpaceX 误作「太空公司」、SpaceXSI 前后不一，摘要欧化；
3) TechCrunch Megaspeed：标题「丑闻中心的公司」生硬；
4) Unite.AI「Claude Ship」误作「Claude·舰」、「PR」误作「公关」（应为拉取请求）；
5) SiliconANGLE 摘要「所以这是合适的」欧化句式崩坏；
6) MIT「Many languages」标题尚可，摘要「音调的/俄罗斯语」用词不准；
7) Marktechpost GLM-5.4：整篇机翻崩坏（扎伊/循环变压器/重量船/文本窗口等）；
8) OpenAI Richpanel：品牌名误音译为「理查班尔/里奇潘尔」。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
以英文原标题为 key 匹配，避免 id 手工录入偏差。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "Elon Musk and others rejoice as Jensen Huang is reinstated at Nvidia amid scandal": (
        "黄仁勋在丑闻中复职英伟达，埃隆·马斯克等人欣喜",
        "「错误已经得到纠正」，埃隆·马斯克附和道。",
    ),
    "States sue SpaceX to stop Grok from generating child sex images, revenge porn": (
        "多州起诉 SpaceX，要求阻止 Grok 生成儿童性图像与报复性色情内容",
        "周一，弗吉尼亚州和俄勒冈州成为首批起诉 SpaceX 的州，指控 Grok 持续未经遏止地对主要为妇女和儿童的真实照片进行性化。SpaceX 于 2 月收购 xAI，如今必须应对 Grok「spicy mode」（辣妹模式）争议性上线带来的持续清算——马斯克曾大力宣传这一模型功能，但很快发现它生成了大量非自愿亲密影像（NCII）与儿童性虐待影像（CSAM）。最初的防护措施极为松懈，Grok 有时甚至会在用户未提出要求的情况下生成裸体图像。尽管 X Safety 与 xAI（现更名为 SpaceXSI）起初保持沉默，马斯克旗下公司最终道歉，并声称已实施额外防护措施、重新设计政策以屏蔽有害输出。",
    ),
    "Megaspeed, the company at the center of the Jensen Huang scandal, appears headed for a US blacklist": (
        "卷入黄仁勋丑闻的 Megaspeed 或被列入美国黑名单",
        "此前由 Alice Huang 领导的 Megaspeed，除非获得联邦政府颁发的特别许可，否则将被禁止与美国公司开展业务。",
    ),
    "Anthropic Launches Claude Ship to Review, Fix and Approve PRs": (
        "Anthropic 推出 Claude Ship，可审查、修复并批准拉取请求（PR）",
        "2026 年 11 月 23 日，Anthropic 推出 Claude Ship，面向使用 GitHub 仓库的 Claude Team 与企业组织开放 Beta 测试。它将已正式可用的 Code Review 与两个新的公开 Beta 智能体——PR Steward 和 Claude Approvals——结合起来，帮助拉取请求完成审查、修复与批准决策，共同解决代码写就之后的交接环节。",
    ),
    "Cisco and OpenAI launch Shirudo open-source infrastructure shield to prevent AI-driven cyberattacks": (
        "思科与 OpenAI 推出开源基础设施防护方案 Shirudo，防范 AI 驱动的网络攻击",
        "借助人工智能，网络犯罪分子已能在数秒内发现软件漏洞并加以利用。企业需要更好的自卫手段，因此全球顶尖 AI 公司之一 OpenAI Group PBC 与思科系统公司（Cisco Systems Inc.）联手推出防护方案，可谓恰逢其时。",
    ),
    "Many languages, one common neural code": (
        "众多语言，一套共通的神经密码",
        "语言有数千种形态。有些是有声调的语言，如越南语，音高的变化传达不同的含义。英语依赖精确的语序，但对俄语而言语序没那么重要——词语调换并不改变原意。尽管语言世界如此多样，MIT 的一项研究发现，人类大脑可能以某种通用的方式处理各类语言。人工智能使这一发现成为可能。在今日发表于《自然·神经科学》（Nature Neuroscience）的研究中，研究人员用多语言模型预测人脑对不同语言的反应。这些模型还帮助研究者在一共使用 21 种不同语言的人群中检测到共通的大脑处理过程。「当然，人类彼此交谈的方式存在许多差异。」",
    ),
    "Z AI Releases GLM-5.4: A 750B Loop Transformer That Runs 28 Layers Twice": (
        "Z.ai 发布 GLM-5.4：750B 循环 Transformer，28 层运行两轮",
        "Z.ai 发布 GLM-5.4，这是其首款基于循环 Transformer（Loop Transformer）架构的旗舰模型。GLM-5.4 将 GLM-5 基础模型的 28 层重复运行两轮迭代；Z.ai 称其智能水平可与 2 万亿至 3 万亿参数模型相媲美。对开发者而言，其卖点是「通用编码」（Generalized Coding）：把代码作为生成视频、游戏、3D 着色器与 CAD 的工具。要点速览——规模：750B 级基座，活跃参数未披露。上下文窗口：官方未列出（博客讨论了在 100 万上下文下的部署）。运行方式：目前仅支持 Z.ai 托管（GLM Coding Plan、ZCode、Z.ai Chat）；权重发布前不披露自托管硬件要求。性能：尚无旗舰基准表，Z.ai 声称与 2T–3T 参数模型持平；最佳成绩为 Z.ai 30B 循环消融实验中 AIME25 提升 11.3 分（19.17→30.42），最小增益为 IFBench 提升 3.3 分（50.20→53.47）。",
    ),
    "Richpanel helps companies automate 50% of support in 30 days": (
        "Richpanel 帮助企业在 30 天内实现 50% 的客服自动化",
        "Richpanel 使用 GPT-6 Astra 与 GPT-6.1 Sol 为其 AI 客服智能体配备工具与流程规范，并用 GPT-6 Luna 驱动对话。",
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    changed = added_t = added_s = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en not in FIX:
            continue
        title_zh, summary_zh = FIX[en]
        it["title_zh"] = title_zh
        it["summary_zh"] = summary_zh
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:55])
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

    print("[fix_0600_1124] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_0600_1124] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0 if changed == len(FIX) else 1


if __name__ == "__main__":
    raise SystemExit(main())
