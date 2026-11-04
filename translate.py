"""
翻译模块：英文 -> 简体中文

三级策略（按优先级，保证受限网络下仍能出译文）：
  1. NLLB-200（facebook/nllb-200-distilled-600M）—— 本地离线，质量最佳
  2. Marian opus-mt-en-zh —— 本地离线备用，速度快但质量一般
  3. 返回原文并标记 translated=False

说明：外部在线翻译服务（Google / MyMemory / Bing / DeepL）在当前沙箱网络下
均不可达（超时 / 额度耗尽 / 返回空响应），因此全部走离线模型，
并通过「多模型 + 结果清洗」保证译文可读。
"""
import os
import re
import threading
import time

import torch

from zh_t2s import to_simplified

# 充分利用多核 CPU（沙箱 32 核），显著加快批量翻译。
# 实测 16 线程在 batch 解码上优于 32 线程（线程争抢反而拖慢），故取 min(16, 核数)。
try:
    _CORES = len(os.sched_getaffinity(0))
except AttributeError:
    _CORES = os.cpu_count() or 8
torch.set_num_threads(max(1, min(16, _CORES)))

# bfloat16 是否可用（实测探测，首次调用时填充）
_BF16 = None

BASE = os.path.dirname(os.path.abspath(__file__))
NLLB_DIR = os.path.join(BASE, "models", "nllb-200-600M")
# bf16 预转换权重目录（存在则优先）。
#
# 背景：沙箱 cgroup 内存上限仅 8GB。若直接用 fp32 checkpoint 加载，
# transformers 会先把 1.4B 参数按 fp32 载入（约 2.8GB），再转换到 bf16，
# 转换期峰值可达 5GB+，叠加上译调度器与抓取协程极易触发 OOM kill
# （线上表现为发布后 404 / 进程被 killed）。
#
# 预转换好的 bf16 权重（safetensors 分片）直接就是目标 dtype，
# 加载峰值约为其本身大小（2.8GB），显著降低 OOM 风险。
NLLB_BF16_DIR = os.path.join(BASE, "models", "nllb-200-600M-bf16")
if os.path.exists(os.path.join(NLLB_BF16_DIR, "model.safetensors.index.json")):
    NLLB_DIR = NLLB_BF16_DIR
MARIAN_DIR = os.path.join(BASE, "models", "opus-mt-en-zh")

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HOME", os.path.join(BASE, ".hf_cache"))
# 关闭 transformers/huggingface 的进度条与告警噪声。
# NLLB 模型有 512 个分片，加载时的 tqdm 进度会往 stdout 灌进
# 数百 KB 的 ANSI 控制序列，把真正的抓取/翻译日志完全淹没，
# 单次启动即可产生 300KB+ 日志，巡检时几乎无法阅读。
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")

# NLLB 目标语言代码
NLLB_TARGET = "zho_Hans"

# 单次 NLLB 推理的子批大小。
# 显存/内存占用随「批大小 × beam 数 × 生成长度」增长；容器内存上限 8GB，
# 一次推理上百条会被 oom_kill 静默杀掉。取 8 条为一批：内存峰值低且可控，
# 同时保留足够的并行度，110 条的批量翻译可在数分钟内完成。
NLLB_BATCH_SIZE = 8

_state = {
    "nllb": {"model": None, "tok": None, "tried": False},
    "marian": {"model": None, "tok": None, "tried": False},
}
_load_lock = threading.Lock()

_CJK = re.compile(r"[\u4e00-\u9fff]")


# ---------------- 模型加载 ----------------
def _load_nllb():
    with _load_lock:
        if _state["nllb"]["tried"]:
            s = _state["nllb"]
            return s["model"], s["tok"]
        _state["nllb"]["tried"] = True
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

            tok = AutoTokenizer.from_pretrained(NLLB_DIR, local_files_only=True)
            tok.src_lang = "eng_Latn"
            # bfloat16 在 CPU 上推理较 float32 快约 7 倍，且对翻译质量影响可忽略
            dtype = torch.bfloat16 if torch.cuda.is_available() or _supports_bf16() else torch.float32
            model = AutoModelForSeq2SeqLM.from_pretrained(
                NLLB_DIR,
                local_files_only=True,
                dtype=dtype,
                # 关闭分片加载进度条：512 个分片的 tqdm 进度会往日志里
                # 灌进数百 KB 的 ANSI 噪声，淹没真正的抓取/翻译记录，
                # 单次启动日志就能到 300KB，极易撑爆巡检时的日志读取。
                low_cpu_mem_usage=True,
            )
            model.eval()
            _state["nllb"]["tok"] = tok
            _state["nllb"]["model"] = model
            print(
                f"[translate] NLLB-200 加载成功（主引擎, dtype={dtype}）", flush=True
            )
            return model, tok
        except Exception as e:  # noqa
            print(f"[translate] NLLB-200 加载失败: {e!r}", flush=True)
            return None, None


def _supports_bf16():
    """检测当前 CPU 是否能高效执行 bfloat16 算子。

    通过一次极小的 bfloat16 矩阵乘做实测——比读取 flags 更可靠
    （不同发行版的 flag 名称不一致）。
    """
    global _BF16
    if _BF16 is not None:
        return _BF16
    try:
        a = torch.randn(64, 64, dtype=torch.bfloat16)
        t0 = time.time()
        (a @ a).sum().item()
        # 若走软件模拟回退，单次矩阵乘会异常缓慢
        _BF16 = (time.time() - t0) < 1.0
    except Exception:
        _BF16 = False
    print(f"[translate] bfloat16 加速可用={_BF16}", flush=True)
    return _BF16


def _load_marian():
    with _load_lock:
        if _state["marian"]["tried"]:
            s = _state["marian"]
            return s["model"], s["tok"]
        _state["marian"]["tried"] = True
        try:
            from transformers import MarianMTModel, MarianTokenizer

            tok = MarianTokenizer.from_pretrained(
                "Helsinki-NLP/opus-mt-en-zh", cache_dir=MARIAN_DIR, local_files_only=True
            )
            model = MarianMTModel.from_pretrained(
                "Helsinki-NLP/opus-mt-en-zh", cache_dir=MARIAN_DIR, local_files_only=True
            )
            model.eval()
            _state["marian"]["tok"] = tok
            _state["marian"]["model"] = model
            print("[translate] Marian opus-mt 加载成功（备用引擎）", flush=True)
            return model, tok
        except Exception as e:  # noqa
            print(f"[translate] Marian 加载失败: {e!r}", flush=True)
            return None, None


# ---------------- 译文清洗 ----------------
_JUNK_PATTERNS = [
    re.compile(r"^\s*[-–—]*\s*"),
    re.compile(r"\s*[-–—]\s*$"),
    # 量词后多余的助词："一个的小脸" -> "一个小脸"、"它们的的" -> "它们的"
    re.compile(r"(个)的(?![确年月])"),
    re.compile(r"的的(?![年月])"),
    re.compile(r"了了+"),
    re.compile(r"是是+"),
]

# 半角标点 -> 全角（仅在中文语境中转换，保留英文/数字间原样）
_PUNCT_MAP = {
    ",": "，",
    ":": "：",
    ";": "；",
    "?": "？",
    "!": "！",
}
_CJK = re.compile(r"[\u4e00-\u9fff]")
# 这些英文语境中半角标点应保留
_KEEP_HALF = re.compile(
    r"[A-Za-z0-9][,;:?!]|[,;:?!][A-Za-z0-9]"
)
# 句末句号：中文语境应换成全角句号，但小数点/缩写号需保留（如 4.73、U.S.）
_SENTENCE_END_DOT = re.compile(r"(?<=[^0-9A-Za-z])\.(?=\s|$)")

# 英文专名 / 机构 / 度量衡的常见缩写：这些词的结尾句号属于缩写本身，
# 不能当成句末句号转成全角（如「Inc. 已经」「U.S. 监管」）。
_ABBR_WORDS = (
    "inc", "corp", "ltd", "llc", "plc", "co", "st", "mr", "mrs", "ms", "dr",
    "prof", "sr", "jr", "vs", "etc", "e.g", "i.e", "u.s", "u.k", "a.m", "p.m",
    "no", "fig", "vol", "pp", "al",
)


def _is_abbr_dot(text, i):
    """判断 text[i] 处的句号是否属于英文缩写（而非句末句号）。

    取句号前紧邻的英文单词（含内部点，如 U.S.），命中常见缩写表则返回 True。
    """
    if i <= 0:
        return False
    j = i
    while j > 0 and (text[j - 1].isalnum() or text[j - 1] == "."):
        j -= 1
    word = text[j:i].strip(".").lower()
    if not word:
        return False
    return word in _ABBR_WORDS


def _normalize_punct(text):
    """把中文语境中的半角标点转成全角，英文语境保持半角。

    判定规则：标点两侧只要有一侧是中文，即视为中文语境，转全角
    （如「据报道,OpenAI」->「据报道，OpenAI」）；
    两侧都是英文/数字时（如 "Claude,Codex"、"1,000"）保持半角。

    例外：「两个拉丁词之间的半角逗号」在中文句子里一定是译文残留。
    模型照搬英文原文的并列结构时，会留下「AI,ML 和数据工程」这类
    半角逗号——它既不是英文语境（整句是中文），也不是千分位
    （两侧是字母而非数字），留在中文正文里排版上是错的。
    故此处单独识别：两侧均为字母的半角逗号，且所在文本含中文时，
    统一转全角「，」。千分位（数字,数字）不受影响。
    """
    if not text:
        return text
    in_zh = bool(_CJK.search(text))
    out = list(text)
    for i, ch in enumerate(out):
        if ch not in _PUNCT_MAP:
            continue
        prev = out[i - 1] if i > 0 else ""
        nxt = out[i + 1] if i + 1 < len(out) else ""
        prev_cjk = bool(_CJK.match(prev)) if prev else False
        nxt_cjk = bool(_CJK.match(nxt)) if nxt else False
        if prev_cjk or nxt_cjk:
            # 中文语境：转全角
            out[i] = _PUNCT_MAP[ch]
            continue
        # 两侧都是英文/数字 -> 英文语境，保持半角
        if prev.isascii() and prev.isalnum() and nxt.isascii() and nxt.isalnum():
            # 例外：两个拉丁词之间的半角逗号 + 整段含中文 => 译文残留，
            # 转全角（千分位是数字,数字，已被上面的 isalnum 分支排除）。
            if (
                in_zh
                and ch == ","
                and prev.isascii()
                and prev.isalpha()
                and nxt.isascii()
                and nxt.isalpha()
            ):
                out[i] = _PUNCT_MAP[ch]
            continue
    return "".join(out)


def _normalize_sentence_end(text):
    """中文译文的句末句号统一为全角句号，避免出现「中文+.」的混排。

    保护规则：小数点（4.73）、版本号（1.0）、缩写（U.S.）保持半角。

    2026-11-01 21:00 巡检补充：此前只判断「前一个字符是中文」，
    导致「Web 搜索 API.可通过」「954%的 ROI. 看看」这类
    「英文/数字 + 半角句号 + 中文」的句末句号漏转，
    在正文里表现为中英混排的句读断裂。
    现补两条规则：
      1) 小数点只在「前后都是数字」时保留半角（4.73、27.3）；
         若句号后不是数字，则按句末句号处理（「iOS 27.3.苹果表示」）。
      2) 句号后（可隔空格）紧跟中文时转全角「。」；
         例外是句号属于英文缩写（Inc. / U.S. 等），此时保持半角并补空格。
    """
    if not text:
        return text
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch != ".":
            out.append(ch)
            i += 1
            continue
        prev = text[i - 1] if i > 0 else ""
        nxt = text[i + 1] if i + 1 < n else ""
        # 小数点 / 版本号：前后都是数字 -> 保留半角（4.73、27.3）
        if prev.isdigit() and nxt.isdigit():
            out.append(ch)
            i += 1
            continue
        # 前面是中文 -> 中文句号
        if _CJK.match(prev or " "):
            out.append("。")
            i += 1
            continue
        # 半角句号紧跟英文大写字母（中间无空格）：模型吞掉了英文原文里
        # 句号后的空格，形成「近 80%.Pando 现在……」「以下）.OpenAI Pando
        # 是什么？」这种中英粘连。
        # 判定：句号前不是拉丁字母（排除 U.S.A、Dr.Smith 这类缩写点），
        # 且句号后紧跟 ASCII 大写字母。此时该句号是句末句号，
        # 转全角「。」，与中文句读一致。
        if nxt and "A" <= nxt <= "Z" and prev and not (prev.isascii() and prev.isalpha()):
            out.append("。")
            i += 1
            continue
        # 整句以 "." 结尾且前文含中文 -> 中文句号
        if not nxt and _CJK.search(text[:i]):
            out.append("。")
            i += 1
            continue
        # 句号后（可隔空格）紧跟中文 -> 中文句末，转全角
        j = i + 1
        while j < n and text[j].isspace():
            j += 1
        after = text[j] if j < n else ""
        if after and _CJK.match(after):
            if _is_abbr_dot(text, i):
                # 缩写点（Inc. / U.S.）：保持半角，与后接中文之间补一个空格
                out.append(ch)
                out.append(" ")
            else:
                out.append("。")
            i = j
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _fix_quote_pairs(text):
    """修复译文中的引号配对问题。

    NLLB 偶发漏掉收尾引号，导致译文里出现奇数个直引号（悬空引号）。
    这里把直引号成对转换为中文直角引号；
    若原始引号数为奇数，说明原文漏了收尾引号，在末尾补一个。

    2026-11-03 10:00 巡检：输出形态由中文弯引号改为直角引号。
    原因是站内排版惯例——模型原生输出的中文引号就是直角引号
    （全站 64 条摘要用直角引号，仅 4 条因英文原文带直引号而留存弯引号），
    弯引号属于少数派，读起来与全站不一致。
    同时校验脚本的引号门禁只校验直角引号配对，改用直角引号后
    这类条目才纳入门禁覆盖范围。
    """
    if not text or '"' not in text:
        return text
    n = text.count('"')
    if n == 0:
        return text

    out = []
    open_q = True
    for ch in text:
        if ch == '"':
            out.append("「" if open_q else "」")
            open_q = not open_q
        else:
            out.append(ch)
    res = "".join(out)
    # 原始引号数为奇数：说明原文漏了收尾引号，补在句末
    if n % 2 == 1:
        res = res.rstrip()
        res += "」"
    return res


def _normalize_curly_quotes(text):
    """把中文弯引号「“」「”」统一成站内通用的直角引号「「」「」」。

    2026-11-03 10:00 巡检新增。
    站内排版惯例是直角引号（全站绝大多数摘要用直角引号），弯引号只
    出现在「英文原文自带直引号」的少数条目上，读起来与全站不一致。
    这里做一次成对替换，让全站引号风格统一。

    安全性：仅在文本同时含弯引号且不含直角引号时才替换——若两者共存，
    说明存在嵌套引号，替换会破坏层级关系，此时保持原样。
    """
    if not text:
        return text
    if ("“" not in text) and ("”" not in text):
        return text
    if ("「" in text) or ("」" in text):
        # 弯引号与直角引号共存，视为嵌套引号，保持原样不动。
        return text
    return text.replace("“", "「").replace("”", "」")


