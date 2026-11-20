# -*- coding: utf-8 -*-
"""2026-11-21 00:00 巡检：本轮新增 5 条中 4 条 NLLB 机翻硬伤人工定稿。

1) Bloomberg —— 标题/摘要「博」「博新闻」为 Bloomberg 截断错译。
2) Riemann/Lean —— 「里曼」应为黎曼、「利安/利恩代码」应为 Lean 代码、
   「人类数学家」错译 Anthropic mathematician。
3) Anthropic Slides —— 标题「人类幻灯片延长损失」语义完全崩坏。
4) mathocalypse —— 标题「马托克利普斯」音译生硬，改为「数学末日」。

三层覆盖：news.json 回填 + JSON 覆盖表 + (regen) manual_overrides.py。
"""
import json
import os
import report

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
N_JSON = os.path.join(BASE, "data", "news.json")

# (id, 定稿中文标题, 定稿中文摘要 或 None 表示沿用原摘要)
FIXES = [
    ("dc35ccef307691db1e982b8abfb8423b",
     "彭博社对 1000 万份招聘信息的分析显示，中国受 AI 影响的岗位下降速度比其他岗位快 10 个百分点",
     "彭博新闻社对 1000 万份招聘信息的分析显示，AI 正在加剧中国本已疲软的劳动力市场。入门级从业者与创意产业受到的影响最为明显——目前超过 90% 的中国微短剧已使用 AI 制作。前央行顾问蔡昉警告称，AI 带来的更大冲击仍将到来。"),
    ("f664cfc01128e72519a58ff517405ce8",
     "莱文特·阿尔波格未经证实的黎曼猜想主张，让 Claude 的 Lean 代码成为焦点",
     "2026 年 11 月 20 日，莱文特·阿尔波格表示，他认为自己与 Claude 发现了黎曼猜想的证明，以及解决广义黎曼猜想的方法。Anthropic 的数学家发布了一份个人声明，附上相关 Lean 代码链接，但并未给出对这一完整论证的独立验证。阿尔波格也是哈佛大学学会的会员。"),
    ("6905ae3a85e8fe5fc1f0ab537dcfc99d",
     "Anthropic 上市首日股价下跌，AI 类股票延续跌势",
     "据路透社 2026 年 11 月 20 日报道，Anthropic 股价在纳斯达克上市后回落，拖累美股低开：纳斯达克综合指数开盘下跌 286.5 点（1.20%），报 23592.669 点；标普 500 指数下跌 25.4 点（0.35%），报 7150.39 点；道琼斯工业平均指数下跌 25.2 点（0.05%），报 49071.82 点。Anthropic 最新价报 88.24 美元，较 11 月 19 日收盘价低约 9%。大型科技股普跌表明，这次上市几乎未能扭转更广泛的市场抛售。"),
    ("9419bc7490ad3f83b9fb9d4b2c6d0ef9",
     "「数学末日」之后，数学家们思考未来",
     None),
]


def main():
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(N_JSON, encoding="utf-8"))
    by_id = {it["id"]: it for it in news["items"]}

    ok = 0
    for iid, zh_t, zh_s in FIXES:
        it = by_id.get(iid)
        if not it:
            print("[WARN] id 未找到:", iid)
            continue
        en = (it.get("title") or "").strip()  # 直接取自数据，避免引号字符手抄错误
        titles[en] = zh_t
        if zh_s is not None:
            summaries[en] = zh_s
        it["title_zh"] = zh_t
        if zh_s is not None:
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
