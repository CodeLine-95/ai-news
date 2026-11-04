"""
AI 资讯聚合服务
- 每小时（及启动时）自动从多个 RSS 源拉取最新 AI 资讯
- 英文资讯自动翻译为中文（本地离线模型 + 在线后端兜底）
- 按天分组、时间精确到分
- 提供 REST API 与静态前端；前端轮询实现无需手动同步按钮的自动更新
"""
import json
import os
import re
import sys
import threading
import time
from datetime import datetime, timezone, timedelta

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import fetcher
import report
import translate
import enrich_summaries

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
OVERRIDE_FILE = os.path.join(BASE, "data", "titles_override.json")
SUMMARY_OVERRIDE_FILE = os.path.join(BASE, "data", "summaries_override.json")

# 译文尾部残留的「由某某」署名（InfoQ 等源 RSS description 以 "By <作者>" 结尾）
BYLINE_ZH_RE = re.compile(
    r"由[A-Za-z][A-Za-z.\- ]*(?:，\s*[A-Za-z][A-Za-z.\- ]*)*$"
)
STATIC_DIR = os.path.join(BASE, "static")
TZ = timezone(timedelta(hours=8))
LOG_FILE = os.path.join(BASE, "data", "server.log")


# ---------- 日志落盘 ----------
class _Tee:
    """把 stdout/stderr 同时写到终端与日志文件。

    2026-11-02 12:00 巡检发现：日志落盘原先靠 shell 重定向
    （nohup ... >> data/server.log）实现，进程被平台重启后重定向就丢了，
    日志文件停在 11:17 无法巡检。改为在进程内部做 tee，
    无论以何种方式启动（含平台拉起）日志都会持续写入 data/server.log。
    """

    def __init__(self, stream, fh):
        self._stream = stream
        self._fh = fh

    def write(self, data):
        try:
            self._stream.write(data)
        except Exception:  # noqa
            pass
        try:
            self._fh.write(data)
            self._fh.flush()
        except Exception:  # noqa
            pass
        return len(data)

    def flush(self):
        for s in (self._stream, self._fh):
            try:
                s.flush()
            except Exception:  # noqa
                pass

    def isatty(self):
        try:
            return self._stream.isatty()
        except Exception:  # noqa
            return False

    def fileno(self):
        return self._stream.fileno()


_LOG_FH = None


def setup_file_logging():
    """把标准输出/错误重定向到终端 + data/server.log（幂等）。"""
    global _LOG_FH
    if _LOG_FH is not None:
        return
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        # 追加模式；日志可能很大，超过 8MB 时截断一次，避免无限膨胀。
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 8 * 1024 * 1024:
            with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                f.seek(-4 * 1024 * 1024, os.SEEK_END)
                tail = f.read()
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write("[log truncated]\n")
                f.write(tail)
        _LOG_FH = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
        sys.stdout = _Tee(sys.stdout, _LOG_FH)
        sys.stderr = _Tee(sys.stderr, _LOG_FH)
    except Exception as e:  # noqa
        _LOG_FH = None
        print("[server] 日志文件打开失败:", e, flush=True)

FETCH_INTERVAL = 3600  # 每小时拉取一次
# 两轮抓取之间的最小间隔（秒）。抓取对齐到整点，但启动首轮若跑得很快，
# 距离下一个整点可能只剩几秒，此时这一轮是无意义的重复抓取。
MIN_CYCLE_GAP = 300
MAX_AGE_DAYS = 31      # 保留最近 31 天（比 30 天多留一天缓冲，
                       # 避免边界条目正好卡在 cutoff 上被每小时调度反复滚出，
                       # 造成报告天数与条数逐小时抖动）
UPGRADE_PER_CYCLE = 40 # 每轮最多把多少条离线译文升级为在线译文（避免单轮过慢）
ENRICH_PER_CYCLE = 6   # 每轮最多补齐多少条缺失摘要（逐条请求文章页，需限速）
# 摘要翻译的 beam 数。实测 beams=3 比 beams=1 明显更准：
#   "stock price has taken a beating"  beams=1 → "股价已经升"（反了）
#   beams=3 → "股价已经下跌"；"largest post-earnings drops"
#   beams=1 → "最大的利后下跌"，beams=3 → "最大的利后跌幅之一"。
# 增量场景每轮只有少量新条目，用 beams=3 的耗时可接受。
SUMMARY_BEAMS = 3
# 每批翻译多少条新条目后落盘一次。
# 单轮新增可能达上百条（回填历史漏采条目时），一次性翻译会长时间占满 CPU
# 甚至触发 OOM；按批处理并增量落库可保证进度不丢失。
TRANSLATE_BATCH = 12

