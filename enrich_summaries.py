"""为缺少摘要的条目从文章页补齐正文摘要。

部分信源（如 Google DeepMind、MIT Tech Review 的个别条目）在 RSS 中
不提供 description/content，条目入库后摘要为空，报告里会缺失正文。

本模块读取条目链接页面的 og:description / meta description 作为摘要回填。
仅对「确实没有摘要」的条目发起请求，且限速，避免影响每小时抓取主循环。

用法：
    python3 enrich_summaries.py          # 补齐全部缺摘要条目
    python3 enrich_summaries.py --limit 5 # 仅补齐前 5 条
"""
import argparse
import html
import json
import os
import re
import sys
import time

import requests

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# og:description / twitter:description / name=description
_META_PATTERNS = [
    re.compile(
        r'<meta[^>]+(?:property|name)=["\'](?:og:description|twitter:description|description)["\']'
        r'[^>]*content=["\']([^"\']+)["\']',
        re.IGNORECASE,
    ),
    re.compile(
        r'<meta[^>]+content=["\']([^"\']+)["\']'
        r'[^>]*(?:property|name)=["\'](?:og:description|twitter:description|description)["\']',
        re.IGNORECASE,
    ),
]

# 站点通用的无意义描述，不作为摘要
_JUNK_DESC = re.compile(
    r"^(?:enable javascript|browser does not support|javascript is disabled"
    r"|subscribe|sign in|log in)",
    re.IGNORECASE,
)

_SESSION = requests.Session()
_SESSION.mount(
    "https://",
    requests.adapters.HTTPAdapter(pool_connections=8, pool_maxsize=8, max_retries=0),
)


def page_description(url, timeout=20):
    """抓取文章页的描述性元标签；失败返回空串。"""
    try:
        r = _SESSION.get(url, timeout=timeout, headers=HEADERS, allow_redirects=True)
    except Exception:
        return ""
    if r.status_code >= 400:
        return ""
    try:
        text = r.text
    except Exception:
        return ""
    for pat in _META_PATTERNS:
        m = pat.search(text)
        if m:
            desc = html.unescape(m.group(1)).strip()
            if len(desc) >= 20 and not _JUNK_DESC.match(desc):
                return re.sub(r"\s+", " ", desc)
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="最多补齐条数，0=不限")
    args = ap.parse_args()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    targets = [
        it
        for it in items
        if it.get("lang") == "en"
        and not (it.get("summary") or "").strip()
        and not (it.get("summary_zh") or "").strip()
    ]
    if args.limit:
        targets = targets[: args.limit]

    print(f"待补齐 {len(targets)} 条", flush=True)
    filled = 0
    for i, it in enumerate(targets, 1):
        desc = page_description(it.get("link") or "")
        if desc:
            it["summary"] = desc
            filled += 1
            print(f"[{i}/{len(targets)}] {it['source']} | {desc[:70]}", flush=True)
        else:
            print(f"[{i}/{len(targets)}] {it['source']} | 未取到描述，跳过", flush=True)
        # 每条之间稍作间隔，避免对站点造成压力
        time.sleep(0.5)

    if filled:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"已补齐 {filled} 条摘要，已写回 {DATA_FILE}", flush=True)
    else:
        print("无可补齐条目", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
