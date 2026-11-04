"""每轮巡检的深度校验脚本：报告格式 + 数据质量门禁。"""
import json
import re
import collections
import datetime
import os

BASE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(BASE, "data", "news.json"), encoding="utf-8"))
items = data["items"]
md = open(os.path.join(BASE, "AI资讯摘要.md"), encoding="utf-8").read()

issues = collections.Counter()
notes = []

# ---------- 报告结构 ----------
decl = {}
for m in re.finditer(r"^## (\d{4}-\d{2}-\d{2})（周(.+?)）· (\d+) 条", md, re.M):
    decl[m.group(1)] = (int(m.group(3)), m.group(2))

actual = collections.Counter(i["date"] for i in items)
mism = [(k, decl.get(k, (0, ""))[0], actual.get(k, 0))
        for k in set(list(decl) + list(actual))
        if decl.get(k, (0,))[0] != actual.get(k, 0)]
if mism:
    issues["report_group_mismatch"] = len(mism)
    notes.append("天组声明偏差: %s" % mism)

wd = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
# 注意：正则里「周」在捕获组外，group(2) 拿到的是「一/二/...」，
# 比较时要补回「周」前缀，否则会把 29 个天组全部误判为星期错误。
badwd = [(k, v[1], wd[datetime.date.fromisoformat(k).weekday()])
         for k, v in decl.items()
         if "周" + v[1] != wd[datetime.date.fromisoformat(k).weekday()]]
if badwd:
    issues["weekday_error"] = len(badwd)
    notes.append("星期标注错误: %s" % badwd[:3])

# 每条带 HH:MM 时间戳 + 英文原标题括注
bt = chr(96)
pat = r"^- " + bt + r"(\d{2}:\d{2})" + bt + r" \*\*(.+?)\*\*（原文：(.+?)）"
bullets = re.findall(pat, md, re.M)
if len(bullets) != len(items):
    issues["report_bullet_count"] = abs(len(bullets) - len(items))

# 全量条目在报告「全部资讯」中出现
missing = []
for it in items:
    tag = it["time"] + bt + " **" + it["title_zh"]
    if tag not in md:
        missing.append((it["date"], it["time"], it["title_zh"][:30]))
if missing:
    issues["item_not_in_report"] = len(missing)
    notes.append("未入报告: %s" % missing[:5])

# 括注原标题与数据 title 一致
mismatch_en = []
for (t, zh, en) in bullets:
    pass
en_in_md = set(x[2] for x in bullets)
for it in items:
    if it.get("title") and it["title"] not in en_in_md:
        mismatch_en.append(it["title"][:50])
if mismatch_en:
    issues["en_title_mismatch"] = len(mismatch_en)
    notes.append("原标题不一致: %s" % mismatch_en[:3])

# ---------- 数据质量门禁 ----------
cjk = re.compile(r"[\u4e00-\u9fff]")
for it in items:
    tz = it.get("title_zh", "") or ""
    sz = it.get("summary_zh", "") or ""
    en = it.get("title", "") or ""
    if not it.get("translated"):
        issues["untranslated"] += 1
    if not cjk.search(tz):
        issues["no_cjk_title"] += 1
    if tz.strip() == en.strip() and en.strip():
        issues["zh_eq_en"] += 1
    if not sz.strip():
        issues["empty_summary"] += 1
    if len(sz) > 1000:
        issues["summary_over_1000"] += 1
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(it.get("date", ""))):
        issues["date_format_error"] += 1
    if not re.match(r"^\d{2}:\d{2}$", str(it.get("time", ""))):
        issues["time_format_error"] += 1
    if re.search(r"[\u4e00-\u9fff]\s+[\u4e00-\u9fff]", tz):
        issues["cjk_glue_title"] += 1
    if re.search(r"[\u4e00-\u9fff]\s+[\u4e00-\u9fff]", sz[:300]):
        issues["cjk_glue_summary"] += 1
    if "\ufffd" in tz + sz:
        issues["garbled"] += 1
    if re.search(r"(.)\1{3,}", sz):
        issues["dup_char"] += 1
    if re.search(r"(阅读原文|了解更多|点击查看|Read more|Learn more)\s*$", sz.strip()):
        issues["cta_residue"] += 1
    # 半角标点紧贴中文（真正的排版瑕疵）。注意不能用 \uff01-\uff5e 区间去查，
    # 那是「全角 ASCII」（！＂＃…），中文正常标点 ，。：； 都落在该区间内，
    # 会把 100% 合规的条目全部误判。真正要查的是 ASCII 半角标点贴中文。
    if re.search(r"[\u4e00-\u9fff][,.!?;:]|[,.!?;:][\u4e00-\u9fff]", tz + sz):
        issues["halfwidth_punct"] += 1