def _clean_zh(text):
    """清理译文的冗余符号、异常空格与重复片段。"""
    if not text:
        return ""
    t = text.strip()
    # NLLB 把英文破折号译成 " - - "，中文语境还原为中文破折号「——」
    t = re.sub(r"\s+-\s+-\s+", "——", t)
    for p in _JUNK_PATTERNS:
        t = p.sub("", t)
    # 折叠紧邻的重复词（机器翻译常见 "公司公司"、"人类人类"）
    t = re.sub(r"([\u4e00-\u9fff]{2,4})\1{1,}", r"\1", t)
    # 折叠紧邻的重复虚词（NLLB 常见 "将将"、"的的"、"了了"、"在在"）。
    # 只针对高频虚词——泛用「任意单字去重」会误伤正常叠词
    # （如「源源不断」「软乎乎」「短短」被砍成「源不断」「软乎」「短」），
    # 因此这里用虚词白名单，其余单字重复一律保留。
    _DUP_FUNCTION_WORDS = (
        "将", "的", "了", "在", "是", "和", "就", "也", "都", "很",
        "不", "有", "把", "被", "会", "能", "要", "说", "让", "使",
        "对", "从", "与", "及", "其", "这", "那", "些", "个", "只",
        "每", "更", "已", "才", "再", "又", "并", "则", "如", "因",
        "但", "却", "该", "于", "为", "以", "所", "其", "之", "或",
    )
    # 2026-11-03 07:00 巡检修复：「能」在白名单里，会把「智能能力」
    # 折成「智能力」、「智能能耗」折成「智能耗」——中文里「智能」「性能」
    # 「能耗」本身就是以「能」结尾的词，紧跟一个「能」字时并非翻译重复。
    # 判定方式：若被折叠的「能」字后面紧跟的字能与其构成常用词
    # （能力/性能/能耗/产能/效能/智能/可能/本能/动能…），则不折叠。
    _DUP_KEEP_NEXT = (
        "能力", "性能", "能耗", "产能", "效能", "智能", "可能", "本能",
        "动能", "效能", "机能", "万能", "才能", "功能", "性能", "产能",
    )

    def _fold_dup(m):
        w = m.group(0)
        c = w[0]
        if c not in _DUP_FUNCTION_WORDS:
            return w
        # 「能」类字要检查下一个字：构成常用词时不折叠。
        # m.end() 指向被折叠片段之后的位置，即第二个字的起始处。
        nxt = t[m.end():m.end() + 1] if m.end() < len(t) else ""
        if c == "能" and (c + nxt) in _DUP_KEEP_NEXT:
            return w
        return c

    t = re.sub(r"([\u4e00-\u9fff])\1", _fold_dup, t)
    # 折叠被标点分隔的重复短语（NLLB 长文本退化常见 "美国，美国，美国"、
    # "请问，请问，请问"），同一片段连续出现 3 次以上时只保留一次
    t = re.sub(
        r"([\u4e00-\u9fffA-Za-z]{2,12})([，、,]\s*\1){2,}",
        r"\1",
        t,
    )
    # 标点规范化：中文语境半角 -> 全角
    t = _normalize_punct(t)
    # 括号风格：中文语境统一为全角，与站内既有排版一致。
    t = _normalize_cjk_parens(t)
    # 句末句号：中文句号统一为全角
    t = _normalize_sentence_end(t)
    # 品牌还原后残留的冗余后缀
    for bad, good in _REDUNDANT_SUFFIX:
        if bad in t:
            t = t.replace(bad, good)
    # 引号内多余空格：NLLB 常产出 " 自动" 这种中英混排空格
    t = re.sub(r'"\s+([^"]*?)\s+"', r'"\1"', t)
    # 引号配对：NLLB 偶发漏掉收尾引号（译文里出现奇数个直引号）。
    # 中文语境用弯引号成对包裹更规范；奇数时补上收尾引号，
    # 避免读者看到悬空的引号。
    t = _fix_quote_pairs(t)
    # 弯引号统一为直角引号（站内惯例），与 _fix_quote_pairs 紧邻执行：
    # 先把直引号转成引号对，再统一引号形态。
    t = _normalize_curly_quotes(t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    # 中文标点与英文之间不强行加空格，但去掉中文逗号后的空格
    t = re.sub(r"([\uff0c\u3002\uff1b\uff1a\u3001\uff01\uff1f])\s+", r"\1", t)
    t = re.sub(r"\s+([\uff0c\u3002\uff1b\uff1a\u3001\uff01\uff1f])", r"\1", t)
    # 中英/中数之间补空格：离线模型输出「允许NAACP关于」「在iOS 27.3中」
    # 这类粘连，中文排版惯例要求中西文之间留一个空格。
    # 只在中文与拉丁字母/数字的交界处补，不动纯英文片段内部。
    t = _fix_cjk_latin_spacing(t)
    # 繁体归一：NLLB 偶尔输出繁体（实测「頭號議題」），统一转简体。
    # 放在最后一步，保证前面所有基于简体形态的规则都已生效。
    t = to_simplified(t)
    return t.strip()


def _clean_title_zh(text):
    """清洗中文标题。

    与摘要不同，中文标题的惯例是不加句末标点。
    离线模型常把英文标题末尾的句号一并译成「。」，
    形成「OpenAI 公布了社区安全报告和新的青少年武器限制。」这类
    带尾句号的标题，与人工定稿的 178 条覆盖标题风格不一致。
    这里统一去掉标题末尾的「。」。

    问号「？」与感叹号「！」保留：中文标题本身可以是疑问句
    （如「这对你意味着什么？」），去掉会改变语义。
    """
    if not text:
        return ""
    t = _clean_zh(text)
    # 去掉尾句号（可能有多个，如「……。」，只去最外层）
    while t.endswith("。"):
        t = t[:-1].rstrip()
    return t


def _fix_cjk_latin_spacing(text):
    """在中文字符与拉丁字母/数字的交界处补一个空格。

    中文排版惯例要求中西文之间留空隙。离线模型输出「允许NAACP关于」
    「4.65亿美元」这类粘连，读起来像乱码。
    """
    if not text:
        return text
    t = re.sub(r"(?<=[\u4e00-\u9fff])(?=[A-Za-z0-9])", " ", text)
    t = re.sub(r"(?<=[A-Za-z0-9])(?=[\u4e00-\u9fff])", " ", t)
    # 补完后再去掉标点前后多余空格
    t = re.sub(r"([\uff0c\u3002\uff1b\uff1a\u3001\uff01\uff1f])\s+", r"\1", t)
    t = re.sub(r"\s+([\uff0c\u3002\uff1b\uff1a\u3001\uff01\uff1f])", r"\1", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    # 中文与中文之间不留空格（中文排版惯例）。
    # 术语还原把英文地名/品牌替换成中文后，原文残留的空格会形成
    # 「在 乌兰察布 AI 数据中心」这类粘连，需在此收口。
    t = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", t)
    # 数字与存储/网络单位缩写之间补空格：「1PB」→「1 PB」、
    # 「57TB」→「57 TB」、「10Gbps」→「10 Gbps」。
    # 科技资讯里这类单位极密集（PB/TB/GB/MB/KB/MiB/Gbps），
    # 粘连后数字与单位难以一眼分开。
    t = re.sub(
        r"(?<=\d)\s*(?=(?:PB|TB|GB|MB|KB|MiB|GiB|TiB|Gbps|Mbps)\b)",
        " ", t)
    return t.strip()


# ---------- 术语还原 ----------
# 离线模型会把品牌名音译（OpenAI→"开通AI"、Nvidia→"尼维迪亚"）。
# 这里用原文标题做锚点，把译文中出现的音译/错译片段还原为标准写法。
BRAND_TERMS = [
    # (标准写法, 可能出现的译法/音译)
    # 2026-11-02 19:00 巡检新增：「开通 AI」带空格形态此前漏登记，
    # 导致品牌还原整条失效（模型输出「开通 AI 的 Lehane」还原不回 OpenAI）。
    # 离线模型在「开通AI」与「开通 AI」之间不稳定，同一词条两次抓取可得到
    # 不同形态，因此空格形态必须一并登记。
    ("OpenAI", ["开通AI", "开通 AI", "开放AI", "开放 AI", "开放人工智能",
                "OpensAI", "OpneAI", "欧盆AI",
                "开放国际", "开放国际协会", "开放艾", "美国国际会计学会"]),
    # 「anthropic」一词本义是「人类的」，离线模型常直接意译成
    # 「人类」/「人类公司」/「人类论文说」，把公司名彻底丢掉。
    # 因此把这几种意译形态也列入还原表。
    # 「Anthropic Engineer」这类「公司名 + 职务」的搭配，模型会把 Anthropic
    # 意译成「人类的」，产出「人类工程师」——公司名彻底丢失，故补入还原表。
    ("Anthropic", ["安特罗皮克", "人类学", "安思罗匹克", "安索匹克", "anthropic公司",
                   "大赦国际", "人类学国际职业介绍所", "人类学国际",
                   "人类公司", "人类组织"]),
    ("Google", ["谷歌", "古歌", "哥OGLE"]),
    ("Microsoft", ["微软", "微软公司"]),
    ("Meta", ["元公司", "梅塔", "Facebook母公司"]),
    ("Nvidia", ["尼维迪亚", "英伟达", "NVIDIA公司", "恩维迪亚"]),
    # 2026-11-03 14:00 巡检：PATEO（车联网 Tier1）被音译成「帕蒂奥」，
    # 中文读者无法定位公司。保留英文品牌名。
    ("PATEO", ["帕蒂奥"]),
    # ── 2026-11-03 03:00 巡检新增 ──
    # 大模型品牌：模型常把它们音译成「基米」「基米尼」「杰姆」等，
    # 音译形态不稳定，必须逐一登记才能还原回标准写法。
    ("Kimi", ["基米", "奇米", "基米奇"]),
    ("GLM", ["基姆", "智谱GLM", "格姆"]),
    ("Qwen", ["千问", "通义千问", "权问"]),
    ("GPT", ["GPΤ", "基皮提"]),
    # 「Deep Principle」是发布 Hydrogen-1.0 的机构名，
    # 模型把它意译成「深度原理」「深度原则」，品牌识别度尽失。
    ("Deep Principle", ["深度原理", "深度原则", "深刻原理"]),
    # SGLang 是开源推理框架，模型常译成「SGL 语言」「速格朗」。
    ("SGLang", ["SGL语言", "速格朗", "sg朗"]),
    # Z.ai 是智谱的国际化品牌名，模型常把 "Z.ai's" 译成 "Z.ais"。
    ("Z.ai", ["Z.ais", "智谱AI"]),
    # NVIDIA 的 AI 工作站产品线「DGX Spark」。模型常把 Spark 当普通词意译成
    # 「火花/引发光」，产品名就丢了，故单独还原。
    ("DGX Spark", ["火花", "引发光", "星火", "火花工作台"]),
    ("Spark", ["引发光", "火花"]),
    ("Apple", ["苹果公司", "苹果"]),
    # 2026-11-03 09:00 巡检新增：Salesforce 是美国头部 CRM 云软件公司，
    # 模型按普通英文词意译成「销售力量」，标题主语完全错位
    # （「Salesforce Agrees to Buy Cresta」→「销售力量同意购买 Cresta」）。
    # 必须保留英文品牌名。
    ("Salesforce", ["销售力量", "销售团队", "销售力"]),
    # 2026-11-03 16:00 巡检新增：Windward 是以色列航运 AI 公司
    # （海上可见性 / 船舶识别），模型按普通英文词意译成「风向」，
    # 标题主语完全错位，中文读者也无法定位这家公司。
    ("Windward", ["风向", "风舵", "顺风"]),
    ("Apple Intelligence", ["苹果情报", "果智能", "苹果智能", "苹果情报公司", "苹果情报部"]),
    ("Amazon", ["亚马逊", "亚马孙"]),
    ("Tesla", ["特斯拉", "泰斯拉"]),
    ("Intel", ["英特尔", "因特尔"]),
    ("DeepMind", ["深度思维", "深度智力", "谷歌深明"]),
    ("Hugging Face", ["拥抱脸", "抱脸"]),
    ("Linux", ["Linux", "林纳斯"]),
    ("Windows", ["Windows", "视窗", "窗户系统"]),
    ("Claude", ["克劳德", "克劳德模型"]),
    ("Gemini", ["双子座", "杰米尼", "Gemini", "基米尼"]),
    # Gemini 4 的机器人版本代号 Argon：模型常把 "Argon" 译成化学元素「氩」，
    # 需还原为产品代号，否则标题会变成无意义的「Gemini 4氩机器人」。
    ("Argon", ["氩气", "氩", "阿贡", "阿尔贡", "Argon"]),
    # Gemini 4 的版本代号：模型会把 Carbon 译成化学元素「碳」，
    # 需还原为产品代号，否则标题会变成「Gemini 4碳」。
    ("Carbon", ["Carbon"]),
    ("ChatGPT", ["聊天 GPT", "聊天GPT", "ChatGPT", "查特格博特"]),
    ("Mistral", ["米斯特拉尔", "mistral"]),
    ("Cohere", ["科赫里", "cohere", "联合项目", "协调项目", "聚合项目"]),
    # 「困惑性」「困惑」也是 NLLB 对 Perplexity 的直译产物，必须还原为品牌名。
    ("Perplexity", ["困惑度", "困惑性", "困惑", "珀plexity"]),
    ("Databricks", ["数据砖块", "Databricks"]),
    ("Copilot", ["副驾驶", "领航员"]),
    ("Kubernetes", ["库伯内特斯"]),
    ("PyTorch", ["PyTorch", "派ytorch"]),
    ("LangChain", ["LangChain", "兰链"]),
    ("Snowflake", ["雪花", "Snowflake"]),
    ("ByteDance", ["字节跳动"]),
    ("Tencent", ["腾讯"]),
    ("Alibaba", ["阿里巴巴", "阿里"]),
    ("Baidu", ["百度"]),
    ("Netflix", ["网飞", "奈飞"]),
    ("SpaceX", ["太空探索技术公司", "SpaceX"]),
    ("Nscale", ["恩斯凯尔", "Nscale"]),
    ("Vercel", ["维尔塞尔", "Vercel"]),
    ("Wired", ["连线杂志", " Wired", "连线", "电线"]),
    ("Oracle", ["甲骨文组织", "甲骨文"]),
    ("IBM", ["国际商业机器", "IBM"]),
    ("Samsung", ["三星", "三星电子"]),
    ("Qualcomm", ["高通", "QUALCOMM"]),
    ("xAI", ["叉AI", "xAI公司"]),
    # ── 2026-11-03 05:00 巡检新增 ──
    # Sierra（智能体公司）/ Ghostwriter（其产品）/ Agent Studio（平台）
    # 三个专名被离线模型分别意译成「塞拉拉」「幽灵作家」「智能体工作室」，
    # 中文读者无法与英文原文对应，统一还原为英文原名。
    ("Sierra", ["塞拉拉"]),
    ("Ghostwriter", ["幽灵作家"]),
    ("Agent Studio", ["智能体工作室"]),
    # xAI 的两个 Grok Bot 产品名：Data Bot / Shared Bot。
    ("Data Bot", ["数据机器人"]),
    ("Shared Bot", ["共享机器人"]),
    ("Mistral AI", ["米斯特拉尔AI"]),
    ("Cloudflare", ["云飞拉", "云flare", "Cloudflare"]),
    ("Chronon", ["慢性", "克罗农", "Chronon"]),
    ("Antigravity", ["反重力", "安提重力", "Antigravity"]),
    ("Le Chonk", ["勒昌克", "Le Chonk"]),
    ("Prime Intellect", ["智力"]),
    ("Samaya", ["萨马雅"]),
    ("Baseten", ["巴塞顿", "贝塞顿"]),
    ("TokenEconomizer", ["代币经济学家", "token经济学家"]),
    # ---- 本轮巡检新增：音译失真 / 品牌未还原 ----
    # Cisco Talos：Talos 是威胁情报团队名，模型音译成「西斯科塔洛斯」，
    # 直接读作品牌名会让人以为是另一家公司。
    ("Cisco Talos", ["西斯科塔洛斯", "思科塔洛斯", "塔洛斯"]),
    # Powerlattice：能源基础设施公司，模型意译成「发电台」，名称丢失。
    ("Powerlattice", ["发电台", "动力格子", "电力格子"]),
    # Project Suncatcher：Google 的轨道 TPU 项目名，模型意译成「太阳捕捉器」。
    ("Project Suncatcher", ["太阳捕捉器", "太阳捕手", "追日者"]),
    # DeepMind：模型有时意译成「深思」，公司名丢失。
    ("DeepMind", ["深思", "深度心智"]),
    # Databricks：模型意译成「数据公司」，与通用词混淆。
    ("Databricks", ["数据砖", "数据公司"]),
    # Genie：DeepMind 的世界模型系列名，模型音译成「吉尼」。
    ("Genie", ["吉尼", "杰尼", "精灵"]),
    # TokenEconomizer 已在上；补充插件名在译文中的大小写粘连形态。
    ("Sophos", ["索福斯", "索弗斯"]),
    ("Pollo AI", ["波罗AI", "波罗 AI"]),
    ("Radisson", ["拉迪森", "拉迪逊"]),
    ("HiPHI", ["希菲", "海菲"]),
    # ADNOC：阿布扎比国家石油公司，简称在英文报道中直接出现。
    # 离线模型把它音译成「亚诺克」，读者完全无法识别是哪家公司。
    # 还原为通行英文简称「ADNOC」，与摘要里模型自己保留的写法一致。
    #
    # 2026-11-03 11:00 巡检修复：移除「阿布扎比国家石油」这个变体。
    # 它是合法中文名「阿布扎比国家石油公司」的前缀，替换后产出
    # 「ADNOC 公司 ADNOC」这种自相矛盾的双写形态。
    # 中文全称本身是正确译法，无需还原；只需处理音译变体。
    ("ADNOC", ["亚诺克", "阿德诺克"]),
    # Envision：远景能源（Envision Energy），模型意译成「展望」，
    # 在中文里完全读不出是公司名。还原为通行英文品牌名。
    ("Envision", ["展望", "远景能源集团"]),
    ("Ironclad", ["铁甲", "铁甲公司"]),
    ("Ollie", ["奥利"]),
    ("Sapan Pandya", ["萨潘·潘迪亚", "萨潘·潘迪亚"]),
    ("Daybreak", ["破晓", "拂晓"]),
    # 2026-11-03 07:00 巡检新增：Trajectory 是一家 AI 模型训练创业公司，
    # 模型把它意译成「轨迹」，中文里完全读不出是公司名（"轨迹"还是
    # 一个普通技术词）。用 BRAND_TERMS 还原成英文原名。
    ("Trajectory", ["轨迹"]),
    # ---- 本轮巡检新增：以下品牌此前被离线模型意译/音译失真 ----
    # 注意：意译型品牌名（Block→区块）不能用 BRAND_TERMS 的通用还原，
    # 因为「区块」在「区块链」语境下是正确的译法，会误伤。
    # 这类改用 TERM_FIXES 的原文触发词精确匹配（见下方 TERM_FIXES）。
    # Prime Intellect：模型意译成「总理智能」，完全丢失公司名。
    ("Prime Intellect", ["总理智能", "首要智力"]),
    # PageBreak（Google 的 AI 安全智能体）：模型意译成「页面破解」。
    ("PageBreak", ["页面破解", "页面中断"]),
    # Retell（语音 AI 公司）：模型音译成「雷特尔」。
    ("Retell", ["雷特尔"]),
    # Greptile（AI 代码审查公司）：模型音译成「格雷普蒂尔」。
    ("Greptile", ["格雷普蒂尔"]),
    # Clarivate（知识产权数据公司）：模型把专有名词当普通动词直译成
    # 「澄清器」，中文完全认不出是哪家公司。保留英文原名。
    ("Clarivate", ["澄清器", "澄清工具", "厘清器"]),
    # Check Point（网络安全公司）：模型音译成「检查点」。
    ("Check Point", ["检查点"]),
    # Orchestra Bio（OpenAI 收购的生物科技公司）。
    ("Orchestra Bio", ["乐队生物", "乐团生物", "管弦乐团生物"]),
    # Anima（医疗 AI 公司）：模型意译成「艾尼玛」。
    ("Anima", ["艾尼玛", "阿尼玛"]),
    # Macmillan（出版集团）：模型音译成「麦克米兰」。
    ("Macmillan", ["麦克米兰", "麦克米兰公司"]),
    # Legora（法律 AI 公司）：模型音译成「利戈拉」。
    ("Legora", ["利戈拉", "莱戈拉"]),
    # Cognizant：模型意译成「认知作用/认知形态」。
    ("Cognizant", ["认知作用", "认知形态"]),
    # Nace AI：模型意译成「纳斯 AI」。
    ("Nace AI", ["纳斯 AI", "纳斯人工智能"]),
    # DeepSeek：模型意译成「深度寻找」，完全丢失品牌名。
    ("DeepSeek", ["深度寻找"]),
    # ---- 2026-11-02 14:00 巡检新增：AI 芯片/研究机构品牌名被音译 ----
    # SemiAnalysis（AI 芯片研究机构）：模型把它意译成「半分析」，
    # 读者会误以为是一篇讲「半分析」的文章，而非机构名。
    ("SemiAnalysis", ["半分析", "半分析公司"]),
    # Ceva（AI DSP/NPU 厂商）：模型音译成「塞瓦」。
    ("Ceva", ["塞瓦"]),
    # Mobilint（韩国 AI 半导体公司）：模型音译成「莫比林特」。
    ("Mobilint", ["莫比林特"]),
    # ---- 2026-11-02 22:00 巡检新增：数据中心 / 医疗设备公司品牌失真 ----
    # Emerald AI（数据中心灵活性公司）：模型意译成「玉 AI」「黄金 AI」，
    # 中文里完全读不出是公司名，读者会当成普通名词理解。
    ("Emerald AI", ["玉 AI", "玉AI", "黄金 AI", "黄金AI", "翡翠 AI"]),
    # Signia（助听器公司）：模型音译成「索尼亚」。
    ("Signia", ["索尼亚", "西格尼亚", "希格尼亚"]),
    # Uber：模型音译成「优步」，中文里读起来像一家不相干的公司，
    # 而 Uber 在中文财经报道里通常直接保留英文原名。
    ("Uber", ["优步", "优歩"]),
    # ── 2026-11-03 06:00 巡检新增：05:40—05:54 四条 Unite.AI 条目品牌失真 ──
    # DeepSeek Harness：模型把产品名整体音译成「深度搜索带」，
    # 中文读者既认不出是 DeepSeek，也认不出 Harness 是运行框架。
    ("DeepSeek Harness", ["深度搜索带", "深度搜索框架", "深度搜索"]),
    # Omen AI：模型把公司名音译成「欧门 AI」。
    ("Omen AI", ["欧门 AI", "欧门AI", "欧门人工智能"]),
    # Aquatic Labs：模型把实验室名意译成「水力实验室」，
    # 与「水力工程」混淆，完全认不出是家传感器初创公司。
    ("Aquatic Labs", ["水力实验室", "水生实验室", "水域实验室"]),
    # LongCat：模型音译成「龙猫」，丢失模型品牌。
    ("LongCat", ["龙猫", "朗猫"]),
    # ── 2026-11-03 12:00 巡检新增 ──
    # Dreambeans（Google Labs 的个性化故事应用）：模型把品牌名意译成
    # 「梦」，标题产出「Google 带来了梦个性化 AI 故事到印度」，
    # 中文读者完全认不出这是产品名。品牌名必须保留英文原名。
    ("Dreambeans", ["梦个性化", "梦豆", "梦幻豆"]),
]

# 通用 AI 领域术语：无论原文是否出现品牌名，都按固定搭配还原。
# (需在译文中出现的错误片段, 正确写法, 触发所需的英文关键词)
TERM_FIXES = [
    # ---- 2026-11-03 02:30 巡检新增 ----
    # 1) Brave 是浏览器厂商名（Security/Privacy 浏览器），
    #    NLLB 按普通英文词意译成「勇敢」，正文里出现「勇敢软件」
    #    「勇敢指数」，中文读者无法定位公司。必须保留英文品牌名。
    ("勇敢软件", "Brave Software", ["brave software"]),
    ("勇敢指数", "Brave Index", ["brave index"]),
    ("勇敢的网络浏览器", "Brave 网络浏览器", ["brave web browser"]),
    ("勇敢浏览器", "Brave 浏览器", ["brave web browser", "brave browser"]),
    # 2) Larridin 是 AI 支出衡量创业公司名，被音译成「拉里丁」。
    ("拉里丁", "Larridin", ["larridin"]),
    # 3) discharge summary（出院小结，医疗文书）被直译成「排放总结」，
    #    语义完全相反，属医疗领域的专业性错误。
    ("排放总结", "出院小结", ["discharge summary", "discharge summaries"]),
    ("出院小结", "出院小结", ["discharge summary", "discharge summaries"]),
    # 4) "Series A"（A 轮融资）是「A 轮」不是「A 系列」。
    ("的 A 系列", "的 A 轮", ["series a"]),
    # 5) 专有名词 "chasm"（网名）被意译成单字「化」，须还原。
    # 原文是 "going by the name \"chasm\" was among the first to note..."，
    # NLLB 产出「……爱好者称之为“化”是上周晚些时候……」。
    # 用「（网名「chasm」）」替换整段称谓结构，句子才通顺。
    ("称之为“化”", "（网名「chasm」）", ["chasm"]),
    ("名为“化”", "名为「chasm」", ["chasm"]),
    ("叫“化”", "叫「chasm」", ["chasm"]),
    # 6) "the AI copying boom"（AI 仿制热潮）中 boom 被译成「繁荣」，
    #    导致「不会阻止 AI 复制繁荣」整句语义崩坏。
    ("AI 复制繁荣", "AI 仿制热潮", ["copying boom"]),
    ("复制热潮", "仿制热潮", ["copying boom"]),
    # 7) "Georgia" 在数据中心/电网语境指美国佐治亚州。既有规则只覆盖
    #    「格鲁齐亚」一个变体，NLLB 还会产出「乔治亚州」，一并覆盖。
    ("乔治亚州", "佐治亚州", ["effingham", "atlanta", "georgia power",
                              "georgia county", "savannah"]),
    # 7) "Effingham County"（佐治亚州埃芬汉县）除「埃菲金汉」外，
    #    还有「埃芬汉姆」这一变体（县名被误加音节）。
    ("埃芬汉姆", "埃芬汉", ["effingham"]),
    # 8) "former Apple CEO"（前苹果 CEO）被拆成「果前首席执行官」——
    #    Apple 被意译成单字「果」，former 的「前」又跑到品牌名后面，
    #    产出「果前首席执行官」这种完全读不通的形态。
    # 通用的「果前」还原用正则 + 负向前查（见 _PROPER_NOUN_FIXES），
    # 避免误伤「苹果前 CEO」这类正确写法。
    ("果前首席执行官", "前苹果首席执行官", ["former apple ceo", "tim cook"]),
    # 9) "The Information" 是科技媒体名（报道 Apple 机器人项目的媒体），
    #    被译成引号包裹的「信息」，读者无从判断是哪家媒体。
    ("告诉“信息”", "告诉《The Information》", ["the information"]),
    ("“信息”公司", "《The Information》", ["the information"]),
    # ---- 2026-11-03 02:00 巡检新增 ----
    # 1) Photo RAW 是 ON1 的产品名（RAW 图像处理软件），NLLB 逐词直译成
    #    「照片 RAW」。产品名必须整体保留英文。
    ("照片 RAW", "Photo RAW", ["photo raw"]),
    ("照片RAW", "Photo RAW", ["photo raw"]),
    # 2) LifeVal 是 OpenAI 的基准名，被拆译成「生命 Val」。品牌名整体保留。
    ("生命 Val", "LifeVal", ["lifeval"]),
    ("生命Val", "LifeVal", ["lifeval"]),
    # 3) "seed funding"（种子轮融资）在摘要中整段留成英文未译。
    ("的 seed funding", "的种子轮融资", ["seed funding"]),
    ("seed funding", "种子轮融资", ["seed funding"]),
    # 4) "Culling Assistant"（挑图/选片助手，摄影后期语境）被直译成
    #    「除助手」。业界标准译法是「挑图助手」。
    ("AI 除助手", "AI 挑图助手", ["culling"]),
    ("除助手", "挑图助手", ["culling"]),
    # 5) "Silicon Valley" 固定译法「硅谷」，NLLB 偶发直译成「谷地址」。
    # 注意：不能用 TERM_FIXES 的纯字符串替换——「谷地址」是「硅谷地址」的
    # 子串，已译对的文本会被二次替换成「硅硅硅谷地址」。
    # 该规则改由 _PROPER_NOUN_FIXES 的负向前查版本处理（见下方）。
    # 同时修复历史遗留的重复形态（早期版本规则误伤产生的「硅硅硅谷」）。
    ("硅硅硅谷", "硅谷", ["silicon valley"]),
    # 6) "agentic analytics"（智能体分析）里 agentic 被译成「代理」，
    #    与「代理服务器」混淆，AI 语境应写作「智能体」。
    ("代理分析", "智能体分析", ["agentic"]),
    ("代理式分析", "智能体分析", ["agentic"]),
    # 7) "TechCrunch Founder Summit" 是会议名，不应拆成「科技创始人峰会」。
    ("科技创始人峰会", "TechCrunch 创始人峰会", ["techcrunch founder summit"]),
    # 8) "Behavioral World Model" 固定译法「行为世界模型」，
    #    NLLB 偶发译成「行为世界模式」。
    ("行为世界模式", "行为世界模型", ["behavioral world model"]),
    # 9) "42AI ... $62.5M in seed funding" 整句被倒装成
    #    「行为世界模型种子资金」这类不通的动宾结构。
    ("行为世界模型种子资金", "行为世界模型的种子轮融资", ["behavioral world model"]),
    # ---- 2026-11-03 01:00 巡检新增 ----
    # 1) NLLB 把 Perplexity 当普通名词译成「困惑性」「困惑」，须还原品牌名。
    ("困惑性", "Perplexity", ["perplexity"]),
    # Anthropic 在标题开头被模型译成「人类细节」，实为 Anthropic + Details 混译。
    ("人类细节", "Anthropic", ["anthropic"]),
    # AI stack（AI 技术栈）被直译成「AI 堆」。
    ("AI 堆", "AI 技术栈", ["ai stack", "ai stacks"]),
    # stealth mode 固定译法「隐身」（出现 stealth 关键词时生效，不误伤正常语义）。
    ("隐形模式", "隐身模式", ["stealth"]),
    ("从隐形中", "走出隐身模式", ["stealth"]),
    # Marathon Management Partners 是投资机构名，直译为「马拉松管理合作伙伴」属误译。
    ("马拉松管理合作伙伴", "Marathon Management Partners", ["marathon management partners"]),
    ("马拉松管理伙伴", "Marathon Management Partners", ["marathon management partners"]),
    ("智能智", "智能体", ["agent"]),
    ("信息捷者", "信息窃取者", ["infostealer"]),
    ("信息窃取", "信息窃取", ["infostealer"]),
    ("登录证书", "登录凭据", ["credential"]),
    ("Discord会议", "Discord会话", ["discord", "session"]),
    ("同号签名人", "共同签署方", ["cosigner"]),
    ("代用证券", "token", ["token"]),
    ("大模型代理", "大模型智能体", ["agent"]),
    ("人工智能代理", "AI智能体", ["agent"]),
    ("人工智能特工", "AI智能体", ["agent"]),
    ("人工智能智能体", "AI智能体", ["agent"]),
    ("AI代理物", "AI智能体", ["agent"]),
    ("AI代理商", "AI智能体", ["agent"]),
    ("AI代理", "AI智能体", ["agent"]),
    ("代理商", "智能体", ["agent"]),
    ("代理物", "智能体", ["agent"]),
    ("代理品", "智能体", ["agent"]),
    # ---- 本轮巡检新增：AI 语境下裸「代理」系统性误译 ----
    # 离线模型把 agent 一律译成「代理」，在中文里极易被读成
    # 「代理人 / 代理商 / 代理服务器」，与行业通用写法「智能体」不符。
    # 触发词用 "agent"（子串）：agency 不含 agent，因此「human agency」
    # 这类确实该译「自主权/能动性」的语义天然不会被误伤。
    # 需要更长匹配才能命中的组合词放在前面，_apply_term_fixes 按长度降序处理。
    ("安全代理", "安全智能体", ["agent"]),
    ("代理代码", "智能体代码", ["agent"]),
    ("代理模型", "智能体模型", ["agent"]),
    ("代理插件", "智能体插件", ["agent"]),
    ("代理工具", "智能体工具", ["agent"]),
    ("代理系统", "智能体系统", ["agent"]),
    ("代理任务", "智能体任务", ["agent"]),
    ("代理平台", "智能体平台", ["agent"]),
    ("代理推断", "智能体推理", ["agent"]),
    ("自主代理", "自主智能体", ["agent"]),
    ("浏览器代理", "浏览器智能体", ["agent"]),
    ("代理人工智能", "智能体人工智能", ["agent"]),
    ("代码代理", "代码智能体", ["agent"]),
    ("个人代理", "个人智能体", ["agent"]),
    ("专业代理", "专业智能体", ["agent"]),
    ("经理代理", "经理智能体", ["agent"]),
    ("特工", "智能体", ["agent"]),
    ("机器人智能体", "智能体", ["agent"]),
    ("智能体商", "智能体", ["agent"]),
    ("智能体品", "智能体", ["agent"]),
    ("智能体物", "智能体", ["agent"]),
    ("危险因素", "风险因素", ["risk factor"]),
    ("模型特征", "模型规范", ["model spec"]),
    # ---- 本轮巡检新增：训练 / 强化学习 两处系统性误译 ----
    # "training" 在 AI 语境指「训练」，模型译成「培训」（教人培训）不对；
    # "reinforcement learning" 的行业标准译名是「强化学习」，
    # 译成「增强学习」（augmentation）是直译错误。
    ("人工智能培训", "AI 训练", ["training"]),
    ("增强学习", "强化学习", ["reinforcement learning"]),
    ("大赦国际的培训", "Anthropic 的培训", ["anthropic"]),
    ("谷歌深明", "DeepMind", ["deepmind"]),
    # ---- 2026-11-01 21:00 巡检新增：企业级 / 法务语境术语 ----
    # "law enforcement referrals" 指的是「向执法机构举报/移交线索」，
    # 离线模型译成「执法提议」，语义完全不同（提议 = proposal）。
    ("执法提议", "执法举报线索", ["law enforcement referral"]),
    # "unified logging" 是「统一日志」，不是「统一登录」（后者是 SSO）。
    # 同句中的 "billing" 被译成「发票」（= invoice），实际指「计费」。
    ("统一登录", "统一日志", ["unified logging"]),
    ("发票", "计费", ["unified logging"]),
    # "bring-your-own-provider keys"（BYOP）是云厂商通行说法，
    # 译作「自带服务商密钥」比直译「带你自己的提供商密钥」可读得多。
    ("带你自己的提供商密钥", "自带服务商密钥", ["bring-your-own-provider"]),
    # "risks institutional context loss" 整段被模型意译崩坏，
    # 拆成两个短语分别还原。
    ("风险损失机构背景", "有导致机构性上下文丢失的风险", ["institutional context loss"]),
    # "engineering pipeline" 在人才梯队语境指「工程人才管道/梯队」，
    # 直译「工程管道」会让读者误以为是管路。
    ("工程管道", "工程人才梯队", ["engineering pipeline"]),
    # quadruped robot（四足机器人）被模型译成「四旋翼机器人」，
    # 这是形态学硬错误：quadruped = 四足，不是四旋翼。
    ("四旋翼机器人", "四足机器人", ["quadruped"]),
    ("杰米尼", "Gemini", ["gemini"]),
    ("双子座", "Gemini", ["gemini"]),
    ("困惑度", "Perplexity", ["perplexity"]),
    ("深度思维", "DeepMind", ["deepmind"]),
    ("数据砖块", "Databricks", ["databricks"]),
    ("副驾驶", "Copilot", ["copilot"]),
    ("甲骨文组织", "Oracle", ["oracle"]),
    ("恩维迪亚", "Nvidia", ["nvidia"]),
    ("尼维迪亚", "Nvidia", ["nvidia"]),
    ("克劳德", "Claude", ["claude"]),
    ("米斯特拉尔", "Mistral", ["mistral"]),
    ("查特格博特", "ChatGPT", ["chatgpt"]),
    ("聊天GPT", "ChatGPT", ["chatgpt"]),
    ("聊天 GPT", "ChatGPT", ["chatgpt"]),
    ("维尔塞尔", "Vercel", ["vercel"]),
    ("恩斯凯尔", "Nscale", ["nscale"]),
    ("库伯内特斯", "Kubernetes", ["kubernetes"]),
    ("苹果情报", "Apple Intelligence", ["apple intelligence"]),
    ("派ytorch", "PyTorch", ["pytorch"]),
    ("抱脸", "Hugging Face", ["hugging face"]),
    ("梅塔", "Meta", ["meta"]),
    ("网飞", "Netflix", ["netflix"]),
    ("奈飞", "Netflix", ["netflix"]),
    ("林纳斯", "Linux", ["linux"]),
    ("视窗", "Windows", ["windows"]),
    # 品牌名后紧跟动词时，用「品牌 + 动词」整体还原，避免丢掉动词
    ("智力发行", "Prime Intellect 发行", ["prime intellect"]),
    ("双子球", "Gemini", ["gemini"]),
    ("阿贡", "Argon", ["argon"]),
    ("人类学", "Anthropic", ["anthropic"]),
    # "Anthropic Engineer" 被模型意译成「人类工程师」——公司名变成了普通词。
    # 还原时保留后半截职务（工程师），否则标题会退化成「遇见Anthropic」。
    ("人类工程师", "Anthropic 工程师", ["anthropic"]),
    ("人类工作者", "Anthropic 工作者", ["anthropic"]),
    ("人类开发者", "Anthropic 开发者", ["anthropic"]),
    ("人类研究员", "Anthropic 研究员", ["anthropic"]),
    # "Anthropic Says ..." 被模型意译成「人类论文说」，还原为「Anthropic 说」
    ("人类论文说", "Anthropic 说", ["anthropic"]),
    ("大赦国际", "Anthropic", ["anthropic"]),
    ("反重力", "Antigravity", ["antigravity"]),
    ("云飞拉", "Cloudflare", ["cloudflare"]),
    ("慢性", "Chronon", ["chronon"]),
    ("文学硕士", "LLM", ["llm"]),
    ("法学士", "LLM", ["llm"]),
    ("揭示了", "发布了", ["unveils", "announces", "launches", "releases"]),
    ("揭示", "发布", ["unveils", "announces", "launches", "releases"]),
    ("边界模型", "前沿模型", ["frontier model"]),
    ("边界智能体", "前沿智能体", ["frontier ai agent", "frontier agent"]),
    ("边境模型", "前沿模型", ["frontier model"]),
    # "frontier AI model" 被译成「边界AI模型」，统一为「前沿 AI 模型」
    ("边界AI模型", "前沿 AI 模型", ["frontier ai model", "frontier model"]),
    ("边界AI", "前沿 AI", ["frontier"]),
    # "frontier AI" 单独出现时，模型会译成「边境 AI」「跨界 AI」。
    # 这两种译法在中文里都读作「地理边境」，与 AI 语境下的
    # 「前沿 / 最先进」语义完全不符，属于需要确定性纠正的误译。
    # 触发词用 "frontier"，因此「跨境 / 跨界合作」等正常语境不受影响。
    ("边境 AI", "前沿 AI", ["frontier"]),
    ("边境AI", "前沿 AI", ["frontier"]),
    ("跨界 AI", "前沿 AI", ["frontier"]),
    ("跨界AI", "前沿 AI", ["frontier"]),
    # "data center campus" 被译成「数据中心校园」——「校园」在中文里
    # 指学校，与数据中心的「园区」是两回事。站内另一条同类报道
    # （OpenAI「AI 算力园区」）已用「园区」，此处统一为同一译法。
    # 触发词 "campus"，故真正的学校语境（大学校园）不受影响。
    ("数据中心校园", "数据中心园区", ["campus"]),
    ("AI 数据中心校园", "AI 数据中心园区", ["campus"]),
    # Ulanqab：内蒙古乌兰察布市。模型音译成「乌兰卡布」，
    # 标题里又直接留英文。统一还原为标准中文地名「乌兰察布」。
    ("乌兰卡布", "乌兰察布", ["ulanqab"]),
    ("Ulanqab", "乌兰察布", ["ulanqab"]),
    # Autoware：自动驾驶开源项目名。模型把它意译成「自动化工」，
    # 项目名彻底丢失（中文里读作「自动化工厂」）。还原为项目名。
    ("自动化工", "Autoware", ["autoware"]),
    # TIER IV：自动驾驶公司名。模型偶发把罗马数字 IV 误写成 IVER
    # （把 IV 当成英文单词缩写），公司名被改坏。还原为标准写法。
    ("TIER IVER", "TIER IV", ["tier iv"]),
    ("Tier Iver", "TIER IV", ["tier iv"]),
    # "Claude" 被模型拼成 "Clode"
    ("Clode", "Claude", ["claude"]),
    # "embodied reasoning" 被译成「体现推理」，行业通用译法为「具身推理」
    ("体现推理", "具身推理", ["embodied reasoning"]),
    ("ERQA", "ERQA", ["embodied reasoning"]),
    # "zero-shot" 被译成「零镜头」，应为「零样本」
    ("零镜头", "零样本", ["zero-shot"]),
    # "egocentric" 被译成「自私的」，在计算机视觉语境应为「第一人称的/自我中心的」
    ("自私的人类视频", "第一人称人类视频", ["egocentric"]),
    ("自私的人", "第一人称", ["egocentric"]),
    # "policy token" 是标准术语，不应译成「政策代币」
    ("政策代币", "policy token", ["policy token"]),
    # "被AI除" —— 原文 "opt out of being scraped by AI" 漏译
    ("选择不被AI除", "选择退出被 AI 抓取", ["scraped"]),
    ("不被AI除", "不被 AI 抓取", ["scraped"]),
    # "opt out of scraping" 的标题译法，模型给出「以选择不使用扫描」这类病句
    ("以选择不使用扫描", "以支持一种新的退出抓取方式", ["opt out of scraping"]),
    ("使用扫描", "退出抓取", ["scraping"]),
    # "Gemini 4Argon" 数字与品牌粘连
    ("4Argon", "4 Argon", ["argon"]),
    ("Gemini 4Argon", "Gemini 4 Argon", ["argon"]),
    # "agent-desktop" 是 Vercel 开源项目名
    ("代理桌面", "agent-desktop", ["agent-desktop"]),
    ("Gemini 4碳", "Gemini 4 Carbon", ["carbon"]),
    ("Gemini4碳", "Gemini 4 Carbon", ["carbon"]),
    # 2026-11-03 16:00 巡检新增：模型现在会在「4」与「碳」之间补空格，
    # 产出「Gemini 4 碳」，上面两条无空格规则命中不了，版本代号丢失。
    # 同前缀要求保证「低碳」不会被误改。
    ("Gemini 4 碳", "Gemini 4 Carbon", ["carbon"]),
    ("Gemini4 碳", "Gemini 4 Carbon", ["carbon"]),
    ("云飞", "Cloudflare", ["cloudflare"]),
    ("10万代币", "100万 token", ["million token", "1m token", "one-million"]),
    ("10万令牌", "100万 token", ["million token", "1m token", "one-million"]),
    ("深思发表", "DeepMind 发布", ["deepmind"]),
    ("Gemini 4安安", "Gemini 4 Argon", ["argon"]),
    ("安安", "Argon", ["argon"]),
    ("抗重力", "Antigravity", ["antigravity"]),
    ("Google深思", "Google DeepMind", ["deepmind"]),
    ("深思熟悉", "DeepMind 探讨", ["deepmind"]),
    # ---- 领域固定搭配：模型把术语直译/漏译，按源文关键词还原 ----
    # 全双工语音
    ("完全双重", "全双工", ["full-duplex"]),
    ("双重演讲", "双工语音", ["full-duplex"]),
    ("完全双重的语音模型", "全双工语音模型", ["full-duplex"]),
    # 后训练
    ("后训练的", "后训练的", ["post-trained"]),
    # 张量处理单元
    ("度处理单元", "张量处理单元", ["tensor processing"]),
    # 俳句
    ("海 haiku", "俳句", ["haiku"]),
    ("海俳句", "俳句", ["haiku"]),
    # 畅销作者
    ("最销的作者", "畅销作者", ["bestselling"]),
    # 中期选举
    ("中学期", "中期选举", ["midterm"]),
    # 奶酪诗（cheesy poetry 意译过度）
    ("奶酪诗", "打油诗", ["cheesy poetry"]),
    # 前进/后期通行 -> 前向/反向传播
    ("前进通行", "前向传播", ["forward pass"]),
    ("后期通行", "反向传播", ["backward pass"]),
    ("前期通行", "前向传播", ["forward pass"]),
    # 账本/派对等直译
    ("投了党", "举办了派对", ["threw a party"]),
    # Nscale 所有格：模型输出 "Nscales"，应为 "Nscale 的"
    ("Nscales", "Nscale 的", ["nscale"]),
    ("NscalesAI", "Nscale 的 AI", ["nscale"]),
    # Prime Intellect 重复（品牌还原时把 "Prime" 叠加了两次）
    ("Prime Mega Prime MoE", "Prime Mega MoE", ["prime mega moe"]),
    ("Prime Mega MoE：", "Prime Mega MoE：", ["prime mega moe"]),
    # Google DeepMind / Gemma 4 等被粘连或丢掉空格
    ("GoogleDeepMind", "Google DeepMind", ["deepmind"]),
    ("Gemma4", "Gemma 4", ["gemma"]),
    ("Gemma4模型", "Gemma 4 模型", ["gemma"]),
    # "AI Tamagotchi" 被粘连
    ("AITamagotchi", "AI Tamagotchi", ["tamagotchi"]),
    # 投了党 / NOA 破折号
    ("NOAor", "NOA——即", ["no ordinary assistant"]),
    ("NOAor No Ordinary Assistant", "NOA——“非普通助手”", ["no ordinary assistant"]),
    # 提示词 "token" 复数被吞
    ("每000个代币", "每 100 万个 token", ["per 1m tokens"]),
    ("1M Tokens", "100 万 token", ["1m tokens"]),
    # "Factory" 是公司名（AI 编程工具厂商），被模型当成普通名词译成「工厂」
    ("工厂发布了Droid", "Factory 发布了 Droid", ["factory"]),
    ("在工厂的自己的", "在 Factory 自己的", ["factory"]),
    ("工厂的Droid", "Factory 的 Droid", ["factory"]),
    ("与工厂Droid", "与 Factory Droid", ["factory"]),
    ("相遇：一个模型独立的编码代理，在脚本模式上构建的编码器",
     "相遇：一个与模型无关的编码智能体框架", ["model-independent coding agent"]),
    ("一个模型独立的编码代理", "一个与模型无关的编码智能体框架", ["model-independent coding agent"]),
    ("使程序工具称为默认的工具", "让程序化工具调用成为默认行为", ["programmatic tool calling"]),
    # 品牌 + 缩写后直接接中文，需补一个空格（"Samaya AI发布了" -> "Samaya AI 发布了"）
    ("AI发布", "AI 发布", ["samaya"]),
    ("AI推出", "AI 推出", ["samaya"]),
    ("AI 的 Sterling是", "AI 的 Sterling 是", ["sterling"]),
    # Sterling 被音译成「英」
    ("AIs英是", "AI 的 Sterling 是", ["sterling"]),
    ("萨马雅AIs英", "Samaya AI 的 Sterling", ["sterling"]),
    # 版本号所有格："Claude Fable 5.1s" -> "Claude Fable 5.1 的"
    ("5.1s", "5.1 的", ["fable"]),
    ("5.1s的分数", "5.1 的分数", ["fable"]),
    # ---- 直译过度/术语误译 ----
    # "junk rating" 是信用评级档位，不��� "垃圾评级"
    ("高垃圾评级", "高投机级评级", ["junk rating"]),
    ("垃圾评级", "投机级评级", ["junk"]),
    ("拉诺斯", "泰勒·舒尔茨", ["theranos"]),
    ("泰罗诺斯", "Theranos", ["theranos"]),
    ("举报员", "举报人", ["whistleblower"]),
    ("转换器和发电器", "迭代器与生成器", ["iterators and generators"]),
    ("零碎策略", "分块策略", ["chunking"]),
    ("一个缩策略", "分块策略", ["chunking"]),
    ("文本知情", "上下文感知", ["context-aware"]),
    ("泽斯特", "Zest", ["zest"]),
    ("齐斯特", "Zest", ["zest"]),
    ("AI保理", "AI 智能体", ["zest"]),
    ("布莱恩尼科尔", "Brian Niccol", ["starbucks"]),
    ("宁科尔", "Brian Niccol", ["starbucks"]),
    ("在驱动中个性化", "在每次到店时提供个性化", ["personalized digital menu"]),
    ("到达时识别", "抵达时识别", ["personalized digital menu"]),
    ("未利的公司", "盈利的公司", ["unprofitable"]),
    ("从未利的", "从不盈利的", ["unprofitable"]),
    ("投资后", "投资之后", ["first investment"]),
    ("更昂贵地筹集资金", "以更高的成本融资", ["raise capital"]),
    ("其巨大的支出，这支支了", "其巨额支出，这支撑了", ["funding its"]),
    ("这篇支", "支撑", ["funding its"]),
    ("从未利的公司", "从不盈利的公司", ["unprofitable"]),
    ("而公司可以在继续生产产品时清除这些低调的条款",
     "而公司可以在继续生产产品时取消这些不起眼的条款", ["low-key provisions"]),
    ("颠覆所有类型的企业", "颠覆多类业务", ["upend all kinds of businesses"]),
    ("可能会颠覆所有类型的企业", "可能颠覆多类业务", ["upend all kinds of businesses"]),
    ("公司过去几周都试图向投资者保证", "公司过去几周一直向投资者保证", ["assure investors"]),
    ("更是机会", "更像机会", ["more opportunity"]),
    # ---- 本轮巡检新增的术语/音译失真 ----
    # Anthropic 被音译成"人类"/"人类学"，在 IPO、风险因素等语境下尤其荒谬
    ("人类IPO", "Anthropic IPO", ["anthropic"]),
    ("人类警告其AI", "Anthropic 警告其 AI", ["anthropic"]),
    ("来自антропо的", "来自 Anthropic 的", ["anthropic"]),
    ("антропо", "Anthropic", ["anthropic"]),
    # Credit Saison（公司名）被直译为"信用季节/信用赛季"
    ("信用季节", "Credit Saison", ["credit saison"]),
    ("信用赛季", "Credit Saison", ["credit saison"]),
    # infostealer 语境下"杀害受害者"应为"针对受害者下手"
    ("使用人工智能来杀害受害者", "利用 AI 自动化窃取受害者数据", ["autodox", "infostealer"]),
    ("来杀害受害者", "对受害者下手", ["autodox"]),
    # "Meta could" 被直译为"Meta能够"，导致标题语义断裂
    ("在Meta能够之前", "赶在 Meta 之前", ["before meta could"]),
    # 混合西里尔字母的音译（安тропо克）
    ("安тропо克", "Anthropic", ["anthropic"]),
    ("антропо", "Anthropic", ["anthropic"]),
    # "Will the real X please stand up" 句式：X 被译成"人类主义者"
    ("真正的人类主义者", "真正的 Anthropic", ["anthropic"]),
    ("人类主义者，请站起来", "Anthropic，请站起来", ["anthropic"]),
    # ---- 本轮巡检（2026-11-01 06:00）新增 ----
    # "AI agents" 被译成"AI智能体人"（智能体 + 人，冗余且不通顺）
    ("AI智能体人", "AI智能体", ["agent"]),
    # "NAACP"（美国有色人种协进会）被直译成"美国联邦航空协会"，语义完全错误
    ("美国联邦航空协会 (NAACP)", "美国有色人种协进会（NAACP）", ["naacp"]),
    ("美国联邦航空协会", "美国有色人种协进会", ["naacp"]),
    # "Prime Intellect Releases" 品牌后缺空格
    ("发行Prime", "发行 Prime", ["prime intellect"]),
    # 半角冒号夹在中文里，读起来突兀，统一为全角
    ("Sterling:一个", "Sterling：一个", ["sterling"]),
    # ---- 本轮巡检（2026-11-01 11:00）新增 ----
    # "reckless" 被拆成"鲁"和"和"（"鲁和有害行动"），实为"鲁莽的"
    ("鲁和有害", "鲁莽的有害", ["reckless"]),
    ("鲁和", "鲁莽", ["reckless"]),
    # "Laziness is not a religion." 直译成"惰不是一个宗教"，语义不通
    ("惰不是一个宗教", "惰性不是一种宗教", ["laziness"]),
    # "Overview of Playground"：Playground 是 Google 的产品名，不该直译为"游戏场"
    ("游戏场的概述", "Playground 概览", ["playground"]),
    # "middle ground" 直译成"中途"，实为"折中方案"
    ("寻找中途", "寻求折中方案", ["middle ground"]),
    # "pull request" 直译成"拉动请求"，实为"拉取请求"（PR）
    ("拉动请求", "拉取请求", ["pull request"]),
    # "regurgitating" 直译成"对用户工作的聊天机器人"，语义丢失
    ("对用户工作的聊天机器人", "向用户复述该作品的聊天机器人", ["regurgitating"]),
    # ---- 本轮巡检（2026-11-01 16:00）新增 ----
    # "XSS Bugs" 中 bugs 指安全漏洞，模型译成"错误"（bug detection→错误检测）
    ("XSS 错误", "XSS 漏洞", ["xss"]),
    ("错误检测", "漏洞检测", ["bug detection"]),
    # "forward pass / backward pass" 直译成"前进传递/后退传递"，
    # AI 领域标准译法为"前向传播/反向传播"。
    ("前进传递", "前向传播", ["forward pass"]),
    ("后退传递", "反向传播", ["backward pass"]),
    # "serialization" 译成"串行化"不准确，标准译法是"序列化"
    ("串行化", "序列化", ["serialization"]),
    # "misalignment"（模型与人类意图不一致）译成"错误"过泛，应为"失配"
    ("前沿模型的错误", "前沿模型的失配", ["misalignment"]),
    ("错误排列", "失配", ["misalignment"]),
    # "enterprise context" 译成"企业环境"，context 应为"上下文"
    ("企业环境", "企业上下文", ["enterprise context"]),
    # "AI readiness" 译成"人工智能准备性"，应为"AI 就绪度"
    ("人工智能准备性", "AI 就绪度", ["ai readiness"]),
    # "serving harness" 译成"服务器"，harness 在 AI 语境是"运行框架/支撑框架"
    ("人工智能服务器，打造以持续", "AI 服务框架，打造以持久", ["serving harness"]),
    ("服务器，打造以持续", "服务框架，打造以持久", ["serving harness"]),
    # "full-duplex speech model" 中 speech 被译成"演讲"，应为"语音"
    ("全双工演讲模型", "全双工语音模型", ["full-duplex speech"]),
    ("仅在演讲中训练", "仅用语音训练", ["full-duplex speech"]),
    # "coding agent harness" 中 harness 应为"框架"
    ("编码智能体框架，Harness", "编码智能体框架，基于脚本模式构建", ["coding agent harness"]),
    # "fantasy soccer team" 译成"幻想足球队"，应为"梦幻足球队"
    ("幻想足球队", "梦幻足球队", ["fantasy soccer"]),
    # "a bunch of AI agents in charge of" 译成"负责"，应为"管理"
    ("一群 AI 智能体负责一个", "一群 AI 智能体管理一支", ["agents in charge"]),
    # "your robot's safety functions" 译成"你的机器人安全功能"，通顺化
    ("你的机器人安全功能已经工作了", "机器人的安全功能已经可以正常工作了", ["safety functions"]),
    # "input lies" 译成"输入错误"，原意是"输入是假的/不可信"
    ("如果输入错误了怎么办", "如果输入是假的怎么办", ["input lies"]),
    # "published a paper" 等被模型处理成"错误 1"等噪声
    ("错误 1.", "Mischief 1.", ["mischief"]),
    # "coigner/cosigner" 相关
    ("联合担保方", "联合担保方", ["cosigner"]),
    # "forward pass / backward pass" 之外的噪声
    ("前向传播。总理智能", "前向传播。Prime Intellect", ["prime intellect"]),
    # ---- Block 公司名：模型把 Block 译成「区块」，与「区块链」混淆 ----
    # 只有原文出现 Block 公司专名语境时才替换，避免误伤「区块链」。
    ("区块链 FP8", "分块式 FP8", ["blockwise fp8"]),
    ("区块的人工智能研究实验室", "Block 的 AI 研究实验室", ["block s ai research lab"]),
    ("什么是区块的", "什么是 Block 的", ["block s ai research lab"]),
    ("区块正在使用", "Block 正在使用", ["block is building"]),
    ("区块的 AI", "Block 的 AI", ["block s ai research lab"]),
    # ---- 本轮巡检（16:00）第二批 ----
    # "GPT-6.1 Terra" 中 Terra 是模型代号，不能译成"地球"
    ("GPT-6.1 地球", "GPT-6.1 Terra", ["gpt-6.1 terra"]),
    # "AI-natives"（AI 原生企业）译成"人工智能原住民"
    ("人工智能原住民", "AI 原生企业", ["ai-natives"]),
    # "recommendation embeddings" 译成"推嵌入式"，"嵌入"被吃掉
    ("推嵌入式", "推荐嵌入", ["recommendation embedding"]),
    # "about a third of a percent" 重复成"约约"
    ("约约", "约", ["third of a percent"]),
    # "AI adoption" 译成"人工智能是商业绩吗"类崩坏
    ("人工智能是商业绩吗", "AI 采纳率在上升，但业绩如何", ["ai adoption"]),
    # "enterprise context" 已在上；补 "context" 单独被译成"环境"的场景
    ("与现有企业环境", "与现有企业上下文", ["enterprise context"]),
    # "Open Models"（开放模型）译法统一
    ("采用开放模式来建立私有情报", "采用开放模型构建私有智能", ["open models"]),
    # "AI factories" / "AI factory" 译成"AI 工厂"是对的，但"AI 原生"要统一
    ("AI 原生", "AI 原生", ["ai-native"]),
    # "the chipmaker that sells the chips" 已在 GLOSSARY；补"卖芯片的芯片制造商"
    ("卖芯片的芯片制造商", "卖芯片的芯片厂商", ["chipmaker"]),
    # ---- 本轮巡检（16:00）第三批：摘要级残留 ----
    # "Anima" 在摘要中译成"艾尼马"（BRAND_TERMS 只对标题生效时命中不到）
    ("艾尼马", "Anima", ["anima"]),
    # "No Ordinary Assistant"（NOA）被译成"非普通助手"
    ("非普通助手", "NOA（No Ordinary Assistant）", ["no ordinary assistant"]),
    # "Prime Prime" 重复
    ("Prime Prime", "Prime", ["prime mega moe"]),
    # "GPT-6Astra" 品牌与版本号粘连
    ("GPT-6Astra", "GPT-6 Astra", ["gpt-6astra"]),
    # "frontier capability group" 译成"边境能力集团"
    ("边境能力集团", "前沿能力集团", ["frontier capability"]),
    # "AI 原生企业"是正确译法，但"需求"主语需通顺
    ("AI 原生企业的需求正在比以往任何时候都更快地推进", "AI 原生企业的需求正以前所未有的速度推动", ["ai-natives"]),
    # "近 Real-Time Model Transform" 等专名保留英文即可，"推嵌入式"已在上方处理
    ("降低了嵌入式延迟", "将嵌入陈旧度", ["staleness"]),
    # "收入运行率" 是 SaaS 通行译法，但"每名员工每年的 160 万美元的收入运行率"需通顺
    ("每名员工每年的 160 万美元的收入运行率", "每名员工 160 万美元的年化营收", ["revenue run rate"]),
    # ---- 本轮巡检（16:10）新增：AWS 头条条目的新鲜缺陷 ----
    # "headroom"（余量/预留容量）被模型译成"总部"，语义完全跑偏
    ("保留总部空间", "保留余量", ["headroom"]),
    ("需要的总部保留", "并保留余量", ["headroom"]),
    ("保留总部", "保留余量", ["headroom"]),
    # "sold out" 被译成"被销售"
    ("容量大大被销售", "容量已大部分售罄", ["sold out"]),
    ("AWS 容量大大被销售", "AWS 容量大部分售罄", ["sold out"]),
    # "committed cloud capacity" 译成"承诺云容量"，应通顺化
    ("大型承诺云容量", "大型已承诺云容量", ["committed cloud capacity"]),
    # "Practitioners" 译成"实践者"偏生硬
    ("讨论这些评论的实践者报告了", "就此发表看法的一线从业者反映", ["practitioners"]),
    # ---- 本轮巡检（16:35）新增：自动抓取新条目的品牌失真 ----
    # "Nace AI" 被意译成"纳斯 AI"
    ("纳斯 AI", "Nace AI", ["nace ai"]),
    # "Apple Silicon" 被拆成"果 Silicon"（Apple 还原规则只覆盖单字"果"+特定后缀）
    ("果 Silicon", "Apple Silicon", ["apple silicon"]),
    # "DeepSeek" 被意译成"深度寻找"
    ("深度寻找", "DeepSeek", ["deepseek"]),
    ("深度寻找开源", "DeepSeek 开源", ["deepseek"]),
    # "Router-Worker"（路由器-工作者架构）应保留架构含义
    ("一个路由器工作者编码代理", "一个 Router-Worker 编码智能体", ["router-worker"]),
    # "Open-Sources" 被译成"开源"是对的，但 "Drex Max v1 作为开放权重 .Drex Max"
    # 这类句读断裂需修正
    ("作为开放权重 .", "，采用开放权重发布。", ["open-weights"]),
    # "MIT 授权" 译法不通，MIT License 应为「MIT 许可」
    ("MIT 授权的研究原型", "采用 MIT 许可的研究原型", ["mit license"]),
    # ---- 本轮巡检（17:00）新增：第二批术语与语义修复 ----
    # "capex"（资本开支）被音译成"开普斯"
    ("开普斯开支", "资本开支", ["capex"]),
    ("开普斯", "资本开支", ["capex"]),
    # "midterms"（中期选举）被译成"中学赛"
    ("中学赛", "中期选举", ["midterms"]),
    # "frontier model"（前沿模型）被译成"边境模式"
    ("边境模式培训环境", "前沿模型训练环境", ["frontier model"]),
    ("边境模式", "前沿模型", ["frontier model"]),
    # "Tensor Processing Units"（张量处理单元）被译成"电压处理单元"
    ("电压处理单元", "张量处理单元", ["tensor processing"]),
    # "agent harness"（智能体框架）被译成"代理利用"
    ("代理利用更新", "智能体框架更新", ["factory droid"]),
    ("代理利用", "智能体框架", ["harness"]),
    # Factory（AI 编程公司）：摘要中"工厂"为误译，但"AI 工厂"是正确译法，
    # 故用原文触发词限定，不做全局替换。
    ("工厂已经发布了 Droid", "Factory 发布了 Droid", ["factory droid"]),
    ("每一个工厂测试", "在 Factory 测试的所有框架中", ["factory droid"]),
    # Playwright（浏览器测试框架）被译成"剧作家"
    ("剧作家替换", "Playwright 重放", ["playwright"]),
    # "QCon AI"（会议品牌）被译成"AICon"
    ("AICon 纽约", "QCon AI 纽约", ["qcon"]),
    # 波兰国家网络安全中心 NASK 被音译成"波兰斯纳斯克"
    ("波兰斯纳斯克", "波兰 NASK", ["nask"]),
    # Infini-AI-Lab（开源项目）
    ("恩菲尼-AI-实验室", "Infini-AI-Lab", ["infini-ai-lab"]),
    # Empiric Earth（公司名）被意译成"经验地球"
    ("经验地球", "Empiric Earth", ["empiric earth"]),
    # Fanatics（体育用品零售商）被意译成"狂热分子"
    ("狂热分子和 OpenAI", "Fanatics 与 OpenAI", ["fanatics"]),
    # Runware（初创公司）被意译成"运行软件"
    ("运行软件正在建造", "Runware 正在建造", ["runware"]),
    # Ropes & Gray（律所）被意译成"罗普斯&格雷"
    ("罗普斯&格雷", "Ropes & Gray", ["ropes & gray"]),
    # "transactional diligence"（交易尽职调查）被译成"交易勤奋"
    ("交易勤奋", "交易尽职调查", ["diligence"]),
    # "ad stack"（广告技术栈）被译成"广告堆"
    ("广告堆", "广告技术栈", ["ad stack"]),
    # "open-source inference"（开源推理）被译成"开源推断"
    ("开源推断", "开源推理", ["open-source inference"]),
    # "gross capital raise"（募集资金总额）被译成"总资本筹集"
    ("总资本筹集", "募集资金总额", ["gross capital raise"]),
    # Churchill Capital XI（SPAC 公司）被意译成"丘吉尔十一世"
    ("丘吉尔十一世", "Churchill Capital XI", ["churchill capital"]),
    # "Copilot" 被译成"Copilot 员"
    ("Copilot 员", "Copilot", ["copilot"]),
    # "specialized agents"（专业智能体）
    ("专业代理", "专业智能体", ["specialized agents"]),
    # "fine-tuned model"（微调模型）被译成"精细调节的 AI 模型"
    ("精细调节的 AI 模型", "微调 AI 模型", ["fine-tuned"]),
    # "monetizable assets"（可变现资产）被译成"可利资产"
    ("可利资产", "可变现资产", ["monetizable"]),
    # "credential-theft pass"（凭据窃取环节）被译成"凭证盗窃通过"
    ("凭证盗窃通过", "凭据窃取环节", ["credential-theft"]),
    # "infostealer"（信息窃取器）在摘要中被译成"信息处理器"
    ("Windows 信息处理器", "Windows 信息窃取器", ["infostealer"]),
    # "trade-offs"（权衡取舍）被译成"交易"
    ("机制，交易，评估和控制", "机制、权衡取舍、评估与控制", ["trade-offs"]),
    # "multi-modal RAG"（多模态 RAG）被译成"多模式 RAG"
    ("多模式 RAG 管道", "多模态 RAG 流水线", ["multi-modal rag"]),
    ("多模式 RAG", "多模态 RAG", ["multi-modal rag"]),
    # "source-available"（源码可见）被译成"源源可用"
    ("源源可用的", "源码可见（source-available）的", ["source-available"]),
    # "world model"（世界模型）语境下的 "training" 应为"训练"而非"培训"
    ("开放了培训，评估和部署世界模型的新工具", "开放了训练、评估和部署世界模型的新工具", ["world model"]),
    # "simulation checkpoints"（模拟检查点）被译成"模拟检查站"
    ("模拟检查站", "模拟检查点", ["simulation checkpoint"]),
    # "checkerboard / leaderboard" 语境："排名第五"应为"位列前五"
    ("在六个不同的开放模型排行榜中排名第五", "在六个不同的开放模型排行榜上均位列前五", ["open models leaderboard"]),
    # "Capitol Hill"（国会山）被译成"国会"
    ("勇敢地登上国会？", "勇敢地闯进国会山？", ["capitol hill"]),
    # "context-aware AI"（上下文感知 AI）译法生硬
    ("为上下文感知的人工智能提出了理由", "论证上下文感知 AI 的必要性", ["context-aware"]),
    # "updated Model Spec"（更新版模型规范）缺宾语
    ("一个更新的模型规格，为更有能力和更有益的 AI", "更新版模型规范：打造能力更强、对社会更有益的 AI", ["model spec"]),
    # "Patch the Planet"（项目名）不应意译成"修补星球"
    ("修补星球：", "Patch the Planet：", ["patch the planet"]),
    # "great opportunity to go deceive people"（骗人的绝佳机会）直译丢掉了引号反讽
    ("人工智能繁荣是一个很好的机会去欺骗人们", "AI 热潮正是骗人的绝佳机会", ["deceive people"]),
    # ---- 本轮巡检（2026-11-01 19:00）新增：训练 / 推理 / 多模态 / 具身 ----
    # "training preferences"（AI 训练偏好）被译成「培训偏好」，
    # "training and evaluating"（训练并评估）译成「培训和评估」，
    # "train models"（训练模型）译成「培训模型」——AI 语境一律是「训练」。
    ("培训偏好", "训练偏好", ["training preferences", "training preference"]),
    ("培训和评估", "训练和评估", ["training and evaluating"]),
    ("培训模型", "训练模型", ["train models"]),
    # "inference" 在 AI 语境是「推理」，模型译成「推断」。
    ("本地推断", "本地推理", ["local inference"]),
    ("训练和推断", "训练和推理", ["training and inference"]),
    ("推断堆", "推理栈", ["inference stack"]),
    # 2026-11-03 14:00 巡检：「将本地 AI 推断与……结合在一起」——
    # 原文 local AI inference，既有规则只覆盖「本地推断」，中间夹了
    # "AI" 时匹配不上。AI 语境下 inference 一律是「推理」。
    ("AI 推断", "AI 推理", ["inference"]),
    ("体内推理", "具身推理", ["embodied reasoning"]),
    ("成体推理", "具身推理", ["embodied reasoning"]),
    # "embodied AI"（具身智能）被译成「人工智能体现」
    ("人工智能体现", "具身智能", ["embodied ai"]),
    # "multimodal"（多模态）被译成「多模式」，另有「多模特传感」
    ("多模式", "多模态", ["multimodal"]),
    ("多模特传感", "多模态传感", ["multimodal sensing"]),
    # "speculative decoding"（投机解码）被译成「推测解码」
    ("推测解码", "投机解码", ["speculative decoding"]),
    # "vector database"（向量数据库）被译成「矢量数据库」
    ("矢量数据库", "向量数据库", ["vector database"]),
    # "backcountry"（偏远野外）被译成「后乡」
    ("后乡", "偏远地区", ["backcountry"]),
    # RL "policies trained on the dataset"（在数据集上训练的策略）被译成「政策转移」
    ("政策转移", "策略迁移", ["policies trained on the dataset"]),
    # ---- 本轮巡检新增（20:00）：open model / rubric / 品牌名意译 ----
    # "open models"（开放权重模型）被译成「开放模式」「开放型号」——
    # 「开放模式」在中文里指 open mode，与「开放模型」是完全不同的概念。
    ("开放型号", "开放模型", ["open model", "open models", "open-weight", "open weights"]),
    ("开放模式", "开放模型", ["open model", "open models", "open-weight", "open weights"]),
    # rubric（评分标准）被译成「标准标题」
    ("标准标题", "评分标准", ["rubric"]),
    # 品牌名被意译：Atomic Canyon→「原子峡谷」、Terminal X→「终端 X」
    ("原子峡谷", "Atomic Canyon", ["atomic canyon"]),
    ("终端 X", "Terminal X", ["terminal x"]),
    # ship（发布）/official（官方）/export（导出）在长文本规格段里的意译偏差
    ("代码运输", "代码发布", ["ship", "ships", "shipped"]),
    ("权重和代码运输", "权重与代码发布", ["ship", "ships", "shipped"]),
    ("没有现实性", "官方暂未提供", ["no official", "not public yet", "no real"]),
    ("出口尚未公开", "导出尚未公开", ["export", "onnx"]),
    # ---- 本轮巡检新增（22:00）：全量审查发现的术语/专名误译 ----
    # LLM（Large Language Model）被译成「法律法规」——这是完全错误的领域串味，
    # 中文读者会读成"法律"，触发词 "llm" 在 AI 语境下唯一。
    ("使用法律法规来", "使用 LLM 来", ["llm"]),
    ("法律法规来改善", "LLM 来改善", ["llm"]),
    # master's degree（硕士学位）被译成「学士学位」
    ("计算机科学士学位", "计算机科学硕士学位", ["master"]),
    # Fujifilm（富士胶片）被拆成「富士电影公司」
    ("富士电影公司", "富士胶片公司", ["fujifilm"]),
    ("富士电影", "富士胶片", ["fujifilm"]),
    # Atlassian（企业协作软件公司）被意译成「亚特拉斯人」
    ("亚特拉斯人", "Atlassian", ["atlassian"]),
    # "honor"（遵从/遵循 robots.txt 信号）被译成「授予」
    ("将授予共享的", "将遵循共享的", ["honor"]),
    # "open source"（开源）被译成「公开源」
    ("公开源中的关键漏洞", "开源项目中的关键漏洞", ["open source"]),
    ("公开源", "开源", ["open source"]),
    # "autonomous weapons"（自主武器）被译成「自动武器」——AI 语境应为「自主」
    ("致命自动武器", "致命自主武器", ["autonomous weapons"]),
    # C-BRAIN 联盟名里 "AI" 被译成「人智能」
    ("人智能联盟", "人工智能联盟", ["c-brain"]),
    # "multi-tenancy"（多租户）被译成「多租金」
    ("多租金", "多租户", ["multi-tenancy"]),
    # "single digits"（个位数）被译成「单位数」
    ("单位数", "个位数", ["single digits"]),
    # "resting on its laurels"（安于既有成就）被直译成「依靠自己的荣誉」
    ("依靠自己的荣誉", "躺在自己的功劳簿上", ["laurels"]),
    # "fireside chat"（炉边对话）被直译成「公共火聊天」
    ("公共火聊天", "公开炉边对话", ["fireside"]),
    # "technology stack"（技术栈）被译成「技术堆」
    ("技术堆", "技术栈", ["stack"]),
    # "AI stack"（AI 技术栈）被译成「人工智能堆」
    ("人工智能堆", "AI 技术栈", ["stack"]),
    # "unusually low single-digit"（个位数）被译成「低单位数」
    ("低单位数", "个位数", ["single-digit", "single digit"]),
    # "one-third of a percent"（约三分之一个百分点）漏掉「百分点」
    # 注意：正确写法不能包含错误写法的子串，否则本规则自重入，
    # 每跑一轮就多叠一层 "个百分点"。
    # 历史脏数据里已存在 "增加了约三分之一个百分点"（旧版规则的产物），
    # 它也必须列为错误形式，否则新规则会命中它并再叠一层。
    ("增加了约三分之一个百分点", "增加了约 0.33 个百分点", ["one-third of a percent"]),
    ("增加了约三分之一", "增加了约 0.33 个百分点", ["one-third of a percent"]),
    # "80 percent"（80%）漏掉百分号
    ("他 80 的时间", "他 80% 的时间", ["percent"]),
    ("名额的 80 的时间", "名额的 80% 的时间", ["percent"]),
    # "drive-thru"（得来速通道）被译成「车站」
    ("停车到车站", "驶入得来速通道", ["drive-thru"]),
    # "administrator"（管理者）被译成「校长」
    ("肯塔基大学的校长", "肯塔基大学的管理者", ["administrator"]),
    # "on net"（总的来说）被译成「在网上」
    ("我认为，在网上，世界应该了解宇宙如何运作", "我认为，总的来说，世界应该了解宇宙如何运作", ["on net"]),
    # "single model PRAGMA" 的引号被译成「普拉格马」——PRAGMA 是产品名
    ("普拉格马", "PRAGMA", ["pragma"]),
    # "the right to use AI"（使用 AI 的权利）被译成「免于使用」
    ("宗教豁免，免于在工作中使用人工智能", "在工作中使用 AI 的宗教豁免", ["religious exemption"]),
    # "master's degree" 与 "bachelor's" 混淆：摘要里的「学士」应为「硕士」
    ("学士学位", "硕士学位", ["master"]),
    # "commentator"（评论者）被译成「评论员」
    ("一个评论员花费了大部分时间在现有代码上", "其中一名评论者把大部分精力花在已有代码上", ["reviewer"]),
    # "reviewer"（评审者）应为「评审者」而非「评论员」
    ("一个评论员", "一名评审者", ["reviewer"]),
    # 2026-11-03 10:00 巡检新增："AI apps" 被译成「人工智能应用程序」，
    # 与站内既有写法（「AI 应用」）不一致，标题里显得冗长。
    # 触发词限定为 "ai app"，只影响明确出现该短语的条目。
    ("人工智能应用程序", "AI 应用", ["ai app"]),
    # "earnings call"（财报电话会议）被直译成「收益通话 / 收益电话」
    ("收益通话", "财报电话会议", ["earnings call"]),
    ("收益电话", "财报电话会议", ["earnings call"]),
    ("收益电话中", "财报电话会议上", ["earnings call"]),
    # 2026-11-03 10:00 巡检新增：离线模型对 "earnings call" 还有
    # 「财务电话」这一形态（把 earnings 意译成「财务」）。
    # 只登记了「收益X」时该形态会漏网，摘要里出现
    # 「在周一晚上的财务电话中暗示了…」这种明显不通的说法。
    # "财务电话" 是完整子串，因此放在「财务电话中」之后由长度降序
    # 排序保证「财务电话中」先被处理（TERM_FIXES 按 -len 排序）。
    ("财务电话中", "财报电话会议上", ["earnings call"]),
    ("财务电话", "财报电话会议", ["earnings call"]),
    # "org chart"（组织架构图）未译
    ("org 图表", "组织架构图", ["org chart"]),
    # "behaves as intended"（表现是否符合预期）英文残留
    ("是否 behaving 符合预期", "表现是否符合预期", ["behaves"]),
    # "frontier workloads"（前沿工作负载）被译成「边界工作负载」
    ("边界工作负载", "前沿工作负载", ["frontier workloads"]),
    # "More Perfect Union" 是报道来源媒体名，不能意译
    ("更多完美联盟", "More Perfect Union", ["more perfect union"]),
    # "car-by-car basis"（逐车定制）被直译成「汽车对汽车」
    ("“汽车对汽车”", "“逐车定制”", ["car-by-car"]),
    # "College Planner"（升学规划助手）是功能名
    ("学院规划师", "升学规划助手", ["college planner"]),
    ("即将到达青少年 ChatGPT", "即将上线 ChatGPT 青少年版", ["chatgpt for teens"]),
    # "quizzes"（小测）被译成「测试」
    ("新的闪卡，测试和青少年人工智能委员会", "闪卡、小测验和青少年 AI 委员会", ["quizzes"]),
    # "Roadster" 是特斯拉车型名，不能音译
    ("路德斯特", "Roadster 电动跑车", ["roadster"]),
    # "bottleneck"（瓶颈）被截断成「瓶」
    ("最大的瓶。", "最大的瓶颈。", ["bottleneck"]),
    ("瓶的一个根本原因", "瓶颈的一个根本原因", ["bottleneck"]),
    # "substation to the rack"（从变电站到机架）
    ("从子站到架子", "从变电站到机架", ["substation"]),
    # "siloed systems"（相互割裂的系统）被译成「隔离系统」
    ("隔离系统", "相互割裂的系统", ["siloed"]),
    # "gigawatts"（吉瓦）被译成「千兆瓦」——后者是网速单位
    ("千兆瓦", "吉瓦", ["gigawatt"]),
    # "interconnection queues"（并网排队队列）被译成「互联网队列」
    ("美国互联网队列", "美国并网排队队列", ["interconnection queues"]),
    # "low single-digit to tens of milliseconds"（个位数到数十毫秒）
    ("低单位数到数万毫秒", "个位数到数十毫秒", ["milliseconds"]),
    # "Under pressure to demonstrate"（在需要展示的���力下）
    ("在被压力迫", "在需要展示", ["roi"]),
    # "NBC News" 是媒体名，不能译成「美国广播公司新闻」
    ("美国广播公司新闻", "NBC News", ["nbc news"]),
    # "disarm"（解除武装）被译成「消灭」——在 AI 治理语境是"解除武装"而非"销毁"
    ("呼吁“消灭人工智能”", "呼吁“为 AI 解除武装”", ["disarm"]),
    ("呼吁将人工智能解除武装", "呼吁为人工智能解除武装", ["disarm"]),
    # "robots.txt" 是文件协议名，不能译成「机器人」
    ("将生活在网站的机器人内部", "将写入网站的 robots.txt 中", ["robots.txt"]),
    # "reads"（读取速度）被译成「阅读」
    ("12×更快的阅读", "12× 更快的读取", ["reads"]),
    # "precise visuals"（精确的视觉效果）被译成「精确视图」
    ("精确视图", "精确的视觉效果", ["precise visuals"]),
    # "Apple said" 被截成「果表示」——Apple 品牌还原时残留
    ("果表示", "Apple 表示", ["apple"]),
    # "AI" 被译成「人智能」时，联盟名需还原
    ("神经退行性疾病生物医学研究与人智能联盟", "神经退行性疾病生物医学研究与人工智能联盟", ["c-brain"]),
    # "agentic"（具备智能体能力的）译成「智能体式」后接「与物理」不通
    ("构建智能体式与物理 AI 应用", "构建智能体与物理 AI 应用", ["agentic"]),
    # ---- 2026-11-02 14:00 巡检新增：半导体/边缘 AI 术语误译 ----
    # "fabless"（无晶圆厂）被译成「无形」，在半导体语境下完全不通，
    # 正确写法是「无晶圆厂」。
    ("无形人工智能半导体公司", "无晶圆厂 AI 半导体公司", ["fabless"]),
    ("无形半导体公司", "无晶圆厂半导体公司", ["fabless"]),
    # "edge AI"（边缘 AI）被译成「尖端 AI」——「尖端」对应的是
    # "cutting-edge"，与 edge（边缘）语义完全不同，且会误导读者。
    ("尖端 AI 系统-on-chip", "边缘 AI 系统级芯片", ["edge ai"]),
    ("尖端 AI", "边缘 AI", ["edge ai", "edge computing"]),
    # "system-on-chip" 被译成中英混排的「系统-on-chip」，中文里不通。
    ("系统-on-chip", "系统级芯片", ["system-on-chip"]),
    # ---- 2026-11-02 17:00 巡检新增：融资/开源库/语义层术语误译 ----
    # "EASE"（荷兰医疗器械即服务公司名）被模型意译成「易」+ 残留的 "ASE"，
    # 产出「易 ASE 筹集了……」，公司名彻底丢失。此处按「易 ASE」整体还原。
    # 触发词同时接受 "ease holdings"（出现在摘要）与 "ease "（标题里
    # EASE 作为全大写词出现，源文本小写化后即为 "ease "）。
    ("易 ASE", "EASE", ["ease holdings", "ease "]),
    ("易ASE", "EASE", ["ease holdings", "ease "]),
    # "Raises $9.5M Equity" 中 equity 指「股权/股本次融资」，
    # 模型译成「资产」——在融资语境下「资产」是完全错误的（assets ≠ equity）。
    ("万美元的资产", "万美元的股权", ["equity", "raises"]),
    ("万元的资产", "万元的股权", ["equity", "raises"]),
    # "Auto Ontology"（NVIDIA 语义层产品名）被意译成「自动解读」，
    # 产品名丢失。副标题里的 "open library" 也被译成「开放的图书馆」——
    # 软件语境下的 library 是「库」，不是「图书馆」。
    ("自动解读", "Auto Ontology", ["auto ontology"]),
    ("开放的图书馆", "开源库", ["open library"]),
    # "builds a context layer"（构建上下文层）被译成「构建了一个文本层」，
    # context layer 是数据工程的标准说法「上下文层」。
    ("构建了一个文本层", "构建了一个上下文层", ["context layer"]),
    # "The eval repo ships a harness, not results"（评测仓库提供的是测试
    # 框架而非结果）——harness 在软件语境是「测试框架」，模型译成「运势」。
    ("发送了一个运势", "提供的是测试框架", ["harness"]),
    ("运势，而不是结果", "测试框架，而不是结果", ["harness"]),
    # "compiles a SIMT GPU directly into the weights of Qwen3.5-2B"——
    # weights 在 AI 语境是「权重」，不是「重量」。
    ("的重量", "的权重", ["weights"]),
    # "Agents use that layer to write SQL against certified business
    # definitions"——against 在此表示「针对」，模型译成「相反」导致语义反转。
    ("写 SQL 与认证的商业定义相反", "针对经过认证的业务定义编写 SQL", ["certified business definitions"]),
    # "Inference uses hosted NVIDIA NIM endpoints"——inference 是「推理」，
    # endpoints 是「端点」，模型译成「终点」。
    ("Inference 使用", "推理使用", ["inference"]),
    ("NIM 终点", "NIM 端点", ["nvidia nim"]),
    # ---- 2026-11-02 17:00 巡检新增：品牌意译与融资阶段术语 ----
    # "Marble Cognition"（AI 办公智能体创业公司）被逐词意译成「理石认知」，
    # 公司名变成一个通顺但完全对不上的中文词组。此处按整体还原。
    ("理石认知", "Marble Cognition", ["marble cognition"]),
    # "Pre-Seed"（种子前融资轮）被译成「预种子」「预种」，
    # 中文创投语境的标准说法是「种子前轮」。
    # 注意措辞：替换结果不能再带「资金/融资」二字，否则与原文的
    # "funding" 叠加后会出现「种子前轮融资资金」这类重复。
    ("万美元的预种资金", "万美元的种子前轮融资", ["pre-seed"]),
    ("的预种子", "的种子前轮融资", ["pre-seed"]),
    ("预种资金", "种子前轮融资", ["pre-seed"]),
    # ---- 2026-11-02 20:00 巡检新增：智能体架构术语（memory / context）----
    # 背景：InfoQ AI 19:00 那条《Systemic Approach to Memory, Knowledge,
    # and Context in Agentic AI Architectures》把三个核心概念全译错了：
    #   context  -> "背景" / "环境"   （应为「上下文」）
    #   memory   -> "内存"            （应为「记忆」）
    #   curated  -> "策划"            （应为「精选」）
    # 这些词在中文 AI 技术语境里有相对固定的译法，译错不影响可读性
    # 但会让读者抓不到重点，因此按触发词精确修复。
    #
    # 注意「内存」一词在中文里同时指 RAM（硬件内存），所以不能无条件替换。
    # 这里只在原文出现 agentic / agent memory / memory stack 等
    # "记忆型 memory" 语境时才把「内存」还原为「记忆」，
    # 硬件语境（unified memory / memory bandwidth / peak memory）保持不动。
    ("环境引擎", "上下文引擎", ["context engine"]),
    ("环境，内存和知识", "上下文、记忆和知识", ["separates context, memory"]),
    ("记忆，知识和背景", "记忆、知识和上下文", ["memory, knowledge, and context"]),
    ("对记忆，知识和背景", "对记忆、知识和上下文", ["memory, knowledge, and context"]),
    ("策划知识", "精选知识", ["curated knowledge"]),
    ("层次内存", "分层记忆", ["tiered memory"]),
    ("内存堆", "记忆栈", ["memory stack"]),
    ("记忆堆", "记忆栈", ["memory stack"]),
    ("关键内存类型", "关键记忆类型", ["memory types"]),
    # "inject" 在软件语境是「注入」，模型偶发译成「注射」（医学校译）。
    # 用整串短语一次性修复，避免多条短规则先后命中留下半角逗号。
    ("选择，注射，压缩", "选择、注入、压缩", ["selects", "injects", "compresses"]),
    ("注射，压缩", "注入、压缩", ["injects", "compresses"]),
    ("选择，注射", "选择、注入", ["selects", "injects"]),
    # "context stuffing"（上下文填充）是 LLM 的已知反模式，
    # 模型译成「文本填充」完全丢失了"context"这层含义。
    ("文本填充", "上下文填充", ["context stuffing"]),
    # "patterns" 在软件架构语境是「模式」，模型译成「图案」（图像义）。
    ("构建块，图案和框架", "构建模块、模式与框架", ["building blocks", "patterns"]),
    # "typing your query into a good old search engine"——query 在搜索语境
    # 是「查询词」，模型译成「输入查询」后动词宾语关系断裂，
    # 整句读作「通过输入查询到一个搜索引擎」（搜索��擎被当成宾语）。
    ("通过输入查询到", "在搜索框中输入查询词后使用", ["typing your query into"]),
    ("输入查询到", "输入查询词后使用", ["typing your query into"]),
    # ---- 2026-11-02 22:00 巡检新增：所有格 / 粘连 / 语义直译 ----
    # 「ChatGPT's chat and Work tabs」的所有格撇号被模型吃掉，
    # 产出「ChatGPTs 聊天和工作 tabb 合并」——中文读者会把它当成
    # 复数产品名「ChatGPTs」，而不是「ChatGPT 的」。登记两种撇号形态
    # 作为触发词（原文用的是 U+2019 右单引号）。
    ("ChatGPTs", "ChatGPT 的", ["chatgpt’s", "chatgpt's"]),
    # 「EPRI's DCFlex Initiative」的所有格与后续词粘连成「EPRIsDCFlex」。
    ("EPRIsDCFlex", "EPRI 的 DCFlex", ["dcflex"]),
    # 「EPRIsDCFlex」的所有格粘连修完后，「full member」被直译成
    # 「全会员」（像健身房年卡），这里按整句片段还原为「正式成员」。
    ("的全会员", "的正式成员", ["full member"]),
    # 「start counting what ships」里的 ships 是动词（交付/上线），
    # 模型按名词「货物」直译成「什么货」，标题完全读不通。
    ("什么货", "真正交付的成果", ["what ships"]),
    # 「the more calls it makes」的 calls 是「调用次数」，
    # 模型译成「打电话」，语义完全跑偏。按整句片段替换，避免拼出
    # 「现在如今…」这类叠词病句。
    ("智能体越有用，就越多打电话", "智能体越有用，发起的调用就越多",
     ["the more calls it makes"]),
    # 「People-First」被逐词直译成「人员首发」，中文不成立。
    # 整句直译（"以人工智能为主的人员首发的城市"）语序依然不通，
    # 因此这里按整串替换，避免逐词替换后拼出「以人为本的城市」这种病句。
    ("以人工智能为主的人员首发的城市", "以人为本的 AI 城市", ["people-first"]),
    ("人员首发", "以人为本", ["people-first"]),
    # 「Now it is AI's turn」直译成「现在是人工智能的轮到」，语序不通。
    ("现在是人工智能的轮到", "如今轮到人工智能登场了", ["it is ai's turn"]),
    # NLLB 偶发把英文单词的重复字母带进译文（tabs → "tabb"），
    # 中文读者看到孤立英文残片会以为是乱码。触发词为原文的 "tabs"。
    ("tabb", "标签页", ["tabs"]),
    # ---- 2026-11-02 22:00 巡检新增：MCP / 上下文语境下的直译缺陷 ----
    # 「engineering context」被译成「工程背景」——在软件工程语境里
    # context 指的是「上下文」，不是「背景」。触发词放宽到 "context layer"
    # 与 "engineering context"，摘要里英文常写成 "into context that ..."，
    # 因此另加 "software-delivery data into context" 这一组合触发。
    ("工程背景", "工程上下文", ["engineering context", "context layer",
                                "into context that"]),
    # 「MCP Gateway」被译成「MCP 门户」——网关是技术术语，
    # 「门户」在中文里指门户站点，语义完全不同。
    ("MCP 门户", "MCP 网关", ["mcp gateway"]),
    ("该门户", "该网关", ["mcp gateway"]),
    # 「sensitive data redaction」是数据脱敏，不是「数据编辑」。
    ("敏感数据编辑", "敏感数据脱敏", ["sensitive data redaction"]),
    # 「tool registration」与「runtime execution」是 MCP 网关的两个机制。
    ("工具注册和运行时间执行", "工具注册与运行时执行", ["runtime execution"]),
    # ---- 2026-11-02 23:00 巡检新增：品牌失真 / 内容数量语境 ----
    # 「calls for a new enterprise discipline」直译成「要求建立新的企业纪律」，
    # 中文里 calls for 表示「需要/呼唤」，discipline 在管理语境下是「方法论/规范」。
    ("要求建立新的企业纪律", "需要一套全新的企业方法论", ["calls for a new"]),
    ("企业纪律", "企业方法论", ["enterprise discipline"]),
    # 「confuse it with another company」直译成「将其混到另一个公司」，
    # 语义与语序双错。按整串替换，避免逐词替换后拼出病句。
    ("将其混到另一个公司", "把这家企业与另一家公司混为一谈",
     ["confuse it with another company"]),
    # 「unsupported claims」被译成「无证指控」——「指控」在中文里带指控罪意味，
    # 这里只是「无依据的说法」。
    ("无证指控", "无依据的说法", ["unsupported claims"]),
    # 「put too much emphasis on volume」直译成「太重视了量」，
    # volume 在内容营销语境指内容数量。
    ("太重视了量", "过于看重内容数量", ["emphasis on volume"]),
    ("重视了量", "看重内容数量", ["emphasis on volume"]),
    # 「publish」在内容语境下应为「发布」而非「出版」。
    ("出版更多的内容", "发布更多内容", ["publish more"]),
    # ---- 2026-11-02 23:00 巡检新增：算力园区 / 液冷 / 专名 ----
    # 「compute campus」被译成「计算机校园」——campus 在这里指园区，
    # compute 指算力，是算力园区的固定中文写法。
    ("计算机校园", "算力园区", ["compute campus", "compute campuses"]),
    ("未来的算力校园", "未来的算力园区", ["compute campus"]),
    # 「Grid Protectors Program」是项目专名，直译成「电网保护程序」丢失专名感。
    ("电网保护程序", "电网守护者计划", ["grid protectors"]),
    # 「liquid know-how」在数据中心语境下指水处理与液冷方面的技术专长，
    # 直译成「液体技术」完全无法理解。
    ("液体技术", "水处理与液冷技术", ["liquid know-how", "liquid cooling"]),
    # 金额千分位：$16 million → 1,600 万美元。
    ("1600万美元", "1,600 万美元", ["$16 million"]),
    ("1600 万美元", "1,600 万美元", ["$16 million"]),
    # ---- 2026-11-03 00:00 巡检新增：campus 变体 / 专名 / 地名 / 单位 ----
    # 「电脑校园」是同一术语的另一变体：模型把 compute campus 译成
    # 「电脑校园」，与「计算机校园」一样指算力园区。
    ("电脑校园", "算力园区", ["compute campus", "compute campuses"]),
    ("算力校园", "算力园区", ["compute campus", "compute campuses"]),
    # 「电网保护者计划」是「电网守护者计划」的直译变体，项目专名需统一。
    ("电网保护者计划", "电网守护者计划", ["grid protectors"]),
    # 「埃菲金汉」是 Effingham County 的错误音译，正确为「埃芬汉」。
    ("埃菲金汉", "埃芬汉", ["effingham"]),
    # 「格鲁吉亚」是国名 Georgia（country）。原文里的 Georgia 指的是
    # 美国佐治亚州（数据中心、电网场景），必须译「佐治亚州」，
    # 否则会读成东欧国家，属严重事实错误。
    # 触发词只用无歧义的美国佐治亚州标记，避免误伤真正的国名 Georgia。
    ("格鲁吉亚", "佐治亚州", ["effingham", "atlanta", "georgia power",
                              "georgia county", "savannah"]),
    # 「埃菲金汉县校园」→「埃芬汉县园区」：地名 + campus 双重误译。
    ("县校园", "县园区", ["effingham", "compute campus"]),
    # 「这是一个国家计划」漏译 nationwide 的「全国性」语义。
    ("这是一个国家计划", "这是一项全国性行动", ["nationwide effort", "national effort"]),
    # 功率单位千分位：1,000 megawatts → 1,000 兆瓦。
    ("1000兆瓦", "1,000 兆瓦", ["1,000 megawatts", "1000 megawatts"]),
    ("1000 兆瓦", "1,000 兆瓦", ["1,000 megawatts", "1000 megawatts"]),
    # 金额千分位：$62.5 million → 6,250 万美元。
    # NLLB 把 "$62.5M" 译成「6250 万美元」，缺千分位，与站内既有写法
    # （1,600 万美元 / 6,250 万美元）不一致，需统一。
    ("6250万美元", "6,250 万美元", ["$62.5m", "$62.5 million", "62.5 million"]),
    ("6250 万美元", "6,250 万美元", ["$62.5m", "$62.5 million", "62.5 million"]),
    # ── 2026-11-03 03:00 周期新增条目的术语缺陷 ──
    # "post-training Z.ai's GLM-5.3" 被译成「后期培训」——
    # post-training 在 AI 语境下固定译「后训练」，不是「后期培训」。
    ("后期培训", "后训练", ["post-training", "post training"]),
    # "open-weight scientific model" 译成「开放重量」——
    # open-weight 是「开放权重」（可下载权重），不是「开放重量」。
    ("开放重量", "开放权重", ["open-weight", "open weight"]),
    # "1M-token context" 译成「1M 代码语境」——
    # token 在 AI 语境下固定译「token」，context 译「上下文」。
    ("代码语境", "token 上下文", ["1m-token context", "token context"]),
    # "The weights ship under the MIT License" 译成「权重在 MIT 许可下运输」——
    # ship 在软件语境下是「发布/开源」，不是「运输」。
    ("许可下运输", "许可下发布", ["mit license"]),
    # "Performance: Beats GPT-6-Astra" 译成「打败」——
    # 基准跑分语境下 "beats" 固定译「击败」。
    ("打败 GPT-6-Astra", "击败 GPT-6-Astra", ["beats gpt-6-astra"]),
    # "What is Hydrogen-1.0?" 译成「什么是-1.0?」——
    # 遮蔽层还原后专名完整，此规则兜底"专名 + 问号"被拆开的形态。
    ("什么是-1.0?", "什么是 Hydrogen-1.0?", ["what is hydrogen"]),
    # ── 2026-11-03 03:35 周期新增条目的系统性误译 ──
    # "Anthropic Launches…" 中 Anthropic 被音译替换成「人类」+ Launches→「发射」，
    # 结果标题变成「人类发射信息线程」。anthropic 品牌表里已有「人类学」等变体，
    # 这里补「人类发射」这类由音译+动词粘连产生的变体。
    ("人类发射", "Anthropic 推出", ["anthropic launches"]),
    ("人类启动", "Anthropic 推出", ["anthropic launches"]),
    # "scraping … copyrighted … distributing" 被译成「删除了其版权保护的网站」，
    # scraping→删除、copyrighted→网站，均为错配。
    ("删除了其版权保护的网站", "抓取了该媒体受版权保护的内容", ["scraping"]),
    # "builds context into AI code review" → 「构建了文本」
    ("构建了文本", "将上下文引入", ["builds context into"]),
    # "active sessions where latency matters" → 「延迟重要的活跃会议」
    ("延迟重要的活跃会议", "对时延敏感的活跃会话", ["latency matters"]),
    ("截图仍然与线程保持", "截图需随会话保留", ["screenshots remain with the thread"]),
    # ── 2026-11-03 05:00 周期新增条目的系统性误译 ──
    # A) xAI Introduces Data Bot to Bring Shared Analytics Skills to Grok Bot
    #    「Data Bot」「Shared Bot」是产品名，被意译成「数据机器人」「共享机器人」，
    #    中文读者无法定位到具体产品；统一还原为英文产品名。
    ("数据机器人", "Data Bot", ["data bot"]),
    ("共享机器人", "Shared Bot", ["shared bot"]),
    #    unite.ai 原文把 SpaceXAI 误拼为 "SpaceXSI"（源站笔误，
    #    且 og:description 与正文共 7 处），模型照抄后中文出现「太空 XSI」。
    #    按事实实体还原为 SpaceXAI。
    ("SpaceXSI", "SpaceXAI", ["spacexsi"]),
    ("太空 XSI", "SpaceXAI", ["spacexsi"]),
    ("太空XSI", "SpaceXAI", ["spacexsi"]),
    # B) Oracle Files Concurrent Common Stock and Senior Notes Offerings
    #    senior notes 是「优先票据」（债券品种），不是「资深笔记」。
    ("资深笔记", "优先票据", ["senior notes"]),
    ("高级证券备忘录补充文件", "优先票据招股说明书补充文件", ["prospectus supplement"]),
    ("高级证券", "优先票据", ["senior notes"]),
    ("股票明信片补充", "普通股招股说明书补充", ["prospectus supplement"]),
    ("公开报价空白", "公开发行价格留空", ["public offering price"]),
    ("同时的股票和", "同时发行的普通股和", ["concurrent common stock"]),
    ("同时提供", "同时发行", ["concurrent offerings"]),
    # C) Sierra Puts Ghostwriter at the Center of Agent Studio Workflows
    #    「journey editing」是智能体工作流里的「旅程编排」，
    #    被按「旅行编辑」直译，语义完全跑偏。
    ("旅行编辑", "旅程编排", ["journey editing"]),
    ("编辑行程", "编排旅程", ["journey editing", "edit journeys"]),
    # 标题里 "Oracle Files …" 的 Files（动词，提交/申报）未译。
    ("Oracle Files", "Oracle 提交", ["oracle files"]),
    # "its agent-building agent" 被拆成「其智能体构建智能体」，
    # 关系错乱，须明确为「用于构建智能体的 Ghostwriter」。
    ("围绕其智能体构建智能体", "围绕用于构建智能体的 Ghostwriter",
     ["agent-building agent"]),
    # ── 2026-11-03 06:00 巡检新增：05:40—05:54 四条 Unite.AI 条目术语失真 ──
    # A) OpenAI's LifeVal Evaluation …
    #   "personal agents" 被译出冗余「人」字：「个人智能体人的帮助」。
    ("个人智能体人", "个人智能体", ["personal agents"]),
    #   "finding childcare" 译成「寻找照顾」——childcare 是育儿照护服务，
    #   「照顾」在中文里指照料行为，完全不是一回事。
    ("寻找照顾", "寻找育儿照护", ["childcare"]),
    ("查找儿童护理", "寻找育儿照护", ["childcare"]),
    # B) LongCat-2.5 …
    #   "natively multimodal" 译成「原始多模态」——natively 是「原生」，
    #   「原始」是 raw/original，语义相反。
    ("原始多模态", "原生多模态", ["natively multimodal"]),
    #   "long-horizon" 是「长时程」（AI 论文固定译法），
    #   按「视线/视野」直译后中文完全无法理解。
    ("长视野", "长时程", ["long-horizon", "long horizon"]),
    ("长视线", "长时程", ["long-horizon", "long horizon"]),
    #   "training" 是「训练」不是「培训」。
    ("它的培训包括", "其训练过程包括", ["its training incorporates"]),
    #   "agentic coding" 是「智能体编程」。
    ("智能体编码", "智能体编程", ["agentic coding"]),
    # C) Omen AI …
    #   "sensing technologies" 是「传感技术」，不是「传感器技术」；
    #   加上后半句「的研发和开发」会变成同义反复。
    ("传感器的研发和开发", "传感技术的研发", ["sensing technologies"]),
    # ---- 2026-11-03 07:00 巡检新增 ----
    # D) Anthropic 的意译形态仍会漏网。
    #   "Anthropic warns that ..." 被 NLLB 译成「人类警告说」——
    #   "warns" 连同公司名一起被意译，中文里完全看不出是 Anthropic。
    #   既有规则只覆盖了「人类学」「人类论文说」「人类工程师」等固定搭配，
    #   「警告」这个动词还没登记，本轮新条目再次逃逸。
    #   注意：这里只登记「人类+言说动词」这种中文里本就不成立的搭配，
    #   「人类表示」「人类称」这类通用说法留给 _fix_anthropic_subject()
    #   按「句首主语」定位，避免文章里同时出现 Anthropic 与人类时误伤。
    ("人类警告说", "Anthropic 警告说", ["anthropic"]),
    ("人类警告", "Anthropic 警告", ["anthropic"]),
    ("人类论文说", "Anthropic 说", ["anthropic"]),
    # E) 财报类金融术语直译：
    #   "Gross margin"（毛利率）被逐词译成「总利率」，
    #   在中文里「总利率」不是财务术语，读者无法定位指标。
    ("总利率", "毛利率", ["gross margin"]),
    #   "diluted earnings per share"（摊薄每股收益）被译成「股票均利率」，
    #   这个中文词根本不存在，是 EPS 被拆词直译的产物。
    ("股票均利率", "摊薄每股收益", ["diluted earnings per share", "diluted eps"]),
    ("摊薄每股盈利", "摊薄每股收益", ["diluted earnings per share", "diluted eps"]),
    #   "diluted EPS" 单独出现时也统一成「摊薄每股收益」，
    #   避免同一条里「稀释的 EPS」「摊薄每股收益」两种叫法并存。
    ("稀释的 EPS", "摊薄每股收益", ["diluted eps", "diluted earnings per share"]),
    ("稀释每股收益", "摊薄每股收益", ["diluted eps", "diluted earnings per share"]),
    #   "net income"（净利润）不是「净收入」。
    ("净收入为", "净利润为", ["net income"]),
    # F) "AI doomers"（AI 悲观论者）被译成「人工智能毁灭者」，
    #   措辞夸张且非中文习惯表达。
    ("人工智能毁灭者", "AI 悲观论者", ["ai doomers", "doomer"]),
    ("毁灭者", "悲观论者", ["ai doomers", "doomer"]),
    # G) "self-building AI"（自我构建 AI）：「自建 AI」在中文里
    #   通常指「企业自己搭一套 AI」，与本义（AI 自我构建）不符。
    ("自建 AI", "自我构建 AI", ["self-building ai"]),
    #   收购句里机构名与下一句主语粘连成「Aquatic Labs.Aquatic Labs」。
    ("Aquatic Labs.Aquatic Labs", "Aquatic Labs。Aquatic Labs", ["aquatic labs"]),
    # D) DeepSeek Harness …
    #   "prerelease" 是「预发布版本」，不是「预测版本」。
    ("预测版本", "预发布版本", ["prerelease", "pre-release"]),
    ("预发布版本", "预发布版本", ["prerelease", "pre-release"]),
    #   插件管理里的入口项名 "Let Agent create a plugin" 应保持原样引述，
    #   并把「进入插件管理」的语序理顺。
    ("Let Agent 创建插件进入插件管理",
     "名为「Let Agent create a plugin」的入口项", ["let agent create a plugin"]),
    #   "carries the existing draft into Creator mode" 是「把已有草稿带入」，
    #   不是「输入」。
    ("将现有的草稿输入", "把已有草稿带入", ["carries the existing draft"]),
    # ── 2026-11-03 09:00 巡检新增（4 类根因）────────────────────
    #
    # 1) Brave 作公司名时被 NLLB 当普通形容词意译成「勇敢」。
    #    「勇敢」单独成词时（而非「勇敢的软件」这类固定搭配），
    #    由 _fix_brave_company 统一处理：它需要判断 Brave 是公司名还是
    #    普通动词（"Brave Capitol Hill" 意为「勇闯国会山」），
    #    规则表做不到，故不在此处登记。
    # 2) The Letter Company 被拆成「字母公司」——"Letter" 在这里是
    #    公司名（发布 Letterpress-1 的初创公司），但 NLLB 按普通名词
    #    「字母/信」直译，品牌彻底丢失。标题里更糟：整个品牌词被丢掉，
    #    只剩「公司发布了…」，这种整段丢失只能靠人工定稿兜底。
    ("字母公司", "The Letter Company", ["the letter company", "letterpress"]),
    # 3) Y Combinator（美国顶级加速器）被意译成「Y 组合者」，
    #    中文读者完全无法定位机构，必须保留英文原名。
    ("Y 组合者", "Y Combinator", ["y combinator"]),
    # 4) 通用技术术语直译失真：
    #    "pull request" 译成「带动请求」（已有「拉动请求」规则，补这一种）；
    #    "git repository" 译成「吉特库」（Git 是专名，不该音译）；
    #    "fine-tuned" 译成「精细调节」（应为「微调」）；
    #    "implied enterprise value" 译成「企业价值意味着」
    #    （应为「隐含企业价值」，财务并购语境的标准说法）。
    ("带动请求", "拉取请求", ["pull request"]),
    ("吉特库", "Git 仓库", ["git repository", "git repo"]),
    ("精细调节的小模型", "微调后的小模型", ["fine-tuned"]),
    ("精细调节", "微调", ["fine-tuned"]),
    ("企业价值意味着", "隐含企业价值为", ["implied enterprise value"]),
    # ── 2026-11-03 11:00 巡检新增（Zyphra / Driscoll 两条新条目）────────
    #
    # 1) Zyphra 是 AI 芯片/模型创业公司名（发布 ZHA 层次化注意力方法），
    #    被 NLLB 音译成「齐弗拉」。与站内 Apple/Anthropic/Salesforce
    #    的处理一致：创业公司名一律保留英文原名，中文读者无法通过
    #    音译定位到该公司。
    ("齐弗拉", "Zyphra", ["zyphra"]),
    # 2) 注意力机制的三组核心术语，NLLB 全部按普通词意译，技术含义走样：
    #    "sparse attention"（稀疏注意力）→「稀有注意力」，
    #    "hierarchical attention"（层次化注意力）→「等级注意力」，
    #    "dense attention"（稠密注意力）→「密集关注」。
    #    这三个词是 Transformer 架构的基础术语，译错后整段技术描述不可读。
    ("稀有注意力", "稀疏注意力", ["sparse attention"]),
    ("等级注意力", "层次化注意力", ["hierarchical attention"]),
    ("密集关注", "稠密注意力", ["dense attention"]),
    # 3) "subquadratic"（次二次复杂度）是算法复杂度标准术语，
    #    直译成「次次级」后完全不成词。
    ("次次级", "次二次", ["subquadratic"]),
    # 4) "frozen pretrained models"（冻结的预训练模型）→「冷预训练」，
    #    "distilled into"（蒸馏到）→「蒸成」，两处都是术语直译失真。
    ("冷预训练", "冻结的预训练", ["frozen pretrained", "frozen pre-trained"]),
    ("蒸成", "蒸馏到", ["distilled into"]),
    # 5) "context" 在「上下文长度 / context window」语境应译「上下文」，
    #    NLLB 译成「语境」；站点既有 1M context 语境，同一术语须统一。
    ("语境", "上下文", ["context window", "context length", "256k context"]),
    # 6) "Secretary of the Army"（美国陆军部长）官方译名为「陆军部长」，
    #    NLLB 按字面译成「陆军秘书」。这是美国国防部最高级别的文职官职，
    #    译错会影响读者对新闻重要性的判断。
    ("陆军秘书", "陆军部长", ["secretary of the army", "army secretary"]),
    ("前陆军部长", "前陆军部长", ["secretary of the army", "army secretary"]),
    # 7) "retrofits frozen pretrained models"（回溯改造冻结的预训练模型）
    #    与 "Speedups come from..."（加速比来自…）在原文里是独立小句，
    #    NLLB 把句首主语当普通词留着未译，中英混排。中文须补全主语。
    ("Retrofits 冻结的预训练模型", "可回溯改造冻结的预训练模型",
     ["retrofits frozen pretrained models"]),
    ("Speedups 来自", "加速比来自", ["speedups come from"]),
    # ── 2026-11-03 11:15 巡检新增（OpenAI 两条安全公告）────────────
    # 1) "bug bounty"（漏洞赏金）是安全领域的固定术语，
    #    直译成「bug 奖励」后中文不成词（"奖励更大的 bug 奖励的捍卫者"）。
    #    业界通行译法是「漏洞赏金」。
    ("安全 Bug Bounty 奖励", "安全漏洞赏金奖励", ["security bug bounty"]),
    ("Bug Bounty 奖励", "漏洞赏金奖励", ["bug bounty"]),
    ("Bug Bounty", "漏洞赏金（bug bounty）", ["bug bounty"]),
    ("bug 奖励", "漏洞赏金", ["bug bounty"]),
    # 2) "campaign bonuses"（专项活动奖金）中 priority（优先）与
    #    campaign（专项活动）被拆错位，产出「优先活动奖励」。
    ("优先活动奖励", "优先响应专项活动奖金", ["priority campaign bonuses"]),
    ("报告质量，忠诚度和优先活动奖励", "报告质量、忠诚度与优先响应三项专项活动奖金",
     ["report quality, loyalty, and priority campaign bonuses"]),
    # 3) Cathedral Systems 是合作安全公司名，被意译成「大教堂系统」，
    #    中文读者完全无法识别是哪家公司，必须保留英文原名。
    ("大教堂系统", "Cathedral Systems", ["cathedral systems"]),
    ("大教堂系统公司", "Cathedral Systems", ["cathedral systems"]),
    # 2026-11-03 14:00 巡检：原文只写 "Cathedral"（不带 Systems）时，
    # 既有规则匹配不到，「大教堂的研究人员」变成一个虚构机构。
    ("大教堂的研究人员", "Cathedral 的研究人员", ["cathedral"]),
    ("大教堂", "Cathedral", ["cathedral"]),
    # 2026-11-03 14:00 巡检："raised rewards and introduced bonuses"
    # 被译成「提高了奖励和引入了奖励」——同义重复，读起来像机器故障。
    ("提高了奖励和引入了奖励", "提高了奖励额度并新增了专项奖金", ["introduced bonuses"]),
    ("奖励和引入了奖励", "奖励额度并新增了专项奖金", ["introduced bonuses"]),
    # "critical payouts"（严重漏洞的赏金支付）被译成「关键付款」，
    # 金融术语串味，读者会误解为付款流程。
    ("特殊的关键付款", "特别严重的漏洞赏金", ["critical payouts"]),
    ("关键付款", "漏洞赏金", ["critical payout"]),
    # 4) "harden ... defenses"（加固防御体系）→「加强其防御」，
    #    漏掉"体系"这层含义；"its defenses" 统一为「其防御体系」。
    ("加强其防御", "对其防御体系进行加固", ["harden", "strengthen its defenses"]),
    ("以加强 OpenAI", "加固 OpenAI 防御体系", ["harden openai"]),
    # ── 2026-11-03 11:20 巡检新增 ────────────────────────────────
    # 1) "responsible AI"（负责任的 AI）是 AI 治理领域的固定术语，
    #    模型把 responsible 整个丢掉，产出「为…的 AI 提供建议」，
    #    语义完全走样。术语必须补回。
    ("负责任的 AI", "负责任的 AI", ["responsible ai"]),
    ("可负责任的 AI", "负责任的 AI", ["responsible ai"]),
    # 2) "advise on X for Y"（就 X 在 Y 方面提供建议）语序被模型颠倒，
    #    产出「为负责…的 AI 提供建议」，中文不成句。
    ("任命丹·迪斯科尔为负责国家安全现代化，网络弹性和与美国盟国合作的 AI 提供建议",
     "任命丹·迪斯科尔就负责任的 AI 提供建议，议题涵盖国家安全现代化、网络韧性与对美国盟友的协作",
     ["appoints dan driscoll to advise on responsible ai"]),
    # ── 2026-11-03 15:00 巡检新增 ────────────────────────────────
    # 1) "petabyte"（PB = 10^15 字节）被模型逐字直译成「一百字节」——
    #    「petabyte」里的 peta（千五）被当成「一百」，量级差 10^13 倍，
    #    属严重事实错误（原文说的是每天近 1 PB 的数据量）。
    #    存储单位统一保留英文缩写，避免模型自行拆词造词。
    ("一百字节", "1 PB", ["petabyte"]),
    ("拍字节", "1 PB", ["petabyte"]),
    # 2) "median push latency"（Git 推送延迟中位数）——"push" 在 Git 语境
    #    是「推送」不是「推迟」，模型译成「中位 push 延迟」，
    #    标题里又写成「中位推迟」，中英夹杂且语义走样。
    ("中位 push 延迟", "推送延迟中位数", ["median push latency", "push latency"]),
    ("中位推迟", "推送延迟中位数", ["median push latency", "push latency"]),
    ("平均推进延迟", "推送延迟中位数", ["median push latency"]),
    # 3) "non-trunk history"（非主干历史）——Git 的 trunk 是「主干」，
    #    模型译成「干部」，中文读者会理解成党政机构的「干部」。
    ("非干部历史", "非主干历史", ["non-trunk"]),
    ("非干部", "非主干", ["non-trunk", "trunk"]),
    # 4) "Commodity hardware"（通用商用硬件）——直译成「商品硬件」，
    #    中文里不成词。
    ("商品硬件", "通用商用硬件", ["commodity hardware"]),
    # 5) "concurrent pushers"（并发推送方）——"pusher" 指推送 Git 的客户端，
    #    模型译成「推进器」（航天器部件），语义完全无关。
    ("同时推进的推进器", "并发推送方", ["concurrent pushers"]),
    ("数千个同时推进的推进器", "数千个并发推送方", ["concurrent pushers"]),
    # 6) "saturate 10 Gbps links"（跑满 10 Gbps 链路）——模型把 saturate
    #    吞成单字「化」，句子读不通。
    #    注意 _clean_zh 的数字+单位补空格规则先于术语修复执行，
    #    故此处须同时登记带空格与不带空格两种形态。
    ("时化 10 Gbps 链接", "时可跑满 10 Gbps 链路", ["saturate"]),
    ("化 10 Gbps 链接", "跑满 10 Gbps 链路", ["saturate"]),
    ("时化 10Gbps 链接", "时可跑满 10 Gbps 链路", ["saturate"]),
    ("化 10Gbps 链接", "跑满 10 Gbps 链路", ["saturate"]),
    # 7) "per OpenAI's own testing"（据 OpenAI 自身测试）——模型译成
    #    「每次 OpenAI 自己的测试」，"per"（依据）被误读为「每次」。
    #    注意原文用的是排版撇号 U+2019（’），不是 ASCII 撇号，
    #    因此触发词取不含撇号的「own testing」。
    ("每次 OpenAI 自己的测试", "据 OpenAI 自身测试", ["own testing"]),
    # 8) MarkTechPost 模板的 "Worst:" 标签——模型有时译成「最糟糕的是：」，
    #    与站内主流写法「最差：」不一致。
    ("最糟糕的是：", "最差：", ["worst:"]),
    # ── 2026-11-03 16:00 巡检新增（NVIDIA 城市 AI 两条）────────────
    # 9) "Physical and agentic AI"（物理 AI 与智能体 AI）——模型把
    #    "agentic"（具备智能体能力的）译成「机器人」，产出
    #    「物理和机器人人工智能」，语义完全跑偏（机器人 AI 是另一回事）。
    #    触发词取 "physical and agentic"，确保只在同一句里出现
    #    physical + agentic 时才改，不会误伤真正的 robotics 表述。
    ("物理和机器人人工智能", "物理和智能体人工智能", ["physical and agentic"]),
    ("机器人人工智能", "智能体人工智能", ["physical and agentic"]),
    # 10) "Shared computing infrastructure"（共享计算基础设施）——
    #     "shared"（共享的）被译成「分享的」，中文里「分享的计算基础设施」
    #     不成词，读者会误解为"把基础设施分享出去"。
    ("分享的计算基础设施", "共享的计算基础设施", ["shared computing infrastructure"]),
    ("分享的计算资源", "共享的计算资源", ["shared computing infrastructure"]),
    # 11) "digital twins"（数字孪生）——译成「数字双胞胎」。两种译法
    #     在中文技术圈都出现过，但本站既有条目（MIT Tech Review、
    #     NVIDIA Blog 10-22）用的是「数字孪生」，统一到同一写法。
    ("数字双胞胎", "数字孪生", ["digital twin"]),
    # 12) "GTC Berlin"（NVIDIA 开发者大会柏林场）——模型把地名 Berlin
    #     译成「柏林」。会议专名应保留英文原名，与站内在研的
    #     "GTC Berlin" 写法一致（10-22、10-21 两条已是 GTC 柏林）。
    #     注意：源文触发词用 "gtc berlin"，避免误伤真正的城市柏林。
    ("GTC 柏林", "GTC Berlin", ["gtc berlin"]),
    # 13) "cameras, sensors and operational systems"（摄像头、传感器与
    #     业务系统）——模型把 "operational systems"（业务/运营系统）
    #     译成「操作系统」，中文里「操作系统」特指 OS，含义完全不同。
    ("传感器和操作系统", "传感器和业务系统", ["operational systems"]),
    ("摄像头，传感器和业务系统", "摄像头、传感器和业务系统",
     ["operational systems"]),
    ("摄像头，传感器和操作系统", "摄像头、传感器和业务系统",
     ["operational systems"]),
    # 14) 中文并列项之间应用顿号而非逗号。模型逐词直译英文的
    #     comma-separated list 时会保留逗号，排出「摄像头，传感器和
    #     操作系统」这种中文排版不合规的形态。
    #     这里只登记本轮实测到的具体枚举串，不做通用替换——
    #     全库 359 条中形如「A，B和C」的片段有 52 处，绝大多数是
    #     正常的中文分句而非并列枚举，通用规则会大面积误伤。
    ("包括居民援助，交通管理，城市规划和工业运营",
     "包括居民援助、交通管理、城市规划和工业运营",
     ["resident assistance", "traffic management"]),
    ("共享计算基础设施，AI 智能体和数字双胞胎结合在一起",
     "共享计算基础设施、AI 智能体和数字孪生结合在一起",
     ["shared computing infrastructure"]),
    ("用于规划，维护和公共服务", "用于规划、维护和公共服务",
     ["planning, maintenance"]),
    ("城市部门，邻近的市政和当地开发人员", "城市部门、邻近的市政和当地开发人员",
     ["neighboring municipalities"]),
    # 15) 「共享的计算基础设施，AI 智能体和数字孪生结合在一起」——
    #     英文 "combine shared computing infrastructure, AI agents and
    #     digital twins" 是三项并列，中文应用顿号分隔。
    ("共享的计算基础设施，AI 智能体和数字孪生结合在一起",
     "共享的计算基础设施、AI 智能体和数字孪生结合在一起",
     ["shared computing infrastructure"]),
    # 同上，模型有时不产出「的」字（"共享计算基础设施"），
    # 故两种形态都要登记。
    ("共享计算基础设施，AI 智能体和数字孪生结合在一起",
     "共享计算基础设施、AI 智能体和数字孪生结合在一起",
     ["shared computing infrastructure"]),
    # 16) "enormous amounts of data"（海量数据）——模型逐词直译成
    #     「大量的数据」，「的」字冗余，中文习惯说「大量数据」。
    ("大量的数据", "大量数据", ["enormous amounts of data"]),
]

# 译文中冗余的结构助词/后缀（品牌名还原后可能残留）
_REDUNDANT_SUFFIX = [
    ("Apple Intelligence公司", "Apple Intelligence"),
    ("OpenAI协会", "OpenAI"),
    ("AI 智能体", "AI智能体"),
]

# 品牌所有格：离线模型常把 "Meta's" 译成 "Metas"，中文里读起来很别扭，
# 统一还原为「品牌 + 的」。
_POSSESSIVE = [
    ("Metas", "Meta 的"),
    ("Microsofts", "Microsoft 的"),
    ("Nvidias", "Nvidia 的"),
    ("Googles", "Google 的"),
    ("Apples", "Apple 的"),
    ("Anthropics", "Anthropic 的"),
    ("OpenAIs", "OpenAI 的"),
    ("Amazons", "Amazon 的"),
    ("Intels", "Intel 的"),
]


# 专有描述短语中英对照：这些短语含专有名词，模型常整段留成英文不译。
# 与 TERM_FIXES 不同，这里不需要源文触发——短语本身高度特异，可直接安全替换。
GLOSSARY = [
    ("A 3B-Active Finance Research Agent Model", "一个 3B 主动金融研究智能体模型"),
    ("3B-Active Finance Research Agent Model", "3B 主动金融研究智能体模型"),
    # 注意：这里不要放 "No Ordinary Assistant" -> "非普通助手"。
    # TERM_FIXES 里有 "非普通助手" -> "NOA（No Ordinary Assistant）"，
    # 两张表若都存在就会互相翻转，导致 NOA 括号每跑一轮多套一层。
    # 保留英文原名本身即可（用户要求支持看原文），中文首次出现时
    # 由 TERM_FIXES 统一成 "NOA（No Ordinary Assistant）"。
    ("Agent Computer Use", "智能体计算机操作"),
    ("Full-Duplex Speech Model", "全双工语音模型"),
    ("full-duplex speech-to-speech model", "全双工语音到语音模型"),
    ("open-weight decision model", "开放权重决策模型"),
    ("Decision Model", "决策模型"),
    ("post-trained", "后训练的"),
    ("Tensor Processing Units", "张量处理单元"),
    ("haiku about being in space", "关于身处太空的俳句"),
    ("a model-independent coding agent harness", "一个与模型无关的编码智能体框架"),
    ("makes programmatic tool calling the default", "让程序化工具调用成为默认行为"),
    ("forward pass", "前向传播"),
    ("backward pass", "反向传播"),
    ("fused Mega MoE kernel", "融合式 Mega MoE 内核"),
    ("Trainable Fused MoE Kernel", "可训练融合式 MoE 内核"),
    ("beats", "击败"),
    # ── 2026-11-03 03:00 周期新增条目的语义崩坏 ──
    # "Anthropic clamps down on Claude's AI video game clones" 被译成
    # 「受到人类的压力」——clamps down on 是「收紧限制」，与「压力」无关。
    ("clamps down on", "收紧对"),
    ("Retro gaming", "复古游戏"),
    ("decompilations", "反编译"),
    ("recompilations", "重编译"),
    ("and ports", "和移植作品"),
    ("at 11x lower cost", "成本低至 1/11"),
    ("a first response from space", "来自太空的首次响应"),
    ("cheesy poetry", "打油诗"),
    ("writing poetry", "写诗"),
    ("in space", "在太空中"),
    ("cost of the tokens", "token 成本"),
    ("token costs", "token 成本"),
    ("cut the coding agent costs", "降低编码智能体成本"),
    ("an open-source plugin", "一个开源插件"),
    ("learns from past sessions", "从历史会话中学习"),
    ("at 20 ms P50 latency", "在 20 毫秒 P50 延迟下"),
    ("costs $0.01 per million input tokens", "每百万输入 token 成本 0.01 美元"),
    ("full-duplex", "全双工"),
    ("cosign the loan", "为贷款共同签字"),
    ("the chipmaker that sells the chips", "卖芯片的芯片厂商"),
    ("no size, benchmarks or weights", "未公布模型规模、基准或权重"),
    ("trained only on human conversation audio", "仅用人类对话音频训练"),
    ("the midterms", "中期选举"),
    ("Bestselling authors", "畅销作者"),
    ("Big Five publishers", "五大出版商"),
    ("a workplace AI assistant", "一个职场 AI 助理"),
    ("was later killed", "后来被下线"),
    ("threw a party", "举办了派对"),
    ("the first TPU in space", "首个进入太空的 TPU"),
    ("a personal AI agent", "一个个人 AI 智能体"),
    ("a secure Pentagon system", "一套五角大楼机密系统"),
    ("the vulnerability could be patched", "漏洞才得以修补"),
    ("on a DOD network", "在国防部网络内"),
    ("a satellite AI server", "一颗卫星 AI 服务器"),
    ("transmits its first response to Earth", "首次向地球传输响应"),
    ("data center satellite", "数据中心卫星"),
    # 2026-11-03 09:00 巡检新增：模型把修饰性定语整段留成英文未译，
    # 产出「购买 Cresta for Voice-Led 客户服务 AI」这类中英拼接。
    # 这里只补「通用描述性短语」，专有品牌名（如 Ceva NeuPro NPU）
    # 保持英文原样是正确的，不在此列。
    ("for Voice-Led", "面向语音交互的"),
    # 2026-11-03 13:00 巡检：模型把整段修饰语留成英文未译，
    # 产出「Anthropic 发布了 FlashProve for Cryptographic AI 推理证据」
    # 这类中英拼接。这里补通用学术修饰语。
    ("Cryptographic AI Inference Proofs", "密码学 AI 推理证明"),
    ("for Cryptographic AI", "，面向密码学 AI 的"),
    ("Cryptographic AI", "密码学 AI"),
    ("Voice-Led", "语音交互式"),
    ("voice-led", "语音交互式"),
    ("with human-in-the-loop", "带人工介入"),
    ("human-in-the-loop", "人在环路"),
]


# 品牌复合名粘连的显式拆分（"GoogleDeepMind" -> "Google DeepMind"）。
# 逐个列出，避免通用规则误伤真实单词（如 Metaverse 不能拆成 Meta verse）。
_JOINED_BRANDS = [
    ("GoogleDeepMind", "Google DeepMind"),
    ("DeepMindGemma", "DeepMind Gemma"),
    ("OpenAIResearch", "OpenAI Research"),
    ("AnthropicClaude", "Anthropic Claude"),
    ("MetaAI", "Meta AI"),
    ("HuggingFace", "Hugging Face"),
    ("AppleIntelligence", "Apple Intelligence"),
    ("MicrosoftResearch", "Microsoft Research"),
    ("GoogleAntigravity", "Google Antigravity"),
    ("OpenAIDaybreak", "OpenAI Daybreak"),
    ("ProjectSuncatcher", "Project Suncatcher"),
]


def _apply_glossary(text):
    """把译文里残留的英文专有短语按对照表补译。

    按短语长度降序替换，保证长短语先于其子串命中。

    2026-11-03 11:00 巡检修复：跳过「中文（英文原文）」形态的括注。
    本站摘要会在中文译名后用全角括号括注英文原名（如「复古游戏
    （Retro gaming）」），这是**刻意保留的原文对照**，不是翻译残留。
    原实现无条件替换，导致括注里的英文被二次译成中文，
    产出「复古游戏（复古游戏）」这种自相矛盾的形态。
    判定：英文短语紧跟在全角左括号之后，且其括号外的前文已含
    对应中文译名时，视为原文括注，跳过替换。
    """
    if not text:
        return text
    out = text
    for en, zh in sorted(GLOSSARY, key=lambda x: -len(x[0])):
        if en not in out:
            continue
        # 逐个出现位置判断：只有「紧跟全角左括号且括号外已有中文译名」
        # 的那一处是原文括注，其余位置照常补译。
        pos = 0
        while True:
            idx = out.find(en, pos)
            if idx < 0:
                break
            prefix = out[:idx]
            is_annotation = (
                prefix.endswith("（")
                and zh in prefix[:-1].rsplit("（", 1)[-1]
            )
            if is_annotation:
                pos = idx + len(en)
                continue
            out = out[:idx] + zh + out[idx + len(en):]
            pos = idx + len(zh)
    return out


def _digits(token):
    """取数字 token 的数字集合（忽略小数点、千分位、百分号）。"""
    return set(re.findall(r"\d", token))


# 英文数量级词 -> 换算成「亿」的倍数
# 亿 = 1e8；thousand=1e3 -> 1e-5 亿；million=1e6 -> 0.01 亿；
# billion=1e9 -> 10 亿；trillion=1e12 -> 10000 亿
_SCALE_WORDS = {
    "trillion": 10000.0,
    "billion": 10.0,
    "million": 0.01,
    "thousand": 0.00001,
}

# 中文数量级词 -> 换算成「亿」的倍数
_ZH_SCALE = {"亿": 1.0, "万": 0.0001}

_EN_SCALED_RE = re.compile(
    r"(\d+(?:[.,]\d+)*)\s*[-–—]?\s*(trillion|billion|million|thousand)\b",
    re.IGNORECASE)
_ZH_SCALED_RE = re.compile(r"(\d+(?:[.,]\d+)*)\s*(亿|万)")

# 英文缩写数量级：$86M / $12B / 1.5K —— 科技资讯里极常见，
# 早期只认 million/billion 全拼，导致这类缩写完全逃过数量级校正。
# 只匹配大写缩写（小写 m/b/k/t 在正文里更可能是单位或普通字母），
# 故单独用一条大小写敏感的正则，避免误伤。
_EN_ABBR_RE = re.compile(r"(\d+(?:[.,]\d+)*)\s*([TBMK])\b")
_EN_ABBR_SCALE = {
    "T": 10000.0,
    "B": 10.0,
    "M": 0.01,
    "K": 0.00001,
}


def _fmt_num(v):
    """数值转中文可读写法：去掉无意义的小数尾零（3000.0 -> 3000）。"""
    if float(v).is_integer():
        return str(int(v))
    return ("%f" % v).rstrip("0").rstrip(".")


def _align_scale_magnitude(zh, en):
    """修正数量级被译错的数值。

    离线模型常把「300 billion」译成「3亿美元」、「57 million」译成
    「57万」、「$9.06 billion」译成「9.06亿美元」——量级差 10~1000 倍，
    属于严重事实错误，且不会被数字集合比对（_align_numbers）发现，
    因为数字本身没变、变的单位。

    策略：抽出英文侧的「数值 + 数量级词」与中文侧的「数值 + 亿/万」，
    换算成统一单位（亿）后按出现顺序配对。只有当比值恰为 10/100/1000
    等整十倍数量级时才纠正——这正是模型换算错位量的特征；而四舍五入
    造成的 1.1~1.3 倍偏差一律不动，避免误伤正常翻译。

    幂等性：本函数必须可重复执行（清洗流程会多次调用）。
    早期实现用「原始 zh 的偏移量」去改写「已被改过的 out」，
    导致第二次执行时偏移错位，把「260亿美元」改成「260亿亿亿美元」，
    越修越坏。现改为「从后往前」替换，保证偏移不失效。
    """
    if not zh or not en:
        return zh
    en_pairs = []
    for m in _EN_SCALED_RE.finditer(en):
        try:
            val = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        mult = _SCALE_WORDS.get(m.group(2).lower())
        if mult:
            # 记录原始文本，用于判断数值是否带小数位
            en_pairs.append((m.start(), val * mult, val, mult, m.group(1)))
    # 缩写形式（$86M / $12B）：与全拼分开收集，避免大写缩写被小写正则漏掉
    for m in _EN_ABBR_RE.finditer(en):
        try:
            val = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        mult = _EN_ABBR_SCALE.get(m.group(2))
        if mult:
            en_pairs.append((m.start(), val * mult, val, mult, m.group(1)))
    # 按出现位置排序，保证与中文侧按顺序配对
    en_pairs.sort(key=lambda p: p[0])
    if not en_pairs:
        return zh

    zh_matches = list(_ZH_SCALED_RE.finditer(zh))
    if not zh_matches:
        return zh

    # 收集「要替换的区间」，最后从后往前应用，避免偏移失效。
    replacements = []
    for (en_pos, en_val, en_mant, en_mult, en_raw), zm in zip(en_pairs, zh_matches):
        try:
            zh_val = float(zm.group(1).replace(",", "")) * _ZH_SCALE[zm.group(2)]
        except (ValueError, KeyError):
            continue
        if en_val <= 0 or zh_val <= 0:
            continue
        ratio = en_val / zh_val
        # 命中 10 的整数次幂（容差 3%）才纠正。
        # ratio > 1：中文侧偏小（如 $86M 译成「86万」，实际应「8600万」）
        # ratio < 1：中文侧偏大（如 $12B 译成「12亿」，实际应「120亿」）
        for p in (1000, 100, 10, 0.1, 0.01, 0.001):
            if abs(ratio - p) <= p * 0.03:
                # correct 的单位是「亿」。先按原值判大小，再分别格式化：
                # 若先 round 到 2 位小数，$100K（0.001 亿）会被抹成 0，
                # 导致「0万美元」这种更糟的结果。
                if en_val >= 1:
                    new_text = "%s亿" % _fmt_num(round(en_val, 2))
                else:
                    new_text = "%s万" % _fmt_num(round(en_val * 10000, 2))
                replacements.append((zm.start(), zm.end(), new_text))
                break
        else:
            # ---- 小数位被截断的专门处理 ----
            # 离线模型常把「$1.3 million」译成「100 万美元」——
            # 即把尾数 1.3 直接截断成 1.0，数量级对但具体金额错了 30%。
            # 这种偏差不是 10 的整数次幂，故上面的量级校正抓不到。
            # 判定条件（全部满足才纠正，误伤面极小）：
            #   1) 英文数值原文带小数位且小数部分非零；
            #   2) 中文侧数值换算成英文同一单位后，恰好等于英文值向下取整；
            #   3) 二者不相等（即中文侧确实丢掉了小数部分）。
            # 例：EN "1.3 million" -> ZH "100 万"（1.0 million）-> 修正为「130 万」
            if "." not in en_raw and "," not in en_raw:
                continue
            if en_mant <= 0 or en_mult <= 0:
                continue
            zh_in_en_units = zh_val / en_mult
            if abs(zh_in_en_units - en_mant) < 1e-9:
                continue
            if abs(zh_in_en_units - int(en_mant)) > 1e-9:
                continue
            # 纠正值仍用中文单位表达
            if en_val >= 1:
                new_text = "%s亿" % _fmt_num(round(en_val, 2))
            else:
                new_text = "%s万" % _fmt_num(round(en_val * 10000, 2))
            replacements.append((zm.start(), zm.end(), new_text))

    if not replacements:
        return zh

    # 从后往前替换，保证前面的偏移量依然有效
    out = zh
    for start, end, new_text in sorted(replacements, key=lambda r: -r[0]):
        out = out[:start] + new_text + out[end:]
    return out


def _align_numbers(zh, en):
    """修正模型静默改错的数值（如 "65.2%" 被译成 "6.5%"）。

    离线模型偶尔会把 "65.2%" 译成 "6.5%"、"30.9%" 译成 "3.09%"——
    这类错误不会被任何标点或术语规则发现，却直接误导读者。

    策略：不做按位置硬替换（那会因中英语序差异造成串位），
    而是找出「中文里多出来的数字」和「英文里对应的数字」，
    在数字集合相似（>=60% 数字重合）时，用英文侧原值回填中文侧错值。
    """
    if not zh or not en:
        return zh

    # ---- 解析数值 token ----
    # 关键点 1：百分号要单独记。英文正文写 "57 percent"，正则只能抓到 "57"，
    # 而中文是 "57%"。若按原字符串比对，"57%" 会被当成「中文侧多余的数」，
    # 然后被英文侧的 "57" 覆盖，百分号就此丢失。
    # 关键点 2：中文侧「10 万」「2.5 万」这类带量级词的数字不能参与本函数的
    # 数值比对——它们的写法本身就正确（10 万 == 100,000），只是表达方式与英文
    # 不同，应交给 _align_scale_magnitude 处理。若参与比对，"10" 会被英文的
    # "100,000" 覆盖，变成 "100,000 万"，数量级直接错 10000 倍。
    num_re = re.compile(r"(\d+(?:[.,]\d+)*)(\s*%)?")

    def _norm(v):
        return v.replace(",", "")

    en_items = [(m.group(1), bool(m.group(2))) for m in num_re.finditer(en)]
    zh_items = []
    for m in num_re.finditer(zh):
        # 量级词可能与数字之间有空格（"10 万"），判断时需跳过空白。
        tail = zh[m.end():m.end() + 2].lstrip()
        has_scale = bool(tail) and tail[0] in ("万", "亿", "千", "百")
        # 关键点 3：中文月份「11 月」不能参与本函数的数值比对。
        # 英文的月份是单词（November / March …），不产生任何数字 token，
        # 而中文写成「11 月」的纯数字——两侧的月份天然无法对齐。
        # 若放任它进入「中文侧多余数字」候选池，就会被英文里形近的数字
        # 回填覆盖：实测 "November" 的中文「11 月」被品牌名 ON1 里的
        # 数字 1 覆盖成「1 月」（数字集合 {1} 与 {1} 相似度 1.0），
        # 日期直接错一个月。因此月份位置必须像量级词一样被排除。
        has_month = bool(tail) and tail[0] == "月"
        zh_items.append((m.group(1), bool(m.group(2)), has_scale, has_month))
    if not en_items or not zh_items:
        return zh

    en_vals = [_norm(n) for n, _ in en_items]
    zh_vals = [_norm(n) for n, _, _, _ in zh_items]

    # 英文侧存在、中文侧缺失的数值：模型改错时通常中文侧会出现一个形近新值
    # （如 65.2% -> 6.5%）。
    missing = []
    for n, pct in en_items:
        if _norm(n) in zh_vals:
            continue
        if any(_norm(n) == v and pct == p for v, p, _, _ in zh_items):
            continue
        missing.append((n, pct))
    if not missing:
        return zh

    # 2026-11-03 11:00 巡检修复：数量级悬殊时禁止回填。
    #
    # 本函数的隐含前提是「中英两侧数字一一对应，模型只是把某个数字
    # 抄错了（如 65.2% → 6.5%）」。但离线模型经常把摘要**截断**——
    # 英文原文有 21 个数字，中文只译了前半段（12 个）。
    # 此时英文侧缺失的数字（10.9%、16.29…）是「原文有但译文没译」，
    # 而中文侧唯一的"多余"数字（1.0，实际对应 "the first version"）
    # 会被误判为形近错值并遭回填，产生「1.0 版本」→「10.9 版本」
    # 这种凭空造出的数字——静默改错数字比术语错误更误导读者。
    #
    # 判定：两侧可参与比对的数字数量差距过大时，整段不做回填。
    # 阈值取 2：允许单侧多出 1~2 个数字（真实抄错场景常见 1 个），
    # 但拒绝「差 3 个以上」的整体性截断。
    _zh_alignable = [1 for (_, _, has_scale, has_month) in zh_items
                      if not has_scale and not has_month]
    if abs(len(en_items) - len(_zh_alignable)) > 2:
        return zh

    # 中文侧「多余」的数值候选。带量级词（万/亿/千/百）的数字一律排除，
    # 它们不是错值，只是中文写法与英文不同；月份（11 月）同样排除，
    # 理由见上（英文月份是单词，数值比对对它没有意义，且会错月份）。
    extra = []
    for (n, pct, has_scale, has_month), raw in zip(zh_items, zh_items):
        if has_scale or has_month:
            continue
        if _norm(n) in en_vals:
            continue
        extra.append((n, pct))
    if not extra:
        return zh

    out = zh
    for e, e_pct in missing:
        de = _digits(e)
        if not de:
            continue
        # 在中文侧的「多余数字」里找形近者（同数字集合相似度最高且 >=0.6）
        best, best_score = None, 0.0
        for z, z_pct in extra:
            dz = _digits(z)
            if not dz:
                continue
            score = len(de & dz) / len(de | dz)
            if score > best_score:
                best, best_score = (z, z_pct), score
        if best is None or best_score < 0.6:
            continue
        best_str, best_pct = best
        # 关键：必须按「完整数值 token」边界替换，不能用朴素的 str.replace。
        # 否则中文侧的 "2026" 若被误判为形近多余数字（与英文 "202.6" 相似度
        # 达阈值），朴素替换会把 "2026" 中的 "202" 替换掉，得到 "202.6"，
        # 每跑一轮就被啃掉一位数字（2026 -> 202.6 -> 20.6 -> 2.6 ...）。
        # 加上前后不可为数字/小数点/逗号的前后瞻，保证只整体替换独立数值。
        pat = r"(?<![\d.,])" + re.escape(best_str) + r"(?![\d.,])"
        # 中文侧原本带百分号、英文侧没有 % 时（如 "57%" vs "57 percent"），
        # 回填要保留百分号，否则会丢掉语义。
        repl = e + ("%" if (best_pct and not e_pct) else "")
        new_out, n_sub = re.subn(pat, repl.replace("\\", "\\\\"), out, count=1)
        if n_sub == 0:
            # 形近数字只以上文子串形式存在（如 "2" 在 "25,000" 内），
            # 属于误判，不做替换。
            continue
        out = new_out
        extra.remove(best)
    return out



def _fix_latin_spacing(text):
    """修复品牌名与后续拉丁词粘连导致的缺空格问题。

    离线模型输出 "SamayaAI"、"GoogleDeepMind"、"ClaudeCode" 这类粘连，
    品牌还原后同样可能留下粘连（如 "Samaya" + "AI"）。
    """
    if not text:
        return text
    out = text
    # 只拆「品牌 + 全大写缩写」这一种安全形态（如 SamayaAI -> Samaya AI）。
    # 不做通用的「品牌 + 首字母大写词」拆分，否则 Metaverse 会被误拆成 "Meta verse"。
    for canonical, _variants in BRAND_TERMS:
        if not canonical or not canonical[-1].islower():
            continue
        out = re.sub(
            rf"(?<![A-Za-z]){re.escape(canonical)}(?=[A-Z]{{2,}})",
            canonical + " ",
            out,
        )
    # 显式的复合品牌名粘连（Title case 形态，逐个列出以免误伤）。
    for joined, split in _JOINED_BRANDS:
        out = out.replace(joined, split)
    # 品牌名后紧跟数字版本号 => 补空格（"Gemma4" -> "Gemma 4"）
    for canonical, _variants in BRAND_TERMS:
        if not canonical or not canonical[-1].islower():
            continue
        out = re.sub(
            rf"(?<![A-Za-z0-9]){re.escape(canonical)}(?=\d)",
            canonical + " ",
            out,
        )
    return out


def _apply_term_fixes(text, source_low):
    """按 TERM_FIXES 表把错误译名替换为标准写法。

    仅当英文原文包含对应触发关键词时才替换，避免误伤正常中文
    （如「低碳」不会被误改成「低Carbon」）。
    """
    if not text:
        return text
    out = text
    for wrong, right, triggers in sorted(TERM_FIXES, key=lambda x: -len(x[0])):
        if wrong == right:
            continue
        if wrong not in out:
            continue
        if any(t in source_low for t in triggers):
            out = out.replace(wrong, right)
    return out


# AI 语境下「代理」应统一写作「智能体」。
#
# 离线模型把 agent 一律译成「代理」，在中文里极易被读成「代理人 /
# 代理商 / 代理服务器」，与行业通用写法「智能体」不符。这是本轮巡检
# 中最系统性的缺陷（20 条命中）。
#
# 安全性设计：
#   1) 触发条件是英文原文出现 "agent" 这个子串。agency（自主权 / 能动性）
#      不含 agent，因此 "human agency" 这类确实该译「自主权」的语义
#      天然不会被误伤；
#   2) 排除「代理服务器 / 代理 IP / 代理键」等真正的网络代理义；
#   3) 只替换「代理」二字本身，不动「代理权 / 代理制度」等独立词义。
_AGENT_KEEP = (
    "代理服务器", "代理主机", "代理 IP", "代理ip", "代理键", "代理认证",
    "代理制度", "代理权", "代理协议",
)

# 英文里 agent 相关的确定性搭配，用于把「代理 X」还原为「X 智能体」
# 等更贴合中文表达的说法（离线模型常把 agentic 译成「代理式」）。
_AGENT_PHRASE_FIXES = (
    ("代理式智能体", "智能体式"),
    ("代理式 AI", "智能体式 AI"),
    ("代理人工智能", "智能体人工智能"),
    # 「代理人」在 agent 语境下是「agents」的复数直译，应为「智能体」。
    # 若先做通用替换会得到「智能体人」，因此必须在通用替换前处理。
    ("代理人", "智能体"),
    ("自主代理", "自主智能体"),
)


def _fix_agent_wording(text, source_low):
    """把 AI 语境下误译的「代理」统一还原为「智能体」。

    仅在英文原文出现 agent 时生效，因此网络代理（proxy server）与
    人类自主权（human agency）等语义不会被误伤。
    """
    if not text or "代理" not in text:
        return text
    if "agent" not in source_low:
        return text
    out = text
    # 先把网络代理 / 独立词义占位保护起来，最后再放回。
    marks = {}
    for i, keep in enumerate(_AGENT_KEEP):
        if keep in out:
            mark = "\x00KEEP%d\x00" % i
            marks[mark] = keep
            out = out.replace(keep, mark)
    for wrong, right in _AGENT_PHRASE_FIXES:
        if wrong in out:
            out = out.replace(wrong, right)
    out = out.replace("代理", "智能体")
    for mark, keep in marks.items():
        out = out.replace(mark, keep)
    return out


# 加密货币语境下的 token 译作「代币」是正确的，不能被统一替换。
_CRYPTO_MARKERS = ("crypto", "blockchain", "nft", "web3", "tokenomics",
                   "cryptocurrency", "defi", "stablecoin")


def _fix_token_wording(text, source_low):
    """把 AI 语境下的「代币」统一还原为「token」。

    LLM 领域 token 指模型处理的文本单元，行业通用写法是直接保留英文
    token（而非「代币」/「令牌」），否则读者会与加密货币混淆。
    仅当原文出现 token 且不含加密货币关键词时才替换。
    """
    if not text or "代币" not in text:
        return text
    if "token" not in source_low:
        return text
    if any(m in source_low for m in _CRYPTO_MARKERS):
        return text
    return text.replace("代币", "token")


def _normalize_cjk_parens(text):
    """把中文语境里的半角括号转成全角，与全站排版风格保持一致。

    中文正文的括号按惯例用全角「（）」。离线模型在音译专名后
    常输出半角形式，如「萨姆·阿尔特曼 (Sam Altman)」「装 (CPG)」，
    夹在中文句子里显得突兀，且与站内其余 68 处全角括号不统一。

    转换以「配对」为单位：找到左括号后向右扫描到配对的右括号，
    只要这一对括号的内部或两侧涉及中文，就把整对都转成全角，
    避免出现「token (以及应该做什么）」这种半角开头、全角结尾的
    不配对括号。纯英文语境（如 "(APAC)" 独立成段）保持半角。
    """
    if not text or "(" not in text:
        return text
    out = list(text)
    n = len(out)
    for i in range(n):
        if out[i] != "(":
            continue
        # 向右找配对的右括号
        depth = 0
        close = -1
        for j in range(i, n):
            if out[j] == "(":
                depth += 1
            elif out[j] == ")":
                depth -= 1
                if depth == 0:
                    close = j
                    break
        if close < 0:
            continue  # 没有配对，放弃转换
        inner = "".join(out[i + 1:close])
        # 左括号前的有效字符（跳过空格）
        prev = ""
        for j in range(i - 1, -1, -1):
            if out[j].strip():
                prev = out[j]
                break
        nxt = ""
        for j in range(close + 1, n):
            if out[j].strip():
                nxt = out[j]
                break
        involves_zh = (
            bool(_CJK.match(prev))
            or bool(_CJK.match(nxt))
            or bool(_CJK.search(inner))
        )
        if not involves_zh:
            continue
        out[i] = "（"
        out[close] = "）"
        # 左括号与前文之间的空格去掉（全角括号紧贴前字，与站内 68 处一致）
        for j in range(i - 1, -1, -1):
            if not out[j].strip():
                out[j] = ""
            else:
                break
    res = "".join(out)
    # 全角括号内的多余空格去掉
    res = re.sub(r"（\s+", "（", res)
    res = re.sub(r"\s+）", "）", res)
    # 闭括号后紧跟中文时不留空格（站内 48 处全角括号后均直接接中文）
    res = re.sub(r"）\s+(?=[\u4e00-\u9fff])", "）", res)
    return res


def _fix_signing_wording(text, source_low):
    """修复「签署」重复的标题结构。

    离线模型遇到英文 "X signs deal with Y" 时，会产出
    「X签署了与Y签署多年协议」——「签署」出现两次，句子读起来是病句。
    这是模型对 "signs ... deal" 这一双重结构的典型误处理。

    处理方式：把「签署了与……签署」折叠成「与……签署」，
    即删掉第一个谓语「签署了」，保留介词短语与真正的谓语。
    仅在英文原文同时出现 sign 与 deal 时生效，
    因此「签署请愿书」「已签署最终协议」等正常表达不会被误伤。
    """
    if not text or "签署了与" not in text:
        return text
    if "sign" not in source_low or "deal" not in source_low:
        return text
    # 只处理首个出现的「签署了与」：其后若还有「签署」即判定为重复谓语。
    idx = text.find("签署了与")
    head, tail = text[:idx], text[idx + len("签署了与"):]
    if "签署" not in tail:
        return text
    return head + "与" + tail


# 货币单位补全：模型把「£22.4M」译成「2240 万英」，中文里「万英」不是
# 完整单位（应为「万英镑」）。这类截断在英文原文含货币符号时可精确识别，
# 因此做成「原文有符号 -> 中文补单位」的确定性规则。
_CURRENCY_UNITS = [
    ("£", "镑", ("万英", "亿英")),
    ("€", "元", ("万欧", "亿欧")),
    ("¥", "元", ("万日", "亿日")),
]


def _fix_currency_units(text, source_text):
    """补全被截断的中文货币单位。

    NLLB 在处理「£22.4 million」这类写法时，常把货币符号意译成单字
    「英」「欧」「日」，产出「2240 万英」这种缺字的中文——中文读者
    无法理解「万英」是什么单位。

    处理方式：原文出现对应货币符号时，若译文出现「万X」「亿X」形式
    的截断单位，则整体替换为「万英镑」「亿英镑」等完整写法。
    仅在原文确实含该货币符号时生效，不会误伤「亿万」「万物」等词。
    """
    if not text or not source_text:
        return text
    out = text
    for symbol, ch, stems in _CURRENCY_UNITS:
        if symbol not in source_text:
            continue
        for stem in stems:
            # 「万英」后面若已跟「镑/币」，说明单位本就完整，不重复替换。
            out = re.sub(
                rf"{stem}(?![{ch}币])",
                stem + ch,
                out,
            )
    return out


# MarkTechPost 摘要是固定模板：正文之后是 "TL;DR Size: ... Runs on: ...
# Performance: ... Best: ... Worst: ..." 这样的标签行。模型会把其中一部分
# 标签译成中文、另一部分原样留成英文，导致同一条摘要里中英标签混杂
# （如「TL;DR 尺寸：……Runs on:Docker Compose……Performance：……」）。
# 这里把残留的英文标签统一译为中文标签。
_STRUCT_LABELS = [
    ("Runs on", "运行方式"),
    ("Performance", "性能表现"),
    ("Best", "最佳"),
    ("Worst", "最差"),
    ("Library", "库"),
    ("Size", "规模"),
    ("Scale", "规模"),
    ("Context", "上下文"),
    ("Base model context", "基础模型上下文"),
    ("DR Runs on", "DR 运行方式"),
    ("DR Library", "DR 库"),
    ("DR Package", "DR 软件包"),
    ("DR Size", "DR 规模"),
    ("DR Footprint", "DR 资源占用"),
    ("The key finding", "核心结论"),
    ("Design", "设计"),
]


def _fix_struct_labels(text):
    """把摘要中残留的英文结构标签译为中文标签。

    仅处理「标签 + 冒号」这种固定形态，且要求标签位于句首或标点之后，
    避免误伤正常句子里的英文单词（如 "Best practices"）。

    2026-11-03 15:00 巡检补充：标签也可能紧跟在英文前缀 "TL;DR " 之后
    （MarkTechPost 模板固定以 "TL;DR Size: ..." 开头）。此前该位置既不是
    句首、也不是中文标点之后，正则的负向断言直接失配，导致
    「TL;DR Scale：」这类残留英文标签逃过修复。这里把 "TL;DR " 也
    纳入允许的标签起始位置。
    """
    if not text:
        return text
    out = text
    for en, zh in _STRUCT_LABELS:
        # 匹配：句首、中文标点之后、或英文前缀 "TL;DR " 之后紧跟英文标签 + 冒号
        pattern = (
            rf"(?:(?<=^)|(?<=[。；：\uff0c\u3001])|(?<=TL;DR ))"
            rf"\s*{re.escape(en)}\s*[:：]"
        )
        out = re.sub(pattern, zh + "：", out)
        # 半角冒号紧贴标签（如 "Runs on:Docker"）同样处理
        pattern2 = (
            rf"(?:(?<=^)|(?<=[。；：\uff0c\u3001])|(?<=TL;DR ))"
            rf"\s*{re.escape(en)}:"
        )
        out = re.sub(pattern2, zh + "：", out)
    return out


# 中文形态的模板标签归一。
#
# 模型把英文标签译成中文时，用词不统一：同一个 "Runs on:" 会时而译成
# 「运行方式：」、时而译成「运行：」；"Worst:" 时而译成「最差：」、
# 时而译成「最糟糕的是：」。站内主流写法分别是「运行方式：」（13 条）
# 与「最差：」（4 条），少数派形态显得体例不一。
#
# 这里做词形归一，但必须锚定在「标签位」上（标签位于句首或中文标点之后、
# 且以冒号结尾），否则会误伤正文里的正常词组（如「程序运行：正常」）。
# 触发条件也绑定英文原文里的对应标签，避免对无关条目生效。
_ZH_LABEL_VARIANTS = [
    ("运行：", "运行方式：", ("runs on:",)),
    ("最糟糕的是：", "最差：", ("worst:",)),
    ("最佳表现：", "最佳：", ("best:",)),
]


def _fix_zh_label_variants(text, source_low):
    """把中文形态的模板标签归一到站内主流写法。"""
    if not text or not source_low:
        return text
    out = text
    for wrong, right, triggers in _ZH_LABEL_VARIANTS:
        if not any(t in source_low for t in triggers):
            continue
        # 标签位：句首或中文标点之后，且以冒号结尾
        pattern = (
            rf"(?:(?<=^)|(?<=[。；：\uff0c\u3001])){re.escape(wrong)}"
        )
        out = re.sub(pattern, right, out)
    return out


# Apple 品牌被模型意译成单字「果」时的还原。
# 原文提到 Apple 时，模型有时把 "Apple Silicon" 之外的独立 "Apple"
# 译成「果」（如「运行于：果，NVIDIA GPU」），中文里完全不通。
_APPLE_BARE_RE = re.compile(
    r"(?<![结成水实硕如苹])果(?=\s*[，,、]\s*[A-Za-z]|\s+(?:MPS|M1|M2|M3|M4|Pro|Max|芯片|CPU|GPU)"
    # 2026-11-03 16:00 巡检新增：Apple 硬件产品线的英文名。
    # 根因：NLLB 在「短标题」语境里倾向把独立的 "Apple" 译成单字「果」，
    #   而本正则的前瞻原先只覆盖 MPS / M 系列 / 芯片 / CPU / GPU，
    #   于是 "Apple Watch Audio Intelligence Enters Developer Beta Testing"
    #   -> 「果 Watch 音频智能进入开发者测试」——品牌名整个丢失，
    #   中文读者完全无法定位是哪款产品。
    # 安全性：仍是「果」独立成词（负向前查排除 如果/结果/成果/水果/苹果），
    #   且仅在英文原文出现 apple 时才执行，误伤面极小。
    r"|\s+(?:Watch|Vision|AirPods|AirTag|Pencil|MacBook|iMac|iPhone|iPad|HomePod"
    r"|Studio|Display|Beats|AppleCare)"
    # 「Apple Watch Series 12」这类带序号的写法
    r"|\s+Watch\s+\d)"
)


# 专有名词直译缺陷修复。
#
# 与 TERM_FIXES 的区别：这里的规则用正则而非纯字符串替换，
# 因此可以带负向前查，避免「科学美国」→「科学美国人」在已有
# 「科学美国人」时产出「科学美国人人」。
#
# 每条规则只在英文原文出现对应专名时才生效，不会误伤普通中文。
_PROPER_NOUN_FIXES = (
    # "former Apple CEO" 被拆成「果前首席执行官」。负向前查排除
    # 「苹果前 CEO」这类正确写法，只修真正的「果」单独成词的情形。
    (re.compile(r"(?<!苹)果前"), "前苹果", "former apple ceo"),
    # "Silicon Valley" 译成「谷地址」/「谷地带」（NLLB 把 Silicon 丢掉）。
    # 用正则 + 负向前查：已译成「硅谷地址」时不再重复替换，
    # 否则「谷地址」→「硅谷地址」会因「谷地址」是「硅谷地址」的子串而
    # 二次替换成「硅硅硅谷地址」。
    (re.compile(r"(?<!硅)谷地址"), "硅谷地址", "silicon valley"),
    (re.compile(r"(?<!硅)谷地带"), "硅谷地带", "silicon valley"),
    # "Scientific American"（美国杂志名）译成「科学美国」，缺「人」字。
    # 负向前查：已有「科学美国人」时不再追加。
    (re.compile(r"科学美国(?!人)"), "科学美国人", "scientific american"),
    # "the Semantic Web"（语义网，Web 三大流派之一）译成「语义网络」，
    # 与「语义网络/neural network」混淆。业界标准译名是「语义网」。
    # 负向前查：避免「语义网络」被二次处理成「语义网」之外的怪形态。
    (re.compile(r"语义网络(?!络)"), "语义网", "semantic web"),
    # "World Wide Web" 逐词直译成「世界网络」，中文通用写法是「万维网」。
    (re.compile(r"世界网络"), "万维网", "world wide web"),
    # "At the turn of the millennium" 被拆译成「千一百年之际」。
    (re.compile(r"千一百年之际"), "千年之交", "millennium"),
    (re.compile(r"千一百年"), "千年", "millennium"),
    # "deepfake" 被拆成「深度 fake」——离线模型对不认识的复合词
    # 常见的处理方式是把构词部分意译、词根留英文。中文通用写法是
    # 「深度伪造」。同时覆盖「深度伪造器」「深度伪造技术」等衍生形态。
    (re.compile(r"深度\s*fake", re.I), "深度伪造", "deepfake"),
    (re.compile(r"深度\s*伪造者?"), "深度伪造", "deepfake"),
    # "mundane" 在此意为「平淡无奇的/普通的」，模型译成「世界的」
    # （疑似与 "world-wide" 串味），导致「数百个世界智能应用程序」
    # 这种完全不通的表达。限定在 mundane 出现在原文时触发。
    (re.compile(r"世界智能"), "普通智能", "mundane"),
    (re.compile(r"世界应用程序"), "普通应用程序", "mundane"),
    (re.compile(r"世界应用"), "普通应用", "mundane"),
    # "moves outside its approved business purpose" 被直译成
    # 「在经营目的或安全界限之外移动」——中文里「移动」是名词化的
    # 方位说法，读起来完全不通。正确写法是动词「偏离」。
    # 模式：在<某范围>之外移动 -> 偏离<某范围>
    (re.compile(r"在([^，。；、\n]{2,30}?)之外移动"), r"偏离\1", "moves outside"),
    # "bottleneck" 被离线模型截断成「瓶」（丢掉「颈」），
    # 例如 "a bottleneck for colleagues" → 「同事们的瓶」。
    # 负向前查：已是「瓶颈」不再处理，避免重复加字。
    (re.compile(r"的瓶(?!颈)"), "的瓶颈", "bottleneck"),
)

# NLLB 存在词形混淆：retry（重试）与 retire（退休）音近，
# 模型会把 "Before They Retry" 译成「在退休之前」，语义完全相反。
# 规则只在原文出现 retry 且不含 retire 时生效——
# 若原文同时含两者（真讲退休的语境）则不处理，避免误伤。
_RETRY_CONFUSION = re.compile(r"退休(?=之前|之后|时|前)")


def _fix_proper_nouns(text, source_low):
    """修复专有名词被逐词直译造成的失真。"""
    if not text or not source_low:
        return text
    out = text
    for pattern, repl, trigger in _PROPER_NOUN_FIXES:
        if trigger in source_low:
            out = pattern.sub(repl, out)
    return out


# 语言名音译缺陷修复。
#
# 背景：NLLB 对小语种语言名的音译极不稳定，同一条新闻里 13 个印度语言名
# 被译成「印度语、孟加拉语、泰国语、马拉图语、泰尔语、乌尔都语、古吉拉提、
# 加拿大语、马拉雅语、俄比亚语、班牙语、阿萨姆语、尼泊尔语」——
# 其中「泰国语」（Telugu，实为印度语言）把一种语言安到另一个国家语言上，
# 「加拿大语」（Kannada）更是与国名直接撞车，读者会当成事实错误记住并传播。
#
# 为什么不用 TERM_FIXES 的纯字符串替换：
#   1) 「印度语」是「印度语言」（Indian languages）的子串。TechCrunch 那条
#      原文写的是 "supports 13 Indian languages"，模型译出「13 个印度语言」，
#      纯字符串替换会把它改成「13 个印地语言」——把总称改成了单一语言，
#      反而制造了新的事实错误。必须用负向前查排除「印度语言」。
#   2) 「西班牙语」不是音译错误而是**幻听**：原文 13 种语言里根本没有
#      Spanish，模型把 Punjabi（旁遮普语）错认成西班牙语，导致语言列表
#      凭空多一种、漏一种。若原文本身也含 spanish（真在讲西班牙语），
#      这条替换就会把正确内容改错，因此需要「原文含 punjabi 且不含 spanish」
#      的复合判定，纯字符串表做不到。
#
# 每条规则只在原文确实出现该语言名时生效，不会误伤其他语境。
_LANG_NAME_FIXES = (
    # (正则, 替换, 原文触发词)
    (re.compile(r"印度语(?!言)"), "印地语", "hindi"),
    (re.compile(r"泰国语"), "泰卢固语", "telugu"),
    (re.compile(r"马拉图语"), "马拉地语", "marathi"),
    (re.compile(r"泰尔语"), "泰米尔语", "tamil"),
    (re.compile(r"古吉拉提"), "古吉拉特语", "gujarati"),
    (re.compile(r"加拿大语"), "卡纳达语", "kannada"),
    (re.compile(r"俄比亚语"), "奥迪亚语", "odia"),
    (re.compile(r"马拉雅语"), "马拉雅拉姆语", "malayalam"),
)


def _fix_language_names(text, source_low):
    """修复语言名被逐词音译成无辨识度形态（含跨国名撞车）的问题。

    仅当英文原文出现对应语言名时生效。
    """
    if not text or not source_low:
        return text
    out = text
    for pattern, repl, trigger in _LANG_NAME_FIXES:
        if trigger in source_low:
            out = pattern.sub(repl, out)
    # Punjabi →「西班牙语」是幻听型错误：原文语言清单里并没有 Spanish。
    # 判定要求原文同时含 punjabi 且不含 spanish——
    # 若原文真的在讲西班牙语（spanish），则「西班牙语」是正确的，不能动。
    if "punjabi" in source_low and "spanish" not in source_low:
        out = out.replace("西班牙语", "旁遮普语").replace("班牙语", "旁遮普语")
    return out


def _fix_retry_confusion(text, source_low):
    """修复 retry（重试）被 NLLB 误译为「退休」的词形混淆。

    NLLB 离线模型对 retry / retire 这对音近词的区分不稳定，
    在 "Before They Retry" 这类 AI 语境下会产出「在退休之前」，
    语义与原文完全相反，且中文读者极难察觉（字面通顺、意思错误）。

    触发条件：原文出现 retry，且不含 retire——
    若原文真的在讲退休（retire/retirement），则「退休」是正确译法，不动。
    """
    if not text or "retry" not in source_low:
        return text
    if "retire" in source_low:
        return text
    return _RETRY_CONFUSION.sub("重试", text)


# Brave 是浏览器厂商名（主打隐私保护的 Brave 浏览器）。
#
# 根因：NLLB-200 按普通英文单词处理 "Brave"，在标题位置直接意译成
# 「勇敢」——「Brave Faces Two Publisher Lawsuits」→「勇敢面临两家出版商诉讼」，
# 主语完全错位，中文读者无法定位是哪家公司被起诉。
#
# 为什么不用 TERM_FIXES 的通用规则：Brave 同时是普通英文动词，
# "Why Engineers Should Brave Capitol Hill" 的正解是「勇闯国会山」，
# 不是品牌名。TERM_FIXES 只有「触发词存在就替换」的能力，
# 无法区分这两种语义，必须由本函数按上下文判断。
#
# 判定逻辑：原文出现下列任一「公司语境」搭配才认定为品牌名——
#   品牌固定搭配：Brave Software / Browser / Index / Search / Shield 等；
#   主语位置：Brave + 动作动词（Brave faces / sues / agrees / has ...）；
#   介词宾语：against / by / from / to ... Brave。
# 若原文出现 "capitol hill"（动词用法），一律不动。
_BRAVE_COMPANY_CONTEXT = (
    # 品牌固定搭配
    "brave software", "brave browser", "brave web browser", "brave index",
    "brave search", "brave's", "brave shields", "brave point",
    "brave rewards", "brave api", "brave wallet",
    # 作主语 + 动作动词（新闻标题的典型形态）
    "brave faces", "brave sues", "brave sued", "brave agrees", "brave has",
    "brave is", "brave was", "brave will", "brave says", "brave launches",
    "brave released", "brave releases", "brave announced", "brave introduces",
    "brave files", "brave filed", "brave plans", "brave warns", "brave blocks",
    "brave bans", "brave buys", "brave sells", "brave partners", "brave reports",
    "brave confirms", "brave denies", "brave takes", "brave raises",
    "brave offers", "brave ships", "brave removes", "brave updates",
    "brave patches", "brave accused", "brave targets", "brave and",
    # 作介词宾语
    "against brave", "by brave", "from brave", "to brave", "with brave",
    "for brave", "says brave", "sues brave",
)
_BRAVE_VERB_CONTEXT = ("capitol hill", "brave new world")


def _fix_brave_company(text, source_low):
    """把品牌名 Brave 被意译成的「勇敢」还原为英文原名。

    仅在原文出现 Brave 的公司语境搭配时生效；原文若是动词用法
    （如 "Brave Capitol Hill" = 勇闯国会山）则保持不动。

    还原后由 _fix_cjk_latin_spacing 补中西文间距，
    「勇敢的搜索索引」会变成「Brave 的搜索索引」。
    """
    if not text or "勇敢" not in text:
        return text
    if not any(c in source_low for c in _BRAVE_COMPANY_CONTEXT):
        return text
    if any(c in source_low for c in _BRAVE_VERB_CONTEXT):
        return text
    return text.replace("勇敢", "Brave")


# Anthropic 被模型意译成「人类」，且常出现在句首作主语
# （"Anthropic warns that ..." → 「人类警告说」）。
#
# 为什么不用 TERM_FIXES 的通用规则：像「人类表示」「人类称」这类搭配
# 在中文里本来就成立，若原文里同时提到 Anthropic 与人类（如
# "Anthropic says ... humans are ..."），通用替换会把真正的「人类」
# 错改成「Anthropic」，制造新的错误。
#
# 因此这里只在「句首主语位置」做替换：标题和摘要的开头紧跟言说动词
# （警告/警告说/表示/称/认为/指出/说），基本可判定公司名被意译了。
_ANTHROPIC_SUBJECT_RE = re.compile(
    r"^人类(?=警告说|警告|表示|称|认为|指出|说|表示说|发布|推出|宣布|带来|"
    r"介绍|开源|提出|展示|揭晓|上线)"
)


def _fix_anthropic_subject(text, source_low):
    """把句首被意译成「人类」的 Anthropic 还原为英文原名。

    仅在原文出现 anthropic 时生效，且只改句首主语位置。
    """
    if not text or "anthropic" not in source_low:
        return text
    if "人类" not in text[:12]:
        return text
    return _ANTHROPIC_SUBJECT_RE.sub("Anthropic ", text)


def _fix_bare_apple(text, source_low):
    """把独立成词的「果」还原为「Apple」。

    仅在英文原文出现 apple 时生效，且要求「果」后面紧跟逗号或
    常见 Apple 产品词（MPS / M 系列 / 芯片等），从而避开
    「结果」「成果」「如果」等正常中文词。
    """
    if not text or "apple" not in source_low:
        return text
    if "果" not in text:
        return text
    # 2026-11-03 16:00 巡检新增：去重「果 Apple」与连续重复的「果」。
    # 根因 1：NLLB 把 "Apple Watch's AI features ..." 拆成「果 Apple 的 ...」——
    #   「果」是 Apple 的残译，紧随其后的 "Apple" 又是同一品牌，
    #   两者叠加后既有残字又重复品牌名。
    # 根因 2：NLLB 把 "Apple Watch's ..." 译成「果果的 AI 功能 ...」——
    #   两个「果」其实是同一个 Apple 品牌被拆成两段。
    #   而第五步的裸「果」还原只命中后一个（后接「的」），
    #   于是产出「果Apple 的」这种半还原的畸形结果。
    # 处理：先消掉重复的「果」与「果 Apple」，再走通用的裸「果」还原。
    # 安全性：负向前查排除 如果/结果/后果/水果/苹果/效果/获得 等常用词；
    #   仅在原文出现 apple 时执行。
    text = re.sub(r"(?<![苹结水后因成实树野如效获])果\s*(?=Apple\b)", "", text)
    text = re.sub(r"(?<![苹结水后因成实树野如效获])果{2,}", "Apple", text)
    return _APPLE_BARE_RE.sub("Apple", text)


# ──────────────────────────────────────────────────────────────
# 英文从句残留修复（标题专用）
# ──────────────────────────────────────────────────────────────
# NLLB 偶尔把标题尾部的一整个从句原样留成英文，中英夹杂对中文读者
# 不友好。实测样例（2026-11-03 15:16 Unite.AI）：
#     "Windward Acquires Azimut.ai to Add Visual Vessel Intelligence"
#     -> 「风向收购 Azimut.ai to Add Visual Vessel Intelligence」
# 从句 "to Add Visual Vessel Intelligence" 整段未译。
#
# 判别策略：只认「≥3 个连续英文词 + 其中含英文虚词」的片段。
# 纯品牌列表（Apple Watch Series 12、Live Rewind）不含虚词，
# 因此不会被二次翻译，已有的好译文不会被改坏。
_EN_CLAUSE_FUNCTION_WORDS = {
    "to", "for", "with", "and", "in", "on", "of", "from", "at", "by",
    "into", "via", "across", "that", "which", "while", "after", "before",
    "without", "under", "over", "between",
}
_EN_RUN_RE = re.compile(
    r"[A-Za-z][A-Za-z0-9.'’&+-]*(?:\s+[A-Za-z][A-Za-z0-9.'’&+-]*){2,}"
)


def _repair_stranded_en_clause(text, source_text):
    """把译文中残留成段的英文从句单独翻译后回填。

    仅用于标题（长度短、句式固定）。以首个英文虚词为界把片段切成
    「前置品牌」与「从句」两部分：只翻译从句，前置品牌保持原样。
    这样 "Azimut.ai to Add Visual Vessel Intelligence" 里的
    "Azimut.ai" 不会被单独送进模型而音译成「亚齐米特」。
    """
    if not text:
        return text
    out = text
    for m in list(_EN_RUN_RE.finditer(out)):
        run = m.group(0)
        words = run.split()
        # 片段必须含英文虚词，否则视为品牌列表，不做处理
        if not any(w.lower() in _EN_CLAUSE_FUNCTION_WORDS for w in words):
            continue
        # 以首个虚词为界切分：前半是品牌，后半才是从句
        cut = None
        for idx, w in enumerate(words):
            if w.lower() in _EN_CLAUSE_FUNCTION_WORDS:
                cut = idx
                break
        if cut is None or cut == 0 and len(words) < 3:
            continue
        prefix = " ".join(words[:cut])
        clause = " ".join(words[cut:])
        if not clause:
            continue
        try:
            zh = _translate_nllb_batch([clause], beams=1)[0]
        except Exception:  # noqa
            zh = None
        if not zh:
            continue
        zh = _unmask_terms(zh, [])
        zh = _restore_terms(zh, clause)
        zh = _clean_title_zh(zh)
        # 二次翻译必须真的产出中文，否则保留原片段（宁可不改也不要更糟）
        if not zh or not re.search(r"[\u4e00-\u9fff]", zh):
            continue
        new_run = (prefix + " " + zh).strip() if prefix else zh
        out = out.replace(run, new_run, 1)
    return out


# ──────────────────────────────────────────────────────────────
# 专有名词大小写还原
# ──────────────────────────────────────────────────────────────
# NLLB 对不认识的专有名词会整体小写，中文读者无法定位主体。
# 实测样例（2026-11-03 15:16 Unite.AI）：
#     "...windward 宣布收购 azimut.ai...联合创始人 ami daniel..."
# 而原文中分别是 Windward / Azimut.ai / Ami Daniel。
#
# 规则：原文中「首字母大写、且全文没有出现过小写形态」的词，
# 若译文中出现其小写形态，则恢复为原文大小写。
# 「原文里大小写两种形态都出现过」= 普通英文词（如 The），跳过。
_PROPER_CASE_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "than", "that",
    "this", "these", "those", "it", "its", "is", "are", "was", "were",
    "be", "been", "being", "to", "of", "in", "on", "at", "by", "for",
    "with", "from", "as", "not", "no", "so", "but", "however", "after",
    "before", "now", "new", "all", "how", "why", "what", "who", "when",
    "can", "could", "will", "would", "may", "might", "must", "has",
    "have", "had", "does", "do", "did", "also", "more", "most", "other",
    "some", "such", "only", "own", "same", "very", "just", "up", "down",
    "out", "about", "into", "over", "under", "again", "there", "here",
    "we", "you", "they", "he", "she", "i", "our", "their", "his", "her",
}


def _fix_proper_noun_case(text, source_text):
    """把译文中被模型整体小写的专有名词恢复为原文大小写。

    NLLB 遇到不认识的专有名词时会整体小写（"windward" / "azimut.ai" /
    "ami daniel"），中文读者据此无法定位报道主体。

    判定：原文中首字母大写、且全文没有出现过小写形态的词，
    若译文中出现其小写形态，则恢复原文大小写。
    原文里大小写两种形态都出现过的词视为普通英文词（如 The），跳过。
    """
    if not text or not source_text:
        return text
    out = text
    words = re.findall(r"[A-Za-z][A-Za-z0-9.'’&-]*", source_text)
    seen = set()
    for w in words:
        if not w[:1].isupper() or w.lower() in _PROPER_CASE_STOPWORDS:
            continue
        low = w.lower()
        if low in seen:
            continue
        seen.add(low)
        # 原文中若同时存在小写形态，说明是普通词，跳过
        if re.search(r"(?<![A-Za-z])" + re.escape(low) + r"(?![A-Za-z])",
                     source_text):
            continue
        if re.search(r"(?<![A-Za-z])" + re.escape(low) + r"(?![A-Za-z])", out):
            out = re.sub(
                r"(?<![A-Za-z])" + re.escape(low) + r"(?![A-Za-z])",
                w, out,
            )
    return out



# ──────────────────────────────────────────────────────────────
# 专有名词遮蔽层（masking layer）
# ──────────────────────────────────────────────────────────────
#
# 根因（2026-11-03 巡检定位）：
# NLLB-200 在遇到「带连字符的模型/产品专名」时会拆词并音译，甚至整段丢失：
#     Hydrogen-1.0             -> "1.0"         （词根整个丢失）
#     Gemini-4                 -> "基米尼-4"     （音译）
#     FrontierScience-Research -> "边界科学研究"  （意译成普通词组）
#     Claude-Code              -> "Claude-代码"  （后半段意译）
#
# 复现：translate_list(['Hydrogen-1.0']) => '1.0 是一个研究模型。'
#
# 解法：这类 token 在 NLLB 的词表里没有对应词条，任何"译后修正"都是
# 事后补救——词根丢了就再也找不回来。因此改为「翻译前遮蔽、翻译后还原」：
#     1) 扫描英文原文，识别需要保护的专名（版本号型 / 驼峰型）；
#     2) 用 NLLB 能 100% 原样透传的占位符（ZXQAA…）替换；
#     3) 翻译完成后把占位符换回原始专名。
#
# 实测 ZXQAA 这类纯大写字母串在 NLLB 输出中原样保留（不会被拆、不会音译），
# 因此该方案对模型零污染，只改变专名的呈现形式。
#
# 识别规则刻意保守，只保护「确属专名」的两类：
#   R1 版本号型：形如 Word-1.0 / Word-2 / A-B-C（版本号后缀）
#   R2 驼峰型：  形如 FrontierScience-Research（段内含小写→大写跃迁）
# 刻意排除：普通数量（top-8、5-2B、7e-4）、通用复合词
# （open-source、real-time、end-to-end）——这些本就该翻译成中文，
# 遮蔽反而会让译文夹杂无谓的英文。

# 需要保护的专名：含数字的版本号型 token，或段内含驼峰跃迁的 token。
#
# token 形态统一为「若干段用连字符连接」，段内允许数字与小数点
# （如 Qwen3-235B-A22B、Qwen3.5-2B、GPT-6.1）。
_MASK_TOKEN_RE = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9.]*(?:-[A-Za-z0-9.]+)+\b")
_MASK_CAMEL_RE = re.compile(r"[a-z][A-Z]")

