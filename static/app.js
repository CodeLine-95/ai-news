// AI 信号站 — 前端逻辑
// 后端每小时自动抓取；前端每 60 秒轮询 /api/news，检测到新条目自动重渲染。
// 全站无「手动同步」按钮：数据与页面均自动更新。
// 支持全站切换（中文译文 / 英文原文）与单条切换（看原文 / 看译文）。

const POLL_MS = 60000;
const WEEK = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];

let viewMode = localStorage.getItem("viewMode") || "zh"; // 'zh' | 'en'
const cardOverride = new Map(); // id -> 'zh' | 'en'
let lastIds = new Set();
let nextUpdateTs = null;
let currentItems = [];
let itById = {};
let activeSource = "all"; // 'all' | 具体源名：用于「按数据源分组/筛选」
const sourceCounts = {};   // 源名 -> 当前库内条目数（用于 chips 计数）

// ---------- 主题切换（暗黑 / 默认浅色 / 系统自动） ----------
const THEME_KEY = "themeMode";
let themeMode = localStorage.getItem(THEME_KEY) || "auto"; // 'dark' | 'light' | 'auto'

function effectiveTheme() {
  if (themeMode === "auto") {
    return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  }
  return themeMode;
}
function applyTheme() {
  document.documentElement.setAttribute("data-theme", effectiveTheme());
  // 用显式 add/remove，避免 classList.toggle(force) 在某些渲染上下文下的歧义
  document.querySelectorAll("#themeToggle .seg-btn").forEach((b) => {
    if (b.dataset.theme === themeMode) b.classList.add("active");
    else b.classList.remove("active");
  });
}
function setTheme(t) {
  themeMode = t;
  localStorage.setItem(THEME_KEY, t);
  applyTheme();
}
// 系统自动模式下，跟随操作系统明暗变化实时切换
window.matchMedia("(prefers-color-scheme: light)").addEventListener("change", () => {
  if (themeMode === "auto") applyTheme();
});
document.querySelectorAll("#themeToggle .seg-btn").forEach((b) =>
  b.addEventListener("click", () => setTheme(b.dataset.theme))
);
applyTheme();

const root = document.getElementById("newsRoot");
const toastEl = document.getElementById("toast");

// ---------- 视图切换 ----------
function syncButtons(mode) {
  document.querySelectorAll("#viewToggle .seg-btn").forEach((b) => {
    if (b.dataset.mode === mode) b.classList.add("active");
    else b.classList.remove("active");
  });
}

function setView(mode) {
  viewMode = mode;
  localStorage.setItem("viewMode", mode);
  syncButtons(mode);
  if (currentItems.length) render(currentItems);
}
document.querySelectorAll("#viewToggle .seg-btn").forEach((b) =>
  b.addEventListener("click", () => setView(b.dataset.mode))
);

