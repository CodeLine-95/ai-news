"""译文质量修复：对存量条目做「确定性重清洗 + 定点重译」。

相比全量重译（retranslate.py）本脚本更省时：
  1) 确定性重清洗：直接对已存储的 title_zh / summary_zh 重新跑一遍
     translate._clean_zh + translate._restore_terms，修复半角标点、
     句末句号、品牌所有格、品牌名截断等问题。此步骤不需要模型。
  2) 定点重译：仅当英文原文本身发生变化（样板语被剥离 / HTML 实体被解码）
     时才用 NLLB 重译该条目的标题与摘要。

注意：修复期间请勿同时运行 server.py（两者会争写 data/news.json）。
修复完成后重启服务即可加载新译文。

用法：
    python3 repair.py             # 全量修复
    python3 repair.py --dry-run   # 只报告将要做的改动，不写文件
"""
import argparse
import json
import os
import re
import sys
import time

import translate
import report
import fetcher

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")


def _clean_zh_text(text, source):
    """对已存储的译文重新执行清洗与术语还原。"""
    if not text:
        return text
    out = translate._clean_zh(text)
    if source:
        out = translate._restore_terms(out, source)
    return out


# ---------- 质量闸门 ----------
# 判定译文是否仍然不合格，需要用模型重译。
# 这些检查针对的是「规则层修不掉」的问题：
#   1) 整段英文残留（模型漏译）
#   2) 关键数字缺失或被改错
#   3) 译文与原文长度严重不符（大段丢内容）
_UNTRANSLATED_RE = re.compile(
    r"(?:[A-Za-z][A-Za-z'\-]*[ ]){2,}[A-Za-z][A-Za-z'\-]*"
)
# 允许残留在中文译文里的专有名词/术语（这些本就不该译）
_KEEP_EN = {
    "apple intelligence", "claude opus", "rust cli", "muse charm",
    "uncanny valley", "uc berkeley", "sam altman", "hugging face",
    "model spec", "prime mega moe", "token economizer", "frontier finance",
    "swe bench", "terminal bench", "claude fable", "macbook pro",
    "no ordinary assistant", "techcrunch founder summit",
    "google deepmind gemma", "google deepmind", "deepmind gemma",
    "frontierfinance", "tokeneconomizer", "swe-bench", "terminal-bench",
    "techcrunch", "wired", "anthropic", "openai", "nvidia", "mistral",
    "gemini", "chatgpt", "perplexity", "cohere", "databricks",
    "snowflake", "langchain", "pytorch", "kubernetes", "linux",
    "windows", "oracle", "ibm", "samsung", "qualcomm", "meta",
    "google", "microsoft", "amazon", "tesla", "intel", "apple",
    "vercel", "baseten", "samaya", "sterling", "block", "nscale",
    "claude", "llama", "gemini 4", "gemma 4", "deepseek", "qwen",
    "prime intellect", "prime-rl", "droid", "factory",
    # 人名 / 机构名 / 产品名：本来就应保留英文，不算「残留未译」
    "arthur casals", "arthur casals hien", "hien luu", "chip huyen",
    "daniel dominguez", "srini penchikala", "bain and company",
    "qcon ai new york", "vicone lab", "wikiproject ai cleanup",
    "near real-time model transform", "argon for robotics",
    "policy token", "remato losio", "renato losio", "leela kumili",
    "craig risi", "alasdair allan", "ben linders", "artemisa chatziou",
    "steef-jan wiggers", "bruno couriol", "temasek",
    # 产品名 / 机构名 / 栏目名：保留英文是正确的，不算「残留未译」
    "github copilot cli", "copilot cli", "fujifilm lto ultrium",
    "fujifilm lto ultrium10", "more perfect union",
    "bain and company", "e-conomy sea",
    # 机构名 / 论文标题 / 技术术语：保留英文是正确的
    "ieee xplore ai research suite", "vanguard jing wang",
    "agentic multimodal hindsight",
}
# 摘要过短的判定：按「中文字符数」而非长度比。
# 英文原文常常包含站点样板语（已从中文摘要中剥离），
# 直接比长度会把「清洗后的短摘要」误判为丢内容。
_ZH_MIN_CHARS = 12