links = [i.get("link") for i in items]
if len(set(links)) != len(links):
    issues["dup_links"] = len(links) - len(set(links))
titles = [i.get("title") for i in items]
if len(set(titles)) != len(titles):
    issues["dup_titles"] = len(titles) - len(set(titles))

# 译文质量：标题过短（疑似残句）
short_title = [i["title_zh"] for i in items if 0 < len(i.get("title_zh", "")) < 6]
if short_title:
    issues["short_title"] = len(short_title)
    notes.append("过短标题: %s" % short_title[:3])

# 译文截断：真正的截断特征是结尾悬空（省略号/半角逗号/连字符），
# 而不是「没有句末标点」——中文标题不以标点结尾是完全正常的。
trunc = [i["title_zh"] for i in items
         if i.get("title_zh") and i["title_zh"].rstrip().endswith(("…", "...", "，", ",", "-", "—", "、"))]
if trunc:
    issues["truncated_title"] = len(trunc)
    notes.append("疑似截断标题: %s" % trunc[:3])

# 摘要结尾悬空（省略号）
sum_trunc = [i["title_zh"] for i in items
             if (i.get("summary_zh") or "").rstrip().endswith(("…", "..."))]
if sum_trunc:
    issues["summary_trailing_ellipsis"] = len(sum_trunc)
    notes.append("摘要结尾省略号: %s" % sum_trunc[:3])

# ---------- 译文语义缺陷门禁（2026-11-02 16:00 巡检新增）----------
# 背景：上一轮门禁只查格式（时间戳/括注/标点/空摘要），不查译文语义，
# 因此 15:07 条目的四处语义缺陷（ADNOC 音译成「亚诺克」、frontier AI
# 译成「边境 AI」、谓语重复、括号风格不一）全部逃过检查。
# 这里补三类语义级检查。

