import os, sys
from playwright.sync_api import sync_playwright

OUT = "/workspace/ai-news/screenshots"
os.makedirs(OUT, exist_ok=True)
URL = "http://127.0.0.1:8080"

def wait_ready(page):
    page.wait_for_selector("#statTotal", state="attached")
    # wait until data loaded (total not 0 and entries rendered)
    page.wait_for_function(
        "() => { const t=document.getElementById('statTotal');"
        " return t && t.textContent !== '0' && document.querySelectorAll('.entry').length>0; }",
        timeout=30000,
    )
    page.wait_for_timeout(1200)

def click_theme(page, mode):
    page.click(f"#themeToggle .seg-btn[data-theme='{mode}']")
    page.wait_for_timeout(400)

def click_view(page, mode):
    page.click(f"#viewToggle .seg-btn[data-mode='{mode}']")
    page.wait_for_timeout(400)

shots = []
with sync_playwright() as p:
    # ---- light + zh (default) ----
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width":1280,"height":900}, color_scheme="light")
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle")
    wait_ready(page)
    click_theme(page, "light"); click_view(page, "zh")
    p1 = os.path.join(OUT, "巡检截图-2000-默认浅色.png")
    page.screenshot(path=p1, full_page=False); shots.append(p1)
    # dark + zh
    click_theme(page, "dark"); click_view(page, "zh")
    p2 = os.path.join(OUT, "巡检截图-2000-暗黑.png")
    page.screenshot(path=p2, full_page=False); shots.append(p2)
    # english original view (light)
    click_theme(page, "light"); click_view(page, "en")
    p3 = os.path.join(OUT, "巡检截图-2000-英文原文视图.png")
    page.screenshot(path=p3, full_page=False); shots.append(p3)
    ctx.close(); b.close()

    # ---- auto theme, light system ----
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width":1280,"height":900}, color_scheme="light")
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle")
    wait_ready(page)
    click_theme(page, "auto")
    p4 = os.path.join(OUT, "巡检截图-2000-系统自动-浅.png")
    page.screenshot(path=p4, full_page=False); shots.append(p4)
    ctx.close(); b.close()

    # ---- auto theme, dark system ----
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width":1280,"height":900}, color_scheme="dark")
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle")
    wait_ready(page)
    click_theme(page, "auto")
    p5 = os.path.join(OUT, "巡检截图-2000-系统自动-深.png")
    page.screenshot(path=p5, full_page=False); shots.append(p5)
    ctx.close(); b.close()

for s in shots:
    print("SAVED", s, os.path.getsize(s))
