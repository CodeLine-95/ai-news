# -*- coding: utf-8 -*-
"""01 点巡检第二轮：refresh 新抓取 4 条机翻硬伤人工定稿。"""
import json
import os
import report

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
N_JSON = os.path.join(BASE, "data", "news.json")

# (id, 英文原标题, 定稿中文标题, 定稿中文摘要)
FIXES = [
    ("ff78c8d3e8b6214ef085b08e50e7fbd1",
     "Anthropic Shares Indicated to Open 33% Above IPO Price in Nasdaq Debut",
     "Anthropic 股票预计以高于 IPO 价 33% 开盘，登陆纳斯达克",
     "路透社于 2026 年 11 月 19 日报道，Anthropic 的 A 类股票预计以 110.50 美元开盘，较其 83 美元的 IPO 发行价高出 33%。随着这家 Claude 开发商在纳斯达克首秀，它成为首家上市的前沿 AI 公司。截至美国东部时间上午 11:38 的这一报价只是指示性价格，并非已完成的开盘交易。按此价格计算，Anthropic 市值有望达到 2 万亿美元。"),
    ("bd72c3200d90bc308bdfcefa6d02e9b6",
     "Former Alibaba exec’s Everful raises $48.5M to connect retailers with Chinese factories",
     "前阿里巴巴高管创办的 Everful 融资 4850 万美元，连接零售商与中国工厂",
     "Everful 已融资 4850 万美元，用于扩展其工厂直采平台，帮助零售商从海外制造商直接采购产品。"),
    ("fde7b4eb645067e3d990e8931dfc8001",
     "Google Built a Giant ‘Mirror Dimension’ Internet to Test Its Chrome AI Agents",
     "Google 打造庞大「镜像维度」互联网，用于测试 Chrome AI 智能体",
     "该公司的「平行宇宙」互联网充当一个巨型沙箱，使 Chrome 团队能够在其中妥善训练 AI 浏览智能体，而不必担心它们失控（go rogue）。"),
    ("9449e0229f73eac5f6b7e7a5524832ec",
     "Chinese tech firms face a double hit as chip shipments stop and overseas cloud access disappears",
     "芯片出货中断、海外云访问消失，中国科技公司面临双重打击",
     "美国对 AI 芯片的出口管制收紧正迅速产生影响。中国的月之暗面（Moonshot AI）退出了在印度尼西亚的一笔 1.5 亿美元交易，台积电（TSMC）和三星也已停止向中国客户出货。《纽约时报》的调查发现，阿里巴巴通过一个空壳公司网络，将英伟达（Nvidia）芯片转交给了中国军方研究人员。"),
]


def main():
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(N_JSON, encoding="utf-8"))
    by_id = {it["id"]: it for it in news["items"]}

    ok = 0
    for iid, en, zh_t, zh_s in FIXES:
        titles[en] = zh_t
        summaries[en] = zh_s
        it = by_id.get(iid)
        if not it:
            print("[WARN] id 未找到:", iid)
            continue
        it["title_zh"] = zh_t
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
