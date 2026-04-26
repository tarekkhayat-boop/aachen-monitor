import asyncio
import os
import httpx
from playwright.async_api import async_playwright
from datetime import datetime

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
CHECK_URL = "https://termine.staedteregion-aachen.de/auslaenderamt/suggest"

async def get_page_content():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(CHECK_URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        content = await page.inner_text("body")
        await browser.close()
        return content

def send_telegram_alert(message):
    httpx.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
    )

async def main():
    print(f"[{datetime.now()}] Checking appointments...")
    content = await get_page_content()

    early_keywords = ["April", "Mai", "Apr", "May"]
    found = any(kw in content for kw in early_keywords)

    if found:
        print("✅ Early slot found! Alerting...")
        send_telegram_alert(
            f"🚨 <b>New Aachen appointment available!</b>\n\n"
            f"Book now: {CHECK_URL}"
        )
    else:
        print("❌ Nothing early yet.")

if __name__ == "__main__":
    asyncio.run(main())