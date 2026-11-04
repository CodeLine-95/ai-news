"""2026-11-03 07:00 巡检：人工定稿本轮修复的条目。

本轮修复的三类根因（均已回写 translate.py / fetcher.py）：

1) 重复字折叠规则误伤「能力」
   「智能能力」被折成「智能力」（_fold_dup 把「能能」当成翻译重复）。
   已修 _DUP_KEEP_NEXT 白名单。

2) Anthropic 在句首被意译成「人类」
   "Anthropic warns that ..." → 「人类警告说」。
   已加 _fix_anthropic_subject（按句首主语位置还原，不误伤正文里的「人类」）。

3) 财报术语直译
   gross margin → 「总利率」、diluted EPS → 「股票均利率」、
   net income → 「净收入」、AI doomers → 「人工智能毁灭者」。
   已加对应 TERM_FIXES。

另修了 fetcher 的 Unite.AI 正文兜底（RSS 与 og:description 均被源站
按字符数截断在 "$27." 这种半截数字处，只能取正文前两段补全），
并补全了 5 条存量条目的英文原文。

以下为仍需人工定稿的部分（模型直译语义或语序崩坏）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    # 原文："Apple Posts 12% Revenue Growth as iPhone and Services Set Records"
    # 直译「Apple 发布了 12%的收入增长作为 iPhone 和服务设置纪录」——
    # "as" 在这里是「同时/伴随」而非「作为」，"Set Records" 是「创下纪录」。
    "Apple Posts 12% Revenue Growth as iPhone and Services Set Records":
        "Apple 营收增长 12%，iPhone 与服务业务双双创下纪录",
    # 原文："Anthropic warns that it's very close to RSI capability, aka self-building AI"
    # 直译「人类警告说，它非常接近 RSI 能力，也就是自建 AI」——
    # Anthropic 被意译成「人类」（术语规则已修，此处再定稿兜底）。
    "Anthropic warns that it’s very close to RSI capability, aka self-building AI":
        "Anthropic 称其已非常接近 RSI 能力，即自我构建 AI",
    # 原文："Trajectory raises $45M to make AI model training accessible to nontechnical experts"
    # 直译「轨迹筹集了 4500 万美元，使 AI 模型培训可用于非技术专家」——
    # Trajectory 是公司名（被意译成「轨迹」），且 "make X accessible to Y"
    # 被译成「使 X 可用于 Y」，语义走了样。
    "Trajectory raises $45M to make AI model training accessible to nontechnical experts":
        "Trajectory 融资 4500 万美元，让非技术专家也能用上 AI 模型训练",
}

SUMMARY_FIX = {
    # 原文："The one-year-old startup is now valued at $300 million."
    # 直译「这家一年的初创公司现在估值为 3 亿美元」——
    # "one-year-old" 是「成立一年」，不是「一年的初创公司」。
    "Trajectory raises $45M to make AI model training accessible to nontechnical experts":
        "这家成立仅一年的初创公司目前估值 3 亿美元。",
    # 原文摘要：Apple 公布 FY2026 Q4 财报，营收 1145 亿美元同比增 12%，
    # 摊薄每股收益 2.10 美元增 14%，毛利率 47.9%，净利润 307 亿美元。
    # 直译把 gross margin 译成「总利率」、diluted EPS 译成「股票均利率」，
    # 且「净收入为 307 亿美元，而去年为 275 亿美元」与原文语义有偏差。
    "Apple Posts 12% Revenue Growth as iPhone and Services Set Records":
        "Apple 于 2026 年 11 月 2 日公布 2026 财年第四季度业绩："
        "截至 2026 年 9 月 26 日的季度营收 1145 亿美元，同比增长 12%；"
        "摊薄每股收益 2.10 美元，同比增长 14%。"
        "毛利率为 47.9%，其中包含关税退款带来的约 1 个百分点正面影响；"
        "摊薄每股收益中同样包含 0.05 美元的退款利好。"
        "净利润为 307 亿美元，上年同期为 275 亿美元；"
        "营业利润为 356 亿美元，上年同期为 324 亿美元。",

    # RSI 是 AI 自我训练导致的递归式能力跃升临界点。
    # 直译「它产生了人工智能力的大幅加速」（折叠规则把「智能能力」折坏，
    # 术语规则已修）、「对于人工智能毁灭者来说」（doomers 直译，
    # 术语规则已修），此处再定稿兜底。
    "Anthropic warns that it’s very close to RSI capability, aka self-building AI":
        "RSI 是指 AI 在自我训练上变得足够强，进而引发 AI 能力急剧跃升的那个临界点。"
        "在 AI 悲观论者看来，RSI 代表着无法回头的灾难。",

    # 原文：ChangXin Technology Group（CXMT）2026 Q3 财报。
    # 模型直译把 "as printed in its quarterly report"（按季报原文口径）
    # 译成「按印刷量上升」「按印刷情况」，语义崩坏；
    # "weighted average return on equity" 译成「股票回报率」也不准确。
    "CXMT Q3 Revenue Rises 613% as DRAM Shortage Swings It to Profit":
        "长江存储（CXMT）2026 年第三季度营收 1187.1 亿元人民币，"
        "同比增长 613.18%（按季度报告所载口径），"
        "归属于股东的净利润为 544.3 亿元人民币。"
        "归属于股东的净利润本季度为 544.3 亿元；"
        "扣除非经常性损益后为 552.4 亿元，同比增长 4070.56%（按季报所载口径），"
        "季报对未调整口径的归母利润同比变动标注为不适用。"
        "本季度基本每股收益为 0.8376 元人民币，加权平均净资产收益率为 26.74%，"
        "利润总额为 990.4 亿元人民币。"
        "环比看，公司称第三季度营收较上一季度增长约 19.30%，"
        "净利润约 889.8 亿元人民币，同比增长约 19.38%，"
        "毛利率约 89.53%，较上一季度提升约 1.94 个百分点。",

    # 原文：全球每年约 40 亿份纸质文件流通，仅 1% 已数字化。
    # 直译「只有 1%是数字化的」缺主语、「11.97 亿美元的资金尚未获得」
    # 把"11.97 billion documents"（119.7 亿份文件）误译成「亿美元的资金」。
    "Critically, Enterprise Agents Don’t Understand Highlighting":
        "全球范围内有大量重要但尚未扫描的纸质文件，商业领域尤其严重。"
        "据估计，每年经由全球贸易流转的 40 亿份纸质文件中，"
        "仅 1% 已完成数字化，其余部分超出机器学习的分析能力。"
        "这还只是商业领域问题的粗略评估；"
        "各国政府同样产出大量纸质材料。"
        "美国国家档案馆今年报告称，其馆藏模拟文档中仅 4.04% 已数字化，"
        "仍有 119.7 亿份文件有待处理。",
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
            print("fix title:", it["date"], it["time"], it["source"], "|", t[:56])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_s += 1
            print("fix summary:", it["date"], it["time"], it["source"])

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