# 普通数量/复合词白名单：这些即使命中上面的形态也不该遮蔽。
# 例如 "top-8 routing"（前 8 路专家）、"5-2B"（5 到 2B 的规模区间）、
# "open-source"、"real-time" 等，翻译成中文才是正确处理。
_MASK_NEVER = {
    "top-8", "5-2b", "7e-4", "s-1", "open-source", "open-weight",
    "real-time", "end-to-end", "off-line", "on-premise",
    # 章节/图表/条款编号：译成中文更自然
    "chapter-1", "figure-1", "figure-2", "table-1", "step-1",
    "step-2", "part-1", "part-2", "phase-1", "phase-2", "level-1",
}

# 人工确认的、需要整体保留原形的连字符专名（既无版本号也无驼峰）。
# 收录标准：该词被拆译会丢失品牌识别度，而保留英文对读者无理解障碍。
_MASK_EXTRA = {
    "claude-code", "project-aria", "dsh-superagent", "openai-o1",
    "deep-principle", "frontierscience-research", "gpqa-diamond",
    "swe-bench", "terminal-bench", "cuda-x", "c-brain", "r-ky",
    "volta-autodoxer", "nemotron-3-nano-30b-a3b",
}


def _maskable_tokens(text):
    """从英文原文中挑出需要遮蔽保护的专名 token（保持出现顺序、去重）。

    返回 list[str]，每个元素是原文中的完整 token 文本。
    """
    if not text:
        return []
    found, seen = [], set()

    def _add(tok):
        if tok in seen or tok.lower() in _MASK_NEVER:
            return
        # 纯数字或纯小数（7e-4、2.5）不是专名
        if not re.search(r"[A-Za-z]", tok):
            return
        seen.add(tok)
        found.append(tok)

    for m in _MASK_TOKEN_RE.finditer(text):
        tok = m.group(0)
        # 去掉尾部的点（"GPT-6." 里的句末句号不是 token 的一部分）
        tok = tok.rstrip(".")
        parts = tok.split("-")
        if len(parts) < 2:
            continue
        low = tok.lower()
        if low in _MASK_NEVER:
            continue

        # R1 版本号型：至少一段含数字，且首段是大写字母开头的词
        # （"Hydrogen-1.0"、"Kimi-K3"、"GPT-6-Astra"、"Qwen3-235B-A22B"）。
        # 首段须以字母大写开头，可排除 "top-8"（普通数量）、
        # "5-2B"（规模区间）、"chapter-1"（章节编号）等。
        if parts[0][:1].isupper() and any(re.search(r"\d", p) for p in parts[1:]):
            _add(tok)
            continue

        # R2 驼峰型：某段内含小写→大写跃迁（"FrontierScience"、"NeuPro"），
        # 且末段是大写开头或数字——否则 "SpaceX-owned" 这类普通定语
        # （译作「由 SpaceX 拥有」）会被误保护，"owned" 就译不出来了。
        if any(_MASK_CAMEL_RE.search(s) for s in parts):
            last = parts[-1]
            if last[:1].isupper() or last[:1].isdigit():
                _add(tok)

    # R3 人工确认名单（大小写不敏感匹配，保留原文形态）
    for tok in _MASK_EXTRA:
        m = re.search(re.escape(tok), text, re.IGNORECASE)
        if m:
            _add(m.group(0))

    return found