STATE = {
    "items": [],
    "last_update": None,   # ISO 字符串
    "next_update": None,   # ISO 字符串
    "total_fetched": 0,    # 累计抓取到的新条目数
    "source_health": {},   # 信源 -> 最近一轮抓到的条数（0 表示被限流/失败）
    # 信源 -> 连续抓不到数据的轮数。用于区分「偶发网络抖动」与「真的失效」：
    # 单轮 0 条只说明这一轮没赶上，不代表信源永久失效。
    "source_silent_streak": {},
}
LOCK = threading.Lock()

# 抓取周期的重入保护（见 update_cycle 的注释）。
# _CYCLE_GUARD 只保护 _CYCLE_RUNNING 这个标志位本身；
# 真正的互斥靠「抢不到就跳过」实现，不阻塞调用方。
_CYCLE_GUARD = threading.Lock()
_CYCLE_RUNNING = False

# 连续多少轮抓不到数据才判定该源失效。
# 实测 IEEE Spectrum AI / ML Mastery 等源偶发 TLS 断连，单轮可能抓不到，
# 但下一轮立即恢复（实测 IEEE 单测即得 21 条）。若按单轮判定，这些健康源
# 会被轮流误报为「失效」，运维信噪比被彻底污染。连续 3 轮为 0 才算真失效。
SILENT_STREAK_THRESHOLD = 3


# ---------- 数据持久化 ----------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            STATE["items"] = data.get("items", [])
            STATE["last_update"] = data.get("last_update")
            STATE["next_update"] = data.get("next_update")
            STATE["total_fetched"] = data.get("total_fetched", 0)
            STATE["source_health"] = data.get("source_health", {})
            STATE["source_silent_streak"] = data.get("source_silent_streak", {})
            print(f"[server] 已加载 {len(STATE['items'])} 条历史资讯", flush=True)
        except Exception as e:  # noqa
            print("[server] 加载数据失败:", e, flush=True)


def save_data():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "items": STATE["items"],
                "last_update": STATE["last_update"],
                "next_update": STATE["next_update"],
                "total_fetched": STATE["total_fetched"],
                "source_health": STATE["source_health"],
                "source_silent_streak": STATE["source_silent_streak"],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def load_title_overrides():
    """加载人工核对的标题覆盖表。

    部分标题的模型译文质量不佳（如「Gemini 4 Argon for Robotics」被译成
    「Gemini 4机器人技术的语」），人工核对后的译文写入覆盖表，
    每轮译文升级后重新写回，避免被模型译文覆盖。

    叠加 manual_overrides（代码层的人工核对结果）：data/ 在部署端是持久卷，
    其中的 JSON 覆盖表不会随代码发布更新，只有代码层的覆盖表能跟着发布走。
    """
    overrides = {}
    if os.path.exists(OVERRIDE_FILE):
        try:
            with open(OVERRIDE_FILE, "r", encoding="utf-8") as f:
                overrides.update(json.load(f))
        except Exception as e:  # noqa
            print("[server] 加载标题覆盖表失败:", e, flush=True)
    # 代码层覆盖表后置合并：它是最新一轮人工核对的定稿，优先级最高，
    # 这样部署端持久卷里的旧 JSON 覆盖表也不会把人工译文盖回去。
    try:
        import manual_overrides

        overrides.update(manual_overrides.TITLE_OVERRIDES)
    except Exception as e:  # noqa
        print("[server] 加载代码层标题覆盖表失败:", e, flush=True)
    return overrides


def load_summary_overrides():
    """加载人工核对的摘要覆盖表。

    与标题覆盖表同源人工核对：当术语规则无法修复整段语义崩坏时
    （如「Intel 因禁令而困惑，因此申请豁免出于大量的谨慎」），由人工
    逐条重写译文写入本表，每轮调度后写回，确保不会被模型译文覆盖。

    同样叠加 manual_overrides（代码层），理由见 load_title_overrides。
    """
    overrides = {}
    if os.path.exists(SUMMARY_OVERRIDE_FILE):
        try:
            with open(SUMMARY_OVERRIDE_FILE, "r", encoding="utf-8") as f:
                overrides.update(json.load(f))
        except Exception as e:  # noqa
            print("[server] 加载摘要覆盖表失败:", e, flush=True)
    try:
        import manual_overrides

        overrides.update(manual_overrides.SUMMARY_OVERRIDES)
    except Exception as e:  # noqa
        print("[server] 加载代码层摘要覆盖表失败:", e, flush=True)
    return overrides


