# -*- coding: utf-8 -*-
"""2026-11-24 01:00 例行巡检：定稿本轮新增 10 条 NLLB 机翻硬伤。

整点调度补抓 00:11-00:59 共 10 条，均为 nllb 机翻，主要问题：
1) Google DeepMind：formal verification 误作「正式验证」（应为形式化验证）、
   fusion and chemistry 误作「合和化学」（fusion=核聚变）；
2) TechCrunch Huang：out of the woods 习语直译「走出森林」（应为脱离困境）、
   摘要语义完全崩坏；
3) Unite.AI Elhalwagy：访谈系列漏译、Brunel 误作「布朗尔」；
4) Unite.AI Anthropic Options：Anthropic 词根误译为「人类」（首当其冲的硬伤）、
   IPO 误作「首次公开投标」、摘要尾部分析商名错乱；
5) TechCrunch Trump：called into 误作「召开」（应为致电参会）、
   Huang 误作「黄」、摘要「。.。」标点乱码；
6) Unite.AI Miovision：after a hurricane 误作「风后」；
7) Unite.AI AIVC：品牌名 AIVC 音译为「艾维奇」、「携资金成立」语义残缺；
8) Unite.AI DXL：big-and-tall 服装术语误作「大尺度」、
   commercetools 误作「商业工具」、in-agent checkout 误作「智能体登记」；
9) The Verge Tech leaders：摘要语义崩坏（中国间谍/两名下属/马斯克推文）；
10) Unite.AI Yanpei Cao：中文名被截成「佩博士」、
    volumetric capture 误作「大小捕获」、Tencent/Kuaishou 未统一译名。

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
    "39d193b8654c5d0a79e1ae8b39f90957": (
        "用智能体与形式化验证发现更快的量子算法",
        "研究团队利用智能体团队与形式化验证方法，改进面向核聚变与化学问题的量子算法。",
    ),
    "236394fc670236c22905adc0297ea27a": (
        "黄仁勋尚未脱离困境",
        "可以说，没人料到这一幕。周一上午，黄仁勋在因多段婚外情丑闻辞职后重新出任英伟达 CEO——这些丑闻包括与一名下属、以及一名被指与中国情报部门有关联的女子的关系。",
    ),
    "352d1c17bdcfae15923febaaf490c706": (
        "RootCause.ai 联合创始人兼 CEO 艾曼·埃尔哈瓦吉博士——访谈系列",
        "艾曼·埃尔哈瓦吉博士是 RootCause.ai 的联合创始人兼 CEO，拥有计算机工程、机器状态监测与应用 AI 背景。他在布鲁内尔大学的博士研究专注于数据集合并及机械设备监测。此后他创立了 AI 咨询公司 Numvio，在与企业数据和预测系统的工作中逐渐转向因果模型研究——这类模型可解释业务结果并辅助决策。",
    ),
    "55d795c6b6a2a1d4edaea3978c67229b": (
        "Anthropic 期权上市首小时成交约 16 万份合约",
        "路透社 2026 年 11 月 23 日报道，约 16 万份 Anthropic 期权合约在当天上市首小时内换手。这一新上市的期权工具，让投资者在该公司 IPO 后得以对冲其股价或建立投机头寸。据一家期权分析服务商提供的数据，首日活跃成交使 Anthropic 跻身期权市场交易最活跃的 25 只标的之列。",
    ),
    "a3bc43bbd8d570f9177d279300a0c2a6": (
        "据报道，特朗普致电英伟达董事会会议，力挺黄仁勋回归",
        "「我和他们通过了话，这么说吧……我说服了他们。」特朗普总统告诉 CNBC。",
    ),
    "160f5de2b124bc6aa84f3fd53bdd298d": (
        "埃斯坎比亚县如何借助 Miovision 的 AI 调查交通信号投诉",
        "Miovision 表示，其 AI Studio 帮助埃斯坎比亚县在 5 分钟内梳理完信号投诉，并在一场飓风过后优先安排了对 343 部摄像头的检查。",
    ),
    "faca37debb4e473d54db650c920fb71d": (
        "AIVC 携 1.12 亿美元成立，将企业 AI 项目孵化为公司",
        "AIVC 计划将其 1.12 亿美元战略资金中的大部分投入一家创业工作室，围绕其企业团队已着手解决的问题来孵化公司。",
    ),
    "fed0e9070585476f692ad52e0a81f87f": (
        "DXL 将大码男装搜索引入 Meta 的 Muse 购物智能体",
        "DXL 正通过 Meta 的 AI 购物智能体，让旗下美国服装目录可被搜索到，商品数据来自 commercetools 提供的结构化信息流。此次上线暂不支持在智能体内直接结账。",
    ),
    "8286b401401be26c18b0b17be8090b42": (
        "科技领袖们庆贺黄仁勋回归",
        "设想你是黄仁勋：你（据称）与一名疑似中国间谍的女子一起欺骗了妻子，据称还不止与一名、而是与两名下属发生婚外情，并（据称）「恐吓」员工——这一连串不端行为让你丢掉了曾是全球市值最高公司的 CEO 职位。（股价近来因显而易见的原因大幅下挫。）如今你回来了——而所有朋友都想为你庆贺。埃隆·马斯克率先表态：很高兴，错误得到了纠正。",
    ),
    "66d2a9589c7e05c66d4f1e8e78f3e63a": (
        "Yanpei Cao 博士，VAST 联合创始人兼首席科学家——访谈系列",
        "Yanpei Cao 博士是 VAST 的联合创始人兼首席科学家，负责领导生成式 3D 与交互式世界模型的研究和技术方向。他在清华大学获得博士学位，长期从事计算机图形学、3D 重建与沉浸式内容创作。加入 VAST 前，他曾任腾讯首席研究员，并联合创立了体积视频捕捉公司 Owlii，后者被快手收购。",
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

    print("[fix_0100_1124] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_0100_1124] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0 if changed == len(FIX) else 1


if __name__ == "__main__":
    raise SystemExit(main())