// ---------- 工具 ----------
function esc(s) {
  return (s || "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}

function todayStr() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

function fmtCountdown() {
  if (!nextUpdateTs) return "--:--";
  const diff = Math.max(0, nextUpdateTs - Date.now());
  const m = Math.floor(diff / 60000);
  const s = Math.floor((diff % 60000) / 1000);
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function fmtLastUpdate(iso) {
  if (!iso) return "未知";
  const d = new Date(iso);
  if (isNaN(d)) return "未知";
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
}

// ---------- 数据获取 ----------
// 线上访问经 sharecode 鉴权，需在 API 请求上透传
const SHARE_CODE = new URLSearchParams(location.search).get("sharecode");

function apiUrl(path) {
  if (!SHARE_CODE) return path;
  return path + (path.includes("?") ? "&" : "?") + "sharecode=" + encodeURIComponent(SHARE_CODE);
}

async function fetchNews() {
  try {
    const res = await fetch(apiUrl("/api/news"), { cache: "no-store" });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();
    applyData(data);
  } catch (e) {
    console.error("拉取失败", e);
    root.innerHTML =
      '<div class="empty">信号中断：' + esc(String(e.message || e)) +
      "，系统将在 60 秒后自动重连。</div>";
    document.getElementById("barStatus").textContent = "连接中断";
    document.getElementById("barStatus").style.color = "var(--red)";
  }
}

function applyData(data) {
  currentItems = data.items || [];
  nextUpdateTs = data.next_update ? Date.parse(data.next_update) : null;

  const items = data.items || [];
  const t = todayStr();
  const days = new Set(items.map((i) => i.date)).size;

  // 每个源在库内的条目数（按源分组筛选用）
  for (const k in sourceCounts) delete sourceCounts[k];
  for (const it of items) sourceCounts[it.source] = (sourceCounts[it.source] || 0) + 1;

  document.getElementById("statToday").textContent = items.filter((i) => i.date === t).length;
  document.getElementById("statTotal").textContent = data.total ?? items.length;
  document.getElementById("statTranslated").textContent = data.translated ?? 0;
  document.getElementById("statDays").textContent = days;
  // 已接入数据源数量：以后台 source_health 统计的接入源为准，
  // 直接回答「当前接入了几个数据源」；前端库内去重计数作为兜底。
  const connected = data.sources ?? Object.keys(sourceCounts).length;
  document.getElementById("statSources").textContent = connected;

  // 按数据源分组筛选条：全量接入源（含本轮静默源）与库内计数并集
  buildChips(data.source_list || Object.keys(sourceCounts));

  const barStatus = document.getElementById("barStatus");
  barStatus.textContent = "信号在线 · 最后更新 " + fmtLastUpdate(data.last_update);
  barStatus.style.color = "var(--green)";

  // 页脚信源列表：按实际抓到的源动态渲染，避免与后台源列表脱节
  const srcEl = document.getElementById("footerSources");
  if (srcEl) {
    const srcs = [...new Set(items.map((i) => i.source))].sort();
    srcEl.textContent = "信源 · " + srcs.join(" · ");
  }

  // 新条目检测
  const curIds = new Set(items.map((i) => i.id));
  if (lastIds.size > 0) {
    let added = 0;
    curIds.forEach((id) => { if (!lastIds.has(id)) added++; });
    if (added > 0) showToast(`自动同步：新增 ${added} 条资讯`);
  }
  lastIds = curIds;

  render(items);
}

// ---------- 按数据源分组 / 筛选 ----------
// 构建筛选 chips：全部 + 每个接入源（带当前库内条目数；本轮静默源标灰）。
function buildChips(sourceList) {
  const row = document.getElementById("chipRow");
  if (!row) return;
  // 若当前选中的源已不在接入清单里（理论上不会，但兜底防止卡死筛选），重置
  const names = [...sourceList];
  if (activeSource !== "all" && !names.includes(activeSource)) activeSource = "all";

  const total = currentItems.length;
  const chips = [];
  chips.push(chipHtml("all", "全部", total, activeSource === "all"));

  names
    .map((n) => ({ n, c: sourceCounts[n] || 0 }))
    .sort((a, b) => b.c - a.c || a.n.localeCompare(b.n))
    .forEach(({ n, c }) => {
      chips.push(chipHtml(n, n, c, activeSource === n, c === 0));
    });

  row.innerHTML = chips.join("");
  row.querySelectorAll(".chip").forEach((el) =>
    el.addEventListener("click", () => setActiveSource(el.dataset.src))
  );
}

function chipHtml(src, label, count, active, silent) {
  const cls = "chip" + (active ? " active" : "") + (silent ? " silent" : "");
  const title = silent ? ' title="已接入，本轮暂无新条目"' : "";
  return `<button class="${cls}" data-src="${esc(src)}"${title}>${esc(label)}<span class="chip-count">${count}</span></button>`;
}

function setActiveSource(src) {
  activeSource = src;
  // 仅更新 chips 高亮，避免整段重绘抖动
  document.querySelectorAll("#chipRow .chip").forEach((el) => {
    el.classList.toggle("active", el.dataset.src === src);
  });
  render(currentItems);
}

// ---------- 渲染 ----------
function render(items) {
  items = items || [];
  // 按数据源分组筛选：仅展示选中源（'all' 表示不过滤）
  if (activeSource !== "all") {
    items = items.filter((i) => i.source === activeSource);
  }
  if (!items.length) {
    root.innerHTML =
      '<div class="empty">该数据源暂无信号，系统将每小时自动抓取；' +
      '可点击「全部」查看所有资讯。</div>';
    return;
  }

  const groups = {};
  for (const it of items) {
    (groups[it.date] = groups[it.date] || []).push(it);
  }
  const dates = Object.keys(groups).sort((a, b) => (a < b ? 1 : -1));

  let html = "";
  for (const date of dates) {
    const list = groups[date];
    const [y, m, d] = date.split("-").map(Number);
    const wd = WEEK[new Date(y, m - 1, d).getDay()];
    html += `<section class="day-group">
      <div class="day-head">
        <span class="day-date">${date}</span>
        <span class="day-week">${wd}</span>
        <span class="day-count">${list.length} 条</span>
      </div>
      <div class="items">`;
    for (const it of list) html += entryHtml(it);
    html += `</div></section>`;
  }
  root.innerHTML = html;

  // 绑定单条语言切换
  root.querySelectorAll(".toggle-lang").forEach((btn) =>
    btn.addEventListener("click", () => {
      const id = btn.dataset.id;
      const cur = effectiveMode(itById[id]);
      cardOverride.set(id, cur === "zh" ? "en" : "zh");
      render(currentItems);
    })
  );
}

function effectiveMode(it) {
  if (cardOverride.has(it.id)) return cardOverride.get(it.id);
  return viewMode;
}

function entryHtml(it) {
  itById[it.id] = it;
  const mode = effectiveMode(it);
  const isZh = mode === "zh";
  const title = isZh ? (it.title_zh || it.title) : it.title;
  const summary = isZh ? (it.summary_zh || it.summary) : it.summary;

  let langTag, langCls = "";
  if (it.lang === "zh") {
    langTag = "中文原文";
  } else if (it.translated) {
    langTag = "已中译";
    langCls = "translated";
  } else {
    langTag = "待译";
  }

  const toggleLabel = isZh ? "看英文原文" : "看中文译文";
  const hasToggle = it.lang === "en";

  return `<article class="entry">
    <time class="entry-time" datetime="${esc(it.iso || "")}">${esc(it.time)}</time>
    <div class="entry-top">
      <span class="source-tag">${esc(it.source)}</span>
      <span class="lang-tag ${langCls}">${langTag}</span>
    </div>
    <h3 class="entry-title ${isZh ? "" : "en"}">${esc(title)}</h3>
    ${summary ? `<p class="entry-summary ${isZh ? "" : "en"}">${esc(summary)}</p>` : ""}
    <div class="entry-foot">
      <a class="src-link" href="${esc(it.link)}" target="_blank" rel="noopener">阅读原文 ↗</a>
      ${hasToggle ? `<button class="toggle-lang" data-id="${esc(it.id)}">${toggleLabel}</button>` : ""}
    </div>
  </article>`;
}

// ---------- Toast ----------
let toastTimer = null;
function showToast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastEl.classList.remove("show"), 3400);
}

// ---------- 时钟 / 引擎状态 ----------
function tick() {
  document.getElementById("barNext").textContent = "下次扫描 " + fmtCountdown();
}

async function loadEngine() {
  try {
    const res = await fetch(apiUrl("/api/status"), { cache: "no-store" });
    if (!res.ok) return;
    const s = await res.json();
    if (s.engine) document.getElementById("barEngine").textContent = "翻译引擎 " + s.engine;
  } catch (e) {
    /* 状态接口不可用时保持默认文案 */
  }
}

// ---------- 启动 ----------
syncButtons(viewMode);
fetchNews();
loadEngine();
setInterval(fetchNews, POLL_MS);
setInterval(loadEngine, POLL_MS);
tick();
setInterval(tick, 1000);
