import asyncio
from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:8080'
OUT = '/workspace/ai-news'

async def check_styles(page):
    return await page.evaluate("""() => {
        const res = {};
        let beforeCount = 0;
        for (const sheet of document.styleSheets) {
            let rules;
            try { rules = sheet.cssRules; } catch (e) { continue; }
            for (const rule of rules) {
                if (rule.selectorText && rule.selectorText.includes('.entry::before')) beforeCount++;
            }
        }
        res.entry_before_rules = beforeCount;
        const entry = document.querySelector('.entry');
        res.entry_before_content = entry ? getComputedStyle(entry, '::before').content : '(no .entry)';
        const m = document.querySelector('.metrics');
        if (m) {
            const cs = getComputedStyle(m);
            res.metrics_padding_all_zero = [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft].every(v => parseFloat(v) === 0);
        }
        const btns = Array.from(document.querySelectorAll('button, a'));
        res.sync_buttons = btns.filter(b => /同步|sync|refresh|刷新/i.test(b.textContent || '')).map(b => (b.textContent||'').trim());
        res.entries = document.querySelectorAll('.entry').length;
        res.theme = document.documentElement.getAttribute('data-theme');
        return res;
    }""")

async def shoot(pw, name, color_scheme='light', theme=None, view=None, viewport=None):
    browser = await pw.chromium.launch(args=['--no-sandbox'])
    ctx = await browser.new_context(
        viewport=viewport or {'width': 1440, 'height': 1000},
        device_scale_factor=2,
        locale='zh-CN',
        color_scheme=color_scheme,
    )
    page = await ctx.new_page()
    await page.goto(URL, wait_until='networkidle', timeout=90000)
    await page.wait_for_function("() => document.querySelectorAll('.entry').length > 3", timeout=60000)
    await page.wait_for_timeout(2500)
    if theme:
        try:
            await page.click(f'#themeToggle button[data-theme="{theme}"]')
        except Exception as e:
            print('  theme click skipped:', e)
        await page.wait_for_timeout(1500)
    if view:
        try:
            await page.click(f'#viewToggle button[data-mode="{view}"]')
        except Exception as e:
            print('  view click skipped:', e)
        await page.wait_for_timeout(1500)
    path = f'{OUT}/{name}'
    await page.screenshot(path=path, full_page=False)
    print('saved:', path)
    styles = await check_styles(page)
    print('  styles:', styles)
    await browser.close()
    return styles

async def main():
    async with async_playwright() as pw:
        await shoot(pw, '巡检截图-1400-默认浅色.png', color_scheme='light')
        await shoot(pw, '巡检截图-1400-暗黑.png', color_scheme='dark', theme='dark')
        await shoot(pw, '巡检截图-1400-系统自动.png', color_scheme='light', theme='auto')
        await shoot(pw, '巡检截图-1400-英文原文视图.png', color_scheme='light', view='en')
        print('ALL DONE')

if __name__ == '__main__':
    asyncio.run(main())
