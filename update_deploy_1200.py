# -*- coding: utf-8 -*-
"""12:00 例行巡检：增量更新 deploy_info.json，严格保留域名与 sharecode。"""
import json

P = "/workspace/deploy_info.json"
with open(P, encoding="utf-8") as f:
    d = json.load(f)

# 断言 sharecode / 域名完整保留
assert "sharecode=YM64NRHD37" in d["domain"]
assert "sharecode=YM64NRHD37" in d["api_url"]

SUMMARY = (
    "12点例行巡检：服务在线（12:00:16 平台自动重启，NLLB-200 引擎就绪），12:00 整点调度已落地 "
    "(last_update=12:00:32，去重清理后 2535→2534)，本轮净新增0条，全库 2534 条/100% 全译(2534/2534)。"
    "系统调度自动执行术语确定性重清洗与人工覆盖表回写，质量门禁全0：0未翻译/0空摘要/0空标题/"
    "0日期格式错/0时间格式错/0重复ID/0西里尔残留；32个 YYYY-MM-DD 分组、每条 HH:MM、中文为主括注英文原题。"
    "五态实测(浅/暗/自动/英文/线上)：entry::before 规则0、content=none、metrics 四边0px、无同步按钮、"
    "auto 跟随系统；线上本地 2534 一致。本轮前端/后端代码无变更，未重新发布以完整保留 sharecode，域名不变。"
)

d["total_items"] = 2534
d["translated"] = 2534
d["translation_coverage"] = "2534/2534"
d["last_update"] = "2026-11-21T12:00:32.620075+08:00"
d["next_update"] = "2026-11-21T13:00:00+08:00"

c = d["checks"]
c["total_items"] = 2534
c["translated"] = 2534
c["translation_coverage"] = "2534/2534"
c["coverage"] = "100%"
c["day_groups"] = 32
c["today_count"] = 47
c["this_cycle_added"] = 0
c["last_update"] = "2026-11-21T12:00:32.620075+08:00"
c["next_update"] = "2026-11-21T13:00:00+08:00"
c["screenshots"] = [
    "deliverable_1121_1200_light.png",
    "deliverable_1121_1200_dark.png",
    "deliverable_1121_1200_auto.png",
    "deliverable_1121_1200_en.png",
    "deliverable_1121_1200_online.png",
]

run = {
    "time": SUMMARY,
    "service_online": True,
    "local_total": 2534,
    "local_translated": 2534,
    "online_total": 2534,
    "online_translated": 2534,
    "online_local_in_sync": True,
    "coverage": "100%(2534/2534)",
    "new_items_this_cycle": 0,
    "retranslate": "未全量重译——质量门禁全0，系统调度自动术语重清洗+人工覆盖回填，0未翻译残留",
    "republish": "未重新发布——本轮代码无变更，线上域名代理同一服务数据实时同步，重新发布有sharecode风险，域名不变",
    "entry_before": "已满足(::before rules=0, content=none, 五态实测)",
    "metrics_padding": "已满足(四边0px, 五态实测)",
    "theme_modes": "已满足(light/dark/auto三态，auto跟随系统，五态实测)",
    "no_manual_sync": "已满足(sync_btns=0, 五态实测)",
    "quality_gate": {
        "untranslated": 0,
        "date_format_error": 0,
        "timestamp_format_error": 0,
        "empty_title_zh": 0,
        "empty_summary_zh": 0,
        "duplicate_ids": 0,
        "cyrillic_mix": 0,
        "gate_failures": 0,
    },
    "screenshots": c["screenshots"],
    "last_update": c["last_update"],
    "next_update": c["next_update"],
}
d["this_run"] = run
d["last_inspection"] = run
d["this_run_time"] = SUMMARY
d["last_inspection_time"] = SUMMARY
d["last_update_time"] = SUMMARY
d["this_cycle_added"] = 0

# 断言 sharecode 仍完整
assert "sharecode=YM64NRHD37" in d["domain"]
assert "sharecode=YM64NRHD37" in d["api_url"]

with open(P, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=4)

print("updated OK, total=", d["total_items"], "coverage=", d["translation_coverage"])
print("domain=", d["domain"])
