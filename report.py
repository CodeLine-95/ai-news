"""从 data/news.json 生成简洁的 Markdown 摘要报告。

结构：
  - 顶部速览（条数 / 天数 / 更新时间）
  - 热点议题（由标题词频 + 议题归一化统计得出，反映 AI 走向）
  - 按天分组（日期格式 YYYY-MM-DD + 星期），每条标注时间（精确到分）与来源
  - 英文条目的中文译文为主，括注原文标题，可回看原文
"""
import json
import os
import re
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
OUT_FILE = os.path.join(BASE, "AI资讯摘要.md")

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# 停用词：英文虚词 + 泛用词（AI 本身信息量低）
STOPWORDS = set(
    """
    the a an and or for to of in on at by with from is are was were be been being
    this that these those it its as new now how why what who when where which
    has have had will would can could should may might must said says say just
    more most less than then there their they them our your you we us not but if
    into over under about after before between during while without within
    ai using use used uses make makes made get gets got go goes going
    first second next last latest best better good great big small
    """.split()
)

# 议题归一化：把同义/相关词合并到统一话题，便于聚合统计
TOPIC_ALIASES = {
    "agent": "AI Agent", "agents": "AI Agent", "agentic": "AI Agent",
    "model": "大模型", "models": "大模型", "llm": "大模型", "llms": "大模型",
    "chatbot": "AI 搜索", "reasoning": "推理模型",
    "openai": "OpenAI", "gpt": "OpenAI", "chatgpt": "OpenAI",
    "anthropic": "Anthropic", "claude": "Anthropic",
    "google": "Google", "gemini": "Google", "deepmind": "Google",
    "nvidia": "NVIDIA", "microsoft": "微软", "meta": "Meta",
    "apple": "苹果", "amazon": "亚马逊", "tesla": "特斯拉",
    "chip": "芯片", "chips": "芯片", "gpu": "芯片", "gpus": "芯片",
    "semiconductor": "芯片", "silicon": "芯片",
    "robot": "机器人", "robots": "机器人", "robotics": "机器人",
    "open": "开源", "opensource": "开源",
    "funding": "融资", "raises": "融资", "raised": "融资", "valuation": "融资",
    "series": "融资", "billion": "融资",
    "acquisition": "并购", "acquires": "并购", "acquired": "并购", "buys": "并购",
    "layoff": "裁员", "layoffs": "裁员",
    "regulation": "监管", "regulatory": "监管", "policy": "监管",
    "safety": "AI 安全", "alignment": "AI 安全", "risk": "AI 安全",
    "datacenter": "数据中心", "compute": "数据中心",
    "coding": "AI 编程", "code": "AI 编程", "developer": "AI 编程",
    "software": "AI 编程",
    "enterprise": "企业应用", "business": "企业应用",
    "startup": "创业公司", "startups": "创业公司", "founder": "创业公司",
    "healthcare": "医疗 AI", "medical": "医疗 AI", "health": "医疗 AI",
    "drug": "医疗 AI", "science": "科研 AI", "research": "科研 AI",
    "browsing": "AI 搜索", "search": "AI 搜索",
    "video": "生成式视频", "image": "生成式图像", "multimodal": "多模态",
    "voice": "语音 AI", "audio": "语音 AI", "music": "语音 AI",
    "inference": "推理优化", "quantization": "推理优化",
}


def clip_summary(summ, limit=200):
    """按句边界截断摘要，避免在词中间硬切（如「经营目…」）。

    策略：优先在句末标点处切，其次退到逗号/顿号处，都没有才硬切。
    """
    summ = summ.strip()
    if len(summ) <= limit:
        return summ
    head = summ[:limit]
    # 句末标点（优先全角）。注意 str.rfind 传多字符是按「子串」匹配，
    # 必须逐字符找最靠右的位置。
    for marks in ("。！？!?", "；;，,、 "):
        best = -1
        for ch in marks:
            i = head.rfind(ch)
            if i > best:
                best = i
        if best > limit * 0.5:
            cut = head[: best + 1] if marks != "；;，,、 " else head[:best]
            cut = cut.rstrip()
            # 已在完整句子末尾收尾时不再加省略号
            if cut.endswith(("。", "！", "？", "!", "?", "…")):
                return cut
            return cut + "…"
    return head.rstrip() + "…"


