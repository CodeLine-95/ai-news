# -*- coding: utf-8 -*-
"""2026-11-21 05:00 巡检：定稿本轮首轮抓取新增 17 条 NLLB 机翻硬伤。

沙箱恢复后 04:59 重启，首轮抓取 2501→2519（+18），其中 17 条存在
明显机翻缺陷或漏译：
- 书名误译：Corporate Ordering→「企业订单」；
- 术语错：Riemann→「里曼」、adversarial distillation→「逆境蒸/蒸活动」、
  red team→「红团」、neocloud→「新云」、hyperscaler→「超级计算器」、
  open-weights→「打开权重」；
- 品牌音译崩坏：Signal→「信号」、Spotify→「斯波地夫」、Hebbia→「希布比亚」、
  Thinking Machines Lab→「思考机实验室」、Equifax→「埃基法克斯」；
- 标题完全崩坏：「黄仁勋斯谎言警报」；
- 摘要漏译首句：Inference pushes / OpenAI extract；
- 语义崩坏：「12 个家庭中的 36 个任务」「84.5%的可用信用额度」等。

覆盖三层：news.json 回填 + JSON 覆盖表 + manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "dc1e77b7a8f3a76e3bc6373d20ea9781": (
        "伯克利法学教授、《企业秩序》作者 Stavros Gadinis——访谈系列",
        "Stavros Gadinis 是加州大学伯克利分校法学院 George R. Johnson 法学讲席教授。"
        "他的研究关注公司治理、金融监管，以及企业用于制定和监督决策的内部机制。"
        "进入学术界之前，他曾在欧洲从事公司法律业务。"
        "他的新书《企业秩序：企业如何应对社会冲突》由剑桥大学出版社出版，"
        "探讨在公共规则尚不稳定时，企业如何建立治理体系。",
    ),
    "1f2ff90a62d3e18574ab4b06ea51696b": (
        "OpenAI 推出面向药物化学推理的 MedChemBench 基准",
        "2026 年 11 月 20 日，OpenAI 推出 MedChemBench——一个包含 99 道题的药物化学基准，"
        "并报告 GPT-6.2 Astra 在 xhigh 推理强度设置下取得 84.5% 的可用分值。"
        "该基准考察模型能否将分子结构与实验证据关联起来，以解释结果、比较化合物并预测性质。"
        "其他报告的 xhigh 得分包括：GPT-6 Astra 为 83.3%、GPT-6.1 Sol 为 82.0%、GPT-5.6 Sol 为 58.2%。",
    ),
    "41000322a4017d63ed130bbd010b0765": (
        "引用 Ravi Vakil",
        "Alessandro Masullo 提出了一份广义黎曼假设的证明，Brian Conrad 数月来一直仔细研究，"
        "并给出了详尽反馈，作者正在吸收这些意见，目前看来进展良好。这项工作完全由人类完成，没有使用 AI。"
        "原本希望邀请 Alessandro 到斯坦福大学一年打磨文稿，再经足够多专家审阅后公布。"
        "现在看来，最好先发布当前这份草稿。",
    ),
    "bf3ed8de131d57c7f97eb8f379b0f384": (
        "数据层主导节奏，AI 交易周期缩短至最短 30 天",
        "人工智能已把数据基础设施从后台采购，变成决定 GPU 投资多快回本的瓶颈。"
        "随着超大规模云厂商、新兴云服务商（neocloud）和企业竞相扩展数据层，基础设施的采购方式也在快速变化。"
        "存储行业长期以来的性能专家将这一转变视为机遇。",
    ),
    "f509e696672e071432ea86627c3eb49c": (
        "AI 声称破解有 167 年历史的黎曼假设——人类也做到了",
        "数学家们被最新的 AI 驱动成果所震撼——同时还有一份人类独立给出的竞争性解答。",
    ),
    "86a531776f94955b3d6435d92406f48d": (
        "Signal 在 iOS 27 与 Android 上屏蔽截图，阻止 AI 智能体读取私人聊天",
        "Signal 正在屏蔽截图，以阻止苹果 Siri、Google Gemini 和 Meta Muse 等 AI 智能体读取私人聊天。"
        "该应用称此举是对隐私的「生存性威胁」防御，但承认其保护仍不完整，包括 macOS 平台。"
        "Apple、Google 和 Microsoft 应效仿。",
    ),
    "8ebf90d0cb99cb1ab366f612a3c5400c": (
        "黄仁勋「撒谎」令英伟达董事会在其辞职前警觉",
        "在一系列绯闻指控的背景下——包括与一名直属下属的关系，以及一名被指为中国情报机构工作的对象——"
        "消息人士告诉 WIRED，英伟达董事会的主要顾虑是这位前首席执行官「缺乏坦诚」。",
    ),
    "cc0a4dad659b5596f9be4bdfa50c4d83": (
        "Daniel Ek 投资 AI 研究员的核聚变发电初创公司，他们正在构建什么？",
        "Spotify 创始人 Daniel Ek 正在支持 Europa Fusion——一家由 AI 研究员创立的核聚变发电初创公司。"
        "以下是他们正在构建的内容。",
    ),
    "aa3529783c310a166748d93bee495f0b": (
        "推理将 AI 推向更小的站点，数据层成为决定性因素",
        "推理正在成为企业 AI 支出的重心，而 AI 数据层逐渐成为决定这些投资能否回本的关键。"
        "随着 GPU 成本攀升、零部件持续短缺，AI 背后的架构正从少数超大型设施，转向由更小站点构成的分布式网络。",
    ),
    "534199b72197f21d939d1d4e5671dd3e": (
        "METR 发现 AI 时间跨度约每 110 天翻倍，但研究判断力滞后",
        "METR 于 2026 年 11 月 20 日报告称，公开前沿模型的 50% 时间跨度——"
        "即人类估计的任务时长，模型预计在该时长内有一半概率成功，而非模型自身的运行时长——"
        "在其合并的 TH1.1 与 TH2 评估中约每 110 天翻一番。"
        "扩展后的测试显示，模型在可验证工作上进步显著，但在开放式研究与评估设计上的判断力较弱。"
        "本次更新涵盖截至 Opus 5.5 和 GPT-6 Astra 的公开模型，并考察了与自动化 AI 研发（R&D）相关的能力。"
        "METR 通常在 TH1.1 和 TH2 上评估 15 个模型。新的 TH2 套件包含 12 个类别共 36 项任务："
        "其中 8 个类别目标明确、可自动评分，涵盖优化、机器学习、谜题和游戏；"
        "另有 4 个类别涉及概念推理、判断和开放式研究，缺乏低成本的成功判定标准。",
    ),
    "7a9ffd333d0ce4e6279fbfc39993c7d0": (
        "OpenAI 令攻击者更难套取其最新 AI 模型的内部推理方式",
        "OpenAI 大幅强化了对从 GPT-6.2 Astra 和 GPT-6.2 Sol 中提取内部推理的防护。"
        "在自适应红队测试中，提取受保护推理的成功率从 54% 降至 0.2%。"
        "该公司还每周暂停数千至数万个账户，以打击协同的蒸馏攻击活动。",
    ),
    "e7053c269fcf83d77626df2212568f8b": (
        "OpenAI 强化 GPT-6.2 Astra，抵御推理提取攻击",
        "OpenAI 于 2026 年 11 月 20 日宣布加强对对抗性蒸馏的防御。"
        "据其报告，针对历史请求提取受保护推理的自适应攻击平均成功率，"
        "从采用原有防护的 GPT-6 Astra 上的 54.0%，降至采用更新防护的 GPT-6.2 Astra 上的 0.2%；"
        "针对当前请求的提取，相应平均水平从 22.9% 降至 0.9%。",
    ),
    "25c639903f75ecbf3b1e365a2d533d25": (
        "Thinking Machines Lab 发布面向本地设备的 Inkling 2 Mini",
        "Thinking Machines Lab 于 2026 年 11 月 20 日发布 Inkling 2 Mini——"
        "一款为消费级笔记本电脑打造的开放权重模型。它拥有 264 亿个总参数，内存占用约 20GB，"
        "通过反复经过其中间层来提升推理能力。"
        "Inkling 2 Mini 及配套研究模型 TML-d24-varloop-research 的完整权重已在 Hugging Face 上开放。",
    ),
    "02e3b23adb134d28a8a071c598a5f955": (
        "Equifax 将计费系统迁至 AWS 上的 Oracle 后，减少数据库「救火」工作",
        "多云战略曾意味着要决定哪些工作负载放在哪家服务商。如今数据库服务商正进驻客户已在使用的云平台，"
        "而 AI 项目把这些迁移的价值提升到远超后台办公的层面。Equifax 便是一个例子。",
    ),
    "7121ba7c91734ceb0344baecd70fc9c4": (
        "对抗对抗性蒸馏",
        "OpenAI 应对对抗性蒸馏的分层方案，结合了模型训练、安全防护、检测与执法，以防止模型能力被提取。",
    ),
    "c2d364619a44697410420c90aa43adfb": (
        "Hebbia 称 GPT-6 Astra 提升了金融研究表现",
        "Hebbia 测试了 GPT-6 Astra 在金融研究中的应用。"
        "其发布前评估发现，模型在来源覆盖面、引用相关性和表述质量上均有提升。",
    ),
    "3c753634dc1f4ee5d5fd7d3ce70865cd": (
        "AI 能否帮助科学家识别有前景的候选药物？",
        "MedChemBench 评估 AI 模型解读分子结构、基于实验证据推理，以及在早期药物发现阶段筛选化合物的能力。",
    ),
    "67ba182be7f4477cddfdfa8060cfbcd2": (
        "问答：让多模态基础模型实现更像人类的互动与理解",
        "人类通过感官信息体验世界并与世界互动。这可能意味着学习鸟鸣声与「知更鸟」一词之间的对应关系，"
        "或是在人群中凭视觉识别并跟上朋友「Sarah」。许多情况下，人们能够调用潜在的「多模态」知识——"
        "横跨音频、视频、文本或言语等多种数据类型的信息——在很少甚至没有任何示例的情况下完成这些任务。"
        "人工智能的多模态基础模型正越来越多地获得模仿这一点的能力，然而它们表面上流利的多模态表现，"
        "往往掩盖了实际理解能力的不足。",
    ),
    "718dc2db66a106fb86a93a474a3db287": (
        "漏洞百出的 AI 供应链正以惊人速度泄露用户机密数据",
        "研究人员在经由庞大 AI 服务网络发送的请求中植入了 200 万个数字「诱饵」，"
        "以追踪托付给这些服务的敏感信息究竟发生了什么。结果发现，这个生态系统如同筛子一般"
        "泄漏高度敏感的数据。这一暴露是通过一项巧妙实验发现的，旨在测试敏感信息是否会经由"
        "广泛使用的 AI 服务所构成的庞大链条泄露，以及一旦泄露会如何被利用。"
        "如今许多 AI 应用使用 OpenRouter 或 Vercel 之类的服务充当中介。这些「AI 路由器」"
        "（有时也称「AI 网关」）接收 AI 应用终端用户发送的大量提示，并根据价格最低或最适合当前任务等标准，"
        "将其路由到可用的推理引擎。",
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
        print("fixed:", it.get("date"), it.get("time"), en[:55])

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_0500_newitems] news.json 回填 %d 条" % changed)
    print("[fix_0500_newitems] 覆盖表 %d 标题 / %d 摘要" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
