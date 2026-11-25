"""17:00 例行巡检截图：暗黑 / 浅色 / 系统自动 三档主题。"""
import asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8080/?sharecode=YM64NRHD37"
OUT = "/workspace/ai-news"


async def shoot(browser, theme, filename):
    ctx = await browser.new_context(viewport={"width": 1440, "height": 960}, device_scale_factor=1)
    page = await ctx.new_page()
    # 在页面脚本运行前注入主题偏好
    await page.add_init_script(
        "localStorage.setItem('themeMode', %r);" % theme
    )
    await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(2500)
    actual = await page.evaluate("document.documentElement.getAttribute('data-theme')")
    active = await page.evaluate(
        "document.querySelector('#themeToggle .seg-btn.active')?.dataset.theme || 'none'"
    )
    path = "%s/%s" % (OUT, filename)
    await page.screenshot(path=path, full_page=False)
    print("%s -> 主题=%s 激活按钮=%s 文件=%s" % (theme, actual, active, path))
    await ctx.close()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        await shoot(browser, "dark", "patrol_1700_dark.png")
        await shoot(browser, "light", "patrol_1700_light.png")
        await shoot(browser, "auto", "patrol_1700_auto.png")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
