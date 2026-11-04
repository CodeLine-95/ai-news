"""并行重译：用多进程 NLLB 引擎批量回填历史条目的中文译文。

相比串行 retranslate.py，本脚本把待译条目分片给多个 worker 进程并行处理，
每个 worker 独立加载模型并只写自己的分片结果文件，最后由父进程合并回写
data/news.json，避免多个进程争写同一数据文件。

用法：
    python3.11 retranslate_parallel.py --workers 4 --batch 8
"""
import argparse
import json
import os
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
WORK_DIR = os.path.join(BASE, "data", "_shards")
WORKER_SCRIPT = os.path.join(BASE, "_retranslate_worker.py")


def build_worker_script():
    """生成 worker 脚本：读分片 -> 翻译 -> 写分片结果。"""
    src = '''
import json, os, sys, time
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import translate, fetcher

SHARD_IN = sys.argv[1]
SHARD_OUT = sys.argv[2]

with open(SHARD_IN, "r", encoding="utf-8") as f:
    targets = json.load(f)

t0 = time.time()
translate.translate_list(["warmup"])
print(f"[w] 引擎就绪 {time.time()-t0:.0f}s，共 {len(targets)} 条", flush=True)

out = []
done = 0
t0 = time.time()
BATCH = 8
for i in range(0, len(targets), BATCH):
    batch = targets[i:i+BATCH]
    for it in batch:
        it["summary"] = fetcher._strip_tail_noise(it.get("summary") or "")
    titles = [it["title"] for it in batch]
    sums = [it.get("summary") or "" for it in batch]
    zh_titles, m1 = translate.translate_list(titles, beams=2)
    zh_sums, m2 = translate.translate_list(sums, beams=1)
    for k, it in enumerate(batch):
        if zh_titles[k]:
            it["title_zh"] = zh_titles[k]
            it["translated"] = True
        if zh_sums[k]:
            it["summary_zh"] = zh_sums[k]
        it["method"] = m1 if m1 != "none" else m2
    done += len(batch)
    out.extend(batch)
    with open(SHARD_OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    el = time.time() - t0
    print(f"[w] {done}/{len(targets)} 用时{el:.0f}s 速度{done/el:.2f}条/s", flush=True)
print("[w] 完成", flush=True)
'''
    with open(WORKER_SCRIPT, "w", encoding="utf-8") as f:
        f.write(src)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--skip-nllb", action="store_true",
                    help="跳过已用 nllb 重译过的条目")
    args = ap.parse_args()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    targets = [it for it in items if it.get("lang") == "en"]
    if args.skip_nllb:
        targets = [it for it in targets if it.get("method") != "nllb"]
    if args.limit:
        targets = targets[: args.limit]

    print(f"待重译 {len(targets)} 条，worker 数 {args.workers}", flush=True)
    if not targets:
        print("无需重译")
        return 0

    os.makedirs(WORK_DIR, exist_ok=True)
    build_worker_script()

    # 按摘要长度排序后交错分片，让各 worker 负载均衡
    targets.sort(key=lambda x: len(x.get("summary") or ""))
    n = len(targets)
    shards = [[] for _ in range(args.workers)]
    for i, it in enumerate(targets):
        shards[i % args.workers].append(it)

    procs, shard_files, result_files = [], [], []
    for w, shard in enumerate(shards):
        if not shard:
            continue
        sin = os.path.join(WORK_DIR, f"in_{w}.json")
        sout = os.path.join(WORK_DIR, f"out_{w}.json")
        with open(sin, "w", encoding="utf-8") as f:
            json.dump(shard, f, ensure_ascii=False)
        log = open(f"/tmp/retranslate_w{w}.log", "w")
        p = subprocess.Popen(
            [sys.executable, WORKER_SCRIPT, sin, sout],
            stdout=log, stderr=subprocess.STDOUT, cwd=BASE,
        )
        procs.append((w, p, log))
        shard_files.append(sin)
        result_files.append(sout)
        print(f"  worker{w}: {len(shard)} 条 -> {sout}", flush=True)

    t0 = time.time()
    for w, p, log in procs:
        rc = p.wait()
        log.close()
        print(f"  worker{w} 结束 rc={rc} 用时{time.time()-t0:.0f}s", flush=True)

    # 合并分片结果回写主数据文件
    merged = {}
    for rf in result_files:
        if not os.path.exists(rf):
            continue
        with open(rf, "r", encoding="utf-8") as f:
            for it in json.load(f):
                merged[it["id"]] = it

    updated = 0
    for it in items:
        src = merged.get(it["id"])
        if not src:
            continue
        it["title_zh"] = src.get("title_zh") or it.get("title_zh", "")
        it["summary_zh"] = src.get("summary_zh") or it.get("summary_zh", "")
        it["summary"] = src.get("summary") or it.get("summary", "")
        it["method"] = src.get("method") or it.get("method")
        it["translated"] = bool(it.get("title_zh")) and it["title_zh"] != it.get("title")
        updated += 1

    data["items"] = items
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已合并回写 {updated} 条，总耗时 {time.time()-t0:.0f}s", flush=True)

    # 清理分片临时文件
    for pth in shard_files + result_files:
        try:
            os.remove(pth)
        except OSError:
            pass
    try:
        os.remove(WORKER_SCRIPT)
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
