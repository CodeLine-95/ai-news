
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
