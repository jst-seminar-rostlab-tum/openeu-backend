from crawl4ai.cli import main as crawl4ai_main
from playwright.sync_api import sync_playwright

print("✅ Verifying Playwright browser launch...")
with sync_playwright() as p:
    browser = p.chromium.launch()
    browser.close()
    print("✅ Chromium launched and closed successfully.")

print("✅ Verifying crawl4ai CLI access...")
crawl4ai_main()