# 1) 已知坏译法残留：这些词在 AI 语境下是确定的误译，
#    出现即视为缺陷（与 translate.py 的 TERM_FIXES 同源）。
#    每项带可选的源文触发词——只有原文出现该触发词时才算缺陷。
#    这一点很关键：「自动化工」在「流程自动化工具」这类正常中文里
#    是「自动化」+「工具」的偶然相邻，若无触发词约束会大面积误报。
KNOWN_BAD = {
    "边境 AI": ("frontier AI 应译「前沿 AI」", ["frontier"]),
    "边境AI": ("frontier AI 应译「前沿 AI」", ["frontier"]),
    "跨界 AI": ("frontier AI 应译「前沿 AI」", ["frontier"]),
    "跨界AI": ("frontier AI 应译「前沿 AI」", ["frontier"]),
    "边界 AI": ("frontier AI 应译「前沿 AI」", ["frontier"]),
    "边界AI": ("frontier AI 应译「前沿 AI」", ["frontier"]),
    "亚诺克": ("ADNOC 音译失真", ["adnoc"]),
    "乌兰卡布": ("Ulanqab 应译「乌兰察布」", ["ulanqab"]),
    "数据中心校园": ("campus 在数据中心语境应译「园区」", ["campus"]),
    "展望部署": ("Envision 被意译成「展望」", ["envision"]),
    "自动化工": ("Autoware 项目名丢失", ["autoware"]),
    "TIER IVER": ("TIER IV 罗马数字被误写", ["tier iv"]),
    "聊天 GPT": ("ChatGPT 品牌丢失", ["chatgpt"]),
    "聊天GPT": ("ChatGPT 品牌丢失", ["chatgpt"]),
    # 2026-11-02 19:00 巡检新增：带空格的品牌形态（模型输出「开通 AI」
    # 而还原表只登记了无空格形态「开通AI」），导致整条品牌还原失效。
    "开通 AI": ("OpenAI 品牌丢失（带空格形态）", ["openai"]),
    "开通AI": ("OpenAI 品牌丢失", ["openai"]),
    "开放 AI": ("OpenAI 品牌丢失（带空格形态）", ["openai"]),
    "开放AI": ("OpenAI 品牌丢失", ["openai"]),
    "双子座": ("Gemini 品牌丢失", ["gemini"]),
    "尼维迪亚": ("Nvidia 品牌丢失", ["nvidia"]),
    "云飞拉": ("Cloudflare 品牌丢失", ["cloudflare"]),
    # 2026-11-02 20:00 巡检新增：智能体架构三大概念（memory / context /
    # curated）被意译，译名与中文 AI 技术圈的固定叫法不符。
    "环境引擎": ("context engine 应译「上下文引擎」", ["context engine"]),
    "策划知识": ("curated knowledge 应译「精选知识」", ["curated knowledge"]),
    "层次内存": ("tiered memory 应译「分层记忆」", ["tiered memory"]),
    "内存堆": ("memory stack 应译「记忆栈」", ["memory stack"]),
    "记忆堆": ("memory stack 应译「记忆栈」", ["memory stack"]),
    "文本填充": ("context stuffing 应译「上下文填充」", ["context stuffing"]),
    # 2026-11-02 20:00 巡检补充：「注射」在医疗语境是正确译法
    # （如 "inject the treatment" / "injected drugs into a mouse's brain"），
    # 只有软件语境（select/inject/compress 这类工程动词共现）才该译「注入」。
    # 因此这里用「工程动词共现」而非单纯出现「注射」来判定。
    "注射": ("inject 在软件语境应译「注入」", ["selects", "compresses", "injects into"]),
    # 2026-11-03 05:00 巡检新增：04:01/04:07/04:36 三条新条目的坏译法。
    # 这些译法在中文里字面成句，却把专有名词与金融术语彻底译错，
    # 机械检查若不含进来，下一轮同源条目会再次逃逸。
    "塞拉拉": ("Sierra 品牌音译失真，应还原为英文原名", ["sierra"]),
    "幽灵作家": ("Ghostwriter 是产品名，不应意译为「幽灵作家」", ["ghostwriter"]),
    "智能体工作室": ("Agent Studio 是平台名，不应意译为「智能体工作室」", ["agent studio"]),
    "数据机器人": ("Data Bot 是产品名，不应意译为「数据机器人」", ["data bot"]),
    "共享机器人": ("Shared Bot 是产品名，不应意译为「共享机器人」", ["shared bot"]),
    "资深笔记": ("senior notes 是「优先票据」，不是「资深笔记」", ["senior notes"]),
    "股票明信片补充": ("prospectus supplement 误译为「明信片」", ["prospectus supplement"]),
    "高级证券备忘录补充文件": ("prospectus supplement 应译「招股说明书补充文件」", ["prospectus supplement"]),
    "公开报价空白": ("public offering price 应译「公开发行价格」", ["public offering price"]),
    "旅行编辑": ("journey editing 应译「旅程编排」，非旅行义", ["journey editing"]),
    "编辑行程": ("edit journeys 应译「编辑旅程」，非旅行义", ["journey editing", "edit journeys"]),
    "太空 XSI": ("SpaceXAI 被源站拼作 SpaceXSI，应还原", ["spacexsi"]),
    "SpaceXSI": ("SpaceXAI 被源站拼作 SpaceXSI，应还原", ["spacexsi"]),
    # 2026-11-03 06:00 巡检新增：05:40—05:54 四条新条目的坏译法。
    # 这些译法字面成句，但把品牌名与 AI 术语彻底译错，机械检查必须含进来。
    "深度搜索带": ("DeepSeek Harness 品牌音译失真，应还原为英文原名", ["deepseek harness"]),
    "欧门 AI": ("Omen AI 品牌音译失真，应还原为英文原名", ["omen ai"]),
    "欧门AI": ("Omen AI 品牌音译失真，应还原为英文原名", ["omen ai"]),
    "水力实验室": ("Aquatic Labs 是实验室名，不应意译为「水力实验室」", ["aquatic labs"]),
    "原始多模态": ("natively multimodal 应译「原生多模态」", ["natively multimodal"]),
    "长视野": ("long-horizon 应译「长时程」", ["long-horizon"]),
    "长视线": ("long-horizon 应译「长时程」", ["long-horizon"]),
    "智能体编码": ("agentic coding 应译「智能体编程」", ["agentic coding"]),
    "个人智能体人": ("personal agents 译出冗余「人」字", ["personal agents"]),
    "寻找照顾": ("childcare 是育儿照护，不是「照顾」", ["childcare"]),
    "预测版本": ("prerelease 应译「预发布版本」", ["prerelease"]),
    "传感器的研发和开发": ("sensing technologies 应译「传感技术的研发」", ["sensing technologies"]),
    # ---- 2026-11-03 07:00 巡检新增 ----
    # 本轮的三类根因缺陷此前都能逃过门禁：
    # 1) 重复字折叠规则把「智能能力」折成「智能力」——字面成句，
    #    但中文读者会读成「智·能力」，完全不通。
    #    判定不能只用子串「智能力」，因为「智能能力」本身含「能能力」
    #    而正确写法是「智能能力」——这里用「智能力」且原文含
    #    "capabilit" 触发（智能能力的英文是 AI capabilities）。
    "智能力": ("「智能能力」被重复字折叠规则折成「智能力」", ["capabilit"]),
    # 2) Anthropic 在句首被意译成「人类」，品牌名彻底消失。
    "人类警告": ("Anthropic 品牌丢失，应还原为英文原名", ["anthropic"]),
    "人类表示": ("Anthropic 品牌丢失，应还原为英文原名", ["anthropic"]),
    "人类称": ("Anthropic 品牌丢失，应还原为英文原名", ["anthropic"]),
    # 3) 财报术语逐词直译，中文里根本不成立。
    "总利率": ("gross margin 应译「毛利率」", ["gross margin"]),
    "股票均利率": ("diluted EPS 应译「摊薄每股收益」", ["eps", "earnings per share"]),
    "稀释的 EPS": ("diluted EPS 应译「摊薄每股收益」", ["eps", "earnings per share"]),
    "人工智能毁灭者": ("AI doomers 应译「AI 悲观论者」", ["doomer"]),
    # 4) 创业公司名被意译成普通中文词，读者定位不到公司。
    "轨迹筹集": ("Trajectory 是公司名，应还原为英文原名", ["trajectory raises"]),
    # ---- 2026-11-03 12:00 巡检新增 ----
    # 本轮的新条目暴露出两类此前逃过门禁的缺陷：
    # 1) 品牌名被意译成单字：Dreambeans（Google Labs 的个性化故事应用）
    #    被译成「梦」，标题产出「Google 带来了梦个性化 AI 故事到印度」，
    #    中文读者认不出这是产品名。
    "梦个性化": ("Dreambeans 品牌丢失，应还原为英文原名", ["dreambeans"]),
    "梦豆": ("Dreambeans 品牌丢失，应还原为英文原名", ["dreambeans"]),
    # 2) 语言名被逐词音译成无辨识度形态，其中两种与国名撞车：
    #    Telugu→泰国语（把印度语言安到泰国语言上）、
    #    Kannada→加拿大语（与加拿大国名直接撞车）。
    #    这类是读者会当成事实错误记住并传播的错误，危害高于一般音译瑕疵。
    "泰国语": ("Telugu 应译「泰卢固语」", ["telugu"]),
    "加拿大语": ("Kannada 应译「卡纳达语」", ["kannada"]),
    "马拉图语": ("Marathi 应译「马拉地语」", ["marathi"]),
    "泰尔语": ("Tamil 应译「泰米尔语」", ["tamil"]),
    "古吉拉提": ("Gujarati 应译「古吉拉特语」", ["gujarati"]),
    "俄比亚语": ("Odia 应译「奥迪亚语」", ["odia"]),
    "马拉雅语": ("Malayalam 应译「马拉雅拉姆语」", ["malayalam"]),
    # 3) Punjabi 被模型幻听成「西班牙语」：原文语言清单里根本没有 Spanish，
    #    结果语言列表凭空多出一种、漏掉一种，读者核对时会发现对不上。
    #    注意不能用纯子串判定——若原文本身真含 spanish，
    #    「西班牙语」是正确译法（由 _fix_language_names 复合判定处理）。
    "西班牙语": ("Punjabi 应译「旁遮普语」，非西班牙语", ["punjabi"]),
}