def _mask_index(i):
    """0 -> AA, 1 -> AB, ... 26 -> BA（两位大写字母后缀）。"""
    letters = ""
    n = i
    for _ in range(2):
        letters = chr(ord("A") + n % 26) + letters
        n //= 26
    return letters


def _mask_terms(text):
    """把英文原文中的专名替换成占位符。

    返回 (遮蔽后的文本, [(占位符, 原专名), ...])。
    占位符格式 ZXQAA / ZXQAB / ...，纯大写字母，NLLB 原样透传。

    同一个专名在文中多次出现时，每次出现使用**不同**占位符。
    原因：清洗层的重复片段折叠规则会把连续重复的短片段（如 "ZXQAA，ZXQAA"）
    折叠成一个，导致第二个占位符丢失、还原时该处专名消失。
    """
    if not text:
        return text, []
    tokens = _maskable_tokens(text)
    if not tokens:
        return text, []
    pairs = []
    out = text
    # 从长到短替换，避免 "GPT-6-Astra" 被 "GPT-6" 先切走
    for tok in sorted(tokens, key=len, reverse=True):
        if tok not in out:
            continue
        # 逐段替换：同一专名的每次出现都分配一个独立占位符
        segments = out.split(tok)
        rebuilt = []
        for k, seg in enumerate(segments):
            rebuilt.append(seg)
            if k == len(segments) - 1:
                break
            # 分配一个尚未使用的占位符
            n = len(pairs)
            while True:
                ph = "ZXQ" + _mask_index(n)
                n += 1
                if ph not in out and all(p[0] != ph for p in pairs):
                    break
            rebuilt.append(ph)
            pairs.append((ph, tok))
        out = "".join(rebuilt)
    return out, pairs