def _normalize_spacing(text):
    """规整人工覆盖译文中的中西文间距、括号与引号风格。

    覆盖表里的文本是人工逐字定稿的，不会经过 translate._clean_zh 的
    _fix_cjk_latin_spacing，因此「自己的AI 训练偏好」「许可的meat tool」
    这类中西文粘连会原样入库。这里补一道间距规整，只动空格，
    不改任何文字内容。

    2026-11-02 16:00 巡检补充：同样补上 _normalize_cjk_parens，
    让覆盖表里的半角括号（如「消费品包装 (CPG) 制造商」）也统一为
    全角，与站内既有排版风格一致。

    2026-11-03 10:00 巡检补充：补上 _normalize_curly_quotes，
    让覆盖表里遗留的中文弯引号「“」「”」也统一为站内惯用的直角引号。
    覆盖文本同样不经过 _clean_zh，若不在这里规整，
    人工定稿条目会成为全站引号风格唯一的例外。
    """
    if not text:
        return text
    text = translate._fix_cjk_latin_spacing(text)
    text = translate._normalize_cjk_parens(text)
    text = translate._normalize_curly_quotes(text)
    return text


def apply_title_overrides(items):
    """把覆盖表中的权威标题译文写回条目。"""
    overrides = load_title_overrides()
    if not overrides:
        return 0
    applied = 0
    for it in items:
        en = (it.get("title") or "").strip()
        manual = overrides.get(en)
        if not manual:
            continue
        manual = _normalize_spacing(manual)
        if (it.get("title_zh") or "") != manual:
            it["title_zh"] = manual
            it["translated"] = True
            applied += 1
    if applied:
        print(f"[cycle] 应用人工标题覆盖 {applied} 条", flush=True)
    return applied


def apply_summary_overrides(items):
    """把覆盖表中的权威摘要译文写回条目。"""
    overrides = load_summary_overrides()
    if not overrides:
        return 0
    applied = 0
    for it in items:
        en = (it.get("title") or "").strip()
        manual = overrides.get(en)
        if not manual:
            continue
        manual = _normalize_spacing(manual)
        if (it.get("summary_zh") or "") != manual:
            it["summary_zh"] = manual
            it["translated"] = True
            applied += 1
    if applied:
        print(f"[cycle] 应用人工摘要覆盖 {applied} 条", flush=True)
    return applied


def apply_term_cleanup(items):
    """对存量译文做确定性重清洗（不调用模型）。

    离线翻译模型对品牌名与固定术语的偏差是稳定复现的（Block→区块、
    PageBreak→页面破解、XSS Bugs→XSS 错误 等）。这些偏差不会被后续重译
    自动修好，必须靠术语规则确定性回填，因此每轮调度都跑一次，
    让新加入的 TERM_FIXES / BRAND_TERMS 规则对存量条目持续生效。
    """
    cleaned = 0
    for it in items:
        if it.get("lang") != "en":
            continue
        t = translate._clean_title_zh(it.get("title_zh") or "")
        s = translate._clean_zh(it.get("summary_zh") or "")
        if it.get("title"):
            t = translate._restore_terms(t, it["title"])
        if it.get("summary"):
            s = translate._restore_terms(s, it["summary"])
        s = BYLINE_ZH_RE.sub("", s).strip()
        if t != it.get("title_zh") or s != it.get("summary_zh"):
            cleaned += 1
            it["title_zh"] = t
            it["summary_zh"] = s
    if cleaned:
        print(f"[cycle] 术语确定性重清洗 {cleaned} 条", flush=True)
    return cleaned