def weekday_of(date_str):
    from datetime import date

    y, m, d = map(int, date_str.split("-"))
    return WEEKDAYS[date(y, m, d).weekday()]


def extract_topics(items, top_n=8):
    """从标题中提取议题关键词，按出现次数排序。"""
    counter = Counter()
    for it in items:
        seen = set()
        for w in re.findall(r"[A-Za-z][A-Za-z'\-]{1,}", it.get("title", "").lower()):
            if w in STOPWORDS or len(w) < 2:
                continue
            topic = TOPIC_ALIASES.get(w)
            if topic and topic not in seen:
                counter[topic] += 1
                seen.add(topic)
    return counter.most_common(top_n)


def summarize_day(items, limit=3):
    """挑选当天最具代表性的条目。

    评分依据：标题信息密度 + 摘要完整度 + 是否命中热议议题 + 来源权重
    + 硬新闻信号（并购/融资/监管/裁决/裁员/重大发布/大额金额）
    - 软内容信号（观点/对比/教程/预测）。

    2026-11-02 巡检发现：原实现只看信源权重与篇幅，导致「重点」被
    权重高的媒体上的观点稿/对比稿占据——2026-11-02 当天最重大的
    26 亿美元并购（Unite.AI）反而落选，而 Unite.AI/IEEE Spectrum AI/
    InfoQ AI/Google DeepMind/NVIDIA Blog/ML Mastery 这 6 个信源因未在
    权重表内，全部按默认权重 1 计分，重大新闻被系统性低估。
    故补齐权重表，并引入硬/软内容信号纠偏。
    """
    # 高影响力信源（更有"重点"价值）；未列出的信源按默认权重 1 计分
    source_weight = {
        "TechCrunch": 3, "The Verge": 3, "Ars Technica": 3, "MIT Tech Review": 4,
        "Wired": 2, "VentureBeat": 2, "Google Blog": 3, "OpenAI": 3, "Marktechpost": 1,
        # 补齐原先遗漏的信源：这些源常首发并购/融资/安全等硬新闻，
        # 此前按默认权重 1 计分，导致其重大条目被高权重媒体的观点稿挤掉。
        "Unite.AI": 2, "IEEE Spectrum AI": 2, "InfoQ AI": 2,
        "Google DeepMind": 3, "NVIDIA Blog": 2, "ML Mastery": 1,
    }
    # 硬新闻信号：命中即加分（并购/资本运作 > 监管司法 > 安全事故 > 产品发布）
    hard_signals = [
        (r"收购|并购|入股|控股|融资|募资|IPO|上市|估值", 30),
        (r"禁令|禁运|出口管制|诉讼|判决|裁决|起诉|反垄断|监管|合规|处罚|调查", 26),
        (r"裁员|关闭|停服|破产|泄露|漏洞|入侵|攻击|事故|宕机", 24),
        (r"亿美元|十亿美元|万亿美元|\$\d|\d+\s*billion", 22),
        (r"发布|推出|上线|开源|首个|首次|正式|旗舰|升级为", 16),
    ]
    # 软内容信号：命中即减分（观点/对比/教程/预测类，命中任一即扣）
    soft_signals = [
        (r"我建|我写|我的|笔记|随笔|感想|体会|心得|杂谈|碎碎念", 22),
        (r"对比|相比|评测|盘点|榜单|汇总|回顾|综述|合集|清单", 20),
        (r"如何|怎么|为什么|哪些|是否|能否|该不该|值得|探讨|怎么看", 18),
        (r"预测|展望|未来会|将会|也许|下一个|十年后", 12),
    ]
    # 当日出现频次最高的议题（这些属于"重点"）
    day_topics = {t for t, _ in extract_topics(items, top_n=6)}

    def score(it):
        t = (it.get("title_zh") or it.get("title") or "").strip()
        s = (it.get("summary_zh") or it.get("summary") or "").strip()
        score = source_weight.get(it.get("source"), 1) * 12
        score += min(len(t), 120) / 6
        score += min(len(s), 260) / 12
        # 命中热议议题的条目优先
        tl = t.lower()
        for topic in day_topics:
            key = topic.lower().replace(" ", "")
            if key and key in tl.replace(" ", ""):
                score += 25
                break
        # 硬新闻加分：只取最强的一档信号，避免多项叠加压过所有其他因素
        for pat, w in hard_signals:
            if re.search(pat, t):
                score += w
                break
        # 软内容减分：同样只取最强一档
        for pat, w in soft_signals:
            if re.search(pat, t):
                score -= w
                break
        return score

    ranked = sorted(items, key=score, reverse=True)
    return ranked[:limit]