def _unmask_terms(text, pairs):
    """把译文中的占位符换回原始专名。"""
    if not text or not pairs:
        return text
    out = text
    for ph, tok in pairs:
        if ph in out:
            out = out.replace(ph, tok)
    return out


def _restore_terms(text, source_text):
    """依据英文原文，把译文里的品牌音译与领域术语还原为标准写法。"""
    if not text or not source_text:
        return text
    out = text
    low = source_text.lower()
    # 第零步：数值对齐（静默改错的数字比术语错误更误导读者）。
    out = _align_numbers(out, source_text)
    # 第零点二步：数量级对齐（"300 billion" 被译成 "3亿美元" 这类量级错误）。
    out = _align_scale_magnitude(out, source_text)
    # 第零点五步：专有描述短语中英对照——模型整段留成英文时按对照表补译。
    # 仅在译文确实含中文时生效（纯英文说明翻译失败，不做无意义替换）。
    if _CJK.search(out):
        out = _apply_glossary(out)
    # 第一步：通用术语修复（如 "克劳德特工" -> "Claude 智能体"）。
    # 必须先于品牌还原，否则 "特工"->"智能体" 会被品牌名拆开而漏掉。
    out = _apply_term_fixes(out, low)
    # 第一点二步：AI 语境下「代理」->「智能体」的系统性还原。
    # 放在术语修复之后、品牌还原之前：品牌还原会把 "Anthropic" 之类的
    # 词换回原形，不影响本规则的触发判定。
    out = _fix_agent_wording(out, low)
    # 第一点五步：AI 语境的 token 统一写法（须在术语修复后执行，
    # 否则「代用证券」->「token」之类规则会被后续规则再次改写）。
    out = _fix_token_wording(out, low)
    # 第一点七步：修复「签署了与……签署」这类重复谓语的病句结构。
    # 放在术语/品牌还原之后，保证触发词判定基于最终译文形态。
    out = _fix_signing_wording(out, low)
    # 第一点七点五步：修复 retry（重试）被误译为「退休」的词形混淆。
    out = _fix_retry_confusion(out, low)
    # 第一点八步：补全被截断的货币单位（「2240 万英」→「2240 万英镑」）。
    out = _fix_currency_units(out, source_text)
    # 第一点九步：还原被意译成单字「果」的 Apple 品牌。
    out = _fix_bare_apple(out, low)
    # 第一点九点五步：把残留的英文结构标签（Runs on: / Performance: 等）译为中文。
    out = _fix_struct_labels(out)
    # 第一点九点五五步：中文形态的模板标签归一（「运行：」→「运行方式：」、
    # 「最糟糕的是：」→「最差：」）。必须在英文标签修复之后执行，
    # 否则同一处标签可能先被英文规则改写、形态判定就不一致了。
    out = _fix_zh_label_variants(out, low)
    # 第一点九点八步：修复专有名词被逐词直译造成的失真
    # （World Wide Web→万维网、Scientific American→科学美国人、
    #   turn of the millennium→千年之交）。
    # 放在术语修复与品牌还原之后，保证触发词判定基于最终译文形态。
    out = _fix_proper_nouns(out, low)
    # 第一点九点八五步：修复语言名音译失真（Telugu→泰国语、Kannada→加拿大语、
    #   Punjabi→西班牙语等）。必须放在品牌还原之前——
    #   「Dreambeans」的品牌还原与语言名还原互不影响，但本函数依赖的
    #   触发词判定只读英文原文，位置不影响正确性；
    #   放在此处可确保语言名修复先于品牌还原，避免品牌还原把
    #   「印度语」这类形态再改写一次。
    out = _fix_language_names(out, low)
    # 第二步：品牌名还原。
    # 把所有品牌的译法汇总后按「译法长度」降序统一替换：否则短译法会先命中
    # 长译法的内部（如 "果智能" 命中 "苹果智能"，产出 "苹Apple Intelligence"）。
    pairs = []
    for canonical, variants in BRAND_TERMS:
        if canonical.lower() not in low:
            continue
        for v in variants:
            if v:
                pairs.append((v, canonical))
    for wrong, right in sorted(pairs, key=lambda p: -len(p[0])):
        if wrong in out:
            out = out.replace(wrong, right)
    # 第二点五步：品牌还原后补跑一次术语修复。
    # 必要原因：部分规则依赖品牌还原的结果才能匹配，例如模型把
    # "Gemini 4 Carbon" 译成「双子座4碳」，品牌还原后成为「Gemini 4碳」，
    # 只有此时 "Gemini 4碳" -> "Gemini 4 Carbon" 这类规则才命中得了。
    out = _apply_term_fixes(out, low)
    # 第三步：品牌所有格还原（"Metas" -> "Meta 的"）。
    # 放在品牌还原之后，避免 "Metas" 先被品牌规则改成 "Meta" 而丢掉 's'。
    for wrong, right in _POSSESSIVE:
        if wrong in out:
            out = out.replace(wrong, right)
    # 第四步：硅谷单独成词时被模型译成「谷」，需要还原。
    # 若译文已是「硅谷」则不处理，避免出现「硅硅谷」。
    if "silicon valley" in low and "硅谷" not in out:
        out = re.sub(r"(?<![美斯硅])谷(?![歌])", "硅谷", out)
    # 第五步：品牌名被模型截断成单字（Apple -> "果"），按原文品牌还原。
    # 后缀表覆盖常见搭配（果公司/果首席/果的/果推出…），并用负向前查排除
    # 「如果/结果/水果/苹果」等正常词，避免误伤。
    #
    # 2026-11-03 10:00 巡检补充：「可」进后缀表。
    # 根因："Apple may try to ..." 被模型译成「果可能会试图…」，
    # 而 "may" 的中文是「可能」，其首字「可」原先不在后缀表里，
    # 导致本步整条规则失配，Apple 品牌还原彻底失效，标题主语变成「果」。
    # 安全性：负向前查已排除 如果/结果/成果/水果/苹果/效果/获得 等
    # 以「果」结尾的常用词（如「如果可能」的前字「如」在表内），
    # 且本规则仅在原文出现 "apple" 时才执行，误伤面极小。
    if "apple" in low:
        out = re.sub(
            r"(?<![苹结水后因成实树野如效获])果(?=[将会在推发布推出本智能公司首席的CEO水服可])",
            "Apple ",
            out,
        )
    # 第六步：修复品牌/专名与后续拉丁词的粘连（"SamayaAI" -> "Samaya AI"）。
    out = _fix_latin_spacing(out)
    # 第六点五步：Anthropic 在句首被意译成「人类」的还原。
    # 放在品牌还原之后：此时「人类学」等形态已被品牌表处理，
    # 剩下的「人类+言说动词」才是主语位置的意译残留。
    out = _fix_anthropic_subject(out, low)
    # 第六点七步：Brave 作为浏览器公司名被意译成「勇敢」的还原。
    # 放在品牌还原之后：此处「勇敢」已无其它还原路径可走，
    # 且需要原文上下文才能区分公司名与普通动词用法。
    out = _fix_brave_company(out, low)
    # 第六点八步：专有名词大小写还原。
    # NLLB 对不认识的专名会整体小写（windward / azimut.ai / ami daniel），
    # 中文读者据此无法定位报道主体。放在品牌还原之后，
    # 保证判定基于最终形态的品牌名。
    out = _fix_proper_noun_case(out, source_text)
    # 第七步：品牌还原后可能重新产生中英粘连，统一补空格。
    out = _fix_cjk_latin_spacing(out)
    return out