# 英文数量级词 -> 换算到「亿」的系数
_EN_SCALE = {
    "trillion": 10000.0, "billion": 10.0, "million": 0.01,
    "thousand": 0.0001, "k": 0.0001, "m": 0.01, "b": 10.0,
}
_EN_NUM_SCALE_RE = re.compile(
    r"(\d+(?:[.,]\d+)*)\s*(trillion|billion|million|thousand|[kmb])\b",
    re.IGNORECASE,
)


def _num_key(v):
    return ("%.4f" % float(v)).rstrip("0").rstrip(".")


def _norm_nums(text):
    """把文本中的数值归一化为统一量级后的集合，用于跨语言比对。

    中文侧「3680亿」与英文侧「368 billion」语义一致但字面不同，
    因此按「亿」为基准折算后比较，避免把正确的量级换算误判为丢数。
    """
    out = set()
    for m in _EN_NUM_SCALE_RE.finditer(text or ""):
        try:
            val = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        out.add(_num_key(val * _EN_SCALE[m.group(2).lower()]))
    for m in re.finditer(r"(\d+(?:[.,]\d+)*)\s*(亿|万)", text or ""):
        try:
            val = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        out.add(_num_key(val if m.group(2) == "亿" else val * 0.0001))
    for m in re.finditer(r"\d+(?:[.,]\d+)*", text or ""):
        out.add(m.group(0))
    return out


def _is_complete_en(text):
    """英文文本是否以句末标点收尾（未被截断在半句）。

    与 fetcher._is_complete 同一判定口径：Google Blog / Google DeepMind
    等源的描述本身是短语义片段（无句号），属于源站形态而非截断，
    因此该判定只用于「本来就有句子的长文本」是否被截断。
    """
    s = (text or "").rstrip()
    if not s:
        return False
    return s[-1] in '.!?"\'’”)】…'


def _is_complete_zh(text):
    """中文文本是否以句末标点收尾。"""
    s = (text or "").rstrip()
    if not s:
        return False
    return s[-1] in '。！？”」）！？…'