def main():
    if not os.path.exists(DATA_FILE):
        print("无数据文件")
        return
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    groups = defaultdict(list)
    for it in items:
        groups[it["date"]].append(it)

    dates = sorted(groups.keys(), reverse=True)
    last_update = (data.get("last_update") or "")[:16].replace("T", " ")

    # 翻译覆盖率统计
    en_items = [it for it in items if it.get("lang") == "en"]
    zh_items = [it for it in items if it.get("lang") == "zh"]
    translated = sum(
        1 for it in en_items if it.get("translated") and it.get("title_zh") != it.get("title")
    )
    cover = (translated / len(en_items) * 100) if en_items else 100.0

    L = []
    L.append("# AI 领域重点资讯摘要\n")
    L.append(
        f"> 共 **{len(items)}** 条 · 覆盖 **{len(dates)}** 天 · 最后更新 **{last_update}**\n"
    )
    L.append(
        f"> 英文资讯已译为中文（括注原文标题），翻译覆盖率 **{cover:.0f}%**"
        f"（{translated}/{len(en_items)} 条英文，另有 {len(zh_items)} 条中文原文）；\n"
        "> 数据每小时自动抓取，网站同步更新，无需手动触发。\n"
    )

    topics = extract_topics(items)
    if topics:
        chips = " · ".join(f"**{name}** {cnt}" for name, cnt in topics)
        L.append(f"\n## 热点议题\n\n{chips}\n")

    for date in dates:
        day_items = groups[date]
        wd = weekday_of(date)
        L.append(f"\n## {date}（{wd}）· {len(day_items)} 条\n")

        key = summarize_day(day_items)
        if key:
            L.append("**当日要点**\n")
            for it in key:
                t = it.get("title_zh") or it.get("title", "")
                L.append(f"- `{it['time']}` **{t}** — *{it['source']}*")
            L.append("")

        L.append("**全部资讯**\n")
        for it in day_items:
            title_en = it.get("title", "")
            title_zh = it.get("title_zh") or title_en
            is_en = it.get("lang") == "en" and title_en != title_zh
            head = f"**{title_zh}**"
            if is_en:
                head += f"（原文：{title_en}）"
            L.append(
                f"- `{it['time']}` {head} — *{it['source']}* · [阅读原文]({it['link']})"
            )
            summ = (it.get("summary_zh") or it.get("summary") or "").strip()
            if summ:
                L.append(f"  - {clip_summary(summ)}")
            else:
                # 源本身未提供摘要（如 MIT Tech Review 某些条目）：
                # 标注来源缺失，避免读者误以为抓取遗漏
                L.append(f"  - *（该来源未提供摘要，点击「阅读原文」查看全文）*")

    # 信源分布
    src = Counter(it.get("source", "未知") for it in items)
    if src:
        L.append("\n## 信源分布\n")
        for name, cnt in src.most_common():
            bar = "█" * max(1, round(cnt / max(src.values()) * 20))
            L.append(f"- *{name}* {cnt} 条 `{bar}`")
        L.append("")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(
        f"报告已生成: {OUT_FILE}（{len(items)} 条 / {len(dates)} 天 / "
        f"翻译覆盖率 {cover:.0f}%）"
    )


if __name__ == "__main__":
    main()