def _looks_chinese(text):
    if not text:
        return False
    return len(_CJK.findall(text)) >= max(2, len(text) * 0.15)


# ---------------- 翻译实现 ----------------
def _cap_input(text, limit=900):
    """翻译前的输入兜底截断。

    NLLB 分词器输入上限为 384 token，超长文本会被静默截断，
    导致译文只覆盖原文开头一小部分，且长生成出现重复退化。
    抓取层已做句边界截断，这里作为第二道防线，防止历史存量数据绕过抓取层。
    """
    if not text:
        return text
    if len(text) <= limit:
        return text
    head = text[:limit]
    best = -1
    for mark in (". ", "。 ", "? ", "! ", "; "):
        idx = head.rfind(mark)
        if idx > best:
            best = idx
    if best >= int(limit * 0.4):
        return head[: best + 1].strip()
    sp = head.rfind(" ")
    if sp > int(limit * 0.4):
        return head[:sp].strip()
    return head.strip()


# 长文本分块阈值（字符）。超过该长度的摘要按句边界切块后分批翻译。
#
# 根因：NLLB 单次生成上限 max_new_tokens=300，而 900 字符的英文摘要
# 译成中文约需 600+ token，因此长文本会被硬生生截断（实测 972 字符英文
# 只译出前 268 字符，末尾的「成功率 56%→75%」等关键事实整段丢失）。
# 按句切成 ~380 字符的小块分别翻译再拼接，可完整覆盖原文。
CHUNK_MAX_CHARS = 380

