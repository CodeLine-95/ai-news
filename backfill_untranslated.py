"""例行巡检专用：仅回填当前未翻译的英文条目（用 NLLB 引擎）。

区别于 retranslate.py（全量重译 1307 条，需停服），本脚本只处理
translated == False 的少量条目，可在 server.py 运行期间安全执行。
"""
import json
import sys
import time

import translate

BASE = "/workspace/ai-news"
DATA_FILE = f"{BASE}/data/news.json"


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", [])
    targets = [it for it in items if it.get("lang") == "en" and not it.get("translated")]
    if not targets:
        print("无未翻译条目，跳过。")
        return
    print(f"待回填 {len(targets)} 条，引擎加载中 ...", flush=True)
    t0 = time.time()
    translate.translate_list(["warmup"])
    print(f"模型就绪，用时 {time.time() - t0:.1f}s", flush=True)

    titles = [it["title"] for it in targets]
    summaries = [(it.get("summary") or "") for it in targets]
    zh_titles, _ = translate.translate_list(titles, beams=2)
    zh_summaries, _ = translate.translate_list_chunked(summaries, beams=3)

    for k, it in enumerate(targets):
        if zh_titles[k]:
            it["title_zh"] = zh_titles[k]
        if zh_summaries[k]:
            it["summary_zh"] = zh_summaries[k]
        it["translated"] = True
        it["method"] = "nllb"

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已回填 {len(targets)} 条。")


if __name__ == "__main__":
    main()
