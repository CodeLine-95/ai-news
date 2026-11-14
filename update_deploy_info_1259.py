import json

P = "/workspace/deploy_info.json"
d = json.load(open(P, encoding="utf-8"))

now = "2026-11-14 12:59（每小时例行巡检）"
this_run = {
    "time": now,
    "type": "例行巡检（每小时）",
    "service_online": True,
    "local_total": 1709,
    "local_translated": 1709,
    "online_total": 1709,
    "online_translated": 1709,
    "online_local_in_sync": True,
    "coverage": "100%（1709/1709 条由 NLLB 完整译出，0 条未译）",
    "new_items_this_cycle": "自 12:00 整点抓取(1709条)至本次巡检(12:59)无新抓取轮次（下次 13:00）；净增 0 条，维持 1709；今日(2026-11-14)累计 40 条",
    "quality_gate": "0 条真未译、0 条缺中文标题、0 条日期格式错误、0 条时间格式错误",
    "css": {
        "entry_before_removed": True,
        "metrics_padding_zero": True,
        "no_manual_sync_button": True,
        "themes": ["dark", "light", "auto"],
        "verified": "实拍(1114_1259)：默认浅色/暗黑/系统自动三视图均正常，.entry::before=False、.metrics padding=0px、sync_button=False、1709 条渲染正常"
    },
    "republish": "无需——核心应用代码(server.py / static/)未变更；线上为本地后端实时代理，数据每小时整点自动抓取，前端每 60 秒轮询自动刷新",
    "git_push": "核心前端/后端代码未变动，不触发重新发布；仅更新巡检元数据 deploy_info.json 与本轮实拍截图并提交推送",
    "fixes_this_run": [
        "巡检确认服务在线（端口 8080；/api/status 与 /api/news 均返回 1709/1709；last_update 2026-11-14T12:00:25，下次 13:00）",
        "校验线上部署与本地实时同步：online_total=1709 / online_translated=1709 / HTTP 200 可达，与本地一致",
        "校验 AI资讯摘要.md 与实时数据对齐（1709 条 / 32 天 / YYYY-MM-DD / HH:MM / 中文为主括注英文），0 条日期/时间格式错误",
        "CSS 回归实拍：.entry::before=False、.metrics padding 全 0px、默认浅色/暗黑/系统自动三主题及中译/原文视图均正常，全站无手动同步按钮",
        "质量修复评估：retranslate.py 未触发（0 真未译）；核心前端/后端代码未变动，不触发重新发布"
    ],
    "requested_changes_status": {
        "entry_before_removed": "已满足（.entry::before 在 CSS 中不存在，实拍确认 entry_before=False）",
        "metrics_padding_zero": "已满足（桌面/平板/手机三处 .metrics 均 padding:0，实拍确认 metrics_padding=0px）",
        "dark_mode": "已满足（themeToggle 含 暗黑/默认/系统 三态，系统自动跟随 prefers-color-scheme）",
        "light_default": "已满足（data-theme=light 复用语义变量翻转为浅色）",
        "system_auto": "已满足（无闪烁脚本按 localStorage('auto') + matchMedia 动态设置 data-theme）",
        "no_manual_sync": "已满足（全站无同步按钮，前端 60s 轮询 + 后端整点抓取自动同步）"
    }
}

d["this_run"] = this_run
d["last_inspection"] = this_run

if "checks" in d:
    d["checks"]["total_items"] = 1709
    d["checks"]["translated"] = 1709
    d["checks"]["local_total"] = 1709
    d["checks"]["local_translated"] = 1709
    d["checks"]["online_total"] = 1709
    d["checks"]["online_translated"] = 1709
    d["checks"]["coverage"] = "100%"
    d["checks"]["last_update"] = "2026-11-14T12:00:25+08:00"
    d["checks"]["untranslated"] = 0
    d["checks"]["no_cjk"] = 0
    d["checks"]["date_format_error"] = 0
    d["checks"]["timestamp_format_error"] = 0
    d["checks"]["gate_failures"] = 0

# sanity: preserve sharecode and domain
assert "YM64NRHD37" in d["domain"], "sharecode missing!"
assert "YM64NRHD37" in d["api_url"], "sharecode missing!"

json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("deploy_info.json updated with 12:59 patrol record; sharecode preserved:", "YM64NRHD37" in d["domain"])