# 句子边界正则：英文句末标点 + 后续空白
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?;])\s+")


def _split_long_text(text, limit=CHUNK_MAX_CHARS):
    """把长英文文本按句边界切成不超过 limit 字符的小块。

    单句本身超过 limit 时退化为按逗号切分；再不行则硬切。
    返回 list[str]，拼接后可还原原文语义。
    """
    if not text:
        return []
    text = text.strip()
    if len(text) <= limit:
        return [text]

    # 第一步：按句号切分
    sentences = [s for s in _SENT_SPLIT_RE.split(text) if s.strip()]
    chunks, cur = [], ""
    for sent in sentences:
        if len(sent) > limit:
            # 超长单句：先收尾当前块，再对这句做逗号级切分
            if cur:
                chunks.append(cur)
                cur = ""
            pieces = [p for p in re.split(r"(?<=,)\s+", sent) if p.strip()]
            for p in pieces:
                if len(p) > limit:
                    if cur:
                        chunks.append(cur)
                        cur = ""
                    for i in range(0, len(p), limit):
                        chunks.append(p[i: i + limit])
                elif cur and len(cur) + len(p) + 1 > limit:
                    chunks.append(cur)
                    cur = p
                else:
                    cur = (cur + " " + p) if cur else p
            continue
        if cur and len(cur) + len(sent) + 1 > limit:
            chunks.append(cur)
            cur = sent
        else:
            cur = (cur + " " + sent) if cur else sent
    if cur:
        chunks.append(cur)
    return chunks


