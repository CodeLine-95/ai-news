# -*- coding: utf-8 -*-
"""2026-11-02 00:00 例行巡检 —— 人工核对标题定稿（增量）。

来源：独立审查代理对全库 258 条的增量抽检（重点 2026-10-31 及之后的
最新条目 53 条 + 早期随机抽样 25 条），再由主流程逐条复核英文原文后定稿。
本轮共修复标题 14 处，问题类型：
    · 语义崩坏（否定/施受倒置、成分残缺、指代错位）
    · 术语与专名误译（首批 vs 首个、physical AI 双译、NVIDIA/英伟达不统一、
      教宗/教皇称谓不统一、misalignment 生造词）
    · 语序混乱与介词缺失

键为英文原标题（与既有覆盖表同构，server.py 以英文标题做匹配）。
"""

TITLE_OVERRIDES = {
    # 语义崩坏：「宗教豁免」被译成「禁止使用 AI」，含义完全倒置
    'You don’t need to believe in a god to get a religious exemption from using AI at work':
        '你不必信教，就能获准在工作中免于使用 AI',
    # 术语：first wave/features = 首批功能，非「首个功能」
    'Apple Brings First Apple Intelligence Features to China in iOS 27.3':
        'Apple 在 iOS 27.3 中将首批 Apple Intelligence 功能带到中国',
    # 术语：Autodox/doxxing 双关需保留「人肉」含义；Infostealer 统一本地化为「信息窃取」
    'Spooky New Infostealer Malware Uses AI to ‘Autodox’ Victims':
        '诡异的新型信息窃取木马用 AI「人肉」受害者',
    # 术语：教宗称谓统一为「十四世」；「为 AI 解除武装」是硬译
    'Pope Leo XIV Calls to “Disarm” AI, Urges Ban on Lethal Autonomous Weapons':
        '教宗利奥十四世呼吁「解除」AI 的武装，敦促禁止致命自主武器',
    'Pope Leo calls for the disarmament of AI: ‘Machines are tools, not persons’':
        '教宗利奥十四世呼吁解除 AI 的武装：「机器是工具，而非人」',
    # 术语：misalignment = 对齐失配，「对齐偏离」为生造词
    'How we detect frontier model misalignment':
        '我们如何检测前沿模型的对齐失配',
    # 语序：介词缺失，「在 iOS 27.3 带到中国」不通
    'Apple Intelligence is finally coming to China with iOS 27.3':
        'Apple Intelligence 终于将随 iOS 27.3 带到中国',
    # 术语：全库其余 117 处均用 NVIDIA，仅此条用「英伟达」
    'Nvidia weighs playing the cosigner for Nscale’s AI data center in West Virginia':
        'NVIDIA 考虑为 Nscale 位于西弗吉尼亚州的 AI 数据中心担任联合担保方',
    # 语序：at the drive-thru 修饰「展示」的位置，原译搭配不通
    'Starbucks wants to use AI to show you a ‘personalized digital menu’ at the drive-thru':
        '星巴克希望利用 AI，在得来速通道向你展示「个性化数字菜单」',
    # 语序：同位语结构断裂，「注重用户隐私的 Ollie 其创始人」不成句
    'Ollie, a privacy-focused AI assistant, is shutting down':
        '注重保护用户隐私的 AI 助理 Ollie 即将关停',
    # 语义：漏译标题中的 to scale（推动业务规模化）
    '4 days left: How TechCrunch Founder Summit helps you make more useful connections to scale':
        '倒计时 4 天：TechCrunch 创始人峰会如何帮你建立更有价值的连接，推动业务规模化',
    # 语序：同位语误译为定语谓语
    'OpenAI to Honor Shared Robots.txt Signal for AI Training Preferences':
        'OpenAI 将遵循 robots.txt 中的共享信号以表达 AI 训练偏好',
    # 术语：math onslaught = 数学攻势，非「数学攻击」
    'Sam Altman sympathizes with mathematicians, but says OpenAI’s math onslaught won’t stop':
        '萨姆·阿尔特曼同情数学家，但称 OpenAI 的数学攻势不会停止',
}
