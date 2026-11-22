# -*- coding: utf-8 -*-
"""09:00 巡检：更新仓库内 deploy_info.json 的本轮状态。"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(BASE, "deploy_info.json")
d = json.load(open(P, encoding="utf-8"))

d["checks"].update({
    "total_items": 2547,
    "translated": 2547,
    "translation_coverage": "2547/2547",
    "coverage": "100%",
    "day_groups": 32,
    "today_count": 13,
    "this_cycle_added": 1,
    "no_cjk": 7,
    "untranslated": 0,
    "empty_title_zh": 0,
    "empty_summary_zh": 0,
    "date_format_error": 0,
    "timestamp_format_error": 0,
    "duplicate_ids": 0,
    "entry_before": 0,
    "metrics_padding": "0px",
    "manual_sync_button": False,
    "quality_gate": {
        "untranslated": 0, "date_format_error": 0, "timestamp_format_error": 0,
        "empty_title_zh": 0, "empty_summary_zh": 0, "cyrillic_mix": 0,
        "duplicate_ids": 0, "gate_failures": 0,
    },
    "screenshots": [
        "deliverable_1122_0900_light.png", "deliverable_1122_0900_dark.png",
        "deliverable_1122_0900_auto.png", "deliverable_1122_0900_en.png",
        "deliverable_1122_0900_online.png",
    ],
    "last_update": "2026-11-22T09:18:41.580813+08:00",
    "next_update": "2026-11-22T10:00:00+08:00",
    "online_local_in_sync": True,
})

d["this_run"] = {
    "time": "09:00例行巡检（平台09:18重启+NLLB就绪，首轮补抓落地；本轮新增1条07:56 Simon Willison/Muru）",
    "service_online": True,
    "local_total": 2547, "local_translated": 2547,
    "online_total": 2547, "online_translated": 2547,
    "online_local_in_sync": True,
    "coverage": "100%(2547/2547)",
    "new_items_this_cycle": 1,
    "quality_fix": "人工定稿1条新增机翻硬伤：Muru（Rust服务器产品名）被音译为『摩鲁』、人名 Graham Dumpleton/项目 wrapture 断裂；标题改为『Muru：Graham Dumpleton 打造的 AI 辅助 Rust 服务器』并重写摘要，写入三层覆盖表(news.json+JSON表+代码层)",
    "retranslate": "未批量重译——质量门禁全0，仅1条专名硬伤人工定稿",
    "republish": "未重新发布——线上与本地为同一服务经持久卷实时同步，域名/sharecode完整保留；本轮仅覆盖表与巡检脚本变更，无前后端运行逻辑或样式变更",
    "git_push": "待推送本轮覆盖表定稿+巡检脚本",
    "entry_before": "已满足(::before规则0,content=none,五态实测)",
    "metrics_padding": "已满足(四边0px,五态实测)",
    "theme_modes": "已满足(light/dark/auto三态,auto跟随系统prefers-color-scheme,五态实测)",
    "no_manual_sync": "已满足(sync_btns=0,五态实测)",
    "sources_silent": ["VentureBeat"],
    "sources_flapping": [],
    "screenshots": [
        "deliverable_1122_0900_light.png", "deliverable_1122_0900_dark.png",
        "deliverable_1122_0900_auto.png", "deliverable_1122_0900_en.png",
        "deliverable_1122_0900_online.png",
    ],
    "last_update": "2026-11-22T09:18:41.580813+08:00",
    "next_update": "2026-11-22T10:00:00+08:00",
}

d["this_cycle_added"] = 1
d["total_items"] = 2547
d["translated"] = 2547
d["translation_coverage"] = "2547/2547"
d["coverage"] = "100%"
d["last_update"] = "2026-11-22T09:18:41.580813+08:00"
d["next_update"] = "2026-11-22T10:00:00+08:00"
d["last_inspection_time"] = "09:00例行巡检（09:18重启后首轮补抓，新增1条Muru）"
d["last_update_time"] = "09:00例行巡检（09:18重启后首轮补抓，新增1条Muru）"

json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=4)
print("deploy_info.json updated")