def _translate_nllb_batch(texts, beams=2):
    """NLLB 批量翻译。返回 list，失败项为 None。

    性能要点：
    - max_new_tokens 按输入长度动态收敛（标题短、摘要长），避免为短文本生成上百个无用 token
    - beams=1 走贪心解码；beams=2 在质量与速度间平衡

    内存要点：
    单次 model.generate 的显存/内存占用随「批大小 × beam 数 × 生成长度」
    线性增长。一次性把上百条文本塞进一次推理会直接触发 OOM（容器上限 8GB，
    表现为进程被 oom_kill 静默杀掉、接口无响应）。故这里按 NLLB_BATCH_SIZE
    切成子批逐批推理：内存峰值与批大小解耦，条数再多也不会 OOM。
    """
    model, tok = _load_nllb()
    if model is None:
        return [None] * len(texts)
    valid_idx, valid_txt = [], []
    for i, t in enumerate(texts):
        t = _cap_input((t or "").strip())
        if t:
            valid_idx.append(i)
            valid_txt.append(t)
    out = [None] * len(texts)
    if not valid_txt:
        return out

    # 子批推理：每批最多 NLLB_BATCH_SIZE 条
    for s in range(0, len(valid_txt), NLLB_BATCH_SIZE):
        sub_idx = valid_idx[s : s + NLLB_BATCH_SIZE]
        sub_txt = valid_txt[s : s + NLLB_BATCH_SIZE]
        try:
            tok.src_lang = "eng_Latn"
            batch = tok(
                sub_txt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=384,
            )
            # 按最长输入估算所需生成长度（中文约为英文 token 数的 1.2 倍）
            src_len = int(batch["input_ids"].shape[1])
            max_new = max(24, min(300, int(src_len * 1.6) + 16))

            gen_kwargs = {
                "max_new_tokens": max_new,
                "forced_bos_token_id": tok.convert_tokens_to_ids(NLLB_TARGET),
            }
            if beams > 1:
                gen_kwargs.update({"num_beams": beams, "early_stopping": True})
            else:
                gen_kwargs.update({"num_beams": 1})

            with torch.inference_mode():
                gen = model.generate(**batch, **gen_kwargs)
            decoded = tok.batch_decode(gen, skip_special_tokens=True)
            for k, idx in enumerate(sub_idx):
                out[idx] = _clean_zh(decoded[k])
            # 子批之间主动回收，降低峰值驻留
            del gen, decoded, batch
        except Exception as e:  # noqa
            print(
                f"[translate] NLLB 批量推理失败（子批 {s // NLLB_BATCH_SIZE + 1}）: {e!r}",
                flush=True,
            )
            # 单个子批失败不影响其余子批，失败项保持 None（后续由 marian 兜底）
    return out


def _translate_marian_batch(texts):
    """Marian 批量翻译（备用）。"""
    model, tok = _load_marian()
    if model is None:
        return [None] * len(texts)
    valid_idx, valid_txt = [], []
    for i, t in enumerate(texts):
        t = (t or "").strip()
        if t:
            valid_idx.append(i)
            valid_txt.append(t[:400])
    out = [None] * len(texts)
    if not valid_txt:
        return out
    try:
        batch = tok(
            valid_txt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )
        with torch.inference_mode():
            gen = model.generate(**batch, max_new_tokens=300, num_beams=1)
        decoded = [tok.decode(g, skip_special_tokens=True) for g in gen]
        for k, idx in enumerate(valid_idx):
            out[idx] = _clean_zh(decoded[k])
        return out
    except Exception as e:  # noqa
        print(f"[translate] Marian 批量推理失败: {e!r}", flush=True)
        return [None] * len(texts)


def translate_list(texts, beams=2):
    """批量翻译（英文->中文）。

    返回 (译文列表, 引擎名)。译文列表中失败项为 None。
    """
    if not texts:
        return [], "none"
    # 原文为空或为占位符（TBD 等）时不做翻译，直接原样返回，
    # 避免产出无意义的译文并被质量闸门误判为「漏译」。
    texts = [
        t if (t and t.strip() and t.strip().upper() not in ("TBD", "N/A", "-", "TODO"))
        else (t or "")
        for t in texts
    ]
    # 专名遮蔽：翻译前把模型名等专名替换为占位符，防止 NLLB 音译/丢词；
    # 翻译后立刻还原，使下游的术语还原仍能依据原始英文触发。
    masked_texts, mask_pairs = [], []
    for t in texts:
        mt, pairs = _mask_terms(t)
        masked_texts.append(mt)
        mask_pairs.append(pairs)

    results = _translate_nllb_batch(masked_texts, beams=beams)
    method = "nllb"
    missing = [i for i, v in enumerate(results) if not v]
    if missing:
        backup = _translate_marian_batch([masked_texts[i] for i in missing])
        used_backup = False
        for k, i in enumerate(missing):
            if backup[k]:
                results[i] = backup[k]
                used_backup = True
        method = "nllb+marian" if used_backup else "nllb"
        if all(not v for v in results):
            method = "none"

    # 术语还原：依据英文原文，把音译品牌名还原为标准写法
    for i, r in enumerate(results):
        if r:
            # 先把占位符换回专名，再做术语还原——这样数字对齐等规则
            # 看到的是完整文本，不会把专名里的版本号当成"缺失数字"。
            r = _unmask_terms(r, mask_pairs[i])
            r = _restore_terms(r, texts[i])
            # 标题专用：整段英文从句残留时（"…收购 Azimut.ai to Add Visual
            # Vessel Intelligence"），把该从句单独送一次模型译成中文。
            r = _repair_stranded_en_clause(r, texts[i])
            results[i] = r

    return results, method


def translate_list_chunked(texts, beams=2, chunk_chars=CHUNK_MAX_CHARS):
    """带分块的批量翻译：长文本按句切块，逐块翻译后拼接。

    解决 NLLB 单次生成上限（max_new_tokens=300）导致长摘要被截断的问题。
    每块独立翻译，因此术语还原也按块对应的英文原文执行。
    """
    if not texts:
        return [], "none"
    norm = [
        t if (t and t.strip() and t.strip().upper() not in ("TBD", "N/A", "-", "TODO"))
        else (t or "")
        for t in texts
    ]

    # 展开成「块列表 + 每块归属的原文序号」
    flat, owner = [], []
    for i, t in enumerate(norm):
        if not t:
            continue
        for c in _split_long_text(t, chunk_chars):
            flat.append(c)
            owner.append(i)

    if not flat:
        return [None] * len(texts), "none"

    flat_results, method = translate_list(flat, beams=beams)

    # 按归属序号拼接回原条目
    pieces = {}
    for idx, orig_i in enumerate(owner):
        r = flat_results[idx]
        if not r:
            continue
        pieces.setdefault(orig_i, []).append(r)

    out = []
    for i in range(len(texts)):
        parts = pieces.get(i)
        if not parts:
            out.append(None)
            continue
        joined = "".join(parts)
        # 术语还原需覆盖整段英文原文（块级还原后可能出现跨块的品牌名）
        out.append(_restore_terms(joined, norm[i]))
    return out, method


def translate(text):
    """单条翻译。返回 (中文文本, 是否成功, 引擎名)。"""
    if not text or not text.strip():
        return text, False, "none"
    res, method = translate_list([text])
    t = res[0]
    if t and _looks_chinese(t):
        return t, True, method
    return text, False, method


def detect_lang(text):
    """简单语言检测：含足够多 CJK 字符视为中文，否则英文。"""
    if not text:
        return "en"
    cjk = len(_CJK.findall(text))
    return "zh" if cjk >= max(3, len(text) * 0.2) else "en"


def engine_status():
    """返回当前翻译引擎状态，供状态接口展示。"""
    nllb_ok = _state["nllb"]["model"] is not None
    marian_ok = _state["marian"]["model"] is not None
    if nllb_ok:
        engine = "NLLB-200 离线模型"
    elif marian_ok:
        engine = "opus-mt 离线模型"
    else:
        engine = "未就绪"
    return {
        "engine": engine,
        "nllb_ready": nllb_ok,
        "marian_ready": marian_ok,
        "note": "外部在线翻译服务在当前网络不可达，全部走本地模型",
    }


if __name__ == "__main__":
    samples = [
        "OpenAI released a new AI model that can reason about long documents.",
        "An AI agent injected drugs into a live mouse's brain.",
        "Nvidia weighs playing the cosigner for Nscale's AI data center in West Virginia.",
    ]
    for s in samples:
        out, ok, m = translate(s)
        print(f"[{m}] {out}")
    print(engine_status())
