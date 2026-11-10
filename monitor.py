import os
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
EVENT_NAME = os.environ.get("GITHUB_EVENT_NAME")
URL = "https://shop.vodafone.om/ar/product/iphone-18-pro/"

def send_telegram_alert(message):
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(api_url, json=payload, timeout=10)

def check_vodafone_stock():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        try:
            page.goto(URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)

            for option in ["256", "برغندي", "Burgundy"]:
                locator = page.get_by_text(option, exact=False)
                if locator.count() > 0:
                    try:
                        locator.first.click(timeout=2000)
                        page.wait_for_timeout(1000)
                    except:
                        pass

            content = page.content()
            in_stock = ["أضف إلى السلة", "اشتر الآن", "Add to cart", "Buy Now"]
            out_of_stock = ["نفدت الكمية", "غير متوفر", "أعلمني عند التوفر", "Out of stock", "Notify Me"]

            if any(w in content for w in in_stock) and not any(w in content for w in out_of_stock):
                return True
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    is_available = check_vodafone_stock()
    if is_available:
        send_telegram_alert(
            "🚨 <b>تنبيه توفر المخزون!</b>\n\n"
            "هاتف <b>iPhone 18 Pro (256GB - برغندي)</b> متوفر الآن في فودافون عُمان!\n\n"
            f"🔗 <a href='{URL}'>اضغط هنا للشراء المباشر</a>"
        )
    elif EVENT_NAME == "workflow_dispatch":
        send_telegram_alert(
            "✅ <b>تم الربط بنجاح!</b>\n"
            "البوت يعمل الآن في السحابة، والهاتف غير متوفر حالياً. سيصلك إشعار فوري بمجرد توفره."
        )
