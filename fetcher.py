"""
RSS 抓取模块：从多个 AI 资讯源拉取最新条目。
每个源独立 try/except，单个源失败不影响其他源。
"""
import hashlib
import re
import socket
import html
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

import feedparser
import requests

# 全局兜底超时，防止个别源挂起整个抓取周期
socket.setdefaulttimeout(15)

PER_FEED_TIMEOUT = 15   # 单源请求超时
OVERALL_TIMEOUT = 45    # 整体抓取硬上限，避免单源卡死
# 整体超时后，仍在运行的任务最多再等这么久才放弃。
# 说明：as_completed(timeout=) 抛 TimeoutError 时，已经跑完但还没被
# yield 出来的 future 结果会被直接丢弃 —— 表现为「某些源本轮莫名其妙
# 0 条」（Google Blog / Google DeepMind 首轮 TLS 断连后重试成功，
# 但重试耗时超过 45s 整体上限，结果被扔掉）。这里给一个收尾等待窗口，
# 让慢源的成功结果仍能入库。
GRACE_TIMEOUT = 40

# 东八区（北京时间），用于日期分组与时间展示
TZ = timezone(timedelta(hours=8))

FEEDS = [
    ("TechCrunch", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("The Verge", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("Ars Technica", "https://arstechnica.com/ai/feed/"),
    ("MIT Tech Review", "https://www.technologyreview.com/topic/artificial-intelligence/feed/"),
    ("Wired", "https://www.wired.com/feed/tag/ai/latest/rss"),
    ("Marktechpost", "https://www.marktechpost.com/feed/"),
    ("ML Mastery", "https://machinelearningmastery.com/feed/"),
    ("VentureBeat", "https://venturebeat.com/category/ai/feed/"),
    # 注意：blog.google/technology/ai/rss/ 已 301 到 innovation-and-ai 路径，
    # 直接用旧地址在部分网络环境下会触发 TLS 断连，故此处写入最终地址。
    ("Google Blog", "https://blog.google/innovation-and-ai/technology/ai/rss/"),
    ("OpenAI", "https://openai.com/blog/rss.xml"),
    # 备用/增补源：VentureBeat 长期返回 429，DeepMind 与 InfoQ 可补足一手信源
    ("Google DeepMind", "https://deepmind.google/blog/rss.xml"),
    ("InfoQ AI", "https://feed.infoq.com/ai-ml-data-eng/"),
    ("NVIDIA Blog", "https://blogs.nvidia.com/feed/"),
    # 补位源：IEEE Spectrum 的 AI 频道覆盖研究/工程向硬资讯，稳定性好
    ("IEEE Spectrum AI", "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss"),
    # 补位源：unite.ai 聚合 AI 论文与产业动态，可顶替偶发 403 的 ML Mastery
    ("Unite.AI", "https://www.unite.ai/feed/"),
    # 2026-11-04 新增数据源：扩宽一手/研究/产业信源（均经本环境可达性实测，
    # 且近 1-2 天有更新，落在 MAX_AGE_DAYS=31 时间窗内）
    ("MIT News AI", "https://news.mit.edu/rss/topic/artificial-intelligence2"),
    ("The Decoder", "https://the-decoder.com/feed/"),
    # 以下两个为综合/个人源，需走严格 AI 相关性过滤，避免非 AI 内容混入
    ("Simon Willison", "https://simonwillison.net/atom/everything/"),
    ("SiliconANGLE", "https://siliconangle.com/feed/"),
]

# 部分源响应较慢（DeepMind 冷启动常需 20s+），单独放宽超时
SOURCE_TIMEOUT = {
    "Google DeepMind": 30,
    "NVIDIA Blog": 20,
    "InfoQ AI": 20,
}

# NVIDIA 官方博客是综合科技博客，含大量游戏/硬件宣发稿。
# 该源需要 AI 相关性过滤，避免 GeForce 游戏之类混入 AI 资讯流。
AI_KEYWORDS = re.compile(
    r"\b(ai|a\.i\.|artificial intelligence|agentic|agent|agents|genai|llm|llms|"
    r"machine learning|ml|deep learning|neural|transformer|model|models|"
    r"training|inference|inferencing|copilot|copilots|chatbot|gpt|chatgpt|"
    r"claude|gemini|llama|qwen|deepseek|nvidia ?ai|ai ?factory|ai ?cloud|"
    r"embodied|robot|robotics|vision language|vlm|diffusion|open ?source|"
    r"humanoid|reasoning|multimodal|embedding|fine-?tun|rag\b|"
    r"人工智能|大模型|智能体|机器学习|深度学习|神经网络|智能驾驶|机器人)\b",
    re.IGNORECASE,
)

# 命中这些词的条目即使含 AI 关键词也判定为非 AI（游戏/硬件宣发为主）
NON_AI_MARKERS = re.compile(
    r"\b(geforce ?now|gfn thursday|call of duty|steam |xbox|playstation|"
    r"nintendo|switch 2|steam deck|ray tracing|dlss|fsr \d|driver update|"
    r"graphics card|gpu buy|best deals|price drop|black friday deals|"
    r"holiday deals|gaming|laptop|monitor|gpu\b|cpu\b)\b",
    re.IGNORECASE,
)


def is_ai_relevant(title, summary, source):
    """相关性过滤：仅对综合型博客源生效，AI 垂直源不额外拦截。"""
    if source not in STRICT_RELEVANCE_SOURCES:
        return True
    text = f"{title} {summary}"
    if not AI_KEYWORDS.search(text):
        return False
    # AI 关键词命中但同时是硬件/游戏宣发：再看 AI 词密度
    hits = len(AI_KEYWORDS.findall(text))
    if hits == 0:
        return False
    if NON_AI_MARKERS.search(text) and hits <= 1:
        return False
    return True


# 需要执行严格 AI 相关性过滤的源（综合博客类 / 个人博客 / 综合科技媒体）
STRICT_RELEVANCE_SOURCES = {"NVIDIA Blog", "Simon Willison", "SiliconANGLE"}

# 部分源（如 VentureBeat）会对数据中心 IP 永久返回 429。
# 对被限流的源做有限退避重试；确认是 429（IP 级封禁）时只试一次，
# 避免每轮白等几秒拖慢整轮抓取。
_RETRY_STATUS = {403, 429, 500, 502, 503, 504}
_RETRY_TIMES = 2
_RETRY_SLEEP = 3.0
# 429 表示 IP 已被封禁，重试无意义，仅重试一次
_RETRY_TIMES_429 = 1

# 扫描 feed 时允许连续出现的超窗（早于时间窗下界）条目数。
# 少数源存在个别乱序，需容忍少量乱序后才停止扫描，避免漏掉后面的新条目。
_STALE_TOLERANCE = 5

# 按源覆盖 User-Agent。
# unite.ai 的 WAF 会对「完整 Chrome UA 指纹」直接返回 520，
# 换成简单 UA 反而稳定返回 200；此处按源覆盖即可。
_SOURCE_UA = {
    "Unite.AI": "Mozilla/5.0",
}

_TAG_RE = re.compile(r"<[^>]+>")
_ENT_RE = re.compile(r"&(?:[a-z]+|#[0-9]+|#x[0-9a-fA-F]+);")

# 共享 Session：复用 TCP/TLS 连接。
# 部分源（如 deepmind.google）新建连接时握手可达 30-40s，
# 复用连接后仅需 0.2-0.8s，是整轮抓取能否在超时内完成的关键。
_SESSION = requests.Session()
_SESSION.mount(
    "https://",
    requests.adapters.HTTPAdapter(pool_connections=16, pool_maxsize=16, max_retries=0),
)
_SESSION.mount(
    "http://",
    requests.adapters.HTTPAdapter(pool_connections=16, pool_maxsize=16, max_retries=0),
)

# RSS 摘要尾部的样板噪声：站点推广语与被截断的标记
# 策略：先按"标记词"定位并截断，再清理尾部残留的截断标记
_TAIL_MARKERS = [
    "appeared first on",
    "This story originally appeared in",
    "Continue reading",
    "Read more",
    # The Verge 的 <content> 正文末尾固定带这句跳转语
    "Read the full story at",
]
_TAIL_TRIM = [
    re.compile(r"\s*\[\s*\]?\s*$"),
    re.compile(r"\s*\[[\s…]*\]\s*$"),
    re.compile(r"\s*…\s*$"),
    re.compile(r"\s*\.{2,}\s*$"),
]
# 样板语只在摘要末尾出现；正文中间出现的 "Read more" 等短语不应被误伤
_TAIL_WINDOW = 240
# 样板语标记之后通常只剩站点名等极短尾巴（"appeared first on MarkTechPost ."），
# 正文里的 "Read more" 后面则仍有大量内容，据此区分真样板语与正文
_TAIL_TRAILING_MAX = 80
# 尾部署名（"By Renato Losio" / "By Chip Huyen, Daniel Dominguez" 等）：
# 这是作者署名而非正文内容，若保留会在译文里留下「由Renato Losio」这类
# 半中半英的悬空结尾。抓取阶段直接剥离。
_BYLINE_RE = re.compile(
    r"(?<=[.!?%])\s*By\s+(?:[A-Z][A-Za-z.\-]*(?:\s+|,\s*|$)){1,10}$"
)
# 夹在正文中间的站点 CTA 噪声（不是结尾样板语，需单独清理）。
# MIT Tech Review 的摘要结构为：
#     "...are decidedly mixed. DOWNLOAD THE REPORT Failure to produce..."
# 其中 "DOWNLOAD THE REPORT" 是「下载报告」按钮文案，位于正文中间，
# 尾部分类器（_TAIL_MARKERS）清不掉。若不清洗，译文会出现
# 「下载报告 未能产出……」这种无意义断裂句。
_INLINE_CTA = [
    re.compile(r"\s*DOWNLOAD\s+THE\s+REPORT\s*", re.I),
    re.compile(r"\s*DOWNLOAD\s+THE\s+FULL\s+REPORT\s*", re.I),
]
# MarkTechPost 复读标题的长度上限：仅当 "The post" 紧邻推广语时才判定为样板语
_MTP_TITLE_WINDOW = 200

# 摘要开头的赞助商前缀（IEEE Spectrum 常见）：这些不是文章内容
_HEAD_SPONSOR_PATTERNS = [
    re.compile(
        r"^This article is (?:brought to you|sponsored|presented) by [^.]{0,80}\.\s*",
        re.IGNORECASE,
    ),
    re.compile(r"^This story originally appeared in [^.]{0,80}\.\s*", re.IGNORECASE),
]

# 摘要开头的「订阅引导语」（MIT Tech Review 等站点常见）：
#     "To get stories like this in your inbox first, sign up here . <正文>"
# 这类句子不是文章内容，是站点求订阅的引导。不剥离的话，
# 译文首句会变成「要先在收件箱里收到这样的故事，请在这里注册」，
# 与正文语义完全无关，读者会以为这是文章开头。
#
# 判定要点：
#   1) 出现在摘要开头（^锚定），不是正文中间出现的同类表述；
#   2) 整句是「订阅/注册 + 收件箱」话术，句长有限（<=120 字符），
#      避免把正文里真实的「订阅用户将…」误删。
_HEAD_CTA_PATTERNS = [
    re.compile(
        r"^To get (?:stories|news|articles) like this in your inbox[^.]{0,80}\.\s*",
        re.IGNORECASE,
    ),
    re.compile(r"^Sign up (?:here|for|to receive)[^.]{0,80}\.\s*", re.IGNORECASE),
    re.compile(
        r"^To (?:get|receive) [^.]{0,40}(?:in your inbox|in your email|newsletter)[^.]{0,60}\.\s*",
        re.IGNORECASE,
    ),
]


# MarkTechPost 的摘要末尾会复读一遍文章标题，形式有两种：
#   a) "... appeared first on MarkTechPost ."
#   b) "... The post <标题>"
# 两种都需要整段剥离，否则译文里会残留未翻译的英文标题复读。
_POST_MARKER = "the post "


def _strip_title_repeat(text, title):
    """剥离摘要末尾对文章标题的复读（MarkTechPost 特有）。

    做法：若摘要末尾出现 "The post "，且其后内容与文章标题高度相似
    （按词集合 Jaccard 相似度判定），则整段删除。

    相似度阈值取得较高，避免误删正文中真实提到标题的句子。
    """
    if not text or not title:
        return text
    low = text.lower()
    idx = low.rfind(_POST_MARKER)
    if idx == -1:
        return text
    head = text[:idx].strip()
    repeat = text[idx + len(_POST_MARKER) :].strip()
    if not repeat:
        return text
    # 复读标题与文章标题的词集合相似度
    def words(s):
        return set(re.findall(r"[A-Za-z0-9]+", s.lower()))

    w_rep, w_title = words(repeat), words(title)
    if not w_rep or not w_title:
        return text
    inter = len(w_rep & w_title)
    union = len(w_rep | w_title)
    sim = inter / union if union else 0.0
    if sim >= 0.55 and len(head) >= 20:
        return head
    return text


def _strip_tail_noise(text, title=None):
    """去掉 RSS 摘要尾部的站点推广语与截断标记（保留正文）。

    两类样板语需要处理：
      1) MarkTechPost 专用格式
         "<正文>. The post <标题> appeared first on <站点>."
         其中 "The post" 之后整段是标题复读，必须从 "The post" 处截断，
         否则译文里会残留一整句未翻译的英文标题复读。
      2) 通用推广语 "Continue reading" / "Read more" /
         "This story originally appeared in" 等，直接在标记词处截断。

    判定样板语的关键信号：标记词之后只剩极短的尾巴（站点名等）。
    正文中间自然出现的 "Read more" 后面仍有大量内容，据此不会被误伤。
    """
    if not text:
        return text
    out = text.strip()

    # 1) 按推广语标记定位：取最后一次出现的位置，保留其之前的正文
    low = out.lower()
    cut = None
    for marker in _TAIL_MARKERS:
        idx = low.rfind(marker.lower())
        if idx == -1:
            continue
        # 标记必须落在摘要尾部附近
        if len(out) - idx > _TAIL_WINDOW:
            continue
        # 标记之后只剩极短尾巴才认定为样板语（避免误伤正文中的短语）
        if len(out) - idx - len(marker) > _TAIL_TRAILING_MAX:
            continue
        head = out[:idx]
        # MarkTechPost："The post XXX appeared first on YYY" —— 正文在 "The post " 之前。
        # 仅当 "The post" 紧邻推广语时（说明中间是复读的标题）才回退截断，
        # 否则正文里的 "the post office" 之类会被误判。
        if marker.lower() == "appeared first on":
            post_at = head.lower().rfind("the post ")
            if post_at != -1 and (idx - post_at) <= _MTP_TITLE_WINDOW:
                head = head[:post_at]
        if cut is None or len(head) < len(out[:cut]):
            cut = len(head)
    if cut is not None:
        cand = out[:cut].strip()
        # 保护：正文不能被清空（"This story originally appeared in ..." 这类
        # 整句都是噪声的情形属于例外，允许清空）
        noise_only = any(
            m.lower() in out.lower() and len(cand) < 12 for m in _TAIL_MARKERS
        )
        if len(cand) >= 20 or noise_only:
            out = cand

    # 2) 剥离末尾的标题复读（"The post <标题>"，可能没有 "appeared first on" 后缀）
    out = _strip_title_repeat(out, title)

    # 2) 清理尾部截断标记
    for pat in _TAIL_TRIM:
        new = pat.sub("", out).strip()
        if len(new) >= 20 or len(new) >= len(out) - 5:
            out = new

    # 3) 剥离尾部署名（"By Renato Losio"），它是署名不是正文
    if _BYLINE_RE.search(out):
        stripped = _BYLINE_RE.sub("", out).strip()
        if len(stripped) >= 20:
            out = stripped
    # 4) 剥离夹在正文中间的站点 CTA 噪声。
    # MIT Tech Review 的摘要形如：
    #     "...are decidedly mixed. DOWNLOAD THE REPORT Failure to produce..."
    # 这句 CTA 位于正文中间而非结尾，尾部分类器清不掉，
    # 会让译文出现「下载报告」式的无意义句子。
    for pat in _INLINE_CTA:
        new = pat.sub(" ", out).strip()
        if len(new) >= 20:
            out = new
    return out.strip()


def _strip_head_sponsor(text):
    """剥离摘要开头的赞助商前缀。

    IEEE Spectrum 等源的 description 形如：
        "This article is brought to you by Qualcomm Technologies . <正文>"
    这类前缀不是文章内容，会让译文首句变成推广语。
    """
    if not text:
        return text
    for pat in _HEAD_SPONSOR_PATTERNS:
        m = pat.search(text)
        if m:
            text = text[m.end():].strip()
    # 订阅引导语：剥离后若正文过短（<40 字符），说明整段都是引导语，
    # 此时保留原样，避免返回空摘要。
    for pat in _HEAD_CTA_PATTERNS:
        m = pat.search(text)
        if m and len(text[m.end():].strip()) >= 40:
            text = text[m.end():].strip()
    return text


# 摘要长度上限：部分源（IEEE Spectrum）把整篇正文塞进 description，
# 最长可达 2 万字符。离线翻译模型输入上限 384 token，超长会被静默截断，
# 导致译文只覆盖开头约 5%，且长文本生成出现重复退化。
# 因此在抓取层按句边界截断到可完整翻译的长度。
MAX_SUMMARY_CHARS = 900


def _truncate_summary(text, limit=MAX_SUMMARY_CHARS):
    """按句子边界截断过长摘要，避免翻译时静默丢内容。

    优先在句号处断开；找不到句号时退到空格，最后才硬截断。
    """
    if not text or len(text) <= limit:
        return text
    head = text[:limit]
    # 在后 60% 区间内寻找句末标点，保证截断后仍是完整句子
    best = -1
    for mark in (". ", "。 ", "? ", "! ", "; ", ".\u00a0"):
        idx = head.rfind(mark)
        if idx > best:
            best = idx
    if best >= int(limit * 0.4):
        cut = head[: best + 1].strip()
        if len(cut) >= 60:
            return cut
    # 退化：找最后一个空格
    sp = head.rfind(" ")
    if sp > int(limit * 0.4):
        cut = head[:sp].strip()
        if len(cut) >= 60:
            return cut
    return head.strip()


def _snap_to_sentence(text, min_keep=60):
    """把被源站截断在半句的摘要回退到最后一个完整句边界。

    部分源（The Verge 的 <content>、MIT Tech Review 等）会在正文里用
    "…" 截断付费墙后的内容，剥离跳转语后尾部可能停在半句
    （如 "...launched the satellite into orbit earlier this"）。
    直接送翻译会得到半句译文，因此回退到最后一个句末标点处，
    保证入库摘要与译文都是完整句。

    若回退后剩余内容过短，则保留原样（避免把短摘要清空）。
    """
    if not text:
        return text
    s = text.rstrip()
    if not s or _is_complete(s):
        return text
    # 找最后一个句末标点（句号/问号/叹号），允许其后紧跟右引号/右括号
    best = -1
    for i in range(len(s) - 1, -1, -1):
        if s[i] in ".!?":
            # 跳过紧跟其后的收尾引号
            j = i
            while j + 1 < len(s) and s[j + 1] in '"\'’”)】':
                j += 1
            best = j
            break
    if best < 0:
        return text
    head = s[: best + 1].strip()
    if len(head) < min_keep:
        return text
    return head


def _clean(raw_html, title=None):
    if not raw_html:
        return ""
    # 先解码 HTML 实体再剥标签：若顺序反了，&#8217;（撇号）会被
    # _ENT_RE 替换成空格，产出「EASE s total equity」这类丢掉撇号的
    # 残缺英文——用户点「看翻译原文」时看到的就是坏的原文。
    # 先 unescape 还有个好处：&lt;script&gt; 会被还原成真标签，
    # 从而仍能被紧随其后的 _TAG_RE 清掉，不会漏出可执行内容。
    # 注意：形参名不能叫 html，否则会遮蔽本模块导入的 html 模块。
    txt = html.unescape(raw_html)
    txt = _TAG_RE.sub(" ", txt)
    txt = _ENT_RE.sub(" ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    txt = _strip_tail_noise(txt, title)
    txt = _strip_head_sponsor(txt)
    txt = _truncate_summary(txt)
    # 源站付费墙/摘要字段可能在半句处截断，回退到完整句边界
    txt = _snap_to_sentence(txt)
    return txt


def _clean_title(title):
    """清洗标题：解码 HTML 实体并去掉多余空白。

    RSS 标题里常见 `Google&#8217;s` 这类实体，若不解码会直接进入标题与译文。
    """
    if not title:
        return ""
    txt = _TAG_RE.sub(" ", title)
    txt = html.unescape(txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def _to_local(parsed):
    """feedparser 的 published_parsed 为 UTC，转换为东八区。"""
    if parsed:
        try:
            dt = datetime(*parsed[:6], tzinfo=timezone.utc).astimezone(TZ)
            return dt
        except Exception:  # noqa
            pass
    return datetime.now(TZ)


def _ends_with_half_number(text):
    """判断摘要是否以「半截数字」结尾（被源站按字符数硬截断）。

    特征：句子以「数字 + 句点」收尾，且这个句点其实是小数点的一部分。
    典型例子（Unite.AI）：
        "...Net income was $30.7 billion, compared with $27."
    原文实际是 "$27.5 billion"，截断落在 "$27." 上。

    排除两类正常结尾：
      - 以四位年份结尾（"...on October 15, 2026."）——年份是完整语义单位；
      - 以小数结尾且小数点后本就有数字（"...rose 12.5%."）——但这种
        句末不会带句点前的孤立数字，故此处只按「数字后直接跟句点」判定，
        并排除年份形态。
    """
    if not text:
        return False
    s = text.rstrip()
    if not s.endswith("."):
        return False
    m = re.search(r"(\d+)\.$", s)
    if not m:
        return False
    digits = m.group(1)
    # 四位年份（2026.）是完整日期的正常结尾，不算截断
    if len(digits) == 4 and digits.startswith(("19", "20")):
        return False
    # 句点前必须紧邻数字（即 "数字." 而非 "某词."），确保确实是数字结尾
    return True


def _is_complete(text):
    """判断摘要是否以完整句子收尾（而非被源站截断在半句）。

    The Verge / MIT Tech Review / NVIDIA Blog 等源的 RSS 同时提供
    <summary> 与 <content> 两个字段：前者是源站截断后的短版（常在半句处
    断开），后者是完整正文。若无脑取第一个候选，就会把半句摘要送进翻译，
    导致译文也是半句，且关键事实丢失。
    """
    s = (text or "").rstrip()
    if not s:
        return False
    # 结尾标点：句号/问号/叹号，或右引号、右括号、省略号
    return s[-1] in '.!?"\'’”)】…'


def _entry_summary(entry, title):
    """从 entry 中尽力取摘要正文。

    不同源的摘要字段位置不一致：多数用 <description>，有的只在
    <content:encoded> 里（如 MIT Tech Review 的一条），还有的直接为空。

    选取策略：**完整句优先，其次取更长者**。
    早期实现是「取第一个长度 >= 20 的候选」，对 The Verge 等源会选中
    被源站截断在半句的 <summary>，而把完整的 <content> 丢掉，
    造成 44 条英文摘要半句结尾（对应译文同样半句、关键事实缺失）。
    """
    candidates = [
        entry.get("summary"),
        entry.get("description"),
    ]
    # content 是 list[dict]，value 为 HTML 正文
    for c in entry.get("content") or []:
        if isinstance(c, dict) and c.get("value"):
            candidates.append(c["value"])

    cleaned_all = []
    for raw in candidates:
        if not raw:
            continue
        cleaned = _clean(raw, title)
        if len(cleaned) >= 20:
            cleaned_all.append(cleaned)
    if not cleaned_all:
        # 全部兜底都失败：返回空串，交由上层处理（不伪造内容）
        return ""

    # 1) 优先选以完整句收尾的候选；其中取最长的一条
    complete = [c for c in cleaned_all if _is_complete(c)]
    if complete:
        return max(complete, key=len)
    # 2) 全都不完整时，退而取最长的一条（总比短的好）
    return max(cleaned_all, key=len)


# 需要用文章页 og:description 兜底补全的源。
# 这些源的 RSS 只提供被截断的 <summary>，且没有 <content> 可用，
# 只有文章页的 meta description 是完整句。
_PAGE_FALLBACK_SOURCES = {"ML Mastery"}
# 每个源最多用文章页兜底补全几条（控制单轮抓取耗时）
_PAGE_FALLBACK_MAX = 8

# 需要用文章页正文首段兜底补全的源。
#
# 2026-11-03 07:00 巡检新增：Unite.AI 的 RSS <summary> 与文章页
# og:description 都按固定字符数截断，且截断点恰好落在小数点中间
# （"...compared with $27." —— 原文是 "$27.5 billion"）。
# og:description 补不了，只能取文章页正文的前几个自然段。
_BODY_FALLBACK_SOURCES = {"Unite.AI"}
# 每个源最多用文章页正文兜底补全几条
_BODY_FALLBACK_MAX = 6
# 正文兜底时最多取几个自然段（Unite.AI 的正文首段即新闻导语，
# 第二段是财务细节，足够覆盖被截断的部分）
_BODY_FALLBACK_PARAS = 2


def _page_body_intro(url, timeout=15):
    """抓文章页正文的前几个自然段（用于补全被源站截断的摘要）。

    Unite.AI 是 WordPress 站点，正文在 <p> 标签里。首段前面会混进
    站点导航残留（如 "AI Research Agent Add Unite.AI to your preferred
    sources on Google"），需要按段落长度与已知噪声前缀做清洗。

    返回空串表示抓取失败，调用方应保留原摘要。
    """
    try:
        r = _SESSION.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            },
        )
    except Exception:
        return ""
    if r.status_code >= 400:
        return ""
    try:
        text = r.text
    except Exception:
        return ""
    # 去掉 script / style / noscript，否则会捞进几十万字符的 JS 噪音。
    body = re.sub(
        r"(?is)<(script|style|noscript)\b.*?</\1>", " ", text
    )
    paras = re.findall(r"(?is)<p\b[^>]*>(.*?)</p>", body)
    cleaned = []
    for p in paras:
        t = html.unescape(re.sub(r"(?is)<[^>]+>", "", p))
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) < 80:
            continue
        # 站点导航残留：正文首段前面常跟一段固定的功能介绍。
        for noise in (
            "AI Research Agent Add Unite.AI to your preferred sources on Google",
            "Add Unite.AI to your preferred sources on Google",
        ):
            if t.startswith(noise):
                t = t[len(noise):].strip()
        if len(t) < 80:
            continue
        # 明显是脚本残留的段落（含大段 JS 片段）直接跳过
        if "sourceURL=" in t or "openInNewContext" in t:
            continue
        cleaned.append(t)
        if len(cleaned) >= _BODY_FALLBACK_PARAS:
            break
    if not cleaned:
        return ""
    out = " ".join(cleaned).strip()
    return out


def _page_description(url, timeout=15):
    """抓文章页的 og:description（用于补全被源站截断的摘要）。"""
    try:
        r = _SESSION.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            },
        )
    except Exception:
        return ""
    if r.status_code >= 400:
        return ""
    try:
        text = r.text
    except Exception:
        return ""
    for pat in (
        r'<meta[^>]+(?:property|name)=["\'](?:og:description|twitter:description|description)["\']'
        r'[^>]*content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\']'
        r'[^>]*(?:property|name)=["\'](?:og:description|twitter:description|description)["\']',
    ):
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            desc = html.unescape(m.group(1)).strip()
            desc = re.sub(r"\s+", " ", desc)
            if len(desc) >= 20:
                return desc
    return ""