# ---------- 抓取 + 翻译 + 入库 ----------
def update_cycle():
    """执行一轮抓取 + 翻译 + 入库。

    2026-11-02 11:00 巡检修复：原实现没有重入保护。scheduler_loop 与
    POST /api/refresh 可能同时进入本函数，导致两个抓取周期交错执行：
    两轮各自算自己的 now/cutoff，后完成的一轮会用更早的 now 覆盖
    STATE["last_update"]，实测出现时间戳回退（11:00 被写回 10:59:59），
    同时两轮同时改写 STATE["items"] / 落盘，存在丢条目与重复写入的风险。

    现用一把非阻塞的 CYCLE_LOCK 做重入保护：抢不到锁就直接跳过本轮，
    不排队、不阻塞调度器。抓到锁的一轮独占整个抓取-翻译-落盘流程。
    """
    global _CYCLE_RUNNING
    with _CYCLE_GUARD:
        if _CYCLE_RUNNING:
            print("[cycle] 上一轮抓取尚未结束，本轮跳过", flush=True)
            return 0
        _CYCLE_RUNNING = True
    try:
        return _update_cycle_inner()
    finally:
        with _CYCLE_GUARD:
            _CYCLE_RUNNING = False


def _update_cycle_inner():
    print("[cycle] 开始拉取资讯 ...", flush=True)
    now = datetime.now(TZ)
    cutoff = now - timedelta(days=MAX_AGE_DAYS)
    # 传入时间窗下界：各源按发布时间倒序扫描到窗口边界即止，
    # 避免「每源只取前 N 条」导致窗口内的条目被永久漏采。
    raw = fetcher.fetch_all(since=cutoff)
    existing = {it["id"] for it in STATE["items"]}
    added = 0

    # 信源健康度：记录每个源本轮实际抓到的条数，
    # 用于识别被限流（429）或失效的源，及时补源。
    health = {name: 0 for name, _ in fetcher.FEEDS}
    for r in raw:
        health[r["source"]] = health.get(r["source"], 0) + 1

    # 连续静默轮次累积：只有连续 SILENT_STREAK_THRESHOLD 轮为 0 才判定失效，
    # 避免把偶发 TLS 抖动误报为信源失效（单轮 0 条 ≠ 源已死）。
    streak = dict(STATE.get("source_silent_streak") or {})
    for name in health:
        streak[name] = (streak.get(name, 0) + 1) if health[name] == 0 else 0
    dead = sorted(
        n for n, c in health.items()
        if c == 0 and streak.get(n, 0) >= SILENT_STREAK_THRESHOLD
    )
    flapping = sorted(
        n for n, c in health.items()
        if c == 0 and streak.get(n, 0) < SILENT_STREAK_THRESHOLD
    )
    if dead:
        print(f"[cycle] 确认失效的源: {', '.join(dead)}", flush=True)
    if flapping:
        print(
            f"[cycle] 本轮偶发无数据(不判失效): {', '.join(flapping)}",
            flush=True,
        )
    STATE["source_silent_streak"] = streak

    with LOCK:
        pending = []  # 待翻译的英文条目（含标题/摘要）
        # 跨源标题去重：同一则公告常被多个源转载（如 Google DeepMind 与
        # Google Blog 同时发布同一条 Gemini 公告），URL 不同故 link 去重
        # 拦不住，会在列表里重复出现。此处按「规范化英文标题」去重，
        # 保留最早发布的那条。
        def _norm_title(t):
            return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()

        seen_titles = {
            _norm_title(it.get("title")) for it in STATE["items"] if it.get("title")
        }
        dup_titles = 0
        for r in raw:
            nid = fetcher.make_id(r["link"])
            if nid in existing:
                continue
            existing.add(nid)
            # 只接纳「新近发布」的条目：RSS 源会持续吐出几个月前的旧文，
            # 若不按发布时间过滤，这些旧文会先入库、再被过期清理删掉，
            # 造成「本次新增 N 条」的计数虚高与无谓的翻译开销。
            if r["dt"] < cutoff:
                continue
            tkey = _norm_title(r["title"])
            if tkey and tkey in seen_titles:
                dup_titles += 1
                continue
            seen_titles.add(tkey)
            lang = translate.detect_lang(r["title"])
            item = {
                "id": nid,
                "source": r["source"],
                "link": r["link"],
                "lang": lang,
                "date": r["dt"].strftime("%Y-%m-%d"),
                "time": r["dt"].strftime("%H:%M"),
                "iso": r["dt"].isoformat(),
                "title": r["title"],
                "summary": r["summary"],
                "title_zh": r["title"] if lang == "zh" else "",
                "summary_zh": r["summary"] if lang == "zh" else "",
                "translated": False,
                "method": "",
            }
            if lang == "zh":
                item["translated"] = True
                item["method"] = "native"
            else:
                pending.append(item)
            STATE["items"].append(item)
            added += 1

        # 批量翻译（一次前向传播完成所有标题与摘要，速度快）
        # 摘要走分块翻译：长摘要单次生成会被 max_new_tokens 截断，
        # 分块后能完整覆盖原文（实测 972 字符英文原本只译出前 268 字符）。
        #
        # 分批处理 + 增量落库：一次性翻译上百条会长时间占用 CPU 并有 OOM 风险，
        # 故按 TRANSLATE_BATCH 条一组处理，每组结束即落库，
        # 既保证进度不丢失，也让网站能较快看到已译好的部分。
        #
        # 2026-11-02 00:00 巡检修复：新增「翻译失败条目重试」机制。
        # 原实现只翻译「本轮新入库」的条目（pending），一旦某条目翻译时
        # 翻译引擎尚未就绪（如进程刚启动、模型仍在加载，或内存竞争导致
        # transformers 导入失败），该条目会写入 title_zh = 英文原文、
        # method = "none" 并落库；因 id 已存在于 existing 集合，
        # 后续每一轮调度都会跳过它 —— 该条目将永久停留在未翻译状态，
        # 且没有任何机制会重试它。
        # 现将「英文条目但译文等于原文（未翻译成功）」也纳入 pending，
        # 使其在下一轮调度获得重试机会。
        retry = [
            it
            for it in STATE["items"]
            if it.get("lang") == "en"
            and it.get("title_zh") == it.get("title")
            and not it.get("translated")
        ]
        if retry:
            print("[cycle] 待重试未翻译条目 %d 条" % len(retry), flush=True)
            pending.extend(retry)

        if pending:
            method = "none"
            done = 0
            for s in range(0, len(pending), TRANSLATE_BATCH):
                group = pending[s : s + TRANSLATE_BATCH]
                titles = [it["title"] for it in group]
                summaries = [it["summary"] for it in group]
                zh_titles, m1 = translate.translate_list(titles)
                zh_summaries, m2 = translate.translate_list_chunked(
                    summaries, beams=SUMMARY_BEAMS
                )
                gm = m1 if m1 != "none" else m2
                for i, it in enumerate(group):
                    t = zh_titles[i] or ""
                    s2 = zh_summaries[i] or ""
                    # 翻译失败时保留原有译文（可能为空），不要回退成英文原文：
                    # 回退会让 title_zh == title，从外部看不出「尚未翻译」，
                    # 也会被翻译覆盖率统计误判为已翻译。空值则能如实反映状态，
                    # 并被上面的「待重试」逻辑在下一轮重新翻译。
                    if t:
                        it["title_zh"] = t
                    if s2:
                        it["summary_zh"] = s2
                    it["translated"] = bool(t) and t != it["title"]
                    it["method"] = gm
                done += len(group)
                method = gm if gm != "none" else method
                # 每批结束即落库：即使后续批次被中断，已完成部分也不会丢失
                save_data()
                print(
                    f"[cycle] 批量翻译进度 {done}/{len(pending)}（方式: {gm}）",
                    flush=True,
                )
            print(
                f"[cycle] 批量翻译 {len(pending)} 条英文资讯完成（方式: {method}）",
                flush=True,
            )

        # 用更优引擎（NLLB）重译历史条目：opus-mt 译文质量偏低，逐批升级
        #
        # 2026-11-01 21:00 巡检加固：原实现只筛 method in ("local", "marian")，
        # 但全部存量条目的 method 早已是 "nllb"，该列表恒为空——
        # 意味着「已入库的条目永远不会被重译」，早期代码版本留下的
        # 缺陷译文（长摘要截断、小数位截断等）就此固化。
        # 现改为：除旧引擎条目外，还纳入「摘要明显短于英文原文」
        # 的疑似截断条目，以及人工标记 needs_retranslate 的条目。
        # 这类条目数量有限（实测个位数），每轮限量重译，
        # 不会显著拖慢调度，也不会与 8GB cgroup 内存上限冲突。
        upgraded = 0
        stale = []
        for it in STATE["items"]:
            if it.get("lang") != "en":
                continue
            if it.get("method") in ("local", "marian"):
                stale.append(it)
                continue
            if it.get("needs_retranslate"):
                stale.append(it)
                continue
            # 疑似截断：英文摘要不短，但中文摘要长度不足英文的 22%
            # （正常中文压缩比约 30%~45%，低于 22% 基本可判定丢内容）
            # 同时限制重试次数：若某条目重译后仍判定为截断，
            # 说明模型对该条目稳定退化，再重译也是同样结果，
            # 只会空耗 CPU，故最多重试 2 次后交给人工覆盖处理。
            if it.get("retranslate_attempts", 0) >= 2:
                continue
            en_len = len((it.get("summary") or "").strip())
            zh_len = len((it.get("summary_zh") or "").strip())
            if en_len >= 200 and zh_len < en_len * 0.22:
                stale.append(it)
        if stale:
            batch = stale[:UPGRADE_PER_CYCLE]
            titles = [it["title"] for it in batch]
            summaries = [it.get("summary") or "" for it in batch]
            zh_titles, m1 = translate.translate_list(titles)
            zh_summaries, m2 = translate.translate_list_chunked(summaries)
            for i, it in enumerate(batch):
                t = zh_titles[i]
                if t and t != it["title"]:
                    it["title_zh"] = t
                    upgraded += 1
                s = zh_summaries[i]
                if s:
                    it["summary_zh"] = s
                it["method"] = m1 if m1 != "none" else m2
                it["translated"] = bool(it.get("title_zh")) and it["title_zh"] != it["title"]
                # 记录重试次数：连续两次重译后仍判定为截断的条目不再自动重试，
                # 改由人工覆盖表定稿，避免每轮空耗 CPU。
                en_len = len((it.get("summary") or "").strip())
                zh_len = len((it.get("summary_zh") or "").strip())
                if en_len >= 200 and zh_len < en_len * 0.22:
                    it["retranslate_attempts"] = it.get("retranslate_attempts", 0) + 1
                else:
                    it.pop("needs_retranslate", None)
                    it.pop("retranslate_attempts", None)
            if upgraded:
                print(f"[cycle] 高质量译文升级 {upgraded} 条", flush=True)

        # 摘要兜底：部分源（DeepMind / MIT Tech Review 某些条目）RSS 不带摘要，
        # 从文章页 og:description 补齐，再交给翻译引擎。
        need_desc = [
            it
            for it in STATE["items"]
            if it.get("lang") == "en"
            and not (it.get("summary") or "").strip()
            and not (it.get("summary_zh") or "").strip()
        ]
        if need_desc:
            filled = 0
            for it in need_desc[:ENRICH_PER_CYCLE]:
                desc = enrich_summaries.page_description(it.get("link") or "")
                if desc:
                    it["summary"] = desc
                    filled += 1
            if filled:
                # 补齐的英文摘要需要重新翻译
                sub = [it for it in need_desc[:ENRICH_PER_CYCLE] if it.get("summary")]
                zh, m = translate.translate_list_chunked([it["summary"] for it in sub], beams=1)
                for it, z in zip(sub, zh):
                    if z:
                        it["summary_zh"] = z
                        it["method"] = m
                print(f"[cycle] 从文章页补齐摘要并翻译 {filled} 条", flush=True)

        # 排序：时间倒序
        STATE["items"].sort(key=lambda x: x["iso"], reverse=True)
        # 清理过期条目
        STATE["items"] = [
            it for it in STATE["items"]
            if datetime.fromisoformat(it["iso"]).astimezone(TZ) >= cutoff
        ]
        # last_update 单调递增：即便有多轮并发/乱序结束，
        # 也不允许用更早的时间戳覆盖更新的值（否则前端显示的
        # 「最后更新」会倒退，运维无法判断数据新鲜度）。
        prev = STATE.get("last_update")
        if prev:
            try:
                prev_dt = datetime.fromisoformat(prev)
            except Exception:  # noqa
                prev_dt = None
            if prev_dt and prev_dt > now:
                now = prev_dt
        STATE["last_update"] = now.isoformat()
        # next_update 与调度器实际使用的唤醒时刻保持一致，
        # 避免前端倒计时显示的时刻与真实抓取时刻不一致。
        STATE["next_update"] = _effective_boundary(now).isoformat()
        STATE["total_fetched"] += added
        STATE["source_health"] = health
        # 术语确定性重清洗（让新增术语规则对存量条目生效）
        apply_term_cleanup(STATE["items"])
        # 人工核对译文优先于模型译文（标题 + 摘要）
        apply_title_overrides(STATE["items"])
        apply_summary_overrides(STATE["items"])
        save_data()

    # 同步重新生成 Markdown 摘要报告，保持与网站数据一致
    try:
        report.main()
    except Exception as e:  # noqa
        print("[cycle] 生成摘要报告失败:", e, flush=True)

    print(f"[cycle] 本次新增 {added} 条，当前共 {len(STATE['items'])} 条", flush=True)
    if dup_titles:
        print(f"[cycle] 跳过跨源重复标题 {dup_titles} 条", flush=True)
    return added