# KNOWN_BAD 的例外规则：键为坏译法，值为「原文出现这些词时该译法反而正确」
# 的触发词列表（全部满足才放行）。
# 目前只有「西班牙语」需要：原文若真的在讲 spanish，
# 「西班牙语」是正确译法，不能按 Punjabi 的坏译法判缺陷。
KNOWN_BAD_EXCLUDE = {
    "西班牙语": ["spanish"],
}

# 截断词检测：「bottleneck」被离线模型截成「瓶」（丢掉「颈」）。
# 不能用子串匹配——正确的「瓶颈」本身也含「瓶」，
# 因此这里按与 translate.py 一致的正则「的瓶(?!颈)」判定。
_bottle_trunc = []
for it in items:
    zh = (it.get("title_zh") or "") + " " + (it.get("summary_zh") or "")
    en_low = ((it.get("title") or "") + " " + (it.get("summary") or "")).lower()
    if "bottleneck" in en_low and re.search(r"的瓶(?!颈)", zh):
        _bottle_trunc.append((it["date"], it["time"], it.get("title_zh", "")[:40]))
if _bottle_trunc:
    issues["truncated_bottleneck"] = len(_bottle_trunc)
    notes.append("bottleneck 截断为「瓶」: %s" % _bottle_trunc[:3])