def _parse_entries(content, name, per_feed, since=None):
    """解析 RSS/Atom 内容为条目列表。

    since 为「时间窗下界」。RSS 源按发布时间倒序排列，因此当遇到第一条
    早于窗口下界的条目时，后续条目只会更旧，可直接停止扫描。

    早期实现固定只取每源前 per_feed 条（per_feed=12）。但 OpenAI、
    IEEE Spectrum、InfoQ 等源的 feed 常有 20+ 条，排在第 13 条之后的
    内容会因截断而**永远抓不到**（每轮都取同样的前 12 条），导致
    时间窗内（默认 30 天）的资讯被整体漏采。故改为「扫到时间窗边界为止」。
    """
    d = feedparser.parse(content)
    items = []
    dropped = 0
    page_fallback_used = 0
    body_fallback_used = 0
    stale_streak = 0
    for e in getattr(d, "entries", []):
        title = _clean_title(e.get("title") or "")
        link = (e.get("link") or "").strip()
        if not title or not link:
            continue
        dt = _to_local(e.get("published_parsed") or e.get("updated_parsed"))
        # feed 大体按时间倒序：越过时间窗下界后，后面的条目通常只会更旧。
        # 少数源存在个别乱序，故允许连续 _STALE_TOLERANCE 条超窗条目后才停止，
        # 避免因单条乱序而提前截断、漏掉后面的新条目。
        if since is not None and dt < since:
            stale_streak += 1
            if stale_streak >= _STALE_TOLERANCE:
                break
            continue
        stale_streak = 0
        summary = _entry_summary(e, title)
        # 摘要仍停在半句时（如 ML Mastery 的 RSS 只给截断版 summary），
        # 退回文章页取完整 og:description 补全。
        if (
            summary
            and not _is_complete(summary)
            and name in _PAGE_FALLBACK_SOURCES
            and page_fallback_used < _PAGE_FALLBACK_MAX
        ):
            desc = _page_description(link)
            # 页面描述即使更短也更有价值：它是完整句，
            # 而 RSS 的 summary 停在半句上（译文也会半句、丢事实）。
            if desc and _is_complete(desc):
                summary = desc
                page_fallback_used += 1
        # 摘要仍停在「半句数字」时（如 Unite.AI 按固定字符数截断，
        # 落在小数点中间："...compared with $27."），og:description
        # 同样被截断，只能取文章页正文前几段补全。
        if (
            summary
            and _ends_with_half_number(summary)
            and name in _BODY_FALLBACK_SOURCES
            and body_fallback_used < _BODY_FALLBACK_MAX
        ):
            body = _page_body_intro(link)
            if body and _is_complete(body) and len(body) > len(summary):
                summary = body
                body_fallback_used += 1
        if not is_ai_relevant(title, summary, name):
            dropped += 1
            continue
        items.append(
            {
                "title": title,
                "summary": summary,
                "link": link,
                "source": name,
                "dt": dt,
            }
        )
    if dropped:
        print(f"[fetcher] {name} 过滤掉 {dropped} 条非 AI 相关内容", flush=True)
    if page_fallback_used:
        print(
            f"[fetcher] {name} 用文章页补全 {page_fallback_used} 条半句摘要",
            flush=True,
        )
    if body_fallback_used:
        print(
            f"[fetcher] {name} 用文章页正文补全 {body_fallback_used} 条截断摘要",
            flush=True,
        )
    return items