def quality_issues(title_zh, summary_zh, title_en, summary_en):
    """返回该条目的质量缺陷列表（空列表 = 通过）。"""
    issues = []
    cjk = re.compile(r"[\u4e00-\u9fff]")

    for label, zh, en in (
        ("标题", title_zh, title_en),
        ("摘要", summary_zh, summary_en),
    ):
        # 英文原文本身为空或占位符（TBD）时，无译文是正常的，不算缺陷
        en_stripped = (en or "").strip()
        if not en_stripped or en_stripped.upper() in ("TBD", "N/A", "-", "TODO"):
            continue
        if not zh:
            issues.append(f"{label}无译文")
            continue
        if not cjk.search(zh):
            issues.append(f"{label}完全未翻译")
            continue
        # 1) 整段英文残留（>=2 个连续英文单词，且不在白名单）
        for m in _UNTRANSLATED_RE.finditer(zh):
            frag = m.group(0).strip().lower()
            if frag in _KEEP_EN:
                continue
            if any(k in frag for k in _KEEP_EN):
                continue
            issues.append(f"{label}残留英文片段「{m.group(0).strip()}」")
            break
        # 2) 中文内容过短（真正的丢内容；按中文字符数判定）
        # 阈值随英文原文长度自适应：原文本身只有一句话时，
        # 中文译文本就短，不应判为丢内容。
        if label == "摘要":
            zh_chars = len(cjk.findall(zh))
            # 译文里可能含产品名等英文（如「Playground 概览」），
            # 纯中文字符少但语义完整，因此同时看总长度。
            total_len = len(zh.strip())
            min_chars = _ZH_MIN_CHARS if len(en) > 120 else 5
            if zh_chars < min_chars and total_len < min_chars + 4:
                issues.append(f"摘要中文过短({zh_chars}字)")
        # 3) 关键数字缺失（英文标题中的数字必须在译文中出现）
        if label == "标题":
            nums = re.findall(r"\d+(?:[.,]\d+)*%?", en)
            zh_nums = re.findall(r"\d+(?:[.,]\d+)*%?", zh)
            en_scaled = _norm_nums(en)
            zh_scaled = _norm_nums(zh)
            for n in nums:
                if n in zh_nums or n.rstrip("%") in zh_nums:
                    continue
                # 量级换算不算丢数：英文 "$368 billion" 译成「3680亿美元」
                # 字面数字不同但语义一致，按亿归一后比较。
                if en_scaled & zh_scaled:
                    continue
                issues.append(f"标题数字 {n} 丢失")
                break

    # 4) 半句截断：英文原文与中文译文都应以句末标点收尾。
    #    仅对「足够长、且原文本身包含完整句子」的文本判定，
    #    避免把 Google Blog / DeepMind 的短语义片段、
    #    以及「封面图说明」这类图片描述误判为缺陷。
    if len(summary_en or "") >= 120 and "." in (summary_en or "")[:200]:
        # 排除图片说明类文本（以 "Cover image" / "Image:" 等开头）
        is_caption = re.match(
            r"^\s*(cover image|image|photo|illustration|picture|图片)\b",
            summary_en or "",
            re.IGNORECASE,
        )
        if not is_caption:
            if not _is_complete_en(summary_en):
                issues.append("英文摘要半句结尾（疑似源站截断）")
            if summary_zh and not _is_complete_zh(summary_zh):
                issues.append("中文摘要半句结尾")
    return issues