# ---------- 调度器 ----------
def apply_manual_overrides_on_startup():
    """启动时用人工定稿覆盖表回填存量译文。

    部署端的 data/ 是持久卷：news.json 与 JSON 覆盖表都可能在多次发布
    之间与本地脱节，导致「本地已修好的译文」在线上又变回模型译文。
    这里在进程启动时（不等第一个调度周期）就把人工定稿回填一遍，
    保证线上访问到的第一条数据就是定稿版本。

    返回回填条数。
    """
    titles = load_title_overrides()
    summaries = load_summary_overrides()
    n = 0
    for it in STATE["items"]:
        en = (it.get("title") or "").strip()
        if not en:
            continue
        if titles.get(en):
            v = _normalize_spacing(titles[en])
            if it.get("title_zh") != v:
                it["title_zh"] = v
                it["translated"] = True
                n += 1
        if summaries.get(en):
            v = _normalize_spacing(summaries[en])
            if it.get("summary_zh") != v:
                it["summary_zh"] = v
                it["translated"] = True
                n += 1
    if n:
        save_data()
        print("[server] 启动回填人工定稿 %d 处" % n, flush=True)
    return n


def _wait_translate_ready(timeout=180):
    """等待翻译引擎就绪，返回是否成功。

    2026-11-02 00:00 巡检修复：原实现中预热（_warmup 线程）与调度抓取
    （scheduler_loop 线程）并行启动，两者之间没有任何同步。实测在容器
    内存竞争时 transformers 导入会失败（ModuleNotFoundError: Could not
    import module 'AutoModelForSeq2SeqLM'），此时首次抓取到的条目会以
    英文原文入库，站点出现「未翻译」条目。
    现改为：调度器在抓取前先等待引擎就绪，最多等待 timeout 秒；
    超时后仍照常抓取（由 update_cycle 内的「待重试」逻辑兜底）。
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            model, tok = translate._load_nllb()
            if model is not None:
                return True
        except Exception as e:  # noqa
            print("[cycle] 等待翻译引擎异常:", e, flush=True)
            return False
        time.sleep(2)
    return False


def _next_boundary(now):
    """返回严格晚于 now 的下一个整点抓取时刻。

    抓取固定对齐到整点（本地时区 08:00 / 09:00 / ...），
    这样每轮的间隔恒为 3600 秒，不受上一轮抓取耗时影响；
    scheduler_loop 与 update_cycle 共用本函数，
    保证 /api/status 声明的 next_update 与真实调度时刻一致。
    """
    step = timedelta(hours=max(1, FETCH_INTERVAL // 3600))
    boundary = now.replace(minute=0, second=0, microsecond=0) + step
    while boundary <= now:
        boundary += step
    return boundary


def _effective_boundary(now):
    """返回本轮真实会唤醒的时刻（含 MIN_CYCLE_GAP 修正）。

    2026-11-02 12:00 巡检发现：MIN_CYCLE_GAP 修正原先只作用于
    scheduler_loop 的局部变量 boundary，而 /api/status 的 next_update
    仍由 _next_boundary(now) 单独计算。两者在「启动首轮跑得快、
    距整点不足 MIN_CYCLE_GAP」时会相差数分钟——站点声明的下次抓取
    时刻早于真实执行时刻，前端倒计时会提前归零显示 00:00。

    现在统一由本函数计算：scheduler_loop 用它决定 sleep 多久，
    update_cycle 用它声明 next_update，两处永远一致。
    """
    boundary = _next_boundary(now)
    if (boundary - now).total_seconds() < MIN_CYCLE_GAP:
        boundary = now + timedelta(seconds=MIN_CYCLE_GAP)
    return boundary


def scheduler_loop():
    # 等待翻译引擎就绪后再开始抓取，避免首轮抓到的新条目因引擎未加载
    # 而以英文原文入库（详见 _wait_translate_ready 的注释）。
    if _wait_translate_ready():
        print("[cycle] 翻译引擎已就绪，开始首轮抓取", flush=True)
    else:
        print("[cycle] 等待翻译引擎超时，仍开始抓取（失败条目将在下轮重试）",
              flush=True)
    # 启动即先拉一次
    try:
        update_cycle()
    except Exception as e:  # noqa
        print("[cycle] 首次拉取异常:", e, flush=True)
    # 固定时刻调度：睡到下一个整点，而不是「本轮结束后再睡 3600 秒」。
    # 原实现每轮的实际间隔是 3600s + 本轮耗时（实测抓取约 20~40s），
    # 误差逐轮累积，站点声明的 next_update 与真实抓取时刻会越差越远。
    while True:
        now = datetime.now(TZ)
        # 统一用 _effective_boundary：声明的 next_update 与真实唤醒时刻一致。
        boundary = _effective_boundary(now)
        sleep_s = (boundary - now).total_seconds()
        # 提前声明本轮真实执行时刻，让 /api/status 与前端倒计时同步。
        STATE["next_update"] = boundary.isoformat()
        print(
            "[cycle] 下轮抓取将在 %s 执行（%.0f 秒后）"
            % (boundary.strftime("%Y-%m-%d %H:%M:%S"), sleep_s),
            flush=True,
        )
        time.sleep(sleep_s)
        try:
            update_cycle()
        except Exception as e:  # noqa
            print("[cycle] 定时拉取异常:", e, flush=True)


# ---------- API ----------
app = FastAPI(title="AI 信号站")


@app.get("/api/news")
def api_news():
    translated = sum(1 for it in STATE["items"] if it.get("translated"))
    return JSONResponse(
        {
            "last_update": STATE["last_update"],
            "next_update": STATE["next_update"],
            "total": len(STATE["items"]),
            "translated": translated,
            "interval_seconds": FETCH_INTERVAL,
            "items": STATE["items"],
        }
    )


@app.get("/api/status")
def api_status():
    translated = sum(1 for it in STATE["items"] if it.get("translated"))
    eng = translate.engine_status()
    health = STATE.get("source_health") or {}
    streak = STATE.get("source_silent_streak") or {}
    # 失效判定：连续多轮为 0 才算真失效（见 SILENT_STREAK_THRESHOLD 说明）
    dead = sorted(
        k for k, v in health.items()
        if v == 0 and streak.get(k, 0) >= SILENT_STREAK_THRESHOLD
    )
    # 偶发抖动：单轮为 0 但尚未达到阈值，单独标注以免误读为失效
    flapping = sorted(
        k for k, v in health.items()
        if v == 0 and streak.get(k, 0) < SILENT_STREAK_THRESHOLD
    )
    return JSONResponse(
        {
            "last_update": STATE["last_update"],
            "next_update": STATE["next_update"],
            "total": len(STATE["items"]),
            "translated": translated,
            "interval_seconds": FETCH_INTERVAL,
            "engine": eng.get("engine"),
            "engine_note": eng.get("note"),
            "sources": len(health),
            "sources_silent": dead,
            "sources_flapping": flapping,
        }
    )


@app.post("/api/refresh")
def api_refresh():
    added = update_cycle()
    return JSONResponse({"ok": True, "added": added, "total": len(STATE["items"])})


@app.get("/api/report")
def api_report():
    """返回最新 Markdown 摘要报告，便于外部消费。"""
    rp = os.path.join(BASE, "AI资讯摘要.md")
    if not os.path.exists(rp):
        return JSONResponse({"ok": False, "error": "报告尚未生成"}, status_code=404)
    with open(rp, "r", encoding="utf-8") as f:
        return JSONResponse({"ok": True, "updated": STATE["last_update"], "markdown": f.read()})


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ---------- 启动 ----------
if __name__ == "__main__":
    setup_file_logging()
    load_data()
    # 启动即用人工定稿回填存量译文（部署端持久卷可能与本地脱节），
    # 保证线上第一条数据就是定稿版本，不必等第一个调度周期。
    try:
        apply_manual_overrides_on_startup()
    except Exception as e:  # noqa
        print("[server] 启动回填人工定稿异常:", e, flush=True)
    # 预热翻译引擎：否则在首次抓到新条目之前，/api/status 会显示
    # 「未就绪」，让站点状态栏给出误导性信息。
    def _warmup():
        try:
            translate.translate_list(["warmup"])
            print("[server] 翻译引擎预热完成", flush=True)
        except Exception as e:  # noqa
            print("[server] 翻译引擎预热失败:", e, flush=True)

    threading.Thread(target=_warmup, daemon=True).start()
    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
