from playwright.sync_api import sync_playwright

print("✅ Verifying Playwright browser launch...")
with sync_playwright() as p:
    browser = p.chromium.launch()
    browser.close()
    print("✅ Chromium launched and closed successfully.")