bad_hits = []
for it in items:
    zh = (it.get("title_zh") or "") + " " + (it.get("summary_zh") or "")
    en_low = ((it.get("title") or "") + " " + (it.get("summary") or "")).lower()
    for bad, spec in KNOWN_BAD.items():
        why, triggers = spec
        if bad not in zh:
            continue
        if triggers and not any(t in en_low for t in triggers):
            continue  # 原文无对应触发词，属正常中文用法，不计缺陷
        # 例外规则：某些坏译法只在「原文没有正确说法」时才成立。
        # 例：「西班牙语」被判为 Punjabi 的坏译法，但若原文确实提到
        # spanish（真在讲西班牙语），那么「西班牙语」是正确译法，不算缺陷。
        excl = KNOWN_BAD_EXCLUDE.get(bad)
        if excl and all(t in en_low for t in excl):
            continue
        bad_hits.append((it["date"], it["time"], bad, why))
if bad_hits:
    issues["known_bad_rendering"] = len(bad_hits)
    notes.append("已知坏译法残留: %s" % bad_hits[:5])

# 2) 谓语重复：「签署了与……签署了/签署……」是病句结构
dup_pred = []
for it in items:
    zh = (it.get("title_zh") or "") + " " + (it.get("summary_zh") or "")
    if "签署了与" in zh and "签署" in zh.split("签署了与", 1)[1]:
        dup_pred.append((it["date"], it["time"], it.get("title_zh", "")[:40]))
if dup_pred:
    issues["duplicate_predicate"] = len(dup_pred)
    notes.append("谓语重复: %s" % dup_pred[:3])