def _service_running():
    """检测本机 8080 端口上是否已有 server.py 在运行。

    修复脚本会整体重写 data/news.json，若服务同时在跑，
    两者会互相覆盖（服务内存里新增的条目会被修复脚本的旧快照覆盖，
    反之亦然）。因此检测到服务在跑时直接拒绝执行。
    """
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect(("127.0.0.1", 8080))
        return True
    except OSError:
        return False
    finally:
        s.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只报告改动，不写文件")
    args = ap.parse_args()

    if _service_running():
        print(
            "[repair] 检测到 server.py 正在运行（端口 8080）。\n"
            "        请先停止服务再执行修复，否则会与服务的写盘相互覆盖。\n"
            "        停止命令：pkill -f 'python3.11 server.py'",
            flush=True,
        )
        return 1

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    if not items:
        print("无数据")
        return 0

    # ---- 第一阶段：确定性重清洗 + 标记需要重译的条目 ----
    need_retranslate = []
    fixed_clean = 0
    fixed_source = 0
    seen_retranslate = set()

    for it in items:
        if it.get("lang") != "en":
            continue

        # 英文原文修正：标题解码 HTML 实体；摘要剥离站点样板语与标题复读
        old_title = it.get("title") or ""
        new_title = fetcher._clean_title(old_title)
        old_summary = it.get("summary") or ""
        new_summary = fetcher._strip_tail_noise(old_summary, new_title)

        title_changed = new_title != old_title
        summary_changed = new_summary != old_summary
        if title_changed or summary_changed:
            fixed_source += 1
            need_retranslate.append(it)

        if title_changed:
            it["title"] = new_title
        if summary_changed:
            it["summary"] = new_summary

        # 译文重清洗（不依赖模型）
        new_title_zh = _clean_zh_text(it.get("title_zh") or "", it.get("title") or "")
        new_summary_zh = _clean_zh_text(
            it.get("summary_zh") or "", it.get("summary") or ""
        )
        if new_title_zh != (it.get("title_zh") or ""):
            fixed_clean += 1
            it["title_zh"] = new_title_zh
        if new_summary_zh != (it.get("summary_zh") or ""):
            it["summary_zh"] = new_summary_zh

        it["translated"] = bool(it.get("title_zh")) and it["title_zh"] != it.get("title")

        # 质量闸门：规则层修完仍不合格的条目，交给模型重译
        issues = quality_issues(
            it.get("title_zh") or "",
            it.get("summary_zh") or "",
            it.get("title") or "",
            it.get("summary") or "",
        )
        if issues:
            it["_issues"] = issues
            key = (it.get("title"), it.get("summary"))
            if key not in seen_retranslate:
                seen_retranslate.add(key)
                need_retranslate.append(it)

    print(
        f"[repair] 确定性重清洗改动 {fixed_clean} 条译文；"
        f"英文原文修正 {fixed_source} 条",
        flush=True,
    )

    if args.dry_run:
        print(f"[repair] 待重译 {len(need_retranslate)} 条（dry-run，未写文件）")
        for it in need_retranslate:
            print(f"  - [{it['date']} {it['time']}] {it.get('title', '')[:60]}")
        return 0

    # ---- 第二阶段：对不合格条目用 NLLB 定点重译（最多 2 轮）----
    for attempt in range(1, 3):
        if not need_retranslate:
            break
        print(
            f"[repair] 第 {attempt} 轮重译 {len(need_retranslate)} 条，引擎加载中 ...",
            flush=True,
        )
        t0 = time.time()
        translate.translate_list(["warmup"])
        print(f"[repair] 模型就绪，用时 {time.time() - t0:.1f}s", flush=True)

        # 批量翻译（一次前向传播处理一批），比逐条翻译快一个数量级
        BATCH = 8
        for i in range(0, len(need_retranslate), BATCH):
            batch = need_retranslate[i : i + BATCH]
            titles = [it.get("title") or "" for it in batch]
            summaries = [it.get("summary") or "" for it in batch]
            # 标题用 beam=2 保质量；摘要更长，用贪心解码显著提速
            zh_titles, m1 = translate.translate_list(titles, beams=2)
            zh_summaries, m2 = translate.translate_list(summaries, beams=3)
            for k, it in enumerate(batch):
                t = zh_titles[k] or ""
                s = zh_summaries[k] or ""
                if t and t != it["title"]:
                    it["title_zh"] = t
                    it["translated"] = True
                if s:
                    it["summary_zh"] = s
                it["method"] = m1 if m1 != "none" else m2
            done = min(i + BATCH, len(need_retranslate))
            print(f"[repair] (第{attempt}轮 {done}/{len(need_retranslate)}) 重译完成", flush=True)

        # 重译后再次过闸门，仍不达标的留待下一轮
        still_bad = []
        for it in need_retranslate:
            issues = quality_issues(
                it.get("title_zh") or "",
                it.get("summary_zh") or "",
                it.get("title") or "",
                it.get("summary") or "",
            )
            if issues:
                it["_issues"] = issues
                still_bad.append(it)
            else:
                it.pop("_issues", None)
        need_retranslate = still_bad
        if need_retranslate:
            print(
                f"[repair] 第 {attempt} 轮后仍有 {len(need_retranslate)} 条未达标，"
                f"再试一轮 ...",
                flush=True,
            )

    if need_retranslate:
        print(f"[repair] 警告：{len(need_retranslate)} 条重译后仍未达标：")
        for it in need_retranslate:
            print(f"  - [{it.get('date')} {it.get('time')}] {it.get('title', '')[:50]}")
            print(f"      {it.get('_issues')}")

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # ---- 第三阶段：重新生成摘要报告 ----
    report.main()

    en = sum(1 for it in items if it.get("lang") == "en")
    tr = sum(
        1
        for it in items
        if it.get("lang") == "en" and it.get("translated") and it.get("title_zh") != it.get("title")
    )
    print(f"[repair] 完成：{tr}/{en} 条英文资讯已中译（覆盖率 {tr / en * 100:.0f}%）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