def _fetch_one(name, url, per_feed, since=None):
    """抓取单个源；对限流/服务端错误做有限次退避重试。"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        # 部分站点（如 IEEE Spectrum）在 Accept 显式声明 rss+xml 时返回 403，
        # 这里用通配 Accept + Referer，兼容性最好。
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    # 按源覆盖 UA（部分源的 WAF 会针对特定 UA 指纹拦截）
    if name in _SOURCE_UA:
        headers["User-Agent"] = _SOURCE_UA[name]
    timeout = SOURCE_TIMEOUT.get(name, PER_FEED_TIMEOUT)
    last_status = None
    for attempt in range(_RETRY_TIMES + 1):
        try:
            r = _SESSION.get(
                url,
                timeout=timeout,
                headers={**headers, "Referer": f"https://{url.split('/')[2]}/"},
                allow_redirects=True,
            )
        except Exception as ex:  # noqa
            # 网络层异常（TLS 断连/超时/重置）多为偶发，退避后重试若干次
            if attempt < _RETRY_TIMES:
                print(
                    f"[fetcher] 源连接异常 {name}（第 {attempt + 1} 次）: {ex}，重试中",
                    flush=True,
                )
                time.sleep(_RETRY_SLEEP)
                continue
            print(f"[fetcher] 源失败 {name}: {ex}", flush=True)
            return []

        last_status = r.status_code
        if r.status_code < 400:
            try:
                return _parse_entries(r.content, name, per_feed, since=since)
            except Exception as ex:  # noqa
                print(f"[fetcher] 源解析失败 {name}: {ex}", flush=True)
                return []

        if r.status_code not in _RETRY_STATUS:
            break
        # 429 = IP 级封禁，重试无意义，只试一次即放弃
        max_attempts = _RETRY_TIMES_429 if r.status_code == 429 else _RETRY_TIMES
        if attempt >= max_attempts:
            break
        # 限流类响应通常持续存在，退避后只做有限次重试，避免拖慢整轮
        time.sleep(_RETRY_SLEEP)

    print(f"[fetcher] 源跳过 {name}: HTTP {last_status}", flush=True)
    return []


def fetch_all(per_feed=12, since=None):
    """并发抓取所有源，整体受 OVERALL_TIMEOUT 硬上限保护，避免单源卡死。

    since 传入时间窗下界（datetime）：各源按发布时间倒序扫描，
    越过该下界即停止，避免固定条数上限导致时间窗内的条目被永久漏采。

    超时处理：as_completed 抛 TimeoutError 后不再 yield 结果，但这些
    future 仍会在后台跑完。旧实现直接 return，等于把「慢源已成功抓到的
    数据」白白丢掉，导致这些源本轮显示 0 条（被误判为信源静默）。
    现在超时后进入收尾等待：给剩余任务最多 GRACE_TIMEOUT 秒，
    期间完成的任务结果照常收集。
    """
    out = []
    with ThreadPoolExecutor(max_workers=len(FEEDS)) as ex:
        futures = {
            ex.submit(_fetch_one, n, u, per_feed, since): n for n, u in FEEDS
        }
        try:
            for fut in as_completed(futures, timeout=OVERALL_TIMEOUT):
                try:
                    out.extend(fut.result())
                except Exception:  # noqa
                    pass
        except Exception:  # noqa
            # 超时后不直接放弃：给仍在运行的任务一个收尾窗口。
            # 注意 future.cancel() 对已在运行的任务无效（只对未启动的
            # 任务生效），所以这里改为等待它们自然结束并收集结果。
            pending = [f for f in futures if not f.done()]
            if pending:
                print(
                    f"[fetcher] 整体超时，{len(pending)} 个源进入收尾等待"
                    f"（最多 {GRACE_TIMEOUT}s）",
                    flush=True,
                )
                deadline = time.time() + GRACE_TIMEOUT
                for f in pending:
                    remaining = deadline - time.time()
                    if remaining <= 0:
                        break
                    try:
                        out.extend(f.result(timeout=remaining))
                    except Exception:  # noqa
                        continue

    # ---- 空结果补抓 ----
    # 本轮抓不到内容的源，若不是被 429 限流（IP 级封禁，重试无意义），
    # 则再单独补抓一次 —— 这些源多为偶发 TLS 断连或首次冷启动握手慢，
    # 补抓后通常能恢复，避免把偶发网络抖动误判为信源失效。
    got = {r["source"] for r in out}
    empty = [(n, u) for n, u in FEEDS if n not in got and n != "VentureBeat"]
    if empty:
        print(
            f"[fetcher] 本轮空结果源补抓: {', '.join(n for n, _ in empty)}",
            flush=True,
        )
        for name, url in empty:
            try:
                got_items = _fetch_one(name, url, per_feed, since)
            except Exception:  # noqa
                continue
            if got_items:
                print(f"[fetcher] 补抓恢复 {name}: {len(got_items)} 条", flush=True)
                out.extend(got_items)
    return out


def make_id(link):
    return hashlib.md5(link.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    items = fetch_all()
    print(f"抓取到 {len(items)} 条")
    for it in items[:3]:
        print("-", it["source"], it["dt"].strftime("%Y-%m-%d %H:%M"), it["title"][:60])