# 3) 括号风格：中文语境统一全角，半角括号视为排版不一致
half_paren = []
for it in items:
    zh = (it.get("title_zh") or "") + " " + (it.get("summary_zh") or "")
    if re.search(r"[\u4e00-\u9fff]\s*\(", zh):
        half_paren.append((it["date"], it["time"], it.get("title_zh", "")[:40]))
if half_paren:
    issues["halfwidth_paren"] = len(half_paren)
    notes.append("半角括号混排: %s" % half_paren[:3])

# 3.5) 引号配对（2026-11-03 09:00 巡检新增）
#     上一轮人工定稿时留下一条外层「未闭合的条目：读者看到悬空左引号，
#     句子读起来断裂。纯格式门禁查不出来（中文里单侧引号完全「合法」），
#     只能靠左右计数是否相等来判定。
#     注：直引号 " 由 translate._fix_quote_pairs 处理并转成弯引号，
#     这里只校验中文弯引号的两级嵌套。
quote_unbalanced = []
for it in items:
    zh = (it.get("title_zh") or "") + (it.get("summary_zh") or "")
    for op, cl in (("「", "」"), ("『", "』")):
        if zh.count(op) != zh.count(cl):
            quote_unbalanced.append(
                (it["date"], it["time"], op,
                 zh.count(op), zh.count(cl), it.get("title_zh", "")[:36]))
            break
if quote_unbalanced:
    issues["quote_unbalanced"] = len(quote_unbalanced)
    notes.append("引号未闭合: %s" % quote_unbalanced[:3])

# 5) 繁体字残留（2026-11-02 20:00 巡检新增）
#    上一轮人工定稿时写入了繁体「頭號議題」，纯格式门禁查不出来——
#    繁体在中文里完全「合法」，但与站内简体排版风格不一致。
#    这里用 zh_t2s 的安全映射表做判定：能被转换的字即为繁体残留。
#    根因修复：translate.py 的 _clean_zh 末尾调用 to_simplified()。
try:
    from zh_t2s import to_simplified

    trad_hits = []
    for it in items:
        for field in ("title_zh", "summary_zh"):
            t = it.get(field) or ""
            if t and to_simplified(t) != t:
                trad_hits.append((it["date"], it["time"], field,
                                  t[:40]))
    if trad_hits:
        issues["traditional_chars"] = len(trad_hits)
        notes.append("繁体字残留: %s" % trad_hits[:3])
except ImportError:
    notes.append("zh_t2s 模块缺失，跳过繁体字检查")

# 4) retry（重试）被 NLLB 误译为「退休」（retire）——词形混淆，语义完全相反。
#    2026-11-02 19:00 巡检新增：此类错误中文读起来完全通顺，
#    纯格式门禁查不出来，只能靠「原文含 retry 且译文出现退休」来判定。
#    若原文同时含 retire（真讲退休），则「退休」是正确译法，不计缺陷。
retry_confusion = []
for it in items:
    en_low = ((it.get("title") or "") + " " + (it.get("summary") or "")).lower()
    if "retry" not in en_low or "retire" in en_low:
        continue
    zh = (it.get("title_zh") or "") + " " + (it.get("summary_zh") or "")
    if "退休" in zh:
        retry_confusion.append((it["date"], it["time"], it.get("title_zh", "")[:40]))
if retry_confusion:
    issues["retry_retire_confusion"] = len(retry_confusion)
    notes.append("retry 误译为退休: %s" % retry_confusion[:3])

translated = sum(1 for i in items if i.get("translated"))
en_items = [i for i in items if i.get("lang") == "en"]
print("=" * 60)
print("总条目数        :", len(items))
print("已翻译条目数    :", translated)
print("翻译覆盖率      : %.1f%% (%d/%d 英文条目)" % (
    translated / len(en_items) * 100 if en_items else 100.0, translated, len(en_items)))
print("天组数          :", len(decl))
print("报告条目行数    :", len(bullets))
print("最后更新        :", data.get("last_update"))
print("下次更新        :", data.get("next_update"))
print("-" * 60)
print("质量门禁结果    :", dict(issues) if issues else "全部通过，0 缺陷")
for n in notes:
    print("  提示:", n)
print("=" * 60)
